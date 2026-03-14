"""
Common data models shared across the platform
"""
from pydantic import BaseModel, Field
from typing import Optional


class Address(BaseModel):
    """Address information for beneficiaries"""
    street: Optional[str] = None
    village: Optional[str] = None
    block: Optional[str] = None
    district: str
    state: str = "Chhattisgarh"
    pincode: Optional[str] = None


class SourceRecord(BaseModel):
    """Reference to a source record from external databases"""
    record_id: str = Field(..., description="Unique identifier of the source record")
    database: str = Field(..., description="Source database name (civil_death, ration_card, aadhaar)")
    matched_fields: dict = Field(default_factory=dict, description="Fields that matched during entity resolution")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the match")
