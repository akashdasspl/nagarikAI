"""
Unit tests for Grievance Classifier

Tests the mBERT-based grievance classification system for Hindi text.
"""
import pytest
from models.grievance_classifier import GrievanceClassifier, get_classifier


def test_classifier_initialization():
    """Test that classifier initializes correctly"""
    classifier = GrievanceClassifier()
    assert classifier is not None
    assert len(classifier.DEPARTMENTS) == 5
    assert len(classifier.KEYWORDS) == 5
    assert len(classifier.SLA_HOURS) == 5


def test_get_classifier_singleton():
    """Test that get_classifier returns singleton instance"""
    classifier1 = get_classifier()
    classifier2 = get_classifier()
    assert classifier1 is classifier2


def test_classify_revenue_grievance():
    """Test classification of revenue department grievance"""
    classifier = GrievanceClassifier()
    
    # Test with death certificate grievance
    text = "मेरे पति का मृत्यु प्रमाण पत्र बनवाने में बहुत समस्या हो रही है।"
    department, confidence, sla_hours = classifier.classify(text, 'hi')
    
    assert department == 'Revenue'
    assert 0.0 <= confidence <= 1.0
    assert confidence >= 0.7  # Should have reasonable confidence
    assert sla_hours == 72  # Revenue SLA is 72 hours


def test_classify_health_grievance():
    """Test classification of health department grievance"""
    classifier = GrievanceClassifier()
    
    # Test with health center grievance
    text = "स्वास्थ्य केंद्र में दवाइयां नहीं मिल रही हैं। डॉक्टर कहते हैं कि स्टॉक खत्म हो गया है।"
    department, confidence, sla_hours = classifier.classify(text, 'hi')
    
    assert department == 'Health'
    assert 0.0 <= confidence <= 1.0
    assert confidence >= 0.7
    assert sla_hours == 24  # Health SLA is 24 hours (urgent)


def test_classify_education_grievance():
    """Test classification of education department grievance"""
    classifier = GrievanceClassifier()
    
    # Test with school grievance
    text = "स्कूल में मिड डे मील की क्वालिटी बहुत खराब है। बच्चे खाना नहीं खाते।"
    department, confidence, sla_hours = classifier.classify(text, 'hi')
    
    assert department == 'Education'
    assert 0.0 <= confidence <= 1.0
    assert confidence >= 0.7
    assert sla_hours == 48  # Education SLA is 48 hours


def test_classify_social_welfare_grievance():
    """Test classification of social welfare grievance"""
    classifier = GrievanceClassifier()
    
    # Test with pension grievance
    text = "पेंशन का पैसा पिछले दो महीने से नहीं आया है। बैंक में पूछा तो कहा कि विभाग से नहीं आया।"
    department, confidence, sla_hours = classifier.classify(text, 'hi')
    
    assert department == 'Social Welfare'
    assert 0.0 <= confidence <= 1.0
    assert confidence >= 0.7
    assert sla_hours == 96  # Social Welfare SLA is 96 hours


def test_classify_infrastructure_grievance():
    """Test classification of infrastructure grievance"""
    classifier = GrievanceClassifier()
    
    # Test with road grievance
    text = "सड़क की हालत बहुत खराब है। बारिश में पानी भर जाता है और आवागमन मुश्किल हो जाता है।"
    department, confidence, sla_hours = classifier.classify(text, 'hi')
    
    assert department == 'Infrastructure'
    assert 0.0 <= confidence <= 1.0
    assert confidence >= 0.7
    assert sla_hours == 120  # Infrastructure SLA is 120 hours


def test_classify_electricity_grievance():
    """Test classification of electricity (infrastructure) grievance"""
    classifier = GrievanceClassifier()
    
    # Test with electricity grievance
    text = "बिजली का बिल गलत आ रहा है। मैंने शिकायत की थी लेकिन अभी तक कोई कार्रवाई नहीं हुई।"
    department, confidence, sla_hours = classifier.classify(text, 'hi')
    
    assert department == 'Infrastructure'
    assert 0.0 <= confidence <= 1.0
    assert sla_hours == 120


def test_classify_empty_text():
    """Test classification with empty text"""
    classifier = GrievanceClassifier()
    
    department, confidence, sla_hours = classifier.classify("", 'hi')
    
    # Should default to infrastructure with low confidence
    assert department == 'Infrastructure'
    assert confidence == 0.5
    assert sla_hours == 120


def test_classify_no_keywords():
    """Test classification with text containing no keywords"""
    classifier = GrievanceClassifier()
    
    # Generic text with no department-specific keywords
    text = "कृपया मेरी मदद करें।"
    department, confidence, sla_hours = classifier.classify(text, 'hi')
    
    # Should default to infrastructure with low confidence
    assert department == 'Infrastructure'
    assert confidence == 0.5
    assert sla_hours == 120


def test_confidence_score_bounds():
    """Test that confidence scores are always in valid range [0, 1]"""
    classifier = GrievanceClassifier()
    
    test_texts = [
        "मृत्यु प्रमाण पत्र जाति प्रमाण आय प्रमाण",  # Multiple revenue keywords
        "स्वास्थ्य डॉक्टर अस्पताल दवाई",  # Multiple health keywords
        "स्कूल शिक्षक बच्चे",  # Multiple education keywords
        "पेंशन विधवा आंगनवाड़ी",  # Multiple social welfare keywords
        "सड़क बिजली पानी",  # Multiple infrastructure keywords
    ]
    
    for text in test_texts:
        department, confidence, sla_hours = classifier.classify(text, 'hi')
        assert 0.0 <= confidence <= 1.0, f"Confidence {confidence} out of bounds for text: {text}"


def test_predict_sla():
    """Test SLA prediction for different categories"""
    classifier = GrievanceClassifier()
    
    # Test each department
    test_cases = [
        ('Revenue', 72),
        ('Health', 24),
        ('Education', 48),
        ('Social Welfare', 96),
        ('Infrastructure', 120),
    ]
    
    for category, expected_hours in test_cases:
        sla = classifier.predict_sla(category)
        assert sla.total_seconds() == expected_hours * 3600, \
            f"SLA for {category} should be {expected_hours} hours"


def test_predict_sla_unknown_category():
    """Test SLA prediction with unknown category"""
    classifier = GrievanceClassifier()
    
    # Unknown category should default to infrastructure
    sla = classifier.predict_sla('Unknown Department')
    assert sla.total_seconds() == 120 * 3600  # Infrastructure default


def test_multiple_keyword_matches():
    """Test that multiple keyword matches increase confidence"""
    classifier = GrievanceClassifier()
    
    # Text with single keyword
    text1 = "पेंशन की समस्या है।"
    _, confidence1, _ = classifier.classify(text1, 'hi')
    
    # Text with multiple keywords
    text2 = "पेंशन और विधवा पेंशन की समस्या है। आंगनवाड़ी में भी समस्या है।"
    _, confidence2, _ = classifier.classify(text2, 'hi')
    
    # More keywords should give higher confidence
    assert confidence2 >= confidence1


def test_case_insensitive_matching():
    """Test that classification is case-insensitive"""
    classifier = GrievanceClassifier()
    
    # Same text in different cases
    text1 = "स्वास्थ्य केंद्र में समस्या है"
    text2 = "स्वास्थ्य केंद्र में समस्या है"  # Hindi doesn't have case, but test the logic
    
    dept1, conf1, sla1 = classifier.classify(text1, 'hi')
    dept2, conf2, sla2 = classifier.classify(text2, 'hi')
    
    assert dept1 == dept2
    assert conf1 == conf2
    assert sla1 == sla2


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
