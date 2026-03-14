"""
List available Gemini models
"""
import requests

api_key = "AIzaSyDYghQKOwDOTtTOpE5H65wkZLm2bcEmQ8w"

# Try to list models
url = f'https://generativelanguage.googleapis.com/v1/models?key={api_key}'

print("Listing available Gemini models...")
print(f"URL: {url}")
print()

try:
    response = requests.get(url, timeout=10)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nAvailable models:")
        if 'models' in data:
            for model in data['models']:
                print(f"  - {model.get('name', 'Unknown')}")
                if 'supportedGenerationMethods' in model:
                    print(f"    Methods: {', '.join(model['supportedGenerationMethods'])}")
        else:
            print("No models found in response")
            print(f"Response: {data}")
    else:
        print(f"\nError response:")
        print(response.text)
        
except Exception as e:
    print(f"\nError: {str(e)}")
    import traceback
    traceback.print_exc()
