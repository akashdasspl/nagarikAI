"""
Demo script for CSC Operator Assistant API (Task 4.2)
Demonstrates the POST /api/application/validate endpoint
"""
import requests
import json
from datetime import datetime

# API endpoint
BASE_URL = "http://localhost:8000"
VALIDATE_ENDPOINT = f"{BASE_URL}/api/application/validate"


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_validation_result(response_data):
    """Print validation result in a formatted way"""
    validation = response_data["validation"]
    
    print(f"Application ID: {validation['application_id']}")
    print(f"Scheme Type: {validation['scheme_type']}")
    print(f"Rejection Risk Score: {validation['rejection_risk_score']:.2f}")
    print(f"Validated At: {validation['validated_at']}")
    print(f"Operator ID: {validation['operator_id']}")
    
    print(f"\nValidation Issues: {len(validation['validation_issues'])}")
    for i, issue in enumerate(validation['validation_issues'], 1):
        print(f"\n  Issue {i}:")
        print(f"    Field: {issue['field_name']}")
        print(f"    Type: {issue['issue_type']}")
        print(f"    Severity: {issue['severity']}")
        print(f"    Impact on Risk: {issue['impact_on_risk']:.2f}")
        print(f"    Description: {issue['description']}")
    
    print(f"\nCorrective Guidance: {len(validation['corrective_guidance'])}")
    for i, guidance in enumerate(validation['corrective_guidance'], 1):
        print(f"\n  Guidance {i} (Priority {guidance['priority']}):")
        print(f"    Hindi: {guidance['guidance_text_hindi']}")
        print(f"    English: {guidance['guidance_text_english']}")
        print(f"    Action: {guidance['suggested_action']}")


def demo_valid_application():
    """Demo 1: Valid application with no issues"""
    print_section("Demo 1: Valid Widow Pension Application")
    
    request_data = {
        "application_id": "APP_DEMO_001",
        "scheme_type": "widow_pension",
        "operator_id": "OP_DEMO_123",
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
    
    print("Request:")
    print(json.dumps(request_data, indent=2))
    
    response = requests.post(VALIDATE_ENDPOINT, json=request_data)
    
    print("\nResponse:")
    print(f"Status Code: {response.status_code}")
    print(f"Message: {response.json()['message']}")
    print_validation_result(response.json())


def demo_missing_fields():
    """Demo 2: Application with missing required fields"""
    print_section("Demo 2: Application with Missing Required Fields")
    
    request_data = {
        "application_id": "APP_DEMO_002",
        "scheme_type": "widow_pension",
        "operator_id": "OP_DEMO_123",
        "application_data": {
            "applicant_name": "Kavita Sharma",
            "date_of_birth": "1990-07-20",
            # Missing spouse_death_certificate (critical)
            "address": "Village Bilaspur",
            # Missing bank_account (high)
            "aadhaar_number": "987654321098"
        }
    }
    
    print("Request:")
    print(json.dumps(request_data, indent=2))
    
    response = requests.post(VALIDATE_ENDPOINT, json=request_data)
    
    print("\nResponse:")
    print(f"Status Code: {response.status_code}")
    print(f"Message: {response.json()['message']}")
    print_validation_result(response.json())


def demo_age_issue():
    """Demo 3: Old age pension with applicant below minimum age"""
    print_section("Demo 3: Old Age Pension - Age Below Minimum")
    
    request_data = {
        "application_id": "APP_DEMO_003",
        "scheme_type": "old_age_pension",
        "operator_id": "OP_DEMO_456",
        "application_data": {
            "applicant_name": "Ram Kumar",
            "date_of_birth": "1980-01-01",  # Age ~44, below 60 minimum
            "age_proof": "AADHAAR_CARD",
            "address": "Village Durg, District Durg, PIN 491001",
            "bank_account": "9876543210987654",
            "aadhaar_number": "111222333444",
            "annual_income": 30000
        }
    }
    
    print("Request:")
    print(json.dumps(request_data, indent=2))
    
    response = requests.post(VALIDATE_ENDPOINT, json=request_data)
    
    print("\nResponse:")
    print(f"Status Code: {response.status_code}")
    print(f"Message: {response.json()['message']}")
    print_validation_result(response.json())


def demo_income_issue():
    """Demo 4: BPL card with income above threshold"""
    print_section("Demo 4: BPL Card - Income Above Threshold")
    
    request_data = {
        "application_id": "APP_DEMO_004",
        "scheme_type": "bpl_card",
        "operator_id": "OP_DEMO_789",
        "application_data": {
            "applicant_name": "Lakshmi Bai",
            "date_of_birth": "1990-05-20",
            "address": "Village Korba, District Korba, PIN 495677",
            "family_members": "4",
            "income_certificate": "INC_CERT_2024_123",
            "aadhaar_number": "555666777888",
            "annual_income": 150000  # Above 50000 threshold for BPL
        }
    }
    
    print("Request:")
    print(json.dumps(request_data, indent=2))
    
    response = requests.post(VALIDATE_ENDPOINT, json=request_data)
    
    print("\nResponse:")
    print(f"Status Code: {response.status_code}")
    print(f"Message: {response.json()['message']}")
    print_validation_result(response.json())


def demo_multiple_issues():
    """Demo 5: Disability pension with multiple issues"""
    print_section("Demo 5: Disability Pension - Multiple Issues")
    
    request_data = {
        "application_id": "APP_DEMO_005",
        "scheme_type": "disability_pension",
        "operator_id": "OP_DEMO_999",
        "application_data": {
            "applicant_name": "Mohan Singh",
            "date_of_birth": "2010-01-01",  # Age ~14, below 18 minimum (critical)
            # Missing disability_certificate (high)
            "address": "Village Raigarh",
            "bank_account": "123",  # Invalid format (medium)
            "aadhaar_number": "12345",  # Invalid format (medium)
            "disability_percentage": 30,  # Below 40% minimum (high)
            "annual_income": 200000  # Above 120000 threshold (high)
        }
    }
    
    print("Request:")
    print(json.dumps(request_data, indent=2))
    
    response = requests.post(VALIDATE_ENDPOINT, json=request_data)
    
    print("\nResponse:")
    print(f"Status Code: {response.status_code}")
    print(f"Message: {response.json()['message']}")
    print_validation_result(response.json())


def demo_valid_disability_pension():
    """Demo 6: Valid disability pension application"""
    print_section("Demo 6: Valid Disability Pension Application")
    
    request_data = {
        "application_id": "APP_DEMO_006",
        "scheme_type": "disability_pension",
        "operator_id": "OP_DEMO_111",
        "application_data": {
            "applicant_name": "Rajesh Kumar",
            "date_of_birth": "1980-06-15",
            "disability_certificate": "DISAB_CERT_2024_456",
            "address": "Village Janjgir, District Janjgir-Champa, PIN 495668",
            "bank_account": "5555666677778888",
            "aadhaar_number": "222333444555",
            "disability_percentage": 65,  # Above 40% minimum
            "annual_income": 40000
        }
    }
    
    print("Request:")
    print(json.dumps(request_data, indent=2))
    
    response = requests.post(VALIDATE_ENDPOINT, json=request_data)
    
    print("\nResponse:")
    print(f"Status Code: {response.status_code}")
    print(f"Message: {response.json()['message']}")
    print_validation_result(response.json())


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("  CSC OPERATOR ASSISTANT API - DEMO")
    print("  Task 4.2: POST /api/application/validate")
    print("=" * 80)
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code != 200:
            print("\nError: API server is not responding correctly")
            print("Please start the server with: uvicorn main:app --reload")
            return
        
        print("\n✓ API server is running")
        
        # Run demos
        demo_valid_application()
        demo_missing_fields()
        demo_age_issue()
        demo_income_issue()
        demo_multiple_issues()
        demo_valid_disability_pension()
        
        print("\n" + "=" * 80)
        print("  DEMO COMPLETED SUCCESSFULLY")
        print("=" * 80 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\nError: Cannot connect to API server")
        print("Please start the server with: uvicorn main:app --reload")
    except Exception as e:
        print(f"\nError: {str(e)}")


if __name__ == "__main__":
    main()
