"""
Local NLP Model for offline form field anomaly detection.
Validates: Requirements 16.1, 16.2, 16.3, 16.4
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FieldAnomaly:
    """Represents a single anomaly detected in a form field."""
    field_name: str
    anomaly_type: str   # format_error | implausible_value | cross_field_inconsistency
    description: str
    severity: str       # critical | high | medium | low


# ---------------------------------------------------------------------------
# Scheme-specific configuration
# ---------------------------------------------------------------------------

_SCHEME_AGE_RULES: Dict[str, Dict[str, Any]] = {
    "widow_pension":      {"min": 18,  "max": 120},
    "disability_pension": {"min": 18,  "max": 120},
    "old_age_pension":    {"min": 60,  "max": 120},
    "ration_card":        {"min": 18,  "max": 120},
    "scholarship":        {"min": 5,   "max": 25},
}

_SCHEME_INCOME_THRESHOLDS: Dict[str, float] = {
    "widow_pension":      100_000,
    "disability_pension": 120_000,
    "old_age_pension":    80_000,
    "ration_card":        150_000,
    "scholarship":        200_000,
}

# Schemes that require the applicant to be an adult (18+)
_ADULT_REQUIRED_SCHEMES = {"widow_pension", "disability_pension", "old_age_pension", "ration_card"}

# Supported scheme types
_SUPPORTED_SCHEMES = [
    "widow_pension",
    "disability_pension",
    "old_age_pension",
    "ration_card",
    "scholarship",
]

# Regex patterns
_DATE_DDMMYYYY = re.compile(r"^\d{2}/\d{2}/\d{4}$")
_DATE_YYYYMMDD = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_AADHAAR = re.compile(r"^\d{12}$")
_PHONE = re.compile(r"^[6-9]\d{9}$")
_HAS_DIGIT = re.compile(r"\d")



# ---------------------------------------------------------------------------
# LocalNLPModel
# ---------------------------------------------------------------------------

class LocalNLPModel:
    """
    Regex-rule-based local NLP model for offline form field anomaly detection.

    All inference is performed synchronously using compiled regex rules so that
    each field parse completes well within the 200 ms budget even on low-end
    devices.  No network connection or heavy ML model is required.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def supported_schemes(self) -> List[str]:
        """Return the list of scheme types covered by this model."""
        return list(_SUPPORTED_SCHEMES)

    def parse_field(
        self,
        field_name: str,
        value: Any,
        scheme_type: str,
    ) -> List[FieldAnomaly]:
        """
        Parse a single form field and return any detected anomalies.

        Args:
            field_name:  Name of the form field (e.g. "age", "aadhaar_number").
            value:       Raw value supplied by the operator (str, int, float, ...).
            scheme_type: Scheme being applied for.

        Returns:
            List of FieldAnomaly objects (empty list means no anomalies).
        """
        str_value = str(value).strip() if value is not None else ""
        return self._parse_field_impl(field_name, str_value, scheme_type)

    def detect_anomalies(
        self,
        application_data: Dict[str, Any],
        scheme_type: str,
    ) -> List[FieldAnomaly]:
        """
        Scan all fields in an application and return every detected anomaly.

        Args:
            application_data: Flat dict of field_name -> value.
            scheme_type:      Scheme being applied for.

        Returns:
            Aggregated list of FieldAnomaly objects across all fields.
        """
        anomalies: List[FieldAnomaly] = []

        for fname, fvalue in application_data.items():
            anomalies.extend(self.parse_field(fname, fvalue, scheme_type))

        anomalies.extend(self._cross_field_checks(application_data, scheme_type))
        return anomalies


    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_field_impl(
        self,
        field_name: str,
        value: str,
        scheme_type: str,
    ) -> List[FieldAnomaly]:
        """Dispatch to the appropriate field validator."""
        fn = field_name.lower()

        if fn == "age":
            return self._validate_age(field_name, value, scheme_type)
        if fn in ("income", "annual_income"):
            return self._validate_income(field_name, value, scheme_type)
        if fn in ("name", "applicant_name", "full_name"):
            return self._validate_name(field_name, value)
        if fn in ("dob", "date_of_birth"):
            return self._validate_date(field_name, value)
        if fn in ("issue_date", "date_of_issue"):
            return self._validate_date(field_name, value)
        if fn == "aadhaar_number":
            return self._validate_aadhaar(field_name, value)
        if fn in ("phone", "phone_number", "mobile", "mobile_number"):
            return self._validate_phone(field_name, value)

        return []

    # ---- Individual field validators ----------------------------------

    def _validate_age(self, field_name: str, value: str, scheme_type: str) -> List[FieldAnomaly]:
        anomalies: List[FieldAnomaly] = []

        try:
            age = float(value)
        except (ValueError, TypeError):
            return [FieldAnomaly(
                field_name=field_name,
                anomaly_type="format_error",
                description="Age must be a numeric value.",
                severity="high",
            )]

        if not (0 <= age <= 120):
            anomalies.append(FieldAnomaly(
                field_name=field_name,
                anomaly_type="implausible_value",
                description=f"Age {age} is outside the plausible range (0-120).",
                severity="high",
            ))
            return anomalies

        rules = _SCHEME_AGE_RULES.get(scheme_type)
        if rules:
            if age < rules["min"]:
                anomalies.append(FieldAnomaly(
                    field_name=field_name,
                    anomaly_type="implausible_value",
                    description=(
                        f"Age {int(age)} is below the minimum of {rules['min']} "
                        f"required for {scheme_type}."
                    ),
                    severity="critical",
                ))
            if age > rules["max"]:
                anomalies.append(FieldAnomaly(
                    field_name=field_name,
                    anomaly_type="implausible_value",
                    description=(
                        f"Age {int(age)} exceeds the maximum of {rules['max']} "
                        f"for {scheme_type}."
                    ),
                    severity="medium",
                ))

        return anomalies

    def _validate_income(self, field_name: str, value: str, scheme_type: str) -> List[FieldAnomaly]:
        anomalies: List[FieldAnomaly] = []

        try:
            income = float(value)
        except (ValueError, TypeError):
            return [FieldAnomaly(
                field_name=field_name,
                anomaly_type="format_error",
                description="Income must be a numeric value.",
                severity="high",
            )]

        if income < 0:
            anomalies.append(FieldAnomaly(
                field_name=field_name,
                anomaly_type="implausible_value",
                description="Income cannot be negative.",
                severity="high",
            ))
            return anomalies

        threshold = _SCHEME_INCOME_THRESHOLDS.get(scheme_type)
        if threshold is not None and income > threshold:
            anomalies.append(FieldAnomaly(
                field_name=field_name,
                anomaly_type="implausible_value",
                description=(
                    f"Income {income:.0f} exceeds the maximum threshold of "
                    f"{threshold:.0f} for {scheme_type}."
                ),
                severity="high",
            ))

        return anomalies

    def _validate_name(self, field_name: str, value: str) -> List[FieldAnomaly]:
        anomalies: List[FieldAnomaly] = []

        if not value:
            anomalies.append(FieldAnomaly(
                field_name=field_name,
                anomaly_type="format_error",
                description="Name must not be empty.",
                severity="high",
            ))
            return anomalies

        if _HAS_DIGIT.search(value):
            anomalies.append(FieldAnomaly(
                field_name=field_name,
                anomaly_type="format_error",
                description="Name must not contain numeric characters.",
                severity="medium",
            ))

        return anomalies

    def _validate_date(self, field_name: str, value: str) -> List[FieldAnomaly]:
        """Accept DD/MM/YYYY or YYYY-MM-DD and verify the date is real."""
        if not value:
            return [FieldAnomaly(
                field_name=field_name,
                anomaly_type="format_error",
                description="Date field must not be empty.",
                severity="high",
            )]

        parsed: Optional[datetime] = None

        if _DATE_DDMMYYYY.match(value):
            try:
                parsed = datetime.strptime(value, "%d/%m/%Y")
            except ValueError:
                pass
        elif _DATE_YYYYMMDD.match(value):
            try:
                parsed = datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                pass

        if parsed is None:
            return [FieldAnomaly(
                field_name=field_name,
                anomaly_type="format_error",
                description=(
                    f"'{value}' is not a valid date. "
                    "Expected format: DD/MM/YYYY or YYYY-MM-DD."
                ),
                severity="high",
            )]

        if parsed > datetime.now():
            return [FieldAnomaly(
                field_name=field_name,
                anomaly_type="implausible_value",
                description=f"Date '{value}' is in the future.",
                severity="medium",
            )]

        return []

    def _validate_aadhaar(self, field_name: str, value: str) -> List[FieldAnomaly]:
        cleaned = value.replace(" ", "").replace("-", "")
        if not _AADHAAR.match(cleaned):
            return [FieldAnomaly(
                field_name=field_name,
                anomaly_type="format_error",
                description="Aadhaar number must be exactly 12 digits.",
                severity="high",
            )]
        return []

    def _validate_phone(self, field_name: str, value: str) -> List[FieldAnomaly]:
        cleaned = value.replace(" ", "").replace("-", "")
        if not _PHONE.match(cleaned):
            return [FieldAnomaly(
                field_name=field_name,
                anomaly_type="format_error",
                description=(
                    "Phone number must be 10 digits and start with 6, 7, 8, or 9."
                ),
                severity="medium",
            )]
        return []

    # ---- Cross-field checks -------------------------------------------

    def _cross_field_checks(
        self,
        application_data: Dict[str, Any],
        scheme_type: str,
    ) -> List[FieldAnomaly]:
        anomalies: List[FieldAnomaly] = []

        # Rule 1: widow_pension -> marital_status must be 'widow' or 'widowed'
        if scheme_type == "widow_pension":
            marital = str(application_data.get("marital_status", "")).strip().lower()
            if marital and marital not in ("widow", "widowed"):
                anomalies.append(FieldAnomaly(
                    field_name="marital_status",
                    anomaly_type="cross_field_inconsistency",
                    description=(
                        f"Marital status '{marital}' is inconsistent with "
                        "widow_pension scheme (expected 'widow' or 'widowed')."
                    ),
                    severity="critical",
                ))

        # Rule 2: adult-required schemes -> age must be >= 18
        if scheme_type in _ADULT_REQUIRED_SCHEMES:
            age_raw = application_data.get("age")
            if age_raw is not None:
                try:
                    age = float(str(age_raw).strip())
                    if age < 18:
                        anomalies.append(FieldAnomaly(
                            field_name="age",
                            anomaly_type="cross_field_inconsistency",
                            description=(
                                f"Age {int(age)} is below 18; {scheme_type} "
                                "requires an adult applicant."
                            ),
                            severity="critical",
                        ))
                except (ValueError, TypeError):
                    pass  # format error already caught by parse_field

        return anomalies
