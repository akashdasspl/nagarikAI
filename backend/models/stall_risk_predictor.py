"""
Stall Risk Predictor for in-progress applications.
Validates: Requirements 20.1, 20.2, 20.3, 20.4
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading


# ---------------------------------------------------------------------------
# Scheme SLA data (hours)
# ---------------------------------------------------------------------------
SCHEME_SLA_HOURS: Dict[str, int] = {
    "widow_pension": 72,
    "disability_pension": 96,
    "old_age": 72,
    "farmer_support": 120,
    "student_scholarship": 48,
}
DEFAULT_SLA_HOURS = 96

# ---------------------------------------------------------------------------
# Mock operator approval rates (operator_id -> approval_rate in [0, 1])
# ---------------------------------------------------------------------------
OPERATOR_APPROVAL_RATES: Dict[str, float] = {
    "OP001": 0.92,
    "OP002": 0.55,
    "OP003": 0.78,
    "OP004": 0.40,
    "OP005": 0.85,
}
DEFAULT_OPERATOR_APPROVAL_RATE = 0.70

# ---------------------------------------------------------------------------
# Severity weights for issue scoring
# ---------------------------------------------------------------------------
ISSUE_SEVERITY_WEIGHTS: Dict[str, float] = {
    "critical": 1.0,
    "high": 0.6,
    "medium": 0.3,
    "low": 0.1,
}

# Bilingual stall reason templates keyed by primary factor
_STALL_REASONS = {
    "validation_issues": {
        "hindi": "गंभीर सत्यापन समस्याएं आवेदन को रोक सकती हैं",
        "english": "Critical validation issues may stall the application",
    },
    "sla_elapsed": {
        "hindi": "SLA समय सीमा पार हो गई है, आवेदन में देरी हो सकती है",
        "english": "SLA deadline has elapsed, application may be delayed",
    },
    "low_operator_rate": {
        "hindi": "ऑपरेटर की अनुमोदन दर कम है, समीक्षा में देरी संभव है",
        "english": "Operator has a low approval rate, review delay is likely",
    },
    "combined": {
        "hindi": "एकाधिक कारकों के कारण आवेदन रुकने का जोखिम है",
        "english": "Multiple factors contribute to stall risk",
    },
}


@dataclass
class StallRiskAssessment:
    """Result of a stall risk computation for a single application."""
    application_id: str
    stall_risk_score: float                    # [0, 1]
    primary_stall_reason_hindi: str
    primary_stall_reason_english: str
    computed_at: datetime
    contributing_factors: List[Dict]           # list of {factor, weight, raw_score}


class StallRiskPredictor:
    """
    Computes Stall_Risk_Score for in-progress applications and maintains a
    Triage_Queue of high-risk applications.

    Score formula (weighted sum, clamped to [0, 1]):
        score = 0.40 * issue_score
              + 0.35 * sla_score
              + 0.25 * operator_risk_score

    where:
        issue_score        = min(1.0, weighted_issue_total / 2.0)
        sla_score          = min(1.0, elapsed_hours / sla_hours)
        operator_risk_score = 1.0 - operator_approval_rate
    """

    def __init__(self) -> None:
        # Tracked applications: application_id -> kwargs dict for recomputation
        self._tracked: Dict[str, Dict] = {}
        # Latest assessments: application_id -> StallRiskAssessment
        self._assessments: Dict[str, StallRiskAssessment] = {}
        self._lock = threading.Lock()
        self._refresh_timer: Optional[threading.Timer] = None
        self._schedule_refresh()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute_stall_risk(
        self,
        application_id: str,
        application_data: Dict,
        validation_issues: List[Dict],
        scheme_type: str,
        submitted_at: datetime,
        operator_id: str,
    ) -> StallRiskAssessment:
        """
        Compute stall risk for a single application.

        Parameters
        ----------
        application_id   : unique application identifier
        application_data : raw application fields (unused in scoring but kept for extensibility)
        validation_issues: list of dicts with at least a 'severity' key
        scheme_type      : one of the known scheme types (or 'default')
        submitted_at     : when the application was submitted
        operator_id      : CSC operator identifier
        """
        now = datetime.utcnow()

        # --- Factor 1: validation issue score (weight 0.40) ---
        weighted_issue_total = sum(
            ISSUE_SEVERITY_WEIGHTS.get(str(issue.get("severity", "low")).lower(), 0.1)
            for issue in validation_issues
        )
        issue_score = min(1.0, weighted_issue_total / 2.0)

        # --- Factor 2: SLA elapsed score (weight 0.35) ---
        sla_hours = SCHEME_SLA_HOURS.get(scheme_type, DEFAULT_SLA_HOURS)
        elapsed_hours = max(0.0, (now - submitted_at).total_seconds() / 3600.0)
        sla_score = min(1.0, elapsed_hours / sla_hours)

        # --- Factor 3: operator risk score (weight 0.25) ---
        approval_rate = OPERATOR_APPROVAL_RATES.get(operator_id, DEFAULT_OPERATOR_APPROVAL_RATE)
        operator_risk_score = 1.0 - approval_rate

        # --- Weighted sum ---
        raw_score = (
            0.40 * issue_score
            + 0.35 * sla_score
            + 0.25 * operator_risk_score
        )
        stall_risk_score = max(0.0, min(1.0, raw_score))

        # --- Determine primary stall reason ---
        factor_scores = {
            "validation_issues": 0.40 * issue_score,
            "sla_elapsed": 0.35 * sla_score,
            "low_operator_rate": 0.25 * operator_risk_score,
        }
        primary_factor = max(factor_scores, key=lambda k: factor_scores[k])

        # If two factors are close (within 0.05), use "combined"
        sorted_scores = sorted(factor_scores.values(), reverse=True)
        if len(sorted_scores) >= 2 and (sorted_scores[0] - sorted_scores[1]) < 0.05:
            primary_factor = "combined"

        reason = _STALL_REASONS[primary_factor]

        contributing_factors = [
            {"factor": "validation_issues", "weight": 0.40, "raw_score": issue_score},
            {"factor": "sla_elapsed", "weight": 0.35, "raw_score": sla_score},
            {"factor": "low_operator_rate", "weight": 0.25, "raw_score": operator_risk_score},
        ]

        assessment = StallRiskAssessment(
            application_id=application_id,
            stall_risk_score=stall_risk_score,
            primary_stall_reason_hindi=reason["hindi"],
            primary_stall_reason_english=reason["english"],
            computed_at=now,
            contributing_factors=contributing_factors,
        )

        with self._lock:
            self._assessments[application_id] = assessment

        return assessment

    def add_application(
        self,
        application_id: str,
        application_data: Dict,
        validation_issues: List[Dict],
        scheme_type: str,
        submitted_at: datetime,
        operator_id: str,
    ) -> StallRiskAssessment:
        """
        Add an application to the tracking set and compute its initial stall risk.
        """
        kwargs = dict(
            application_id=application_id,
            application_data=application_data,
            validation_issues=validation_issues,
            scheme_type=scheme_type,
            submitted_at=submitted_at,
            operator_id=operator_id,
        )
        with self._lock:
            self._tracked[application_id] = kwargs
        return self.compute_stall_risk(**kwargs)

    def resolve_application(self, application_id: str) -> None:
        """Remove an application from tracking and the triage queue."""
        with self._lock:
            self._tracked.pop(application_id, None)
            self._assessments.pop(application_id, None)

    def get_triage_queue(self, threshold: float = 0.6) -> List[StallRiskAssessment]:
        """
        Return all tracked applications with stall_risk_score > threshold,
        sorted by score descending.

        Validates: Requirements 20.2
        """
        with self._lock:
            queue = [
                a for a in self._assessments.values()
                if a.stall_risk_score > threshold
            ]
        queue.sort(key=lambda a: a.stall_risk_score, reverse=True)
        return queue

    def refresh_all(self) -> None:
        """
        Recompute stall risk scores for all tracked in-progress applications.
        Validates: Requirements 20.4
        """
        with self._lock:
            tracked_snapshot = dict(self._tracked)

        for application_id, kwargs in tracked_snapshot.items():
            self.compute_stall_risk(**kwargs)

    # ------------------------------------------------------------------
    # Internal scheduler (every 30 minutes)
    # ------------------------------------------------------------------

    def _schedule_refresh(self) -> None:
        """Schedule the next refresh_all call 30 minutes from now."""
        self._refresh_timer = threading.Timer(
            interval=30 * 60,  # 30 minutes in seconds
            function=self._scheduled_refresh,
        )
        self._refresh_timer.daemon = True
        self._refresh_timer.start()

    def _scheduled_refresh(self) -> None:
        """Called by the background timer; refreshes scores and reschedules."""
        self.refresh_all()
        self._schedule_refresh()

    def stop_scheduler(self) -> None:
        """Cancel the background refresh timer (useful for testing/cleanup)."""
        if self._refresh_timer is not None:
            self._refresh_timer.cancel()
            self._refresh_timer = None
