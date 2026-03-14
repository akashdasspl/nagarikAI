"""
Integration test for CSC Operator Assistant API
Tests the complete flow of application validation
"""
import pytest
from fastapi.testclient import TestClient
from main import app, mock_data
from datetime import datetime

client = TestClient(app)


def test_validation_integration_flow():
    """Test complete flow: validate multiple applications and check stored data"""
    
    # Clear mock data
    mock_data["applications"].clear()
    
    # Step 1: Submit a valid application
    valid_app = {
        "application_id": "INT_APP_001",
        "scheme_type": "widow_pension",
        "operator_id": "OP_INT_001",
        "application_data": {
            "applicant_name": "Integration Test User 1",
            "date_of_birth": "1985-03-15",
            "spouse_death_certificate": "DEATH_INT_001",
            "address": "Integration Test Village",
            "bank_account": "1234567890123456",
            "aadhaar_number": "123456789012",
            "annual_income": 50000
        }
    }
    
    response1 = client.post("/api/application/validate", json=valid_app)
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["success"] is True
    assert data1["validation"]["rejection_risk_score"] == 0.0
    
    # Step 2: Submit an application with issues
    invalid_app = {
        "application_id": "INT_APP_002",
        "scheme_type": "old_age_pension",
        "operator_id": "OP_INT_001",
        "application_data": {
            "applicant_name": "Integration Test User 2",
            "date_of_birth": "1980-01-01",  # Age ~44, below 60 minimum
            "age_proof": "AADHAAR",
            "address": "Integration Test Village",
            "bank_account": "9876543210987654",
            "aadhaar_number": "987654321098",
            "annual_income": 30000
        }
    }
    
    response2 = client.post("/api/application/validate", json=invalid_app)
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["success"] is True
    assert data2["validation"]["rejection_risk_score"] > 0.0
    assert len(data2["validation"]["validation_issues"]) > 0
    
    # Step 3: Verify data is stored in mock_data
    assert len(mock_data["applications"]) == 2
    
    stored_app1 = mock_data["applications"][0]
    assert stored_app1["application_id"] == "INT_APP_001"
    assert stored_app1["rejection_risk_score"] == 0.0
    assert stored_app1["issues_count"] == 0
    
    stored_app2 = mock_data["applications"][1]
    assert stored_app2["application_id"] == "INT_APP_002"
    assert stored_app2["rejection_risk_score"] > 0.0
    assert stored_app2["issues_count"] > 0
    
    # Step 4: Submit another application with multiple issues
    multi_issue_app = {
        "application_id": "INT_APP_003",
        "scheme_type": "disability_pension",
        "operator_id": "OP_INT_002",
        "application_data": {
            "applicant_name": "Integration Test User 3",
            "date_of_birth": "2010-01-01",  # Too young
            # Missing disability_certificate
            "address": "Integration Test Village",
            "bank_account": "123",  # Invalid format
            "aadhaar_number": "12345",  # Invalid format
            "disability_percentage": 30  # Below minimum
        }
    }
    
    response3 = client.post("/api/application/validate", json=multi_issue_app)
    assert response3.status_code == 200
    data3 = response3.json()
    assert data3["success"] is True
    assert data3["validation"]["rejection_risk_score"] >= 0.5  # High risk
    assert len(data3["validation"]["validation_issues"]) >= 3
    assert len(data3["validation"]["corrective_guidance"]) >= 3
    
    # Verify guidance is prioritized
    guidance = data3["validation"]["corrective_guidance"]
    priorities = [g["priority"] for g in guidance]
    assert priorities == sorted(priorities)  # Should be in ascending order
    
    # Step 5: Verify all applications are stored
    assert len(mock_data["applications"]) == 3


def test_validation_model_integration():
    """Test that the rejection risk model is properly integrated"""
    
    test_cases = [
        {
            "scheme": "widow_pension",
            "data": {
                "applicant_name": "Test User",
                "date_of_birth": "1985-01-01",
                "spouse_death_certificate": "DEATH001",
                "address": "Test Village",
                "bank_account": "1234567890123456",
                "aadhaar_number": "123456789012"
            },
            "expected_risk": 0.0
        },
        {
            "scheme": "old_age_pension",
            "data": {
                "applicant_name": "Test User",
                "date_of_birth": "1950-01-01",  # Age ~74, valid
                "age_proof": "AADHAAR",
                "address": "Test Village",
                "bank_account": "1234567890123456",
                "aadhaar_number": "123456789012",
                "annual_income": 50000
            },
            "expected_risk": 0.0
        },
        {
            "scheme": "bpl_card",
            "data": {
                "applicant_name": "Test User",
                "date_of_birth": "1990-01-01",
                "address": "Test Village",
                "family_members": "4",
                "income_certificate": "INC001",
                "aadhaar_number": "123456789012",
                "annual_income": 200000  # Above threshold
            },
            "expected_risk_gt": 0.0  # Should have some risk
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        request_data = {
            "application_id": f"MODEL_TEST_{i+1}",
            "scheme_type": test_case["scheme"],
            "operator_id": "OP_MODEL_TEST",
            "application_data": test_case["data"]
        }
        
        response = client.post("/api/application/validate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        validation = data["validation"]
        
        if "expected_risk" in test_case:
            assert validation["rejection_risk_score"] == test_case["expected_risk"]
        elif "expected_risk_gt" in test_case:
            assert validation["rejection_risk_score"] > test_case["expected_risk_gt"]


def test_validation_guidance_quality():
    """Test that corrective guidance is meaningful and complete"""
    
    request_data = {
        "application_id": "GUIDANCE_TEST",
        "scheme_type": "widow_pension",
        "operator_id": "OP_GUIDANCE_TEST",
        "application_data": {
            "applicant_name": "Test User",
            "date_of_birth": "1990-01-01",
            # Missing multiple required fields
            "address": "Test Village"
        }
    }
    
    response = client.post("/api/application/validate", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    validation = data["validation"]
    
    # Should have issues
    assert len(validation["validation_issues"]) > 0
    
    # Should have guidance for each issue
    assert len(validation["corrective_guidance"]) > 0
    
    # Each guidance should have required fields
    for guidance in validation["corrective_guidance"]:
        assert "issue_id" in guidance
        assert "guidance_text_hindi" in guidance
        assert "guidance_text_english" in guidance
        assert "suggested_action" in guidance
        assert "priority" in guidance
        
        # Text should not be empty
        assert len(guidance["guidance_text_hindi"]) > 0
        assert len(guidance["guidance_text_english"]) > 0
        assert len(guidance["suggested_action"]) > 0
        
        # Priority should be valid
        assert 1 <= guidance["priority"] <= 4


def test_validation_scheme_specific_rules():
    """Test that scheme-specific validation rules are applied correctly"""
    
    # Test disability pension specific rule
    disability_app = {
        "application_id": "SCHEME_TEST_1",
        "scheme_type": "disability_pension",
        "operator_id": "OP_SCHEME_TEST",
        "application_data": {
            "applicant_name": "Test User",
            "date_of_birth": "1980-01-01",
            "disability_certificate": "DISAB001",
            "address": "Test Village",
            "bank_account": "1234567890123456",
            "aadhaar_number": "123456789012",
            "disability_percentage": 35,  # Below 40% minimum
            "annual_income": 50000
        }
    }
    
    response = client.post("/api/application/validate", json=disability_app)
    assert response.status_code == 200
    
    data = response.json()
    validation = data["validation"]
    
    # Should have disability percentage issue
    issues = validation["validation_issues"]
    disability_issues = [i for i in issues if i["field_name"] == "disability_percentage"]
    assert len(disability_issues) > 0
    
    # Test old age pension specific rule
    old_age_app = {
        "application_id": "SCHEME_TEST_2",
        "scheme_type": "old_age_pension",
        "operator_id": "OP_SCHEME_TEST",
        "application_data": {
            "applicant_name": "Test User",
            "date_of_birth": "1980-01-01",  # Age ~44, below 60
            "age_proof": "AADHAAR",
            "address": "Test Village",
            "bank_account": "1234567890123456",
            "aadhaar_number": "123456789012",
            "annual_income": 50000
        }
    }
    
    response = client.post("/api/application/validate", json=old_age_app)
    assert response.status_code == 200
    
    data = response.json()
    validation = data["validation"]
    
    # Should have age issue
    issues = validation["validation_issues"]
    age_issues = [i for i in issues if i["field_name"] == "date_of_birth"]
    assert len(age_issues) > 0
    assert age_issues[0]["severity"] == "critical"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
