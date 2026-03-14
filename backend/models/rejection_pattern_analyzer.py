"""
Rejection Pattern Analyzer for aggregating rejection frequencies per form field and scheme type.
Validates: Requirements 17.1, 17.2, 17.4, 17.5
"""
import csv
import io
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


# Columns excluded from field analysis
EXCLUDED_COLUMNS = {
    "application_id",
    "scheme_type",
    "status",
    "operator_id",
    "created_at",
    "updated_at",
}

# Default CSV paths (relative to backend dir, with fallback)
DEFAULT_CSV_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "data", "applications.csv"),
    os.path.join("backend", "data", "applications.csv"),
    os.path.join("data", "applications.csv"),
]

# Refresh interval: 24 hours
REFRESH_INTERVAL = timedelta(hours=24)


@dataclass
class RejectionPattern:
    """Aggregated rejection pattern for a (field_name, scheme_type) pair."""
    field_name: str
    scheme_type: str
    rejected_count: int
    total_applications: int
    rejection_frequency_score: float
    last_refreshed: datetime


class RejectionPatternAnalyzer:
    """
    Analyzes historical application data to compute rejection frequency scores
    per form field per scheme type.

    Usage:
        analyzer = RejectionPatternAnalyzer()
        high_risk = analyzer.get_high_risk_fields("widow_pension")
        csv_data = analyzer.export_csv("widow_pension")
    """

    def __init__(self, csv_path: Optional[str] = None):
        """
        Initialize the analyzer and load rejection pattern data.

        Args:
            csv_path: Optional path to the applications CSV file.
                      Defaults to data/applications.csv relative to backend dir.
        """
        self._csv_path = csv_path
        # Dict keyed by (field_name, scheme_type) -> RejectionPattern
        self._patterns: Dict[Tuple[str, str], RejectionPattern] = {}
        self._last_computed: Optional[datetime] = None

        self.compute_rejection_frequencies(csv_path)

    def _resolve_csv_path(self, csv_path: Optional[str]) -> str:
        """Resolve the CSV path, trying defaults if not provided."""
        if csv_path:
            return csv_path

        for path in DEFAULT_CSV_PATHS:
            normalized = os.path.normpath(path)
            if os.path.isfile(normalized):
                return normalized

        # Return first default as fallback (will raise on open if missing)
        return os.path.normpath(DEFAULT_CSV_PATHS[0])

    def _needs_refresh(self) -> bool:
        """Check whether data needs to be refreshed (older than 24 hours)."""
        if self._last_computed is None:
            return True
        return datetime.utcnow() - self._last_computed >= REFRESH_INTERVAL

    def compute_rejection_frequencies(self, csv_path: Optional[str] = None) -> None:
        """
        Load the applications CSV and compute rejection frequency scores per
        (field_name, scheme_type) pair.

        For each field column (excluding application_id, status, scheme_type,
        operator_id, created_at, updated_at), counts how many times that field
        had a non-empty value in rejected applications vs total applications.

        rejection_frequency_score = rejected_count / total_applications

        Args:
            csv_path: Optional path override for the applications CSV.
        """
        resolved_path = self._resolve_csv_path(csv_path or self._csv_path)

        # Accumulators: (field_name, scheme_type) -> {rejected: int, total: int}
        counts: Dict[Tuple[str, str], Dict[str, int]] = {}

        with open(resolved_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []

            # Determine which columns are "field columns"
            field_columns = [
                col for col in fieldnames
                if col.strip().lower() not in EXCLUDED_COLUMNS
            ]

            # The scheme_type column — use application_type if scheme_type absent
            scheme_col = "scheme_type" if "scheme_type" in fieldnames else "application_type"

            for row in reader:
                scheme_type = (row.get(scheme_col) or "").strip()
                status = (row.get("status") or "").strip().lower()
                is_rejected = status == "rejected"

                for col in field_columns:
                    value = (row.get(col) or "").strip()
                    if not value:
                        continue  # Only count rows where the field has a value

                    key = (col, scheme_type)
                    if key not in counts:
                        counts[key] = {"rejected": 0, "total": 0}

                    counts[key]["total"] += 1
                    if is_rejected:
                        counts[key]["rejected"] += 1

        now = datetime.utcnow()
        self._patterns = {}
        for (field_name, scheme_type), c in counts.items():
            total = c["total"]
            rejected = c["rejected"]
            score = rejected / total if total > 0 else 0.0
            self._patterns[(field_name, scheme_type)] = RejectionPattern(
                field_name=field_name,
                scheme_type=scheme_type,
                rejected_count=rejected,
                total_applications=total,
                rejection_frequency_score=score,
                last_refreshed=now,
            )

        self._last_computed = now

    def _maybe_refresh(self) -> None:
        """Refresh data if 24 hours have elapsed since last computation."""
        if self._needs_refresh():
            self.compute_rejection_frequencies()

    def get_high_risk_fields(
        self,
        scheme_type: str,
        threshold: float = 0.3,
    ) -> List[RejectionPattern]:
        """
        Return fields for the given scheme_type where rejection_frequency_score
        exceeds the threshold, sorted descending by score, capped at 10 entries.

        Args:
            scheme_type: The scheme type to filter by.
            threshold: Minimum rejection frequency score (exclusive). Default 0.3.

        Returns:
            List of RejectionPattern, sorted descending by score, max 10 entries.
        """
        self._maybe_refresh()

        results = [
            pattern
            for (fn, st), pattern in self._patterns.items()
            if st == scheme_type and pattern.rejection_frequency_score > threshold
        ]

        results.sort(key=lambda p: p.rejection_frequency_score, reverse=True)
        return results[:10]

    def export_csv(self, scheme_type: str) -> str:
        """
        Export rejection pattern data for the given scheme_type as a CSV string.

        Headers: field_name,scheme_type,rejected_count,total_applications,
                 rejection_frequency_score,last_refreshed

        Args:
            scheme_type: The scheme type to export data for.

        Returns:
            CSV-formatted string with all patterns for the scheme type.
        """
        self._maybe_refresh()

        patterns = [
            pattern
            for (fn, st), pattern in self._patterns.items()
            if st == scheme_type
        ]
        patterns.sort(key=lambda p: p.rejection_frequency_score, reverse=True)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "field_name",
            "scheme_type",
            "rejected_count",
            "total_applications",
            "rejection_frequency_score",
            "last_refreshed",
        ])
        for p in patterns:
            writer.writerow([
                p.field_name,
                p.scheme_type,
                p.rejected_count,
                p.total_applications,
                round(p.rejection_frequency_score, 6),
                p.last_refreshed.isoformat(),
            ])

        return output.getvalue()
