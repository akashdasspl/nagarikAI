"""
Demo script for Grievance Classifier

This script demonstrates the mBERT-based grievance classification system
using real Hindi grievance data from the mock database.
"""
import csv
from models.grievance_classifier import get_classifier


def load_grievances(csv_file='data/grievances.csv'):
    """Load grievances from CSV file"""
    grievances = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            grievances.append(row)
    return grievances


def demo_classification():
    """Demonstrate grievance classification"""
    print("=" * 80)
    print("NagarikAI Grievance Classifier Demo")
    print("=" * 80)
    print()
    
    # Get classifier instance
    classifier = get_classifier()
    
    # Load sample grievances
    print("Loading grievances from data/grievances.csv...")
    grievances = load_grievances()
    print(f"Loaded {len(grievances)} grievances")
    print()
    
    # Classify first 10 grievances
    print("Classifying first 10 grievances:")
    print("-" * 80)
    
    for i, grievance in enumerate(grievances[:10], 1):
        text = grievance['complaint_text']
        actual_dept = grievance['department']
        
        # Classify
        predicted_dept, confidence, sla_hours = classifier.classify(text, 'hi')
        
        # Display results
        print(f"\n{i}. Grievance ID: {grievance['grievance_id']}")
        print(f"   Text: {text[:80]}...")
        print(f"   Actual Department: {actual_dept}")
        print(f"   Predicted Department: {predicted_dept}")
        print(f"   Confidence: {confidence:.2%}")
        print(f"   Predicted SLA: {sla_hours} hours ({sla_hours/24:.1f} days)")
        
        # Check if prediction matches
        match = "✓" if predicted_dept.lower() in actual_dept.lower() or actual_dept.lower() in predicted_dept.lower() else "✗"
        print(f"   Match: {match}")
    
    print()
    print("-" * 80)
    
    # Statistics
    print("\nClassification Statistics:")
    print("-" * 80)
    
    dept_counts = {}
    correct = 0
    total = 0
    
    for grievance in grievances:
        text = grievance['complaint_text']
        actual_dept = grievance['department']
        predicted_dept, confidence, _ = classifier.classify(text, 'hi')
        
        # Count by department
        if predicted_dept not in dept_counts:
            dept_counts[predicted_dept] = 0
        dept_counts[predicted_dept] += 1
        
        # Check accuracy (fuzzy match)
        if predicted_dept.lower() in actual_dept.lower() or actual_dept.lower() in predicted_dept.lower():
            correct += 1
        total += 1
    
    print(f"\nTotal Grievances: {total}")
    print(f"Correct Classifications: {correct}")
    print(f"Accuracy: {correct/total:.2%}")
    print()
    
    print("Distribution by Predicted Department:")
    for dept, count in sorted(dept_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {dept}: {count} ({count/total:.1%})")
    
    print()
    print("=" * 80)


def demo_custom_grievances():
    """Demonstrate classification with custom grievances"""
    print("\n" + "=" * 80)
    print("Custom Grievance Classification Demo")
    print("=" * 80)
    print()
    
    classifier = get_classifier()
    
    # Custom test cases
    test_cases = [
        ("मेरा राशन कार्ड नहीं बन रहा है", "Social Welfare"),
        ("स्कूल में शिक्षक नहीं आते हैं", "Education"),
        ("अस्पताल में दवाई नहीं मिल रही", "Health"),
        ("सड़क पर बहुत गड्ढे हैं", "Infrastructure"),
        ("जमीन का खतियान चाहिए", "Revenue"),
        ("बिजली का बिल गलत आया है", "Infrastructure"),
        ("पेंशन का पैसा नहीं आया", "Social Welfare"),
        ("बच्चे को एडमिशन नहीं मिल रहा", "Education"),
        ("डॉक्टर नहीं मिलते हैं", "Health"),
        ("मृत्यु प्रमाण पत्र बनवाना है", "Revenue"),
    ]
    
    correct = 0
    for text, expected_dept in test_cases:
        predicted_dept, confidence, sla_hours = classifier.classify(text, 'hi')
        match = "✓" if expected_dept.lower() in predicted_dept.lower() else "✗"
        
        if expected_dept.lower() in predicted_dept.lower():
            correct += 1
        
        print(f"{match} Text: {text}")
        print(f"  Expected: {expected_dept}")
        print(f"  Predicted: {predicted_dept} (confidence: {confidence:.2%}, SLA: {sla_hours}h)")
        print()
    
    print(f"Accuracy: {correct}/{len(test_cases)} ({correct/len(test_cases):.1%})")
    print("=" * 80)


if __name__ == '__main__':
    # Run demos
    demo_classification()
    demo_custom_grievances()
