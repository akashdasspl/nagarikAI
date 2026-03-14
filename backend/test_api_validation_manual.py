"""
Manual API test for application validation endpoint
Run this with the server running to test the actual HTTP endpoint
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_validation_endpoint():
    """Test the validation endpoint with a sample request"""
    
    print("Testing POST /api/application/validate endpoint...")
    print("-" * 60)
    
    # Test 1: Valid application
    print("\nTest 1: Valid widow pension application")
    request_data = {
        "application_id": "TEST_001",
        "scheme_type": "widow_pension",
        "operator_id": "OP_TEST",
        "application_data": {
            "applicant_name": "Test Applicant",
            "date_of_birth": "1985-03-15",
            "spouse_death_certificate": "DEATH_TEST_001",
            "address": "Test Village, Test District",
            "bank_account": "1234567890123456",
            "aadhaar_number": "123456789012",
            "annual_income": 50000
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/application/validate", json=request_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ Success: {data['message']}")
            print(f"  Risk Score: {data['validation']['rejection_risk_score']}")
            print(f"  Issues Found: {len(data['validation']['validation_issues'])}")
        else:
            print(f"\n✗ Failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to server")
        print("  Please start the server with: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False
    
    # Test 2: Application with issues
    print("\n" + "-" * 60)
    print("\nTest 2: Application with missing fields")
    request_data = {
        "application_id": "TEST_002",
        "scheme_type": "widow_pension",
        "operator_id": "OP_TEST",
        "application_data": {
            "applicant_name": "Test Applicant 2",
            "date_of_birth": "1990-01-01",
            # Missing spouse_death_certificate
            "address": "Test Village"
            # Missing bank_account and aadhaar_number
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/application/validate", json=request_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ Success: {data['message']}")
            print(f"  Risk Score: {data['validation']['rejection_risk_score']}")
            print(f"  Issues Found: {len(data['validation']['validation_issues'])}")
            print(f"  Guidance Items: {len(data['validation']['corrective_guidance'])}")
            
            if data['validation']['validation_issues']:
                print("\n  Issues:")
                for issue in data['validation']['validation_issues']:
                    print(f"    - {issue['field_name']}: {issue['severity']} ({issue['description']})")
        else:
            print(f"\n✗ Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("Manual API test completed successfully!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_validation_endpoint()
