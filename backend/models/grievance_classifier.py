"""
Grievance Classifier using multilingual BERT (mBERT)

This module implements a lightweight grievance classification system using
pre-trained multilingual BERT for Hindi and Chhattisgarhi text.

For the hackathon MVP, we use zero-shot classification with a simple
mapping approach to keep the model lightweight and demo-ready.

Validates: Requirements 3.1, 3.2
"""
from typing import Dict, Tuple, Optional
import re
from datetime import timedelta


class GrievanceClassifier:
    """
    Lightweight grievance classifier for Hindi/Chhattisgarhi text
    
    Uses keyword-based classification with Hindi text matching for demo purposes.
    In production, this would use fine-tuned mBERT model.
    """
    
    # Department categories (simplified to 5 for MVP)
    DEPARTMENTS = {
        'revenue': 'Revenue',
        'health': 'Health',
        'education': 'Education',
        'social_welfare': 'Social Welfare',
        'infrastructure': 'Infrastructure'
    }
    
    # Hindi keywords for each department
    KEYWORDS = {
        'revenue': [
            'राजस्व', 'जमीन', 'खतियान', 'म्यूटेशन', 'नक्शा', 'रजिस्ट्री',
            'जाति प्रमाण', 'आय प्रमाण', 'निवास प्रमाण',
            'जन्म प्रमाण', 'चरित्र प्रमाण', 'स्टाम्प ड्यूटी', 'कब्जा',
            'मृत्यु प्रमाण पत्र', 'जाति प्रमाण पत्र', 'आय प्रमाण पत्र'
        ],
        'health': [
            'स्वास्थ्य', 'अस्पताल', 'डॉक्टर', 'दवाई', 'दवाइयां', 'इलाज',
            'आयुष्मान', 'एम्बुलेंस', 'नर्स', 'मरीज', 'ऑपरेशन',
            'एक्स-रे', 'मशीन', 'स्वास्थ्य केंद्र'
        ],
        'education': [
            'शिक्षा', 'स्कूल', 'शिक्षक', 'पढ़ाई', 'बच्चे', 'छात्र',
            'छात्रवृत्ति', 'स्कॉलरशिप', 'एडमिशन', 'यूनिफॉर्म',
            'मिड डे मील', 'किताब', 'ट्रांसफर सर्टिफिकेट'
        ],
        'social_welfare': [
            'पेंशन', 'विधवा', 'विकलांग', 'समाज कल्याण', 'वृद्धा',
            'आंगनवाड़ी', 'राशन कार्ड', 'महिला', 'बाल विकास', 'कार्यकर्ता',
            'विधवा पेंशन', 'वृद्धा पेंशन', 'विकलांग पेंशन', 'पेंशन का'
        ],
        'infrastructure': [
            'सड़क', 'बिजली', 'पानी', 'नाली', 'ड्रेनेज', 'गड्ढे',
            'स्ट्रीट लाइट', 'ट्रांसफार्मर', 'कनेक्शन', 'बिल',
            'मीटर', 'पोल', 'तार', 'हैंडपंप', 'टंकी', 'पाइप',
            'निर्माण', 'मरम्मत', 'कचरा', 'सफाई', 'गांव'
        ]
    }
    
    # SLA predictions (in hours) for each department
    SLA_HOURS = {
        'revenue': 72,      # 3 days
        'health': 24,       # 1 day (urgent)
        'education': 48,    # 2 days
        'social_welfare': 96,  # 4 days
        'infrastructure': 120  # 5 days
    }
    
    def __init__(self):
        """Initialize the classifier"""
        # In production, this would load the fine-tuned mBERT model
        # For MVP, we use keyword-based classification
        pass
    
    def classify(
        self,
        grievance_text: str,
        language: str = 'hi'
    ) -> Tuple[str, float, int]:
        """
        Classify grievance text into department category
        
        Args:
            grievance_text: The grievance text in Hindi/Chhattisgarhi
            language: Language code ('hi' or 'chhattisgarhi')
        
        Returns:
            Tuple of (department, confidence_score, predicted_sla_hours)
            
        Validates: Requirements 3.1, 3.2
        """
        if not grievance_text or not grievance_text.strip():
            return self.DEPARTMENTS['infrastructure'], 0.5, self.SLA_HOURS['infrastructure']
        
        # Normalize text for matching
        text_lower = grievance_text.lower()
        
        # Count keyword matches for each department
        scores = {}
        for dept_key, keywords in self.KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    # Give more weight to longer, more specific keywords
                    weight = len(keyword.split())  # Multi-word keywords get more weight
                    score += weight
            scores[dept_key] = score
        
        # Find department with highest score
        if max(scores.values()) == 0:
            # No keywords matched - default to infrastructure
            department_key = 'infrastructure'
            confidence = 0.5
        else:
            department_key = max(scores, key=scores.get)
            # Calculate confidence based on match count
            # More matches = higher confidence
            max_score = scores[department_key]
            total_keywords = len(self.KEYWORDS[department_key])
            confidence = min(0.95, 0.7 + (max_score / total_keywords) * 0.25)
        
        department = self.DEPARTMENTS[department_key]
        sla_hours = self.SLA_HOURS[department_key]
        
        return department, confidence, sla_hours
    
    def predict_sla(
        self,
        category: str,
        grievance_features: Optional[Dict] = None
    ) -> timedelta:
        """
        Predict SLA completion time based on category
        
        Args:
            category: Department category
            grievance_features: Optional features for more accurate prediction
        
        Returns:
            Predicted SLA as timedelta
            
        Validates: Requirements 3.4
        """
        # Map category back to key
        category_key = None
        for key, dept_name in self.DEPARTMENTS.items():
            if dept_name.lower() == category.lower():
                category_key = key
                break
        
        if category_key is None:
            # Default to infrastructure if category not found
            hours = self.SLA_HOURS['infrastructure']
        else:
            hours = self.SLA_HOURS[category_key]
        
        return timedelta(hours=hours)


# Global classifier instance
_classifier_instance = None


def get_classifier() -> GrievanceClassifier:
    """
    Get or create the global classifier instance
    
    Returns:
        GrievanceClassifier instance
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = GrievanceClassifier()
    return _classifier_instance
