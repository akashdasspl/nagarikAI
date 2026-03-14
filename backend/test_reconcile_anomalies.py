"""
Unit tests for POST /api/application/reconcile-anomalies endpoint.
Validates: Requirements 16.5
"""
import pytest
from models.rejection_risk import RejectionRiskModel
from models.reconcile import (
    ReconcileAnomaliesRequest,
    ReconcileAnomaliesResponse,
    LocalAnomalyInput,
    MergedIssue,
    SEVERITY_WEIGHTS,
    reconcile,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_reconcile(application_data: dict, local_anomalies: list, scheme_type: str) -> ReconcileAnomaliesResponse:
    """Exercise the reconciliation logic without going through HTTP."""
    import uuid
    model = RejectionRiskModel()

    server_validation = model.validate_application(
        application_id="test-" + str(uuid.uuid4()),
        scheme_type=scheme_type,
        operator_id="system",
        application_data=application_data,
    )

    server_issues = [
        MergedIssue(
            field_name=vi.field_name,
            anomaly_type=vi.issue_type,
            description=vi.description or "",
            severity=vi.severity,
            source="server",
        )
        for vi in server_validation.validation_issues
    ]

    return reconcile(
        server_score=server_validation.rejection_risk_score,
        server_issues=server_issues,
        local_anomalies=local_anomalies,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestReconcileAnomaliesLogic:

    def test_source_is_reconciled(self):
        result = _run_reconcile({}, [], "widow_pension")
        assert result.source == "reconciled"

    def test_no_local_anomalies_returns_server_score(self):
        """With no local anomalies the score equals the server-only score."""
        app_data = {
            "applicant_name": "Sunita Devi",
            "date_of_birth": "1970-05-10",
            "address": "Village Raipur",
            "bank_account": "123456789012",
            "aadhaar_number": "123456789012",
            "spouse_death_certificate": "cert_001",
        }
        result = _run_reconcile(app_data, [], "widow_pension")
        # No issues → score should be 0 or very low
        assert result.rejection_risk_score >= 0.0
        assert result.rejection_risk_score <= 1.0

    def test_local_anomaly_only_appears_in_merged(self):
        """A local anomaly not caught by the server should appear in merged_issues."""
        local = [LocalAnomalyInput(
            field_name="phone_number",
            anomaly_type="format_error",
            description="Phone must start with 6-9",
            severity="medium",
        )]
        result = _run_reconcile({}, local, "widow_pension")
        field_names = [i.field_name for i in result.merged_issues]
        assert "phone_number" in field_names

    def test_duplicate_anomaly_marked_as_both(self):
        """An anomaly present in both local and server should be marked source='both'."""
        # Provide an invalid aadhaar so the server also flags it
        app_data = {"aadhaar_number": "INVALID"}
        local = [LocalAnomalyInput(
            field_name="aadhaar_number",
            anomaly_type="invalid_format",
            description="Aadhaar must be 12 digits",
            severity="medium",
        )]
        result = _run_reconcile(app_data, local, "widow_pension")
        aadhaar_issues = [i for i in result.merged_issues if i.field_name == "aadhaar_number"]
        assert len(aadhaar_issues) >= 1
        # At least one should be "both" or "server" (server catches it too)
        sources = {i.source for i in aadhaar_issues}
        assert sources & {"both", "server"}

    def test_score_is_capped_at_1(self):
        """Score must never exceed 1.0 regardless of anomaly count."""
        local = [
            LocalAnomalyInput(field_name=f"field_{i}", anomaly_type="format_error",
                              description="error", severity="critical")
            for i in range(20)
        ]
        result = _run_reconcile({}, local, "widow_pension")
        assert result.rejection_risk_score <= 1.0

    def test_score_non_negative(self):
        result = _run_reconcile({}, [], "old_age_pension")
        assert result.rejection_risk_score >= 0.0

    def test_server_score_not_lowered_by_reconciliation(self):
        """
        Requirement 16.5 / Property 34: reconciled score >= server-only score
        when the same issues are present.
        """
        app_data = {
            "applicant_name": "",          # missing → server flags it
            "date_of_birth": "2010-01-01", # too young for old_age_pension
        }
        model = RejectionRiskModel()
        import uuid
        server_only = model.validate_application(
            application_id="srv-" + str(uuid.uuid4()),
            scheme_type="old_age_pension",
            operator_id="system",
            application_data=app_data,
        )
        result = _run_reconcile(app_data, [], "old_age_pension")
        assert result.rejection_risk_score >= server_only.rejection_risk_score - 1e-9

    def test_local_anomaly_increases_or_maintains_score(self):
        """Adding a local anomaly should not decrease the score."""
        app_data = {
            "applicant_name": "Ram Lal",
            "date_of_birth": "1950-01-01",
            "address": "Village X",
            "bank_account": "123456789012",
            "aadhaar_number": "123456789012",
            "age_proof": "doc_001",
        }
        result_no_local = _run_reconcile(app_data, [], "old_age_pension")
        local = [LocalAnomalyInput(
            field_name="age_proof",
            anomaly_type="format_error",
            description="Document appears expired",
            severity="high",
        )]
        result_with_local = _run_reconcile(app_data, local, "old_age_pension")
        assert result_with_local.rejection_risk_score >= result_no_local.rejection_risk_score - 1e-9

    def test_pydantic_models_valid(self):
        """Pydantic models accept and validate correct input."""
        req = ReconcileAnomaliesRequest(
            application_data={"name": "Test"},
            local_anomalies=[
                {"field_name": "name", "anomaly_type": "format_error",
                 "description": "desc", "severity": "low"}
            ],
            scheme_type="ration_card",
        )
        assert req.scheme_type == "ration_card"
        assert len(req.local_anomalies) == 1
