"""
Application validation data models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ValidationIssue(BaseModel):
    """Individual validation issue found in an application"""
    field_name: str = Field(..., description="Name of the field with the issue")
    issue_type: str = Field(..., description="Type: missing, mismatch, invalid_format")
    severity: str = Field(..., description="Severity: critical, high, medium, low")
    impact_on_risk: float = Field(..., ge=0.0, le=1.0, description="Contribution to rejection risk")
    description: Optional[str] = Field(None, description="Detailed description of the issue")


class CorrectionGuidance(BaseModel):
    """Guidance for correcting a validation issue"""
    issue_id: str = Field(..., description="ID of the related validation issue")
    guidance_text_hindi: str = Field(..., description="Guidance text in Hindi")
    guidance_text_english: str = Field(..., description="Guidance text in English")
    suggested_action: str = Field(..., description="Specific action to resolve the issue")
    priority: int = Field(..., ge=1, description="Priority (1 = highest)")


class ApplicationValidation(BaseModel):
    """
    Application validation result
    Validates: Requirements 6.1
    """
    application_id: str = Field(..., description="Unique application identifier")
    scheme_type: str = Field(..., description="Type of scheme being applied for")
    rejection_risk_score: float = Field(..., ge=0.0, le=1.0, description="Probability of rejection")
    validation_issues: List[ValidationIssue] = Field(default_factory=list, description="List of validation issues")
    corrective_guidance: List[CorrectionGuidance] = Field(default_factory=list, description="Guidance for corrections")
    validated_at: datetime = Field(default_factory=datetime.utcnow, description="Validation timestamp")
    operator_id: str = Field(..., description="ID of the CSC operator")

    class Config:
        json_schema_extra = {
            "example": {
                "application_id": "APP123456",
                "scheme_type": "widow_pension",
                "rejection_risk_score": 0.35,
                "validation_issues": [
                    {
                        "field_name": "spouse_death_certificate",
                        "issue_type": "missing",
                        "severity": "critical",
                        "impact_on_risk": 0.25,
                        "description": "Death certificate not uploaded"
                    }
                ],
                "corrective_guidance": [
                    {
                        "issue_id": "ISS001",
                        "guidance_text_hindi": "कृपया पति का मृत्यु प्रमाण पत्र अपलोड करें",
                        "guidance_text_english": "Please upload spouse's death certificate",
                        "suggested_action": "Upload death certificate from civil records",
                        "priority": 1
                    }
                ],
                "validated_at": "2024-01-15T14:20:00Z",
                "operator_id": "OP789"
            }
        }


class ApplicationValidationCreate(BaseModel):
    """Request model for validating an application"""
    application_id: str
    scheme_type: str
    operator_id: str
    application_data: dict = Field(..., description="Application form data to validate")


class ApplicationValidationResponse(BaseModel):
    """Response model for validation operations"""
    success: bool
    message: str
    validation: Optional[ApplicationValidation] = None
