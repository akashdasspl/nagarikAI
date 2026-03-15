"""
Quick test to check if Gemini API is working
"""
from models.guidance_interface import GuidanceInterface
import requests
import os

print("Testing Gemini API...")
print("=" * 60)

# Test API key directly
api_key = 'AIzaSyDYghQKOwDOTtTOpE5H65wkZLm2bcEmQ8w'
print(f"API Key: {api_key[:20]}...")
print()

# Test with a simple request
url = f'https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}'

try:
    response = requests.post(
        url,
        headers={'Content-Type': 'application/json'},
        json={
            'contents': [{
                'parts': [{
                    'text': "What is 2+2?"
                }]
            }]
        },
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Gemini API is WORKING!")
        print()
        print("Response:")
        if 'candidates' in data:
            print(data['candidates'][0]['content']['parts'][0]['text'])
        else:
            print(data)
    else:
        print("❌ Gemini API returned an error")
        print()
        print("Response:")
        print(response.text)
        
except Exception as e:
    print("❌ Error calling Gemini API")
    print()
    print(f"Error: {str(e)}")
