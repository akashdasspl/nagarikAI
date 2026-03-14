"""
Integration test for Grievance Intelligence API

This test verifies the complete flow:
1. Server starts successfully
2. Endpoint is accessible
3. Classification works end-to-end
4. Response format is correct

Run with: python -m pytest test_integration_grievance.py -v
"""
import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_api_health():
    """Test that the API is running"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_grievance_endpoint_exists():
    """Test that the grievance submit endpoint exists"""
    # Try with invalid data to check endpoint exists
    response = client.post("/api/grievance/submit", json={})
    # Should return 422 (validation error) not 404 (not found)
    assert response.status_code == 422


def test_complete_grievance_flow():
    """Test complete flow from submission to response"""
    # Submit a grievance
    grievance_data = {
        "citizen_id": "CIT_INTEGRATION_001",
        "text": "मेरा जाति प्रमाण पत्र बनाना है",
        "language": "hi"
    }
    
    response = client.post("/api/grievance/submit", json=grievance_data)
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "success" in data
    assert "message" in data
    assert "grievance" in data
    
    # Check grievance data
    grievance = data["grievance"]
    assert grievance["citizen_id"] == "CIT_INTEGRATION_001"
    assert grievance["text"] == grievance_data["text"]
    assert grievance["language"] == "hi"
    assert grievance["category"] in ["Revenue", "Health", "Education", "Social Welfare", "Infrastructure"]
    assert 0.0 <= grievance["classification_confidence"] <= 1.0
    assert grievance["predicted_sla"] > 0
    assert grievance["status"] == "submitted"
    assert grievance["grievance_id"] is not None


def test_classifier_integration():
    """Test that the classifier is properly integrated"""
    test_cases = [
        {
            "text": "मेरा आय प्रमाण पत्र चाहिए",
            "expected_category": "Revenue"
        },
        {
            "text": "अस्पताल में दवाई नहीं है",
            "expected_category": "Health"
        },
        {
            "text": "मेरी पेंशन नहीं आई",
            "expected_category": "Social Welfare"
        }
    ]
    
    for test_case in test_cases:
        response = client.post("/api/grievance/submit", json={
            "citizen_id": "CIT_TEST",
            "text": test_case["text"],
            "language": "hi"
        })
        
        assert response.status_code == 200
        grievance = response.json()["grievance"]
        assert grievance["category"] == test_case["expected_category"]


def test_sla_mapping():
    """Test that SLA is correctly mapped to departments"""
    sla_mapping = {
        "Revenue": 72,
        "Health": 24,
        "Education": 48,
        "Social Welfare": 96,
        "Infrastructure": 120
    }
    
    # Test each department
    test_texts = {
        "Revenue": "मेरा जाति प्रमाण पत्र चाहिए",
        "Health": "अस्पताल में डॉक्टर नहीं है",
        "Education": "स्कूल में शिक्षक नहीं आते",
        "Social Welfare": "मेरी पेंशन नहीं आई",
        "Infrastructure": "सड़क खराब है"
    }
    
    for department, text in test_texts.items():
        response = client.post("/api/grievance/submit", json={
            "citizen_id": "CIT_SLA_TEST",
            "text": text,
            "language": "hi"
        })
        
        assert response.status_code == 200
        grievance = response.json()["grievance"]
        assert grievance["category"] == department
        assert grievance["predicted_sla"] == sla_mapping[department]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
