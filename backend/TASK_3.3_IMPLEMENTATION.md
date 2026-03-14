# Task 3.3 Implementation: Basic Auto-Escalation Logic

## Overview

Implemented the auto-escalation endpoint that checks grievances against their SLA deadlines and identifies those needing escalation.

## Implementation Details

### Endpoint

**GET /api/grievance/check-escalations**

Checks all unresolved grievances in the mock data store and identifies those that have exceeded their SLA deadline.

### Request

No request body required (GET endpoint).

### Response

```json
{
  "success": true,
  "message": "Checked 5 unresolved grievances. Found 2 needing escalation.",
  "total_checked": 5,
  "escalations_needed": 2,
  "grievances": [
    {
      "grievance_id": "uuid-here",
      "citizen_id": "CIT001",
      "text": "मेरा राशन कार्ड अभी तक नहीं बना है",
      "language": "hi",
      "category": "Food & Civil Supplies",
      "classification_confidence": 0.96,
      "predicted_sla": 72,
      "assigned_department": "Food & Civil Supplies",
      "status": "submitted",
      "escalation_level": 0,
      "submitted_at": "2024-01-15T10:30:00Z",
      "sla_deadline": "2024-01-18T10:30:00Z",
      "resolved_at": null,
      "status_history": []
    }
  ]
}
```

### Logic

1. **Get Current Time**: Retrieve the current timestamp
2. **Filter Unresolved Grievances**: Select grievances with status in `["submitted", "assigned", "in_progress", "escalated"]`
3. **Check SLA Deadline**: For each unresolved grievance, compare `current_time > sla_deadline`
4. **Collect Overdue**: Add grievances that exceed their deadline to the escalation list
5. **Sort by Urgency**: Sort results by how overdue they are (most overdue first)
6. **Return Results**: Return the list of grievances needing escalation

### Key Features

- **Simple Rule-Based**: Uses straightforward time comparison (`current_time > sla_deadline`)
- **Status Filtering**: Only checks unresolved grievances (ignores "resolved" status)
- **Urgency Sorting**: Returns most overdue grievances first for prioritization
- **Comprehensive Response**: Includes total checked count and escalation count for monitoring

## Files Modified

1. **backend/models/grievance.py**
   - Added `EscalationCheckResponse` model for the endpoint response

2. **backend/models/__init__.py**
   - Exported `EscalationCheckResponse` model

3. **backend/main.py**
   - Added `check_escalations()` endpoint handler
   - Imported `EscalationCheckResponse` model

## Files Created

1. **backend/test_escalation.py**
   - Unit tests for the escalation endpoint
   - Tests: empty data, no overdue, with overdue, ignores resolved, mixed statuses
   - All 5 tests passing ✓

2. **backend/test_escalation_integration.py**
   - Integration tests with grievance submission flow
   - Tests: single grievance escalation, multiple grievances
   - All 2 tests passing ✓

3. **backend/demo_escalation.py**
   - Demo script showing the endpoint in action
   - Submits test grievances and checks for escalations

4. **backend/TASK_3.3_IMPLEMENTATION.md**
   - This documentation file

## Requirements Validated

- **Requirement 4.1**: SLA deadline monitoring
  - Endpoint checks grievances against their predicted SLA deadlines
  
- **Requirement 4.2**: Automatic escalation on SLA breach
  - Identifies and returns grievances that have exceeded their SLA deadline

## Testing

### Run Unit Tests
```bash
cd backend
python -m pytest test_escalation.py -v
```

### Run Integration Tests
```bash
cd backend
python -m pytest test_escalation_integration.py -v
```

### Run Demo
```bash
# Start the server first
cd backend
python -m uvicorn main:app --reload

# In another terminal, run the demo
cd backend
python demo_escalation.py
```

## Test Results

✓ All 7 tests passing (5 unit tests + 2 integration tests)

### Test Coverage

1. **Empty Data**: Handles case with no grievances
2. **No Overdue**: Returns empty list when all grievances are on-time
3. **With Overdue**: Correctly identifies overdue grievances
4. **Ignores Resolved**: Excludes resolved grievances from checks
5. **Mixed Statuses**: Handles combination of overdue, on-time, and resolved
6. **Integration Flow**: Works with grievance submission endpoint
7. **Multiple Grievances**: Handles multiple submitted grievances correctly

## Usage Example

```python
import requests

# Check for escalations
response = requests.get("http://localhost:8000/api/grievance/check-escalations")
data = response.json()

print(f"Total checked: {data['total_checked']}")
print(f"Escalations needed: {data['escalations_needed']}")

for grievance in data['grievances']:
    print(f"Overdue: {grievance['grievance_id']} - {grievance['category']}")
```

## Future Enhancements (Post-MVP)

1. **Warning Notifications**: Implement 80% SLA threshold warnings (Requirement 4.1)
2. **Automatic Escalation**: Actually escalate grievances (increment level, reassign officer)
3. **Notification Service**: Send notifications to citizens and officers
4. **Audit Logging**: Log all escalation events to database
5. **Escalation Rules**: Support multiple escalation levels and custom rules
6. **Dashboard Integration**: Display escalation metrics in admin dashboard

## Notes

- This is a simplified MVP implementation for demo purposes
- Uses in-memory mock data store (no persistent database)
- Escalation detection only - does not perform actual escalation actions
- Suitable for hackathon demonstration of the concept
- Production version would need persistent storage and notification integration
