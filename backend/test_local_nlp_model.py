"""
Tests for LocalNLPModel – offline field anomaly detection.
Validates: Requirements 16.1, 16.2, 16.3, 16.4
"""
import time
import pytest
from models.local_nlp_model import FieldAnomaly, LocalNLPModel


@pytest.fixture
def model():
    return LocalNLPModel()


# ---------------------------------------------------------------------------
# supported_schemes
# ---------------------------------------------------------------------------

class TestSupportedSchemes:
    def test_returns_list(self, model):
        schemes = model.supported_schemes()
        assert isinstance(schemes, list)

    def test_contains_required_schemes(self, model):
        schemes = model.supported_schemes()
        for s in ["widow_pension", "disability_pension", "old_age_pension",
                  "ration_card", "scholarship"]:
            assert s in schemes


# ---------------------------------------------------------------------------
# parse_field – age
# ---------------------------------------------------------------------------

class TestParseFieldAge:
    def test_valid_age_no_anomaly(self, model):
        assert model.parse_field("age", "30", "ration_card") == []

    def test_non_numeric_age_format_error(self, model):
        anomalies = model.parse_field("age", "abc", "ration_card")
        assert len(anomalies) == 1
        assert anomalies[0].anomaly_type == "format_error"

    def test_age_above_120_implausible(self, model):
        anomalies = model.parse_field("age", "150", "ration_card")
        assert any(a.anomaly_type == "implausible_value" for a in anomalies)

    def test_age_below_zero_implausible(self, model):
        anomalies = model.parse_field("age", "-1", "ration_card")
        assert any(a.anomaly_type == "implausible_value" for a in anomalies)

    def test_old_age_pension_min_60(self, model):
        anomalies = model.parse_field("age", "55", "old_age_pension")
        assert any(a.severity == "critical" for a in anomalies)

    def test_old_age_pension_exactly_60_ok(self, model):
        assert model.parse_field("age", "60", "old_age_pension") == []

    def test_widow_pension_min_18(self, model):
        anomalies = model.parse_field("age", "16", "widow_pension")
        assert any(a.severity == "critical" for a in anomalies)

    def test_scholarship_max_25(self, model):
        anomalies = model.parse_field("age", "30", "scholarship")
        assert any(a.anomaly_type == "implausible_value" for a in anomalies)

    def test_scholarship_min_5(self, model):
        anomalies = model.parse_field("age", "3", "scholarship")
        assert any(a.anomaly_type == "implausible_value" for a in anomalies)

    def test_scholarship_valid_age(self, model):
        assert model.parse_field("age", "15", "scholarship") == []


# ---------------------------------------------------------------------------
# parse_field – income
# ---------------------------------------------------------------------------

class TestParseFieldIncome:
    def test_valid_income_no_anomaly(self, model):
        assert model.parse_field("income", "50000", "widow_pension") == []

    def test_non_numeric_income_format_error(self, model):
        anomalies = model.parse_field("income", "fifty thousand", "widow_pension")
        assert anomalies[0].anomaly_type == "format_error"

    def test_negative_income_implausible(self, model):
        anomalies = model.parse_field("income", "-100", "widow_pension")
        assert any(a.anomaly_type == "implausible_value" for a in anomalies)

    def test_income_exceeds_threshold(self, model):
        anomalies = model.parse_field("income", "200000", "widow_pension")
        assert any(a.anomaly_type == "implausible_value" for a in anomalies)

    def test_annual_income_field_name(self, model):
        anomalies = model.parse_field("annual_income", "200000", "widow_pension")
        assert any(a.anomaly_type == "implausible_value" for a in anomalies)


# ---------------------------------------------------------------------------
# parse_field – name
# ---------------------------------------------------------------------------

class TestParseFieldName:
    def test_valid_name_no_anomaly(self, model):
        assert model.parse_field("name", "Ramesh Kumar", "ration_card") == []

    def test_empty_name_format_error(self, model):
        anomalies = model.parse_field("name", "", "ration_card")
        assert anomalies[0].anomaly_type == "format_error"

    def test_name_with_digits_format_error(self, model):
        anomalies = model.parse_field("applicant_name", "Ram3sh", "ration_card")
        assert any(a.anomaly_type == "format_error" for a in anomalies)

    def test_full_name_field(self, model):
        assert model.parse_field("full_name", "Sita Devi", "widow_pension") == []


# ---------------------------------------------------------------------------
# parse_field – date fields
# ---------------------------------------------------------------------------

class TestParseFieldDate:
    def test_valid_ddmmyyyy(self, model):
        assert model.parse_field("dob", "15/08/1985", "ration_card") == []

    def test_valid_yyyymmdd(self, model):
        assert model.parse_field("date_of_birth", "1985-08-15", "ration_card") == []

    def test_invalid_format(self, model):
        anomalies = model.parse_field("dob", "15-08-1985", "ration_card")
        assert anomalies[0].anomaly_type == "format_error"

    def test_invalid_calendar_date(self, model):
        anomalies = model.parse_field("dob", "31/02/1990", "ration_card")
        assert anomalies[0].anomaly_type == "format_error"

    def test_future_date_implausible(self, model):
        anomalies = model.parse_field("issue_date", "01/01/2099", "ration_card")
        assert any(a.anomaly_type == "implausible_value" for a in anomalies)

    def test_empty_date_format_error(self, model):
        anomalies = model.parse_field("dob", "", "ration_card")
        assert anomalies[0].anomaly_type == "format_error"


# ---------------------------------------------------------------------------
# parse_field – aadhaar_number
# ---------------------------------------------------------------------------

class TestParseFieldAadhaar:
    def test_valid_aadhaar(self, model):
        assert model.parse_field("aadhaar_number", "123456789012", "ration_card") == []

    def test_aadhaar_with_spaces(self, model):
        assert model.parse_field("aadhaar_number", "1234 5678 9012", "ration_card") == []

    def test_aadhaar_too_short(self, model):
        anomalies = model.parse_field("aadhaar_number", "12345", "ration_card")
        assert anomalies[0].anomaly_type == "format_error"

    def test_aadhaar_with_letters(self, model):
        anomalies = model.parse_field("aadhaar_number", "12345678901X", "ration_card")
        assert anomalies[0].anomaly_type == "format_error"


# ---------------------------------------------------------------------------
# parse_field – phone
# ---------------------------------------------------------------------------

class TestParseFieldPhone:
    def test_valid_phone(self, model):
        assert model.parse_field("phone", "9876543210", "ration_card") == []

    def test_phone_starting_with_5_invalid(self, model):
        anomalies = model.parse_field("phone", "5876543210", "ration_card")
        assert anomalies[0].anomaly_type == "format_error"

    def test_phone_too_short(self, model):
        anomalies = model.parse_field("mobile", "987654321", "ration_card")
        assert anomalies[0].anomaly_type == "format_error"

    def test_phone_starting_with_6_valid(self, model):
        assert model.parse_field("phone_number", "6123456789", "ration_card") == []


# ---------------------------------------------------------------------------
# detect_anomalies – cross-field checks
# ---------------------------------------------------------------------------

class TestDetectAnomalies:
    def test_no_anomalies_clean_application(self, model):
        data = {
            "applicant_name": "Sita Devi",
            "age": "35",
            "income": "60000",
            "aadhaar_number": "123456789012",
            "phone": "9876543210",
            "dob": "15/08/1989",
            "marital_status": "widow",
        }
        anomalies = model.detect_anomalies(data, "widow_pension")
        assert anomalies == []

    def test_multiple_field_errors_detected(self, model):
        data = {
            "applicant_name": "Ram3sh",
            "age": "abc",
            "aadhaar_number": "123",
        }
        anomalies = model.detect_anomalies(data, "ration_card")
        assert len(anomalies) >= 3

    def test_cross_field_widow_pension_wrong_marital_status(self, model):
        data = {
            "applicant_name": "Sita Devi",
            "age": "35",
            "marital_status": "married",
        }
        anomalies = model.detect_anomalies(data, "widow_pension")
        cross = [a for a in anomalies if a.anomaly_type == "cross_field_inconsistency"]
        assert len(cross) >= 1
        assert cross[0].field_name == "marital_status"
        assert cross[0].severity == "critical"

    def test_cross_field_widow_pension_correct_marital_status(self, model):
        data = {"marital_status": "widowed", "age": "40"}
        anomalies = model.detect_anomalies(data, "widow_pension")
        cross = [a for a in anomalies if a.anomaly_type == "cross_field_inconsistency"]
        assert cross == []

    def test_cross_field_adult_required_underage(self, model):
        data = {"age": "15"}
        anomalies = model.detect_anomalies(data, "old_age_pension")
        cross = [a for a in anomalies if a.anomaly_type == "cross_field_inconsistency"]
        assert any(a.field_name == "age" for a in cross)

    def test_returns_list_of_field_anomaly(self, model):
        data = {"age": "abc"}
        anomalies = model.detect_anomalies(data, "ration_card")
        assert all(isinstance(a, FieldAnomaly) for a in anomalies)


# ---------------------------------------------------------------------------
# Performance: < 200 ms per field
# ---------------------------------------------------------------------------

class TestPerformance:
    def test_parse_field_under_200ms(self, model):
        start = time.monotonic()
        model.parse_field("age", "25", "ration_card")
        elapsed_ms = (time.monotonic() - start) * 1000
        assert elapsed_ms < 200, f"parse_field took {elapsed_ms:.1f} ms (limit 200 ms)"

    def test_detect_anomalies_large_application_reasonable_time(self, model):
        data = {
            "applicant_name": "Ramesh Kumar",
            "age": "35",
            "income": "50000",
            "aadhaar_number": "123456789012",
            "phone": "9876543210",
            "dob": "01/01/1989",
            "issue_date": "01/06/2020",
            "marital_status": "widow",
            "annual_income": "50000",
        }
        start = time.monotonic()
        model.detect_anomalies(data, "widow_pension")
        elapsed_ms = (time.monotonic() - start) * 1000
        # Full application scan should still be fast (< 1 second)
        assert elapsed_ms < 1000, f"detect_anomalies took {elapsed_ms:.1f} ms"
