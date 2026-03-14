"""
Manual API test to verify the beneficiary discovery endpoint
"""
import requests
import json

# Test data - death record that should match ration card data
death_record = {
    "record_id": "CDR001",
    "name": "राम कुमार शर्मा",
    "father_name": "श्री मोहन लाल शर्मा",
    "date_of_death": "2023-03-15",
    "age": 67,
    "gender": "M",
    "district": "रायपुर",
    "village": "खमतराई",
    "registration_date": "2023-03-18"
}

# Make request to the API
response = requests.post("http://127.0.0.1:8000/api/beneficiary/discover", json=death_record)

print(f"Status Code: {response.status_code}")
print(f"\nResponse:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
