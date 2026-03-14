"""
Unit tests for Beneficiary Discovery API
Tests Task 2.2: Create Beneficiary Discovery Engine API
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from datetime import date

client = TestClient(app)


def test_discover_beneficiaries_success():
    """Test successful beneficiary discovery from death record"""
    # Use a death record that should match ration card data
    death_record = {
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
    
    response = client.post("/api/beneficiary/discover", json=death_record)
    
    if response.status_code != 200:
        print(f"Error response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert data["success"] is True
    assert data["death_record_id"] == "CDR001"
    assert data["deceased_name"] == "राम कुमार शर्मा"
    assert "beneficiaries" in data
    assert "total_found" in data
    assert isinstance(data["beneficiaries"], list)
    
    # If beneficiaries found, verify their structure
    if data["total_found"] > 0:
        beneficiary = data["beneficiaries"][0]
        assert "beneficiary_name" in beneficiary
        assert "relationship" in beneficiary
        assert "scheme_type" in beneficiary
        assert "confidence_score" in beneficiary
        assert "eligibility_reasoning" in beneficiary
        assert "source_records" in beneficiary
        
        # Verify confidence score is in valid range [0, 1]
        assert 0.0 <= beneficiary["confidence_score"] <= 1.0
        
        # Verify beneficiaries are sorted by confidence (descending)
        scores = [b["confidence_score"] for b in data["beneficiaries"]]
        assert scores == sorted(scores, reverse=True)


def test_discover_beneficiaries_female_deceased():
    """Test beneficiary discovery for female deceased (different scheme logic)"""
    death_record = {
        "record_id": "CDR002",
        "name": "सीता देवी",
        "father_name": "श्री राधे श्याम",
        "date_of_death": "2023-05-22",
        "age": 72,
        "gender": "F",
        "district": "बिलासपुर",
        "village": "तखतपुर",
        "registration_date": "2023-05-25"
    }
    
    response = client.post("/api/beneficiary/discover", json=death_record)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["deceased_name"] == "सीता देवी"


def test_discover_beneficiaries_no_matches():
    """Test beneficiary discovery when no matches are found"""
    death_record = {
        "record_id": "CDR999",
        "name": "अज्ञात व्यक्ति",
        "father_name": "अज्ञात पिता",
        "date_of_death": "2023-12-01",
        "age": 50,
        "gender": "M",
        "district": "अज्ञात",
        "village": "अज्ञात",
    }
    
    response = client.post("/api/beneficiary/discover", json=death_record)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_found"] == 0
    assert len(data["beneficiaries"]) == 0


def test_discover_beneficiaries_invalid_input():
    """Test beneficiary discovery with invalid input"""
    invalid_record = {
        "record_id": "CDR001",
        "name": "Test Name",
        # Missing required fields
    }
    
    response = client.post("/api/beneficiary/discover", json=invalid_record)
    
    # Should return validation error
    assert response.status_code == 422


def test_discover_beneficiaries_confidence_scores():
    """Test that all confidence scores are within valid range [0, 1]"""
    death_record = {
        "record_id": "CDR006",
        "name": "सुनीता देवी पटेल",
        "father_name": "श्री हरि प्रसाद",
        "date_of_death": "2023-04-20",
        "age": 63,
        "gender": "F",
        "district": "बिलासपुर",
        "village": "कोटा",
    }
    
    response = client.post("/api/beneficiary/discover", json=death_record)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify all confidence scores are in [0, 1]
    for beneficiary in data["beneficiaries"]:
        assert 0.0 <= beneficiary["confidence_score"] <= 1.0


def test_discover_beneficiaries_ranking():
    """Test that beneficiaries are ranked by confidence score in descending order"""
    death_record = {
        "record_id": "CDR007",
        "name": "राजेश कुमार",
        "father_name": "श्री गोपाल दास",
        "date_of_death": "2023-06-05",
        "age": 52,
        "gender": "M",
        "district": "दुर्ग",
        "village": "पाटन",
    }
    
    response = client.post("/api/beneficiary/discover", json=death_record)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify ranking (descending order)
    if data["total_found"] > 1:
        scores = [b["confidence_score"] for b in data["beneficiaries"]]
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1], "Beneficiaries should be sorted by confidence score in descending order"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
