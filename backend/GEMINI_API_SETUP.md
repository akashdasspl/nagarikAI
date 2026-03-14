# Gemini API Setup for Guidance Interface

The Guidance Interface uses Google Gemini API for handling complex questions that go beyond the predefined Q&A cache.

## API Configuration

The system uses the Gemini API with the following configuration:
- **Model**: `gemini-2.5-flash` (fast, efficient model for real-time responses)
- **API Version**: v1
- **Timeout**: 10 seconds
- **Temperature**: 0.3 (focused, consistent responses)
- **Max Output Tokens**: 300 (concise responses)

## API Key

The API key is configured in the code:
```python
api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyDYghQKOwDOTtTOpE5H65wkZLm2bcEmQ8w')
```

**Note**: The provided API key has a free tier quota limit. If you encounter quota errors (HTTP 429), you'll need to:
1. Wait for the quota to reset (usually daily)
2. Get a new API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. Upgrade to a paid plan for higher quotas

## How It Works

1. **Simple Questions** (< 100 chars, no complex indicators):
   - Served from in-memory cache
   - Response time: < 1 second
   - Works offline

2. **Complex Questions** (contains "what if", "but", multiple conditions):
   - Detected automatically by `_is_complex_question()`
   - Sent to Gemini API with scheme context
   - Response time: 2-5 seconds
   - Requires internet connection

3. **Fallback Behavior**:
   - If API fails (quota exceeded, network error, timeout)
   - System automatically falls back to cached response
   - No error shown to user
   - Graceful degradation

## Testing

Run the test scripts to verify the integration:

```bash
# Test complex question detection
python test_complex_detection.py

# Test LLM API call
python test_llm_call.py

# Test full integration
python test_gemini_integration.py

# List available models
python test_gemini_models.py
```

## Quota Management

Free tier limits (as of 2024):
- 60 requests per minute
- 1,500 requests per day

If you hit quota limits:
- The system will gracefully fall back to cached responses
- Users won't see any errors
- Quick-access buttons will continue to work normally

## Environment Variables

You can override the API key using an environment variable:

```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_api_key_here
```

## Supported Languages

The LLM supports:
- Hindi (hi)
- Chhattisgarhi (chhattisgarhi)
- English (en)

The system instruction ensures responses are in the requested language.

## Getting a New API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and update the environment variable or code

## Available Models

To see all available Gemini models, run:
```bash
python test_gemini_models.py
```

Current available models include:
- gemini-2.5-flash (recommended - fast and efficient)
- gemini-2.5-pro (more capable, slower)
- gemini-2.0-flash (older version)
- gemini-2.0-flash-lite (lightweight version)
