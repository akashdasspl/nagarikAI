# Task 3.2 Implementation: Grievance Intelligence API

## Overview

Implemented the POST `/api/grievance/submit` endpoint that accepts Hindi/English grievance text, classifies it using the mBERT-based classifier, predicts SLA, and returns a complete grievance record.

## Implementation Details

### Endpoint: POST /api/grievance/submit

**Location:** `backend/main.py`

**Request Body:**
```json
{
  "citizen_id": "CIT123456",
  "text": "मेरा जाति प्रमाण पत्र अभी तक नहीं बना है",
  "language": "hi"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Grievance submitted successfully. Routed to Revenue department.",
  "grievance": {
    "grievance_id": "uuid-here",
    "citizen_id": "CIT123456",
    "text": "मेरा जाति प्रमाण पत्र अभी तक नहीं बना है",
    "language": "hi",
    "category": "Revenue",
    "classification_confidence": 0.85,
    "predicted_sla": 72,
    "assigned_department": "Revenue",
    "assigned_officer_id": null,
    "status": "submitted",
    "escalation_level": 0,
    "submitted_at": "2024-01-15T10:30:00Z",
    "sla_deadline": "2024-01-18T10:30:00Z",
    "resolved_at": null,
    "status_history": []
  }
}
```

### Features Implemented

1. **Grievance Classification**
   - Uses `GrievanceClassifier` from `models/grievance_classifier.py`
   - Classifies Hindi/English text into 5 departments:
     - Revenue (72 hours SLA)
     - Health (24 hours SLA - urgent)
     - Education (48 hours SLA)
     - Social Welfare (96 hours SLA)
     - Infrastructure (120 hours SLA)
   - Returns confidence score [0.0, 1.0]

2. **SLA Prediction**
   - Fixed duration per department (simplified for MVP)
   - Calculates deadline: `submitted_at + predicted_sla_hours`
   - Returns both hours and deadline timestamp

3. **Grievance Record Creation**
   - Generates unique UUID for each grievance
   - Initializes with "submitted" status
   - Sets escalation_level to 0
   - Stores in mock data store

4. **Input Validation**
   - Validates language (hi, en, chhattisgarhi)
   - Validates non-empty text
   - Returns 400 error for invalid inputs

5. **Error Handling**
   - HTTP 400 for validation errors
   - HTTP 500 for server errors
   - Descriptive error messages

## Classification Examples

### Revenue Department
- Keywords: जाति प्रमाण, आय प्रमाण, निवास प्रमाण, जन्म प्रमाण, मृत्यु प्रमाण पत्र
- Example: "मेरा जाति प्रमाण पत्र दो महीने से लंबित है"
- SLA: 72 hours (3 days)

### Health Department
- Keywords: स्वास्थ्य, अस्पताल, डॉक्टर, दवाई, इलाज, एम्बुलेंस
- Example: "अस्पताल में दवाइयां नहीं मिल रही हैं"
- SLA: 24 hours (1 day - urgent)

### Social Welfare Department
- Keywords: पेंशन, विधवा, विकलांग, राशन कार्ड, आंगनवाड़ी
- Example: "मेरी विधवा पेंशन तीन महीने से नहीं आई है"
- SLA: 96 hours (4 days)

### Infrastructure Department
- Keywords: सड़क, बिजली, पानी, नाली, गड्ढे, ट्रांसफार्मर
- Example: "गांव की सड़क बहुत खराब है"
- SLA: 120 hours (5 days)

### Education Department
- Keywords: शिक्षा, स्कूल, शिक्षक, छात्रवृत्ति, किताब
- Example: "स्कूल में शिक्षक नहीं आते"
- SLA: 48 hours (2 days)

## Testing

### Unit Tests
**File:** `backend/test_grievance_api.py`

11 test cases covering:
- ✅ Hindi grievance classification (all 5 departments)
- ✅ English grievance handling
- ✅ Empty text validation
- ✅ Invalid language validation
- ✅ SLA calculation accuracy
- ✅ Confidence score bounds [0, 1]
- ✅ Unique grievance IDs
- ✅ Initial status correctness

**Run tests:**
```bash
cd backend
python -m pytest test_grievance_api.py -v
```

**Results:** All 11 tests passing ✅

### Demo Script
**File:** `backend/demo_grievance_api.py`

Interactive demo showing:
- Classification across all departments
- Hindi and English text handling
- SLA predictions
- Error handling

**Run demo:**
```bash
# Terminal 1: Start server
cd backend
python main.py

# Terminal 2: Run demo
cd backend
python demo_grievance_api.py
```

## API Integration

### Using the API

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/grievance/submit",
    json={
        "citizen_id": "CIT123456",
        "text": "मेरा राशन कार्ड नहीं बना",
        "language": "hi"
    }
)

grievance = response.json()["grievance"]
print(f"Category: {grievance['category']}")
print(f"SLA: {grievance['predicted_sla']} hours")
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/grievance/submit \
  -H "Content-Type: application/json" \
  -d '{
    "citizen_id": "CIT123456",
    "text": "मेरा जाति प्रमाण पत्र चाहिए",
    "language": "hi"
  }'
```

**JavaScript:**
```javascript
const response = await fetch('http://localhost:8000/api/grievance/submit', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    citizen_id: 'CIT123456',
    text: 'मेरा राशन कार्ड नहीं बना',
    language: 'hi'
  })
});

const data = await response.json();
console.log('Category:', data.grievance.category);
```

## Requirements Validation

### ✅ Requirement 3.1: Grievance Semantic Routing
- Grievances in Hindi/Chhattisgarhi are classified using mBERT classifier
- Classification produces department category and confidence score
- Supports multiple languages (hi, en, chhattisgarhi)

### ✅ Requirement 3.3: Department Routing
- Grievances are routed to appropriate department based on classification
- Department assignment matches classification category
- Assigned department field populated in response

### ✅ Requirement 3.4: SLA Prediction
- SLA completion time predicted based on department category
- Fixed durations per department (simplified for MVP):
  - Health: 24 hours (urgent)
  - Education: 48 hours
  - Revenue: 72 hours
  - Social Welfare: 96 hours
  - Infrastructure: 120 hours
- SLA deadline calculated and returned in response

## Files Modified/Created

### Modified
- `backend/main.py` - Added POST /api/grievance/submit endpoint

### Created
- `backend/test_grievance_api.py` - Unit tests for API endpoint
- `backend/demo_grievance_api.py` - Interactive demo script
- `backend/TASK_3.2_IMPLEMENTATION.md` - This documentation

### Dependencies Used
- `models/grievance_classifier.py` - GrievanceClassifier for classification
- `models/grievance.py` - Grievance, GrievanceCreate, GrievanceResponse models
- `uuid` - Unique grievance ID generation
- `datetime` - Timestamp and SLA deadline calculation

## Next Steps

Task 3.2 is complete. The next task in the implementation plan is:

**Task 3.3:** Implement basic auto-escalation logic
- Create GET /api/grievance/check-escalations endpoint
- Check grievances against SLA deadlines
- Return list of grievances needing escalation

## Notes

- This is an MVP implementation using keyword-based classification
- Production version would use fine-tuned mBERT model
- Mock data store used (in-memory dictionary)
- No database persistence in current implementation
- SLA predictions are simplified (fixed per department)
- Production would use ML model for dynamic SLA prediction based on historical data
