"""
NagarikAI Platform - Data Models
Pydantic schemas for API requests and responses
"""

from .enrollment import EnrollmentCase, EnrollmentCaseCreate, EnrollmentCaseResponse
from .grievance import Grievance, GrievanceCreate, GrievanceResponse, StatusTransition, EscalationCheckResponse
from .validation import (
    ApplicationValidation,
    ApplicationValidationCreate,
    ApplicationValidationResponse,
    ValidationIssue,
    CorrectionGuidance
)
from .beneficiary import DeathRecordInput, PotentialBeneficiary, BeneficiaryDiscoveryResponse
from .common import Address, SourceRecord

__all__ = [
    # Enrollment models
    "EnrollmentCase",
    "EnrollmentCaseCreate",
    "EnrollmentCaseResponse",
    # Grievance models
    "Grievance",
    "GrievanceCreate",
    "GrievanceResponse",
    "StatusTransition",
    "EscalationCheckResponse",
    # Validation models
    "ApplicationValidation",
    "ApplicationValidationCreate",
    "ApplicationValidationResponse",
    "ValidationIssue",
    "CorrectionGuidance",
    # Beneficiary models
    "DeathRecordInput",
    "PotentialBeneficiary",
    "BeneficiaryDiscoveryResponse",
    # Common models
    "Address",
    "SourceRecord",
]
