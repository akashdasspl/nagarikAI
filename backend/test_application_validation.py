"""
Test suite for CSC Operator Assistant API (Task 4.2)
Tests the POST /api/application/validate endpoint
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from datetime import datetime

client = TestClient(app)


def test_validate_application_success_no_issues():
    """Test validation with a complete, valid application"""
    request_data = {
        "application_id": "APP001",
        "scheme_type": "widow_pension",
        "operator_id": "OP123",
        "application_data": {
            "applicant_name": "Sunita Devi",
            "date_of_birth": "1985-03-15",
            "spouse_death_certificate": "DEATH123",
            "address": "Village Raipur, Block Dhamtari, District Raipur, PIN 492001",
            "bank_account": "1234567890123",
            "aadhaar_number": "123456789012",
            "annual_income": 50000
        }
    }
    
    response = client.post("/api/application/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "validation" in data
    assert data["validation"]["application_id"] == "APP001"
    assert data["validation"]["scheme_type"] == "widow_pension"
    assert data["validation"]["rejection_risk_score"] == 0.0
    assert len(data["validation"]["validation_issues"]) == 0
    assert len(data["validation"]["corrective_guidance"]) == 0


def test_validate_application_missing_required_field():
    """Test validation with missing required field (high risk)"""
    request_data = {
        "application_id": "APP002",
        "scheme_type": "widow_pension",
        "operator_id": "OP123",
        "application_data": {
            "applicant_name": "Sunita Devi",
            "date_of_birth": "1985-03-15",
            # Missing spouse_death_certificate
            "address": "Village Raipur",
            "bank_account": "1234567890123",
            "aadhaar_number": "123456789012"
        }
    }
    
    response = client.post("/api/application/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    validation = data["validation"]
    assert validation["rejection_risk_score"] > 0.0
    assert len(validation["validation_issues"]) > 0
    
    # Check that missing field is identified
    issue_fields = [issue["field_name"] for issue in validation["validation_issues"]]
    assert "spouse_death_certificate" in issue_fields
    
    # Check that guidance is provided
    assert len(validation["corrective_guidance"]) > 0
    guidance = validation["corrective_guidance"][0]
    assert "guidance_text_hindi" in guidance
    assert "guidance_text_english" in guidance
    assert "suggested_action" in guidance


def test_validate_application_age_below_minimum():
    """Test validation with age below minimum requirement (critical risk)"""
    request_data = {
        "application_id": "APP003",
        "scheme_type": "old_age_pension",
        "operator_id": "OP123",
        "application_data": {
            "applicant_name": "Ram Kumar",
            "date_of_birth": "1980-01-01",  # Age ~44, below 60 minimum
            "age_proof": "AADHAAR",
            "address": "Village Bilaspur",
            "bank_account": "9876543210123",
            "aadhaar_number": "987654321098",
            "annual_income": 30000
        }
    }
    
    response = client.post("/api/application/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    validation = data["validation"]
    assert validation["rejection_risk_score"] >= 0.4  # Critical issue
    
    # Check for age-related issue
    issues = validation["validation_issues"]
    age_issues = [i for i in issues if i["field_name"] == "date_of_birth"]
    assert len(age_issues) > 0
    assert age_issues[0]["severity"] == "critical"


def test_validate_application_income_above_threshold():
    """Test validation with income above maximum threshold (high risk)"""
    request_data = {
        "application_id": "APP004",
        "scheme_type": "bpl_card",
        "operator_id": "OP123",
        "application_data": {
            "applicant_name": "Lakshmi Bai",
            "date_of_birth": "1990-05-20",
            "address": "Village Durg",
            "family_members": "4",
            "income_certificate": "INC123",
            "aadhaar_number": "456789012345",
            "annual_income": 150000  # Above 50000 threshold for BPL
        }
    }
    
    response = client.post("/api/application/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    validation = data["validation"]
    assert validation["rejection_risk_score"] > 0.0
    
    # Check for income-related issue
    issues = validation["validation_issues"]
    income_issues = [i for i in issues if i["field_name"] == "annual_income"]
    assert len(income_issues) > 0
    assert income_issues[0]["severity"] == "high"


def test_validate_application_invalid_aadhaar_format():
    """Test validation with invalid Aadhaar number format (medium risk)"""
    request_data = {
        "application_id": "APP005",
        "scheme_type": "ration_card",
        "operator_id": "OP123",
        "application_data": {
            "applicant_name": "Mohan Singh",
            "date_of_birth": "1975-08-10",
            "address": "Village Korba",
            "family_members": "5",
            "income_certificate": "INC456",
            "aadhaar_number": "12345"  # Invalid: too short
        }
    }
    
    response = client.post("/api/application/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    validation = data["validation"]
    assert validation["rejection_risk_score"] > 0.0
    
    # Check for Aadhaar format issue
    issues = validation["validation_issues"]
    aadhaar_issues = [i for i in issues if i["field_name"] == "aadhaar_number"]
    assert len(aadhaar_issues) > 0
    assert aadhaar_issues[0]["severity"] == "medium"


def test_validate_application_multiple_issues():
    """Test validation with multiple issues of different severities"""
    request_data = {
        "application_id": "APP006",
        "scheme_type": "disability_pension",
        "operator_id": "OP123",
        "application_data": {
            "applicant_name": "Geeta Sharma",
            "date_of_birth": "2010-01-01",  # Age ~14, below 18 minimum (critical)
            # Missing disability_certificate (high)
            "address": "Village Raigarh",
            "bank_account": "123",  # Invalid format (medium)
            "aadhaar_number": "111222333444",
            "disability_percentage": 30  # Below 40% minimum (high)
        }
    }
    
    response = client.post("/api/application/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    validation = data["validation"]
    # Should have high risk due to multiple issues
    assert validation["rejection_risk_score"] >= 0.5
    
    # Should have multiple issues
    assert len(validation["validation_issues"]) >= 3
    
    # Guidance should be prioritized by severity
    guidance = validation["corrective_guidance"]
    assert len(guidance) > 0
    # First guidance item should have highest priority (lowest number)
    priorities = [g["priority"] for g in guidance]
    assert priorities == sorted(priorities)


def test_validate_application_unknown_scheme():
    """Test validation with unknown scheme type"""
    request_data = {
        "application_id": "APP007",
        "scheme_type": "unknown_scheme",
        "operator_id": "OP123",
        "application_data": {
            "applicant_name": "Test User"
        }
    }
    
    response = client.post("/api/application/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    validation = data["validation"]
    # Unknown scheme should be treated as high risk
    assert validation["rejection_risk_score"] >= 0.25


def test_validate_application_missing_request_fields():
    """Test validation with missing required request fields"""
    # Missing application_id
    request_data = {
        "scheme_type": "widow_pension",
        "operator_id": "OP123",
        "application_data": {}
    }
    
    response = client.post("/api/application/validate", json=request_data)
    assert response.status_code == 422  # Validation error from Pydantic


def test_validate_application_disability_percentage_check():
    """Test disability percentage validation for disability pension"""
    request_data = {
        "application_id": "APP008",
        "scheme_type": "disability_pension",
        "operator_id": "OP123",
        "application_data": {
            "applicant_name": "Rajesh Kumar",
            "date_of_birth": "1980-06-15",
            "disability_certificate": "DISAB123",
            "address": "Village Janjgir",
            "bank_account": "5555666677778888",
            "aadhaar_number": "222333444555",
            "disability_percentage": 35,  # Below 40% minimum
            "annual_income": 40000
        }
    }
    
    response = client.post("/api/application/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    validation = data["validation"]
    assert validation["rejection_risk_score"] > 0.0
    
    # Check for disability percentage issue
    issues = validation["validation_issues"]
    disability_issues = [i for i in issues if i["field_name"] == "disability_percentage"]
    assert len(disability_issues) > 0
    assert disability_issues[0]["severity"] == "high"


def test_guidance_contains_hindi_and_english():
    """Test that corrective guidance includes both Hindi and English text"""
    request_data = {
        "application_id": "APP009",
        "scheme_type": "widow_pension",
        "operator_id": "OP123",
        "application_data": {
            "applicant_name": "Kavita Devi",
            "date_of_birth": "1988-02-20",
            # Missing required fields to trigger guidance
            "address": "Village Mahasamund"
        }
    }
    
    response = client.post("/api/application/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    validation = data["validation"]
    guidance = validation["corrective_guidance"]
    
    assert len(guidance) > 0
    for guide in guidance:
        # Each guidance should have both Hindi and English
        assert guide["guidance_text_hindi"] is not None
        assert guide["guidance_text_english"] is not None
        assert len(guide["guidance_text_hindi"]) > 0
        assert len(guide["guidance_text_english"]) > 0
        # Should have suggested action
        assert guide["suggested_action"] is not None
        assert len(guide["suggested_action"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
