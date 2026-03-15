# How to Test Gemini Integration in Guidance Assistant

## Quick Test

1. Go to http://localhost:3001
2. Navigate to "Operator Assistant"
3. Click the lightbulb icon (💡) to open Guidance Assistant
4. Type a complex question in the search box (don't click the quick buttons)

## Test Questions

### English:
- "What if I don't have my birth certificate but I have school records, can I still apply?"
- "My husband died 2 years ago but I never got a death certificate, what should I do?"
- "Can I apply for multiple schemes at the same time or do I need separate applications?"

### Hindi:
- "अगर मेरे पास आधार कार्ड नहीं है लेकिन राशन कार्ड है तो क्या मैं आवेदन कर सकता हूं?"
- "मेरे पति की मृत्यु 2 साल पहले हुई थी लेकिन मुझे मृत्यु प्रमाण पत्र नहीं मिला, मुझे क्या करना चाहिए?"

## Expected Behavior

### If Gemini is Working:
- ⏱️ Response takes 2-5 seconds
- 📝 Detailed, contextual answer
- 🎯 Addresses your specific scenario
- 💬 Natural language response

### If Gemini is NOT Working (Quota Exceeded):
- ⚡ Instant response (< 1 second)
- 📋 Generic cached answer
- 🔄 Falls back to predefined Q&A
- ⚠️ May not fully address your question

## Check Backend Logs

Run this command to see if Gemini API is being called:
```bash
# In backend directory
tail -f logs.txt
```

Look for:
- "Calling Gemini API for complex question"
- "Gemini API response received"
- Or error: "Gemini API quota exceeded" (HTTP 429)

## Current Status

According to previous tests, the Gemini API key has **exceeded quota** (HTTP 429 error).
The system gracefully falls back to cached responses when this happens.

## To Fix Quota Issue

1. Get a new Gemini API key from: https://makersuite.google.com/app/apikey
2. Update the API key in `backend/models/guidance_interface.py`
3. Restart the backend server

## Alternative: Test with Backend Script

```bash
cd backend
python -c "from models.guidance_interface import GuidanceInterface; gi = GuidanceInterface(); print(gi._get_llm_response('What if I have no documents?', 'widow_pension', 'en'))"
```

This will directly test the Gemini API call and show any errors.
