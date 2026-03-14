"""
Test complex question detection logic
"""
from models.guidance_interface import GuidanceInterface

# Create instance
gi = GuidanceInterface()

# Test questions
questions = [
    ("कौन से दस्तावेज़ चाहिए", "Simple - documents"),
    ("पात्रता क्या है", "Simple - eligibility"),
    ("अगर मेरी उम्र 62 साल है और मेरी सालाना आय 75000 रुपये है, लेकिन मेरे पास आयु प्रमाण पत्र नहीं है, तो क्या मैं वृद्धावस्था पेंशन के लिए आवेदन कर सकता हूं?", "Complex - what if scenario"),
    ("What if I have both disability and old age pension?", "Complex - multiple conditions"),
    ("मेरी उम्र 65 है लेकिन आय प्रमाण नहीं है", "Complex - but clause"),
    ("How long does it take?", "Simple - processing time"),
]

print("Testing Complex Question Detection")
print("="*80)

for question, description in questions:
    is_complex = gi._is_complex_question(question)
    print(f"\nQuestion: {question[:80]}...")
    print(f"Description: {description}")
    print(f"Length: {len(question)} characters")
    print(f"Is Complex: {is_complex}")
    print("-"*80)
