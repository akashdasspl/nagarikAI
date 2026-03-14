"""
Unit tests for Grievance Intelligence API

Tests the POST /api/grievance/submit endpoint to ensure:
- Grievances are classified correctly
- SLA predictions are generated
- Response includes all required fields
- Error handling works properly

Validates: Requirements 3.1, 3.3, 3.4
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from datetime import datetime, timedelta


client = TestClient(app)


def test_submit_grievance_hindi_revenue():
    """Test submitting a Hindi grievance about revenue/certificate issues"""
    grievance_data = {
        "citizen_id": "CIT123456",
        "text": "मेरा जाति प्रमाण पत्र अभी तक नहीं बना है। कृपया जल्दी बनाएं।",
        "language": "hi"
    }
    
    response = client.post("/api/grievance/submit", json=grievance_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert data["success"] is True
    assert "message" in data
    assert "grievance" in data
    
    # Check grievance details
    grievance = data["grievance"]
    assert grievance["citizen_id"] == "CIT123456"
    assert grievance["text"] == grievance_data["text"]
    assert grievance["language"] == "hi"
    assert grievance["category"] == "Revenue"  # Should classify as Revenue
    assert 0.0 <= grievance["classification_confidence"] <= 1.0
    assert grievance["predicted_sla"] == 72  # Revenue SLA is 72 hours
    assert grievance["assigned_department"] == "Revenue"
    assert grievance["status"] == "submitted"
    assert grievance["escalation_level"] == 0
    assert grievance["grievance_id"] is not None
    assert grievance["submitted_at"] is not None
    assert grievance["sla_deadline"] is not None


def test_submit_grievance_hindi_health():
    """Test submitting a Hindi grievance about health issues"""
    grievance_data = {
        "citizen_id": "CIT789012",
        "text": "अस्पताल में दवाइयां नहीं मिल रही हैं। डॉक्टर भी नहीं आते।",
        "language": "hi"
    }
    
    response = client.post("/api/grievance/submit", json=grievance_data)
    
    assert response.status_code == 200
    data = response.json()
    
    grievance = data["grievance"]
    assert grievance["category"] == "Health"  # Should classify as Health
    assert grievance["predicted_sla"] == 24  # Health SLA is 24 hours (urgent)


def test_submit_grievance_hindi_social_welfare():
    """Test submitting a Hindi grievance about pension/social welfare"""
    grievance_data = {
        "citizen_id": "CIT345678",
        "text": "मेरी विधवा पेंशन तीन महीने से नहीं आई है। कृपया देखें।",
        "language": "hi"
    }
    
    response = client.post("/api/grievance/submit", json=grievance_data)
    
    assert response.status_code == 200
    data = response.json()
    
    grievance = data["grievance"]
    assert grievance["category"] == "Social Welfare"  # Should classify as Social Welfare
    assert grievance["predicted_sla"] == 96  # Social Welfare SLA is 96 hours


def test_submit_grievance_hindi_infrastructure():
    """Test submitting a Hindi grievance about infrastructure"""
    grievance_data = {
        "citizen_id": "CIT901234",
        "text": "गांव की सड़क बहुत खराब है। बारिश में गड्ढे हो गए हैं।",
        "language": "hi"
    }
    
    response = client.post("/api/grievance/submit", json=grievance_data)
    
    assert response.status_code == 200
    data = response.json()
    
    grievance = data["grievance"]
    assert grievance["category"] == "Infrastructure"  # Should classify as Infrastructure
    assert grievance["predicted_sla"] == 120  # Infrastructure SLA is 120 hours


def test_submit_grievance_english():
    """Test submitting an English grievance"""
    grievance_data = {
        "citizen_id": "CIT567890",
        "text": "My ration card has not been issued yet. Please expedite.",
        "language": "en"
    }
    
    response = client.post("/api/grievance/submit", json=grievance_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # English text won't match Hindi keywords, should default to Infrastructure
    grievance = data["grievance"]
    assert grievance["language"] == "en"
    assert grievance["category"] in ["Revenue", "Health", "Education", "Social Welfare", "Infrastructure"]
    assert 0.0 <= grievance["classification_confidence"] <= 1.0


def test_submit_grievance_empty_text():
    """Test submitting a grievance with empty text"""
    grievance_data = {
        "citizen_id": "CIT123456",
        "text": "",
        "language": "hi"
    }
    
    response = client.post("/api/grievance/submit", json=grievance_data)
    
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_submit_grievance_invalid_language():
    """Test submitting a grievance with unsupported language"""
    grievance_data = {
        "citizen_id": "CIT123456",
        "text": "Some grievance text",
        "language": "fr"  # French not supported
    }
    
    response = client.post("/api/grievance/submit", json=grievance_data)
    
    assert response.status_code == 400
    assert "Unsupported language" in response.json()["detail"]


def test_submit_grievance_sla_calculation():
    """Test that SLA deadline is calculated correctly"""
    grievance_data = {
        "citizen_id": "CIT123456",
        "text": "मेरा आय प्रमाण पत्र चाहिए",  # Revenue category
        "language": "hi"
    }
    
    response = client.post("/api/grievance/submit", json=grievance_data)
    
    assert response.status_code == 200
    data = response.json()
    
    grievance = data["grievance"]
    submitted_at = datetime.fromisoformat(grievance["submitted_at"].replace('Z', '+00:00'))
    sla_deadline = datetime.fromisoformat(grievance["sla_deadline"].replace('Z', '+00:00'))
    
    # Calculate expected deadline
    expected_deadline = submitted_at + timedelta(hours=grievance["predicted_sla"])
    
    # Allow 1 second tolerance for processing time
    time_diff = abs((sla_deadline - expected_deadline).total_seconds())
    assert time_diff < 1


def test_submit_grievance_confidence_bounds():
    """Test that classification confidence is always between 0 and 1"""
    test_texts = [
        "मेरा जाति प्रमाण पत्र चाहिए",
        "अस्पताल में दवाई नहीं है",
        "स्कूल में शिक्षक नहीं आते",
        "पेंशन नहीं मिली",
        "सड़क खराब है"
    ]
    
    for text in test_texts:
        grievance_data = {
            "citizen_id": "CIT123456",
            "text": text,
            "language": "hi"
        }
        
        response = client.post("/api/grievance/submit", json=grievance_data)
        assert response.status_code == 200
        
        grievance = response.json()["grievance"]
        assert 0.0 <= grievance["classification_confidence"] <= 1.0


def test_submit_grievance_unique_ids():
    """Test that each grievance gets a unique ID"""
    grievance_data = {
        "citizen_id": "CIT123456",
        "text": "मेरा राशन कार्ड नहीं बना",
        "language": "hi"
    }
    
    # Submit same grievance twice
    response1 = client.post("/api/grievance/submit", json=grievance_data)
    response2 = client.post("/api/grievance/submit", json=grievance_data)
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    id1 = response1.json()["grievance"]["grievance_id"]
    id2 = response2.json()["grievance"]["grievance_id"]
    
    assert id1 != id2  # IDs should be unique


def test_submit_grievance_initial_status():
    """Test that new grievances have correct initial status"""
    grievance_data = {
        "citizen_id": "CIT123456",
        "text": "मेरा राशन कार्ड नहीं बना",
        "language": "hi"
    }
    
    response = client.post("/api/grievance/submit", json=grievance_data)
    
    assert response.status_code == 200
    grievance = response.json()["grievance"]
    
    assert grievance["status"] == "submitted"
    assert grievance["escalation_level"] == 0
    assert grievance["assigned_officer_id"] is None
    assert grievance["resolved_at"] is None
    assert grievance["status_history"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
