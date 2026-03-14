"""
Integration test for auto-escalation with grievance submission
Tests the complete flow: submit grievance -> check escalations
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from main import app, mock_data

client = TestClient(app)


def test_escalation_integration_flow():
    """Test complete flow: submit grievance with past deadline, then check escalations"""
    # Clear mock data
    mock_data["grievances"] = []
    
    # Submit a grievance
    grievance_data = {
        "citizen_id": "CIT12345",
        "text": "मेरा राशन कार्ड अभी तक नहीं बना है",
        "language": "hi"
    }
    
    submit_response = client.post("/api/grievance/submit", json=grievance_data)
    assert submit_response.status_code == 200
    
    submit_data = submit_response.json()
    assert submit_data["success"] is True
    grievance_id = submit_data["grievance"]["grievance_id"]
    
    # Manually modify the SLA deadline to be in the past (simulate overdue)
    current_time = datetime.now(datetime.UTC) if hasattr(datetime, 'UTC') else datetime.utcnow()
    past_deadline = current_time - timedelta(hours=2)
    
    for grievance in mock_data["grievances"]:
        if grievance["grievance_id"] == grievance_id:
            grievance["sla_deadline"] = past_deadline
            break
    
    # Check escalations
    escalation_response = client.get("/api/grievance/check-escalations")
    assert escalation_response.status_code == 200
    
    escalation_data = escalation_response.json()
    assert escalation_data["success"] is True
    assert escalation_data["total_checked"] == 1
    assert escalation_data["escalations_needed"] == 1
    assert len(escalation_data["grievances"]) == 1
    assert escalation_data["grievances"][0]["grievance_id"] == grievance_id


def test_multiple_grievances_escalation():
    """Test escalation check with multiple submitted grievances"""
    # Clear mock data
    mock_data["grievances"] = []
    
    # Submit multiple grievances
    grievances_data = [
        {"citizen_id": "CIT001", "text": "राशन कार्ड की समस्या", "language": "hi"},
        {"citizen_id": "CIT002", "text": "पेंशन नहीं मिली", "language": "hi"},
        {"citizen_id": "CIT003", "text": "बिजली की समस्या", "language": "hi"},
    ]
    
    submitted_ids = []
    for gdata in grievances_data:
        response = client.post("/api/grievance/submit", json=gdata)
        assert response.status_code == 200
        submitted_ids.append(response.json()["grievance"]["grievance_id"])
    
    # Make first two overdue, keep third one on-time
    current_time = datetime.now(datetime.UTC) if hasattr(datetime, 'UTC') else datetime.utcnow()
    past_deadline = current_time - timedelta(hours=1)
    
    for i, grievance in enumerate(mock_data["grievances"]):
        if i < 2:  # First two are overdue
            grievance["sla_deadline"] = past_deadline
    
    # Check escalations
    escalation_response = client.get("/api/grievance/check-escalations")
    assert escalation_response.status_code == 200
    
    escalation_data = escalation_response.json()
    assert escalation_data["success"] is True
    assert escalation_data["total_checked"] == 3
    assert escalation_data["escalations_needed"] == 2
    assert len(escalation_data["grievances"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
