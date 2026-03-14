"""
Pydantic models and reconciliation logic for offline-to-online anomaly reconciliation.
Validates: Requirements 16.5
"""
from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Severity weights used for score derivation from merged anomaly list
# ---------------------------------------------------------------------------
SEVERITY_WEIGHTS: Dict[str, float] = {
    "critical": 0.40,
    "high": 0.25,
    "medium": 0.15,
    "low": 0.05,
}


class LocalAnomalyInput(BaseModel):
    """A single anomaly flag reported by the offline device."""
    field_name: str
    anomaly_type: str
    description: str
    severity: str  # critical | high | medium | low


class ReconcileAnomaliesRequest(BaseModel):
    """Request body for POST /api/application/reconcile-anomalies."""
    application_data: Dict[str, Any] = Field(
        ..., description="Application fields (field_name -> value)"
    )
    local_anomalies: List[LocalAnomalyInput] = Field(
        default_factory=list,
        description="Anomaly flags from the offline device",
    )
    scheme_type: str = Field(..., description="Scheme type being applied for")


class MergedIssue(BaseModel):
    """A single issue in the reconciled result."""
    field_name: str
    anomaly_type: str
    description: str
    severity: str
    source: str  # "local" | "server" | "both"


class ReconcileAnomaliesResponse(BaseModel):
    """Response body for POST /api/application/reconcile-anomalies."""
    rejection_risk_score: float = Field(..., ge=0.0, le=1.0)
    merged_issues: List[MergedIssue]
    source: str = "reconciled"


def reconcile(
    server_score: float,
    server_issues: List[MergedIssue],
    local_anomalies: List[LocalAnomalyInput],
) -> ReconcileAnomaliesResponse:
    """
    Core reconciliation logic (framework-independent).

    1. Start with server-side issues.
    2. Merge local anomalies, deduplicating by (field_name, anomaly_type).
    3. Derive a score from the merged list and take max(server_score, merged_score).
    """
    merged: Dict[tuple, MergedIssue] = {
        (i.field_name, i.anomaly_type): i for i in server_issues
    }

    for la in local_anomalies:
        key = (la.field_name, la.anomaly_type)
        if key in merged:
            existing = merged[key]
            merged[key] = MergedIssue(
                field_name=existing.field_name,
                anomaly_type=existing.anomaly_type,
                description=existing.description,
                severity=existing.severity,
                source="both",
            )
        else:
            merged[key] = MergedIssue(
                field_name=la.field_name,
                anomaly_type=la.anomaly_type,
                description=la.description,
                severity=la.severity,
                source="local",
            )

    merged_issues = list(merged.values())
    merged_score = min(
        sum(SEVERITY_WEIGHTS.get(i.severity, 0.05) for i in merged_issues),
        1.0,
    )
    final_score = max(server_score, merged_score)

    return ReconcileAnomaliesResponse(
        rejection_risk_score=round(final_score, 4),
        merged_issues=merged_issues,
        source="reconciled",
    )
