"""
Test Gemini LLM call directly
"""
from models.guidance_interface import GuidanceInterface

# Create instance
gi = GuidanceInterface()

# Test complex question
question = "अगर मेरी उम्र 62 साल है और मेरी सालाना आय 75000 रुपये है, लेकिन मेरे पास आयु प्रमाण पत्र नहीं है, तो क्या मैं वृद्धावस्था पेंशन के लिए आवेदन कर सकता हूं?"

print("Testing Gemini LLM Call")
print("="*80)
print(f"Question: {question}")
print(f"Length: {len(question)} characters")
print()

# Test if it's detected as complex
is_complex = gi._is_complex_question(question)
print(f"Is Complex: {is_complex}")
print()

if is_complex:
    print("Calling Gemini LLM...")
    response = gi._get_llm_response(question, "old_age_pension", "hi")
    
    if response:
        print(f"\n✓ LLM Response received:")
        print(f"{response}")
        print(f"\nResponse length: {len(response)} characters")
    else:
        print("\n✗ LLM call failed or returned None")
else:
    print("Question not detected as complex, skipping LLM call")
