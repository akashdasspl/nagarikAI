"""
Demo script for auto-escalation endpoint
Demonstrates Task 3.3: Basic auto-escalation logic
"""
import requests
from datetime import datetime, timedelta
import json

BASE_URL = "http://localhost:8000"


def demo_escalation():
    """Demonstrate the auto-escalation check endpoint"""
    
    print("=" * 60)
    print("NagarikAI Platform - Auto-Escalation Demo")
    print("=" * 60)
    print()
    
    # Step 1: Submit some test grievances
    print("Step 1: Submitting test grievances...")
    print("-" * 60)
    
    grievances = [
        {
            "citizen_id": "CIT001",
            "text": "मेरा राशन कार्ड अभी तक नहीं बना है",
            "language": "hi"
        },
        {
            "citizen_id": "CIT002",
            "text": "पेंशन भुगतान में देरी हो रही है",
            "language": "hi"
        },
        {
            "citizen_id": "CIT003",
            "text": "बिजली कनेक्शन की समस्या",
            "language": "hi"
        }
    ]
    
    submitted_grievances = []
    for i, grievance_data in enumerate(grievances, 1):
        response = requests.post(f"{BASE_URL}/api/grievance/submit", json=grievance_data)
        if response.status_code == 200:
            data = response.json()
            grievance = data["grievance"]
            submitted_grievances.append(grievance)
            print(f"\n✓ Grievance {i} submitted:")
            print(f"  ID: {grievance['grievance_id']}")
            print(f"  Category: {grievance['category']}")
            print(f"  SLA: {grievance['predicted_sla']} hours")
            print(f"  Deadline: {grievance['sla_deadline']}")
        else:
            print(f"\n✗ Failed to submit grievance {i}: {response.text}")
    
    print()
    print("=" * 60)
    
    # Step 2: Check for escalations (initially none should be overdue)
    print("\nStep 2: Checking for escalations (initial check)...")
    print("-" * 60)
    
    response = requests.get(f"{BASE_URL}/api/grievance/check-escalations")
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Escalation check completed:")
        print(f"  Total checked: {data['total_checked']}")
        print(f"  Escalations needed: {data['escalations_needed']}")
        
        if data['escalations_needed'] > 0:
            print(f"\n  Grievances needing escalation:")
            for grievance in data['grievances']:
                print(f"    - {grievance['grievance_id']} ({grievance['category']})")
        else:
            print(f"\n  ✓ No grievances are overdue yet.")
    else:
        print(f"\n✗ Failed to check escalations: {response.text}")
    
    print()
    print("=" * 60)
    
    # Step 3: Explain the escalation logic
    print("\nStep 3: Auto-Escalation Logic")
    print("-" * 60)
    print("""
The auto-escalation endpoint checks all unresolved grievances and identifies
those that have exceeded their SLA deadline.

Logic:
  1. Get all grievances with status: submitted, assigned, in_progress, escalated
  2. For each grievance, check if current_time > sla_deadline
  3. If yes, mark for escalation
  4. Return list sorted by how overdue they are (most urgent first)

Requirements validated:
  - Requirement 4.1: SLA deadline monitoring
  - Requirement 4.2: Automatic escalation on SLA breach
    """)
    
    print("=" * 60)
    print("\nDemo completed!")
    print("\nTo test with overdue grievances:")
    print("  1. Submit grievances using the API")
    print("  2. Manually modify SLA deadlines in mock_data to be in the past")
    print("  3. Call GET /api/grievance/check-escalations")
    print("  4. Overdue grievances will be returned for escalation")
    print()


if __name__ == "__main__":
    try:
        demo_escalation()
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to the API server.")
        print("  Please ensure the server is running:")
        print("  cd backend && python -m uvicorn main:app --reload")
    except Exception as e:
        print(f"\n✗ Error: {e}")
