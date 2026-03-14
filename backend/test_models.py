"""
Simple test to verify Pydantic models work correctly
"""
from datetime import datetime, date, timedelta
from models import (
    EnrollmentCase,
    EnrollmentCaseCreate,
    Grievance,
    GrievanceCreate,
    ApplicationValidation,
    ApplicationValidationCreate,
    Address,
    SourceRecord,
    ValidationIssue,
    CorrectionGuidance,
)


def test_enrollment_case():
    """Test EnrollmentCase model"""
    address = Address(
        village="Raipur",
        block="Raipur",
        district="Raipur",
        state="Chhattisgarh",
        pincode="492001"
    )
    
    source_record = SourceRecord(
        record_id="REC001",
        database="civil_death",
        matched_fields={"name": "Ram Kumar"},
        confidence_score=0.95
    )
    
    case = EnrollmentCase(
        case_id="550e8400-e29b-41d4-a716-446655440000",
        beneficiary_name="Sita Devi",
        beneficiary_dob=date(1975, 3, 15),
        beneficiary_address=address,
        scheme_type="widow_pension",
        confidence_score=0.92,
        eligibility_reasoning="Matched deceased spouse in civil death records",
        source_records=[source_record],
        status="pending"
    )
    
    print(f"✓ EnrollmentCase created: {case.case_id}")
    assert case.beneficiary_name == "Sita Devi"
    assert case.confidence_score == 0.92
    return case


def test_grievance():
    """Test Grievance model"""
    grievance = Grievance(
        grievance_id="660e8400-e29b-41d4-a716-446655440001",
        citizen_id="CIT123456",
        text="मेरा राशन कार्ड अभी तक नहीं बना है",
        language="hi",
        category="Food & Civil Supplies",
        classification_confidence=0.96,
        predicted_sla=72,
        assigned_department="Food & Civil Supplies",
        status="submitted",
        escalation_level=0,
        sla_deadline=datetime.utcnow() + timedelta(hours=72)
    )
    
    print(f"✓ Grievance created: {grievance.grievance_id}")
    assert grievance.citizen_id == "CIT123456"
    assert grievance.language == "hi"
    return grievance


def test_application_validation():
    """Test ApplicationValidation model"""
    issue = ValidationIssue(
        field_name="spouse_death_certificate",
        issue_type="missing",
        severity="critical",
        impact_on_risk=0.25,
        description="Death certificate not uploaded"
    )
    
    guidance = CorrectionGuidance(
        issue_id="ISS001",
        guidance_text_hindi="कृपया पति का मृत्यु प्रमाण पत्र अपलोड करें",
        guidance_text_english="Please upload spouse's death certificate",
        suggested_action="Upload death certificate from civil records",
        priority=1
    )
    
    validation = ApplicationValidation(
        application_id="APP123456",
        scheme_type="widow_pension",
        rejection_risk_score=0.35,
        validation_issues=[issue],
        corrective_guidance=[guidance],
        operator_id="OP789"
    )
    
    print(f"✓ ApplicationValidation created: {validation.application_id}")
    assert validation.rejection_risk_score == 0.35
    assert len(validation.validation_issues) == 1
    return validation


def test_request_models():
    """Test API request models"""
    address = Address(
        district="Raipur",
        state="Chhattisgarh"
    )
    
    # Test EnrollmentCaseCreate
    case_create = EnrollmentCaseCreate(
        beneficiary_name="Test User",
        beneficiary_dob=date(1980, 1, 1),
        beneficiary_address=address,
        scheme_type="disability",
        confidence_score=0.85,
        eligibility_reasoning="Test reasoning"
    )
    print(f"✓ EnrollmentCaseCreate: {case_create.beneficiary_name}")
    
    # Test GrievanceCreate
    grievance_create = GrievanceCreate(
        citizen_id="CIT999",
        text="Test grievance",
        language="hi"
    )
    print(f"✓ GrievanceCreate: {grievance_create.citizen_id}")
    
    # Test ApplicationValidationCreate
    validation_create = ApplicationValidationCreate(
        application_id="APP999",
        scheme_type="widow_pension",
        operator_id="OP999",
        application_data={"field1": "value1"}
    )
    print(f"✓ ApplicationValidationCreate: {validation_create.application_id}")


if __name__ == "__main__":
    print("Testing Pydantic models...\n")
    
    test_enrollment_case()
    test_grievance()
    test_application_validation()
    test_request_models()
    
    print("\n✅ All model tests passed!")
