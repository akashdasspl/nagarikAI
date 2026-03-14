"""
Demo script for Grievance Intelligence API

This script demonstrates the POST /api/grievance/submit endpoint
with various Hindi grievance examples across different departments.

Run the FastAPI server first: python main.py or uvicorn main:app --reload
Then run this script: python demo_grievance_api.py
"""
import requests
import json
from datetime import datetime


BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def submit_grievance(citizen_id, text, language):
    """Submit a grievance and display the response"""
    print(f"\n📝 Submitting grievance:")
    print(f"   Citizen ID: {citizen_id}")
    print(f"   Language: {language}")
    print(f"   Text: {text}")
    
    payload = {
        "citizen_id": citizen_id,
        "text": text,
        "language": language
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/grievance/submit", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            grievance = data["grievance"]
            
            print(f"\n✅ Success!")
            print(f"   Grievance ID: {grievance['grievance_id']}")
            print(f"   Category: {grievance['category']}")
            print(f"   Confidence: {grievance['classification_confidence']:.2%}")
            print(f"   Assigned Department: {grievance['assigned_department']}")
            print(f"   Predicted SLA: {grievance['predicted_sla']} hours")
            print(f"   Status: {grievance['status']}")
            print(f"   SLA Deadline: {grievance['sla_deadline']}")
            
            return grievance
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"   {response.json()}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
        print("   Make sure the FastAPI server is running:")
        print("   python main.py  OR  uvicorn main:app --reload")
        return None
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None


def main():
    """Run demo scenarios"""
    print_section("Grievance Intelligence API Demo")
    print("\nThis demo shows how the API classifies Hindi grievances")
    print("and routes them to appropriate departments with SLA predictions.")
    
    # Test 1: Revenue Department
    print_section("Test 1: Revenue Department - Certificate Issue")
    submit_grievance(
        "CIT001",
        "मेरा जाति प्रमाण पत्र दो महीने से लंबित है। कृपया जल्दी बनाएं।",
        "hi"
    )
    
    # Test 2: Health Department
    print_section("Test 2: Health Department - Hospital Issue")
    submit_grievance(
        "CIT002",
        "सरकारी अस्पताल में दवाइयां नहीं मिल रही हैं। डॉक्टर भी समय पर नहीं आते।",
        "hi"
    )
    
    # Test 3: Social Welfare - Pension
    print_section("Test 3: Social Welfare - Pension Issue")
    submit_grievance(
        "CIT003",
        "मेरी विधवा पेंशन तीन महीने से नहीं आई है। मैं बहुत परेशान हूं।",
        "hi"
    )
    
    # Test 4: Infrastructure - Road
    print_section("Test 4: Infrastructure - Road Issue")
    submit_grievance(
        "CIT004",
        "गांव की मुख्य सड़क बहुत खराब है। बारिश में बड़े गड्ढे हो गए हैं।",
        "hi"
    )
    
    # Test 5: Education Department
    print_section("Test 5: Education Department - School Issue")
    submit_grievance(
        "CIT005",
        "प्राथमिक स्कूल में शिक्षक नहीं आते। बच्चों की पढ़ाई बर्बाद हो रही है।",
        "hi"
    )
    
    # Test 6: Multiple keywords (Revenue)
    print_section("Test 6: Multiple Keywords - Revenue")
    submit_grievance(
        "CIT006",
        "मुझे आय प्रमाण पत्र और निवास प्रमाण पत्र दोनों चाहिए। कृपया बनाएं।",
        "hi"
    )
    
    # Test 7: Infrastructure - Electricity
    print_section("Test 7: Infrastructure - Electricity Issue")
    submit_grievance(
        "CIT007",
        "हमारे गांव में बिजली की समस्या है। ट्रांसफार्मर खराब है।",
        "hi"
    )
    
    # Test 8: Social Welfare - Ration Card
    print_section("Test 8: Social Welfare - Ration Card Issue")
    submit_grievance(
        "CIT008",
        "मेरा राशन कार्ड अभी तक नहीं बना है। आवेदन दो महीने पहले किया था।",
        "hi"
    )
    
    # Test 9: English grievance
    print_section("Test 9: English Grievance")
    submit_grievance(
        "CIT009",
        "My caste certificate application has been pending for 2 months. Please expedite.",
        "en"
    )
    
    # Test 10: Error case - Empty text
    print_section("Test 10: Error Case - Empty Text")
    submit_grievance(
        "CIT010",
        "",
        "hi"
    )
    
    print_section("Demo Complete")
    print("\n✨ All test cases executed!")
    print("\nKey Features Demonstrated:")
    print("  ✓ Hindi text classification using mBERT")
    print("  ✓ Department routing based on classification")
    print("  ✓ SLA prediction (24-120 hours based on department)")
    print("  ✓ Confidence scoring for classifications")
    print("  ✓ Error handling for invalid inputs")
    print("\nValidates Requirements: 3.1, 3.3, 3.4")


if __name__ == "__main__":
    main()
