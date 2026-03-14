"""
Test script to verify Gemini API integration in Guidance Interface
"""
import requests
import json

# Test with a complex question that should trigger LLM
complex_question = "अगर मेरी उम्र 62 साल है और मेरी सालाना आय 75000 रुपये है, लेकिन मेरे पास आयु प्रमाण पत्र नहीं है, तो क्या मैं वृद्धावस्था पेंशन के लिए आवेदन कर सकता हूं?"

# Test with a simple question that should use cached response
simple_question = "कौन से दस्तावेज़ चाहिए"

def test_guidance_query(question, test_name):
    """Test the guidance query endpoint"""
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"{'='*60}")
    print(f"Question: {question}")
    print(f"Question length: {len(question)} characters")
    
    url = "http://localhost:8000/api/guidance/query"
    payload = {
        "intent": "eligibility_criteria",
        "scheme_type": "old_age_pension",
        "active_field": "age",
        "language": "hi",
        "question_text": question
    }
    
    try:
        print("\nSending request to backend...")
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ Success!")
            print(f"Response text: {data['response_text'][:200]}...")
            print(f"Full response length: {len(data['response_text'])} characters")
            return True
        else:
            print(f"\n✗ Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n✗ Request timed out (>15 seconds)")
        return False
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Gemini API Integration in Guidance Interface")
    print("="*60)
    
    # Test 1: Simple question (should use cache)
    test1_result = test_guidance_query(simple_question, "Simple Question (Cached Response)")
    
    # Test 2: Complex question (should use Gemini LLM)
    test2_result = test_guidance_query(complex_question, "Complex Question (Gemini LLM)")
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    print(f"Simple question test: {'✓ PASSED' if test1_result else '✗ FAILED'}")
    print(f"Complex question test: {'✓ PASSED' if test2_result else '✗ FAILED'}")
    print(f"\nOverall: {'✓ ALL TESTS PASSED' if test1_result and test2_result else '✗ SOME TESTS FAILED'}")
