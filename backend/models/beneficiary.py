"""
Beneficiary Discovery data models
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from .common import SourceRecord


class DeathRecordInput(BaseModel):
    """Input model for death record to discover beneficiaries"""
    record_id: str = Field(..., description="Death record ID")
    name: str = Field(..., description="Name of deceased person")
    father_name: str = Field(..., description="Father's name")
    date_of_death: date = Field(..., description="Date of death")
    age: int = Field(..., description="Age at death")
    gender: str = Field(..., description="Gender (M/F)")
    district: str = Field(..., description="District")
    village: str = Field(..., description="Village")
    registration_date: Optional[date] = None

    class Config:
        json_schema_extra = {
            "example": {
                "record_id": "CDR001",
                "name": "राम कुमार शर्मा",
                "father_name": "श्री मोहन लाल शर्मा",
                "date_of_death": "2023-03-15",
                "age": 67,
                "gender": "M",
                "district": "रायपुर",
                "village": "खमतराई",
                "registration_date": "2023-03-18"
            }
        }


class PotentialBeneficiary(BaseModel):
    """Potential beneficiary discovered from death record"""
    beneficiary_name: str = Field(..., description="Name of potential beneficiary")
    relationship: str = Field(..., description="Relationship to deceased (spouse, dependent)")
    scheme_type: str = Field(..., description="Eligible scheme type")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Match confidence score")
    eligibility_reasoning: str = Field(..., description="Human-readable eligibility explanation")
    source_records: List[SourceRecord] = Field(default_factory=list, description="Matched source records")
    contact_info: Optional[dict] = Field(None, description="Contact information if available")


class BeneficiaryDiscoveryResponse(BaseModel):
    """Response model for beneficiary discovery"""
    success: bool
    message: str
    death_record_id: str
    deceased_name: str
    beneficiaries: List[PotentialBeneficiary] = Field(default_factory=list)
    total_found: int = Field(..., description="Total number of beneficiaries found")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Found 2 potential beneficiaries",
                "death_record_id": "CDR001",
                "deceased_name": "राम कुमार शर्मा",
                "beneficiaries": [
                    {
                        "beneficiary_name": "सीता देवी शर्मा",
                        "relationship": "spouse",
                        "scheme_type": "widow_pension",
                        "confidence_score": 0.92,
                        "eligibility_reasoning": "Matched deceased spouse in ration card records with 92% confidence. Eligible for widow pension scheme.",
                        "source_records": []
                    }
                ],
                "total_found": 2
            }
        }
