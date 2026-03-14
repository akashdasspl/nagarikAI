"""
Manual integration test for Beneficiary Discovery UI
Run this to verify the UI can communicate with the backend
"""
import requests
import json

# Test data from civil_death_records.csv
test_data = {
    "record_id": "CDR001",
    "name": "राम कुमार शर्मा",
    "father_name": "श्री मोहन लाल शर्मा",
    "date_of_death": "2023-03-15",
    "age": 67,
    "gender": "M",
    "district": "रायपुर",
    "village": "खमतराई"
}

print("Testing Beneficiary Discovery API...")
print(f"Request: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
print()

try:
    response = requests.post(
        "http://localhost:8000/api/beneficiary/discover",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("Response:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        print()
        
        if data.get("total_found", 0) > 0:
            print(f"✓ Found {data['total_found']} beneficiaries")
            print()
            
            for i, beneficiary in enumerate(data["beneficiaries"], 1):
                print(f"Beneficiary #{i}:")
                print(f"  Name: {beneficiary['beneficiary_name']}")
                print(f"  Relationship: {beneficiary['relationship']}")
                print(f"  Scheme: {beneficiary['scheme_type']}")
                print(f"  Confidence: {beneficiary['confidence_score']:.2%}")
                print(f"  Reasoning: {beneficiary['eligibility_reasoning']}")
                print()
        else:
            print("✓ No beneficiaries found (this is expected for some records)")
    else:
        print(f"✗ Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("✗ Error: Could not connect to backend server")
    print("  Make sure the backend is running on http://localhost:8000")
except Exception as e:
    print(f"✗ Error: {e}")
