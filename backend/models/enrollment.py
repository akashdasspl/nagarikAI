"""
Enrollment case data models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from .common import Address, SourceRecord


class EnrollmentCase(BaseModel):
    """
    Enrollment case for beneficiary discovery
    Validates: Requirements 2.1
    """
    case_id: str = Field(..., description="Unique case identifier (UUID)")
    beneficiary_name: str = Field(..., description="Name of the potential beneficiary")
    beneficiary_dob: date = Field(..., description="Date of birth of the beneficiary")
    beneficiary_address: Address = Field(..., description="Address of the beneficiary")
    scheme_type: str = Field(..., description="Type of scheme (widow_pension, disability, etc.)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Eligibility confidence score")
    eligibility_reasoning: str = Field(..., description="Human-readable explanation of eligibility")
    source_records: List[SourceRecord] = Field(default_factory=list, description="Matched source records")
    assigned_worker_id: Optional[str] = Field(None, description="ID of assigned field worker")
    status: str = Field(
        default="pending",
        description="Case status: pending, assigned, in_progress, completed, rejected"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Case creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "550e8400-e29b-41d4-a716-446655440000",
                "beneficiary_name": "Sita Devi",
                "beneficiary_dob": "1975-03-15",
                "beneficiary_address": {
                    "village": "Raipur",
                    "block": "Raipur",
                    "district": "Raipur",
                    "state": "Chhattisgarh",
                    "pincode": "492001"
                },
                "scheme_type": "widow_pension",
                "confidence_score": 0.92,
                "eligibility_reasoning": "Matched deceased spouse in civil death records",
                "source_records": [],
                "status": "pending"
            }
        }


class EnrollmentCaseCreate(BaseModel):
    """Request model for creating a new enrollment case"""
    beneficiary_name: str
    beneficiary_dob: date
    beneficiary_address: Address
    scheme_type: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    eligibility_reasoning: str
    source_records: List[SourceRecord] = Field(default_factory=list)
    assigned_worker_id: Optional[str] = None


class EnrollmentCaseResponse(BaseModel):
    """Response model for enrollment case operations"""
    success: bool
    message: str
    case: Optional[EnrollmentCase] = None
