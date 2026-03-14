"""
Tests for RejectionPatternAnalyzer
Validates: Requirements 17.1, 17.2, 17.4, 17.5
"""
import csv
import io
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from models.rejection_pattern_analyzer import (
    REFRESH_INTERVAL,
    RejectionPattern,
    RejectionPatternAnalyzer,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_csv(rows: list[dict], fieldnames: list[str] | None = None) -> str:
    """Build a CSV string from a list of row dicts."""
    if not rows and not fieldnames:
        return ""
    fields = fieldnames or list(rows[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def _write_tmp_csv(content: str) -> str:
    """Write content to a temp file and return its path."""
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    )
    f.write(content)
    f.close()
    return f.name


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_ROWS = [
    # scheme_type=widow_pension, 3 total, 2 rejected
    {
        "application_id": "A1",
        "scheme_type": "widow_pension",
        "applicant_name": "Alice",
        "date_of_birth": "1970-01-01",
        "status": "rejected",
        "operator_id": "OP1",
    },
    {
        "application_id": "A2",
        "scheme_type": "widow_pension",
        "applicant_name": "Bob",
        "date_of_birth": "1965-05-10",
        "status": "rejected",
        "operator_id": "OP1",
    },
    {
        "application_id": "A3",
        "scheme_type": "widow_pension",
        "applicant_name": "Carol",
        "date_of_birth": "1980-03-15",
        "status": "approved",
        "operator_id": "OP2",
    },
    # scheme_type=old_age_pension, 2 total, 1 rejected
    {
        "application_id": "A4",
        "scheme_type": "old_age_pension",
        "applicant_name": "Dave",
        "date_of_birth": "1950-07-20",
        "status": "rejected",
        "operator_id": "OP2",
    },
    {
        "application_id": "A5",
        "scheme_type": "old_age_pension",
        "applicant_name": "Eve",
        "date_of_birth": "1948-11-30",
        "status": "approved",
        "operator_id": "OP3",
    },
]

SAMPLE_FIELDS = [
    "application_id",
    "scheme_type",
    "applicant_name",
    "date_of_birth",
    "status",
    "operator_id",
]


@pytest.fixture
def sample_csv_path():
    content = _make_csv(SAMPLE_ROWS, SAMPLE_FIELDS)
    path = _write_tmp_csv(content)
    yield path
    os.unlink(path)


@pytest.fixture
def analyzer(sample_csv_path):
    return RejectionPatternAnalyzer(csv_path=sample_csv_path)


# ---------------------------------------------------------------------------
# Tests: compute_rejection_frequencies (Requirement 17.1)
# ---------------------------------------------------------------------------

class TestComputeRejectionFrequencies:
    def test_patterns_populated_after_init(self, analyzer):
        assert len(analyzer._patterns) > 0

    def test_score_calculation_widow_pension_applicant_name(self, analyzer):
        """2 rejected out of 3 total → score = 2/3 ≈ 0.667"""
        pattern = analyzer._patterns.get(("applicant_name", "widow_pension"))
        assert pattern is not None
        assert pattern.rejected_count == 2
        assert pattern.total_applications == 3
        assert abs(pattern.rejection_frequency_score - 2 / 3) < 1e-9

    def test_score_calculation_old_age_pension(self, analyzer):
        """1 rejected out of 2 total → score = 0.5"""
        pattern = analyzer._patterns.get(("applicant_name", "old_age_pension"))
        assert pattern is not None
        assert pattern.rejected_count == 1
        assert pattern.total_applications == 2
        assert abs(pattern.rejection_frequency_score - 0.5) < 1e-9

    def test_excluded_columns_not_in_patterns(self, analyzer):
        """application_id, scheme_type, status, operator_id must not appear as field_name."""
        excluded = {"application_id", "scheme_type", "status", "operator_id"}
        for (field_name, _) in analyzer._patterns:
            assert field_name not in excluded

    def test_last_refreshed_is_recent(self, analyzer):
        now = datetime.utcnow()
        for pattern in analyzer._patterns.values():
            delta = now - pattern.last_refreshed
            assert delta.total_seconds() < 5

    def test_empty_field_values_not_counted(self):
        """Rows with empty field values should not be counted."""
        rows = [
            {
                "application_id": "X1",
                "scheme_type": "ration_card",
                "applicant_name": "",  # empty
                "status": "rejected",
                "operator_id": "OP1",
            },
            {
                "application_id": "X2",
                "scheme_type": "ration_card",
                "applicant_name": "Alice",
                "status": "approved",
                "operator_id": "OP1",
            },
        ]
        content = _make_csv(rows)
        path = _write_tmp_csv(content)
        try:
            a = RejectionPatternAnalyzer(csv_path=path)
            pattern = a._patterns.get(("applicant_name", "ration_card"))
            # Only X2 has a non-empty applicant_name; X1 is empty so not counted
            assert pattern is not None
            assert pattern.total_applications == 1
            assert pattern.rejected_count == 0
        finally:
            os.unlink(path)

    def test_application_type_column_used_as_scheme_type(self):
        """CSV with application_type instead of scheme_type should work."""
        rows = [
            {
                "application_id": "Y1",
                "application_type": "bpl_card",
                "applicant_name": "Zara",
                "status": "rejected",
            },
            {
                "application_id": "Y2",
                "application_type": "bpl_card",
                "applicant_name": "Yusuf",
                "status": "approved",
            },
        ]
        content = _make_csv(rows)
        path = _write_tmp_csv(content)
        try:
            a = RejectionPatternAnalyzer(csv_path=path)
            pattern = a._patterns.get(("applicant_name", "bpl_card"))
            assert pattern is not None
            assert pattern.total_applications == 2
            assert pattern.rejected_count == 1
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# Tests: get_high_risk_fields (Requirement 17.2)
# ---------------------------------------------------------------------------

class TestGetHighRiskFields:
    def test_returns_only_above_threshold(self, analyzer):
        """Default threshold=0.3; widow_pension applicant_name score ≈ 0.667 > 0.3."""
        results = analyzer.get_high_risk_fields("widow_pension", threshold=0.3)
        for p in results:
            assert p.rejection_frequency_score > 0.3

    def test_sorted_descending(self, analyzer):
        results = analyzer.get_high_risk_fields("widow_pension", threshold=0.0)
        scores = [p.rejection_frequency_score for p in results]
        assert scores == sorted(scores, reverse=True)

    def test_capped_at_10(self):
        """Generate 15 fields for one scheme; result must be ≤ 10."""
        fields = ["application_id", "scheme_type", "status", "operator_id"] + [
            f"field_{i}" for i in range(15)
        ]
        rows = []
        for i in range(15):
            row = {
                "application_id": f"ID{i}",
                "scheme_type": "test_scheme",
                "status": "rejected",
                "operator_id": "OP1",
            }
            for j in range(15):
                row[f"field_{j}"] = f"val_{i}_{j}" if j <= i else ""
            rows.append(row)
        content = _make_csv(rows, fields)
        path = _write_tmp_csv(content)
        try:
            a = RejectionPatternAnalyzer(csv_path=path)
            results = a.get_high_risk_fields("test_scheme", threshold=0.0)
            assert len(results) <= 10
        finally:
            os.unlink(path)

    def test_filters_by_scheme_type(self, analyzer):
        results = analyzer.get_high_risk_fields("widow_pension")
        for p in results:
            assert p.scheme_type == "widow_pension"

    def test_empty_result_for_unknown_scheme(self, analyzer):
        results = analyzer.get_high_risk_fields("nonexistent_scheme")
        assert results == []

    def test_threshold_boundary_exclusive(self, analyzer):
        """Score exactly equal to threshold should NOT be included."""
        rows = [
            {
                "application_id": "B1",
                "scheme_type": "boundary_scheme",
                "field_a": "val",
                "status": "rejected",
                "operator_id": "OP1",
            },
            {
                "application_id": "B2",
                "scheme_type": "boundary_scheme",
                "field_a": "val",
                "status": "rejected",
                "operator_id": "OP1",
            },
            {
                "application_id": "B3",
                "scheme_type": "boundary_scheme",
                "field_a": "val",
                "status": "approved",
                "operator_id": "OP1",
            },
            {
                "application_id": "B4",
                "scheme_type": "boundary_scheme",
                "field_a": "val",
                "status": "approved",
                "operator_id": "OP1",
            },
        ]
        # score = 2/4 = 0.5; threshold=0.5 → should NOT appear
        content = _make_csv(rows)
        path = _write_tmp_csv(content)
        try:
            a = RejectionPatternAnalyzer(csv_path=path)
            results = a.get_high_risk_fields("boundary_scheme", threshold=0.5)
            assert len(results) == 0
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# Tests: export_csv (Requirement 17.5)
# ---------------------------------------------------------------------------

class TestExportCsv:
    def test_returns_string(self, analyzer):
        result = analyzer.export_csv("widow_pension")
        assert isinstance(result, str)

    def test_has_correct_headers(self, analyzer):
        result = analyzer.export_csv("widow_pension")
        reader = csv.DictReader(io.StringIO(result))
        expected_headers = {
            "field_name",
            "scheme_type",
            "rejected_count",
            "total_applications",
            "rejection_frequency_score",
            "last_refreshed",
        }
        assert set(reader.fieldnames) == expected_headers

    def test_only_contains_requested_scheme(self, analyzer):
        result = analyzer.export_csv("widow_pension")
        reader = csv.DictReader(io.StringIO(result))
        for row in reader:
            assert row["scheme_type"] == "widow_pension"

    def test_empty_csv_for_unknown_scheme(self, analyzer):
        result = analyzer.export_csv("nonexistent_scheme")
        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)
        assert rows == []

    def test_scores_are_numeric(self, analyzer):
        result = analyzer.export_csv("widow_pension")
        reader = csv.DictReader(io.StringIO(result))
        for row in reader:
            score = float(row["rejection_frequency_score"])
            assert 0.0 <= score <= 1.0

    def test_counts_are_integers(self, analyzer):
        result = analyzer.export_csv("widow_pension")
        reader = csv.DictReader(io.StringIO(result))
        for row in reader:
            assert int(row["rejected_count"]) >= 0
            assert int(row["total_applications"]) > 0


# ---------------------------------------------------------------------------
# Tests: 24-hour refresh (Requirement 17.4)
# ---------------------------------------------------------------------------

class TestAutoRefresh:
    def test_no_refresh_within_24h(self, analyzer):
        original_time = analyzer._last_computed
        analyzer._maybe_refresh()
        assert analyzer._last_computed == original_time

    def test_refresh_triggered_after_24h(self, sample_csv_path):
        a = RejectionPatternAnalyzer(csv_path=sample_csv_path)
        # Simulate 24+ hours elapsed
        a._last_computed = datetime.utcnow() - REFRESH_INTERVAL - timedelta(seconds=1)
        old_time = a._last_computed
        a._maybe_refresh()
        assert a._last_computed > old_time

    def test_last_refreshed_updated_on_refresh(self, sample_csv_path):
        a = RejectionPatternAnalyzer(csv_path=sample_csv_path)
        a._last_computed = datetime.utcnow() - REFRESH_INTERVAL - timedelta(seconds=1)
        a._maybe_refresh()
        for pattern in a._patterns.values():
            delta = datetime.utcnow() - pattern.last_refreshed
            assert delta.total_seconds() < 5


# ---------------------------------------------------------------------------
# Tests: RejectionPattern dataclass
# ---------------------------------------------------------------------------

class TestRejectionPatternDataclass:
    def test_fields_present(self):
        now = datetime.utcnow()
        p = RejectionPattern(
            field_name="applicant_name",
            scheme_type="widow_pension",
            rejected_count=5,
            total_applications=10,
            rejection_frequency_score=0.5,
            last_refreshed=now,
        )
        assert p.field_name == "applicant_name"
        assert p.scheme_type == "widow_pension"
        assert p.rejected_count == 5
        assert p.total_applications == 10
        assert p.rejection_frequency_score == 0.5
        assert p.last_refreshed == now


# ---------------------------------------------------------------------------
# Integration: uses real applications.csv
# ---------------------------------------------------------------------------

class TestWithRealCsv:
    def test_loads_real_csv_without_error(self):
        """Smoke test: analyzer loads the real applications.csv successfully."""
        a = RejectionPatternAnalyzer()
        assert len(a._patterns) > 0

    def test_real_csv_patterns_have_valid_scores(self):
        a = RejectionPatternAnalyzer()
        for pattern in a._patterns.values():
            assert 0.0 <= pattern.rejection_frequency_score <= 1.0
            assert pattern.total_applications > 0
            assert pattern.rejected_count <= pattern.total_applications
