"""
Test for auto-escalation endpoint
Tests Task 3.3: Implement basic auto-escalation logic
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from main import app, mock_data

client = TestClient(app)


def test_check_escalations_empty():
    """Test escalation check with no grievances"""
    # Clear mock data
    mock_data["grievances"] = []
    
    response = client.get("/api/grievance/check-escalations")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_checked"] == 0
    assert data["escalations_needed"] == 0
    assert len(data["grievances"]) == 0


def test_check_escalations_no_overdue():
    """Test escalation check with grievances that are not overdue"""
    # Clear and set up mock data with future SLA deadlines
    current_time = datetime.now(datetime.UTC) if hasattr(datetime, 'UTC') else datetime.utcnow()
    future_deadline = current_time + timedelta(hours=24)
    
    mock_data["grievances"] = [
        {
            "grievance_id": "test-001",
            "citizen_id": "CIT001",
            "text": "Test grievance 1",
            "language": "hi",
            "category": "Revenue",
            "classification_confidence": 0.95,
            "predicted_sla": 72,
            "assigned_department": "Revenue",
            "assigned_officer_id": None,
            "status": "submitted",
            "escalation_level": 0,
            "submitted_at": current_time.isoformat(),
            "sla_deadline": future_deadline.isoformat(),
            "resolved_at": None,
            "status_history": []
        }
    ]
    
    response = client.get("/api/grievance/check-escalations")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_checked"] == 1
    assert data["escalations_needed"] == 0
    assert len(data["grievances"]) == 0


def test_check_escalations_with_overdue():
    """Test escalation check with overdue grievances"""
    # Clear and set up mock data with past SLA deadlines
    current_time = datetime.now(datetime.UTC) if hasattr(datetime, 'UTC') else datetime.utcnow()
    past_deadline_1 = current_time - timedelta(hours=2)  # 2 hours overdue
    past_deadline_2 = current_time - timedelta(hours=5)  # 5 hours overdue (more urgent)
    
    mock_data["grievances"] = [
        {
            "grievance_id": "test-001",
            "citizen_id": "CIT001",
            "text": "Test grievance 1",
            "language": "hi",
            "category": "Revenue",
            "classification_confidence": 0.95,
            "predicted_sla": 72,
            "assigned_department": "Revenue",
            "assigned_officer_id": None,
            "status": "submitted",
            "escalation_level": 0,
            "submitted_at": (current_time - timedelta(hours=74)).isoformat(),
            "sla_deadline": past_deadline_1.isoformat(),
            "resolved_at": None,
            "status_history": []
        },
        {
            "grievance_id": "test-002",
            "citizen_id": "CIT002",
            "text": "Test grievance 2",
            "language": "hi",
            "category": "Health",
            "classification_confidence": 0.92,
            "predicted_sla": 48,
            "assigned_department": "Health",
            "assigned_officer_id": None,
            "status": "in_progress",
            "escalation_level": 0,
            "submitted_at": (current_time - timedelta(hours=53)).isoformat(),
            "sla_deadline": past_deadline_2.isoformat(),
            "resolved_at": None,
            "status_history": []
        }
    ]
    
    response = client.get("/api/grievance/check-escalations")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_checked"] == 2
    assert data["escalations_needed"] == 2
    assert len(data["grievances"]) == 2
    
    # Verify most overdue is first (test-002 is 5 hours overdue)
    assert data["grievances"][0]["grievance_id"] == "test-002"
    assert data["grievances"][1]["grievance_id"] == "test-001"


def test_check_escalations_ignores_resolved():
    """Test that resolved grievances are not checked for escalation"""
    current_time = datetime.now(datetime.UTC) if hasattr(datetime, 'UTC') else datetime.utcnow()
    past_deadline = current_time - timedelta(hours=2)
    
    mock_data["grievances"] = [
        {
            "grievance_id": "test-001",
            "citizen_id": "CIT001",
            "text": "Test grievance 1",
            "language": "hi",
            "category": "Revenue",
            "classification_confidence": 0.95,
            "predicted_sla": 72,
            "assigned_department": "Revenue",
            "assigned_officer_id": None,
            "status": "resolved",  # Resolved status
            "escalation_level": 0,
            "submitted_at": (current_time - timedelta(hours=74)).isoformat(),
            "sla_deadline": past_deadline.isoformat(),
            "resolved_at": current_time.isoformat(),
            "status_history": []
        }
    ]
    
    response = client.get("/api/grievance/check-escalations")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_checked"] == 0  # Resolved grievances not checked
    assert data["escalations_needed"] == 0
    assert len(data["grievances"]) == 0


def test_check_escalations_mixed_statuses():
    """Test escalation check with mix of overdue, on-time, and resolved grievances"""
    current_time = datetime.now(datetime.UTC) if hasattr(datetime, 'UTC') else datetime.utcnow()
    past_deadline = current_time - timedelta(hours=2)
    future_deadline = current_time + timedelta(hours=24)
    
    mock_data["grievances"] = [
        {
            "grievance_id": "test-overdue",
            "citizen_id": "CIT001",
            "text": "Overdue grievance",
            "language": "hi",
            "category": "Revenue",
            "classification_confidence": 0.95,
            "predicted_sla": 72,
            "assigned_department": "Revenue",
            "assigned_officer_id": None,
            "status": "submitted",
            "escalation_level": 0,
            "submitted_at": (current_time - timedelta(hours=74)).isoformat(),
            "sla_deadline": past_deadline.isoformat(),
            "resolved_at": None,
            "status_history": []
        },
        {
            "grievance_id": "test-ontime",
            "citizen_id": "CIT002",
            "text": "On-time grievance",
            "language": "hi",
            "category": "Health",
            "classification_confidence": 0.92,
            "predicted_sla": 48,
            "assigned_department": "Health",
            "assigned_officer_id": None,
            "status": "in_progress",
            "escalation_level": 0,
            "submitted_at": current_time.isoformat(),
            "sla_deadline": future_deadline.isoformat(),
            "resolved_at": None,
            "status_history": []
        },
        {
            "grievance_id": "test-resolved",
            "citizen_id": "CIT003",
            "text": "Resolved grievance",
            "language": "hi",
            "category": "Education",
            "classification_confidence": 0.90,
            "predicted_sla": 48,
            "assigned_department": "Education",
            "assigned_officer_id": None,
            "status": "resolved",
            "escalation_level": 0,
            "submitted_at": (current_time - timedelta(hours=50)).isoformat(),
            "sla_deadline": past_deadline.isoformat(),
            "resolved_at": current_time.isoformat(),
            "status_history": []
        }
    ]
    
    response = client.get("/api/grievance/check-escalations")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_checked"] == 2  # Only unresolved grievances
    assert data["escalations_needed"] == 1  # Only the overdue one
    assert len(data["grievances"]) == 1
    assert data["grievances"][0]["grievance_id"] == "test-overdue"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
