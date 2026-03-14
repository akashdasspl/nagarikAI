# NagarikAI Platform — Demo Script

**Team blueBox | Hackathon 2026 Chhattisgarh NIC Smart Governance Initiative**

---

## Overview

This script walks through five end-to-end demo scenarios covering all three core AI features of the NagarikAI Platform:

1. **Beneficiary Discovery Engine** — `POST /api/beneficiary/discover`
2. **Grievance Intelligence Layer** — `POST /api/grievance/submit`
3. **CSC Operator Assistant** — `POST /api/application/validate`

**Recommended demo order:** Scenario 1 → 2 → 3 → 4 → 5

**Setup:** Backend on `http://localhost:8000`, Frontend on `http://localhost:5173`

---

## Pre-Demo Checklist

- [ ] Backend running: `cd backend && uvicorn main:app --reload`
- [ ] Frontend running: `cd frontend && npm run dev`
- [ ] Browser open at `http://localhost:5173`
- [ ] Terminal open for API calls (optional — the UI covers everything)
- [ ] Language toggle set to **English** initially; switch to **Hindi** during Scenario 3

---

## Scenario 1: Widow Pension Beneficiary Discovery

**Feature:** Beneficiary Discovery Engine  
**Talking Point:** "The system proactively identifies citizens who are eligible for welfare schemes but have never applied — by cross-referencing civil death records with ration card and Aadhaar databases."

### Demo Steps

1. Navigate to the **Beneficiary Discovery** tab in the UI.
2. Fill in the death record form with the following data:

**Sample Input — Death Record:**
```json
{
  "record_id": "CDR001",
  "name": "राम कुमार शर्मा",
  "father_name": "श्री मोहन लाल शर्मा",
  "date_of_death": "2023-03-15",
  "age": 67,
  "gender": "M",
  "district": "रायपुर",
  "village": "खमतराई"
}
```

3. Click **Discover Beneficiaries**.

**Expected Result:**
- The system finds matches in both the Ration Card DB (`RC2023001`) and Aadhaar DB (`234567890123`) for "राम कुमार शर्मा" from Raipur/Khamtarai.
- Confidence scores are shown (typically 85–95% for exact name+district matches).
- The spouse is flagged as a potential **widow pension** beneficiary.
- Results are ranked by confidence score (highest first).

**Talking Points:**
- "Without NagarikAI, this widow would never know she qualifies for a pension — she'd have to navigate the system herself."
- "The fuzzy matching handles OCR errors and name spelling variations — common in government records."
- "Confidence scores let field workers prioritize which cases to visit first."

---

## Scenario 2: Grievance Classification and Routing (Hindi)

**Feature:** Grievance Intelligence Layer  
**Talking Point:** "Citizens submit grievances in Hindi. Our mBERT model classifies the text and routes it to the right department automatically — no manual triage needed."

### Demo Steps

1. Navigate to the **Grievance Portal** tab.
2. Submit the following grievance:

**Sample Input — Pension Grievance (Hindi):**
```json
{
  "citizen_id": "CIT_DEMO_001",
  "text": "मेरी विधवा पेंशन तीन महीने से नहीं आई है। बैंक में पूछा तो कहा कि विभाग से पैसा नहीं आया। मैं बहुत परेशान हूं, कृपया जल्दी कार्रवाई करें।",
  "language": "hi"
}
```

**Expected Result:**
- Category: `समाज कल्याण विभाग` (Social Welfare Department)
- Confidence: ~80–90%
- Predicted SLA: 72 hours
- Status: `submitted`

3. Now submit a second grievance to show multi-department routing:

**Sample Input — Health Grievance (Hindi):**
```json
{
  "citizen_id": "CIT_DEMO_002",
  "text": "सरकारी अस्पताल में दवाइयां नहीं मिल रही हैं। डॉक्टर भी समय पर नहीं आते। मरीजों को बहुत परेशानी हो रही है।",
  "language": "hi"
}
```

**Expected Result:**
- Category: `स्वास्थ्य विभाग` (Health Department)
- Confidence: ~85–95%
- Predicted SLA: 48 hours

**Talking Points:**
- "The model understands Hindi text semantics — not just keywords."
- "Each department has a different SLA. Health issues get 48 hours; infrastructure gets 120 hours."
- "This replaces a manual process that used to take 2–3 days just for routing."

---

## Scenario 3: Language Toggle — Hindi UI

**Feature:** Multilingual UI  
**Talking Point:** "The entire interface works in Hindi — critical for CSC operators in rural Chhattisgarh who are more comfortable in their native language."

### Demo Steps

1. Click the **language toggle** (EN/HI) in the top navigation bar.
2. The entire UI switches to Hindi.
3. Submit a grievance in Hindi using the Hindi UI.

**Sample Input — Infrastructure Grievance:**
```json
{
  "citizen_id": "CIT_DEMO_003",
  "text": "गांव की मुख्य सड़क बहुत खराब है। बारिश में बड़े गड्ढे हो गए हैं। एक्सीडेंट का खतरा है।",
  "language": "hi"
}
```

**Expected Result:**
- Category: `लोक निर्माण विभाग` (Public Works Department)
- Predicted SLA: 120 hours

4. Switch back to English for the next scenario.

**Talking Points:**
- "Language is not a barrier — operators can work in the language they're most comfortable with."
- "All labels, buttons, and guidance messages are translated."

---

## Scenario 4: Application Validation — High Risk Detection

**Feature:** CSC Operator Assistant  
**Talking Point:** "Before an operator submits an application, NagarikAI checks it for common rejection reasons and gives specific corrective guidance — reducing the 40% rejection rate we see today."

### Demo Steps

1. Navigate to the **Operator Assistant** tab.
2. Enter the following application data (this has multiple issues):

**Sample Input — Disability Pension with Issues:**
```json
{
  "application_id": "APP_DEMO_HIGH_RISK",
  "scheme_type": "disability_pension",
  "operator_id": "OP_CSC_RAIPUR_01",
  "application_data": {
    "applicant_name": "Mohan Singh",
    "date_of_birth": "2010-01-01",
    "address": "Village Raigarh, District Raigarh",
    "bank_account": "123",
    "aadhaar_number": "12345",
    "disability_percentage": 30,
    "annual_income": 200000
  }
}
```

**Expected Result:**
- Rejection Risk Score: **0.85–0.95** (HIGH — shown in red)
- Issues detected:
  - `date_of_birth` — Age below minimum (critical)
  - `disability_percentage` — Below 40% minimum (high)
  - `annual_income` — Above income threshold (high)
  - `bank_account` — Invalid format (medium)
  - `aadhaar_number` — Invalid format (medium)
- Corrective guidance in both Hindi and English for each issue

**Talking Points:**
- "Five issues caught before submission — each one would have caused rejection."
- "The guidance is in Hindi so the operator knows exactly what to fix."
- "The risk score updates in real-time as the operator corrects each field."

---

## Scenario 5: Application Validation — Clean Application

**Feature:** CSC Operator Assistant  
**Talking Point:** "When an application is complete and correct, the system gives a green light — giving the operator confidence to submit."

### Demo Steps

1. Stay on the **Operator Assistant** tab.
2. Enter a clean, valid application:

**Sample Input — Valid Widow Pension Application:**
```json
{
  "application_id": "APP_DEMO_CLEAN",
  "scheme_type": "widow_pension",
  "operator_id": "OP_CSC_RAIPUR_01",
  "application_data": {
    "applicant_name": "Sunita Devi",
    "date_of_birth": "1985-03-15",
    "spouse_death_certificate": "DEATH_CERT_2024_001",
    "address": "Village Raipur, Block Dhamtari, District Raipur, PIN 492001",
    "bank_account": "1234567890123456",
    "aadhaar_number": "123456789012",
    "annual_income": 50000
  }
}
```

**Expected Result:**
- Rejection Risk Score: **0.00–0.10** (LOW — shown in green)
- No validation issues
- Message: "Application validation successful. No issues found."

**Talking Points:**
- "Green means go — the operator can submit with confidence."
- "This is the before/after story: Scenario 4 shows what happens without guidance; Scenario 5 shows the corrected result."

---

## End-to-End Demo Flow Summary

| # | Scenario | Feature | Key Message |
|---|----------|---------|-------------|
| 1 | Widow Pension Discovery | Beneficiary Discovery | Proactive identification of unenrolled citizens |
| 2 | Hindi Grievance Routing | Grievance Intelligence | Automatic classification and department routing |
| 3 | Hindi UI Toggle | Multilingual Support | Inclusive design for rural operators |
| 4 | High-Risk Application | CSC Operator Assistant | Catch rejections before they happen |
| 5 | Clean Application | CSC Operator Assistant | Confidence to submit correct applications |

---

## API Reference for Live Demo

All endpoints accept and return JSON. The backend must be running at `http://localhost:8000`.

### Beneficiary Discovery
```
POST http://localhost:8000/api/beneficiary/discover
Content-Type: application/json
```

### Grievance Submission
```
POST http://localhost:8000/api/grievance/submit
Content-Type: application/json
```

### Application Validation
```
POST http://localhost:8000/api/application/validate
Content-Type: application/json
```

### Health Check
```
GET http://localhost:8000/api/health
```

---

## Backup: Direct API Calls (if UI has issues)

Run `python demo_runner.py` from the `backend/` directory to execute all five scenarios programmatically and verify end-to-end functionality.

---

## Common Questions & Answers

**Q: Is this using real government data?**  
A: No — we use realistic synthetic data modeled on Chhattisgarh district records. Production deployment would connect to actual e-District databases.

**Q: How accurate is the Hindi classification?**  
A: The mBERT model achieves ~85–90% accuracy on our test set. The design targets F1 ≥ 0.94 with fine-tuning on real grievance data.

**Q: Does it work offline?**  
A: The architecture supports offline operation via a Local NLP Model cached on the device. The MVP demo requires connectivity; offline mode is implemented in the enhanced CSC Operator Assistant (Requirements 16–21).

**Q: What languages are supported?**  
A: Hindi (`hi`), English (`en`), and Chhattisgarhi (`chhattisgarhi`) for grievance submission. The UI supports English and Hindi.
