"""
Grievance data models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta


class StatusTransition(BaseModel):
    """Record of a status change in grievance lifecycle"""
    from_status: str = Field(..., description="Previous status")
    to_status: str = Field(..., description="New status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the transition occurred")
    changed_by: Optional[str] = Field(None, description="User who made the change")
    reason: Optional[str] = Field(None, description="Reason for the change")


class Grievance(BaseModel):
    """
    Grievance submitted by citizens
    Validates: Requirements 5.1
    """
    grievance_id: str = Field(..., description="Unique grievance identifier (UUID)")
    citizen_id: str = Field(..., description="ID of the citizen who submitted the grievance")
    text: str = Field(..., description="Original grievance text in Hindi/Chhattisgarhi")
    language: str = Field(..., description="Language code: 'hi' for Hindi or 'chhattisgarhi'")
    category: str = Field(..., description="Classified department/category")
    classification_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence of classification")
    predicted_sla: int = Field(..., description="Predicted SLA in hours")
    assigned_department: str = Field(..., description="Department assigned to handle the grievance")
    assigned_officer_id: Optional[str] = Field(None, description="ID of assigned officer")
    status: str = Field(
        default="submitted",
        description="Status: submitted, assigned, in_progress, resolved, escalated"
    )
    escalation_level: int = Field(default=0, description="Escalation level (0 = initial, 1+ = escalated)")
    submitted_at: datetime = Field(default_factory=datetime.utcnow, description="Submission timestamp")
    sla_deadline: datetime = Field(..., description="SLA deadline for resolution")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    status_history: List[StatusTransition] = Field(default_factory=list, description="History of status changes")

    class Config:
        json_schema_extra = {
            "example": {
                "grievance_id": "660e8400-e29b-41d4-a716-446655440001",
                "citizen_id": "CIT123456",
                "text": "मेरा राशन कार्ड अभी तक नहीं बना है",
                "language": "hi",
                "category": "Food & Civil Supplies",
                "classification_confidence": 0.96,
                "predicted_sla": 72,
                "assigned_department": "Food & Civil Supplies",
                "status": "submitted",
                "escalation_level": 0,
                "submitted_at": "2024-01-15T10:30:00Z",
                "sla_deadline": "2024-01-18T10:30:00Z"
            }
        }


class GrievanceCreate(BaseModel):
    """Request model for creating a new grievance"""
    citizen_id: str
    text: str
    language: str = Field(..., description="Language code: 'hi' or 'chhattisgarhi'")


class GrievanceResponse(BaseModel):
    """Response model for grievance operations"""
    success: bool
    message: str
    grievance: Optional[Grievance] = None


class EscalationCheckResponse(BaseModel):
    """Response model for escalation check operations"""
    success: bool
    message: str
    total_checked: int = Field(..., description="Total number of grievances checked")
    escalations_needed: int = Field(..., description="Number of grievances needing escalation")
    grievances: List[Grievance] = Field(default_factory=list, description="List of grievances needing escalation")
