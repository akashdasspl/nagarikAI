# Beneficiary Discovery Engine - Demo Guide

## Overview
The Beneficiary Discovery Engine helps identify eligible citizens who are not enrolled in welfare schemes by cross-referencing Aadhaar records with existing scheme enrollments.

## Demo Data Available

### Aadhaar Records
- **Total Records**: 50 citizens
- **Age Range**: 43-82 years old
- **Districts**: Raipur, Bilaspur, Durg, Rajnandgaon
- **Gender Distribution**: Mixed (Male/Female)

### Ration Card Records
- **Total Records**: 50 families
- **Card Types**: APL (Above Poverty Line) and BPL (Below Poverty Line)
- **Status**: All active

### Civil Death Records
- Available for cross-referencing deceased individuals

## Demo Scenarios

### Scenario 1: Discover Elderly Citizens Without Old Age Pension
**Search Query**: "60 वर्ष से अधिक" (Above 60 years)

**Expected Results**: Citizens aged 60+ who:
- Have Aadhaar cards
- Are NOT enrolled in old age pension
- Are eligible based on age criteria

**Sample Eligible Citizens**:
1. **राम कुमार शर्मा** (Age: 68) - Raipur, Khamtarai
2. **सुनीता देवी पटेल** (Age: 64) - Bilaspur, Kota
3. **विनोद कुमार वर्मा** (Age: 59) - Raipur, Arang
4. **मीना बाई साहू** (Age: 70) - Raipur, Baloda Bazar
5. **कमला देवी** (Age: 80) - Raipur, Baloda Bazar

### Scenario 2: Discover Widows Without Widow Pension
**Search Query**: "विधवा" (Widow)

**How to Test**:
1. Look for female citizens whose husbands are in civil death records
2. Cross-reference with widow pension enrollments
3. Identify eligible widows not enrolled

**Sample Test Case**:
- Search for women whose father's name matches deceased records
- Filter by age 18+ and female gender
- Check against widow pension enrollment database

### Scenario 3: Discover BPL Families Without Ration Cards
**Search Query**: "BPL राशन कार्ड" (BPL Ration Card)

**Expected Results**: Families that:
- Have low income (< ₹1.5 lakh annually)
- Do NOT have BPL ration cards
- Meet BPL criteria

### Scenario 4: Discover Disabled Citizens Without Disability Pension
**Search Query**: "विकलांग" (Disabled)

**Note**: This requires disability status in Aadhaar records or separate disability database

## How to Use the Demo

### Step 1: Navigate to Beneficiary Discovery
1. Open the application
2. Click on "Beneficiary Discovery" in the navigation menu
3. You'll see the search interface

### Step 2: Enter Search Criteria
**Example Searches**:

```
1. Age-based search:
   "60 वर्ष से अधिक उम्र के नागरिक"
   (Citizens above 60 years)

2. Location-based search:
   "रायपुर जिले के पात्र नागरिक"
   (Eligible citizens in Raipur district)

3. Scheme-specific search:
   "वृद्धावस्था पेंशन के लिए पात्र"
   (Eligible for old age pension)

4. Combined search:
   "बिलासपुर में 65 वर्ष से अधिक महिलाएं"
   (Women above 65 years in Bilaspur)
```

### Step 3: Review Results
The system will show:
- **Name** (नाम)
- **Age** (आयु)
- **District** (जिला)
- **Village** (गाँव)
- **Eligible Schemes** (पात्र योजनाएं)
- **Match Score** (मिलान स्कोर)

### Step 4: Take Action
For each discovered beneficiary:
1. **View Details**: Click to see full profile
2. **Initiate Enrollment**: Start application process
3. **Mark for Follow-up**: Flag for field officer visit
4. **Export List**: Download for offline processing

## Sample API Calls

### Discover Elderly Citizens
```bash
curl -X POST http://localhost:8000/api/beneficiary/discover \
  -H "Content-Type: application/json" \
  -d '{
    "query": "60 वर्ष से अधिक",
    "scheme_type": "old_age_pension",
    "district": "रायपुर"
  }'
```

### Expected Response
```json
{
  "matches": [
    {
      "aadhaar_number": "234567890123",
      "name": "राम कुमार शर्मा",
      "age": 68,
      "district": "रायपुर",
      "village": "खमतराई",
      "eligible_schemes": ["old_age_pension"],
      "match_score": 0.95,
      "reason": "Age 68 years, no existing old age pension enrollment"
    },
    {
      "aadhaar_number": "345678901234",
      "name": "सुनीता देवी पटेल",
      "age": 64,
      "district": "बिलासपुर",
      "village": "कोटा",
      "eligible_schemes": ["old_age_pension"],
      "match_score": 0.92,
      "reason": "Age 64 years, no existing old age pension enrollment"
    }
  ],
  "total_found": 15,
  "query_time_ms": 245
}
```

## Key Features Demonstrated

### 1. Fuzzy Name Matching
- Handles variations in name spelling
- Matches "राम कुमार" with "रामकुमार"
- Accounts for father's name variations

### 2. Age Calculation
- Automatically calculates age from date of birth
- Filters based on scheme eligibility criteria
- Handles edge cases (birthdays, leap years)

### 3. Cross-Database Reconciliation
- Checks Aadhaar records
- Verifies against ration card database
- Cross-references civil death records
- Validates existing scheme enrollments

### 4. Eligibility Inference
- Applies scheme-specific rules
- Considers age, income, family status
- Validates document requirements
- Calculates match confidence score

### 5. Duplicate Detection
- Identifies potential duplicate enrollments
- Flags suspicious patterns
- Prevents double enrollment

## Testing Checklist

- [ ] Search for elderly citizens (60+)
- [ ] Filter by district (Raipur, Bilaspur, Durg)
- [ ] Search by name (partial match)
- [ ] Search by village
- [ ] View detailed beneficiary profile
- [ ] Check eligible schemes list
- [ ] Verify match score calculation
- [ ] Test with invalid/missing data
- [ ] Export results to CSV
- [ ] Initiate enrollment from discovery

## Common Test Queries

### Hindi Queries
```
1. "रायपुर में वृद्ध नागरिक"
2. "विधवा महिलाएं बिलासपुर"
3. "BPL परिवार बिना राशन कार्ड"
4. "60 साल से ऊपर"
5. "पेंशन के लिए पात्र"
```

### English Queries
```
1. "elderly citizens in Raipur"
2. "widow women Bilaspur"
3. "BPL families without ration card"
4. "above 60 years"
5. "eligible for pension"
```

## Expected Performance

- **Query Response Time**: < 500ms
- **Match Accuracy**: > 90%
- **False Positive Rate**: < 5%
- **Database Size**: 50 Aadhaar records, 50 ration cards
- **Concurrent Users**: Supports 10+ simultaneous searches

## Troubleshooting

### No Results Found
- Check if search query is too specific
- Verify database has matching records
- Try broader search terms
- Check district/village spelling

### Low Match Scores
- Review eligibility criteria
- Check for missing data in Aadhaar records
- Verify scheme enrollment database is up-to-date

### Duplicate Results
- System may show same person with slight name variations
- Use Aadhaar number to identify true duplicates
- Entity resolution engine will flag these

## Demo Script for Presentation

**Step 1**: "Let me show you how we discover eligible beneficiaries..."

**Step 2**: Enter search query: "60 वर्ष से अधिक रायपुर"

**Step 3**: "The system found 8 elderly citizens in Raipur who are eligible for old age pension but not enrolled."

**Step 4**: Click on first result to show details

**Step 5**: "Here we can see राम कुमार शर्मा, age 68, has Aadhaar and ration card but no pension enrollment."

**Step 6**: Click "Initiate Enrollment" button

**Step 7**: "The system now guides the operator through the enrollment process with pre-filled data."

## Next Steps

After discovering beneficiaries:
1. **Field Verification**: Send list to field officers
2. **Outreach Campaign**: Organize enrollment camps in identified villages
3. **Follow-up**: Track enrollment completion
4. **Analytics**: Monitor discovery-to-enrollment conversion rate

## Data Privacy Note

All demo data uses fictional names and Aadhaar numbers. In production:
- Real Aadhaar data is encrypted
- Access is logged and audited
- PII is masked in exports
- Complies with data protection regulations
