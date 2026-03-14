"""
Unit tests for rejection risk model
"""
import pytest
from datetime import date, datetime
from models.rejection_risk import RejectionRiskModel
from models.validation import ValidationIssue, CorrectionGuidance


class TestRejectionRiskModel:
    """Test suite for RejectionRiskModel"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.model = RejectionRiskModel()
    
    def test_valid_widow_pension_application(self):
        """Test validation of a complete widow pension application"""
        application_data = {
            'applicant_name': 'Sita Devi',
            'date_of_birth': '1975-03-15',
            'spouse_death_certificate': 'DEATH_CERT_123',
            'address': 'Village Raipur, Block Raipur, District Raipur',
            'bank_account': '1234567890123',
            'aadhaar_number': '123456789012',
            'annual_income': 50000
        }
        
        result = self.model.validate_application(
            application_id='APP001',
            scheme_type='widow_pension',
            operator_id='OP001',
            application_data=application_data
        )
        
        assert result.application_id == 'APP001'
        assert result.scheme_type == 'widow_pension'
        assert result.rejection_risk_score == 0.0
        assert len(result.validation_issues) == 0
        assert len(result.corrective_guidance) == 0
    
    def test_missing_required_fields(self):
        """Test detection of missing required fields (high risk)"""
        application_data = {
            'applicant_name': 'Sita Devi',
            'date_of_birth': '1975-03-15',
            # Missing spouse_death_certificate, address, bank_account, aadhaar_number
        }
        
        result = self.model.validate_application(
            application_id='APP002',
            scheme_type='widow_pension',
            operator_id='OP001',
            application_data=application_data
        )
        
        assert result.rejection_risk_score > 0.0
        assert len(result.validation_issues) == 4  # 4 missing fields
        
        # Check that all missing fields are detected
        missing_fields = [issue.field_name for issue in result.validation_issues]
        assert 'spouse_death_certificate' in missing_fields
        assert 'address' in missing_fields
        assert 'bank_account' in missing_fields
        assert 'aadhaar_number' in missing_fields
        
        # Check severity
        for issue in result.validation_issues:
            assert issue.severity == 'high'
            assert issue.issue_type == 'missing'
            assert issue.impact_on_risk == 0.25
    
    def test_age_below_minimum_critical_risk(self):
        """Test detection of age below minimum (critical risk)"""
        application_data = {
            'applicant_name': 'Minor Applicant',
            'date_of_birth': '2010-01-01',  # Age ~14, below minimum 18
            'spouse_death_certificate': 'DEATH_CERT_123',
            'address': 'Village Raipur',
            'bank_account': '1234567890123',
            'aadhaar_number': '123456789012'
        }
        
        result = self.model.validate_application(
            application_id='APP003',
            scheme_type='widow_pension',
            operator_id='OP001',
            application_data=application_data
        )
        
        assert result.rejection_risk_score >= 0.40  # Critical risk
        
        # Find age-related issue
        age_issues = [issue for issue in result.validation_issues 
                     if issue.field_name == 'date_of_birth']
        assert len(age_issues) == 1
        assert age_issues[0].severity == 'critical'
        assert age_issues[0].impact_on_risk == 0.40
        assert 'below minimum' in age_issues[0].description
    
    def test_income_above_threshold_high_risk(self):
        """Test detection of income above threshold (high risk)"""
        application_data = {
            'applicant_name': 'Rich Applicant',
            'date_of_birth': '1975-03-15',
            'spouse_death_certificate': 'DEATH_CERT_123',
            'address': 'Village Raipur',
            'bank_account': '1234567890123',
            'aadhaar_number': '123456789012',
            'annual_income': 150000  # Above threshold of 100000
        }
        
        result = self.model.validate_application(
            application_id='APP004',
            scheme_type='widow_pension',
            operator_id='OP001',
            application_data=application_data
        )
        
        assert result.rejection_risk_score >= 0.25  # High risk
        
        # Find income-related issue
        income_issues = [issue for issue in result.validation_issues 
                        if issue.field_name == 'annual_income']
        assert len(income_issues) == 1
        assert income_issues[0].severity == 'high'
        assert income_issues[0].impact_on_risk == 0.25
        assert 'exceeds maximum' in income_issues[0].description
    
    def test_invalid_aadhaar_format_medium_risk(self):
        """Test detection of invalid Aadhaar format (medium risk)"""
        application_data = {
            'applicant_name': 'Test Applicant',
            'date_of_birth': '1975-03-15',
            'spouse_death_certificate': 'DEATH_CERT_123',
            'address': 'Village Raipur',
            'bank_account': '1234567890123',
            'aadhaar_number': '12345'  # Invalid: not 12 digits
        }
        
        result = self.model.validate_application(
            application_id='APP005',
            scheme_type='widow_pension',
            operator_id='OP001',
            application_data=application_data
        )
        
        assert result.rejection_risk_score >= 0.15  # Medium risk
        
        # Find Aadhaar-related issue
        aadhaar_issues = [issue for issue in result.validation_issues 
                         if issue.field_name == 'aadhaar_number']
        assert len(aadhaar_issues) == 1
        assert aadhaar_issues[0].severity == 'medium'
        assert aadhaar_issues[0].impact_on_risk == 0.15
        assert 'Invalid Aadhaar' in aadhaar_issues[0].description
    
    def test_invalid_bank_account_format(self):
        """Test detection of invalid bank account format"""
        application_data = {
            'applicant_name': 'Test Applicant',
            'date_of_birth': '1975-03-15',
            'spouse_death_certificate': 'DEATH_CERT_123',
            'address': 'Village Raipur',
            'bank_account': 'ABC123',  # Invalid: not numeric
            'aadhaar_number': '123456789012'
        }
        
        result = self.model.validate_application(
            application_id='APP006',
            scheme_type='widow_pension',
            operator_id='OP001',
            application_data=application_data
        )
        
        # Find bank account issue
        bank_issues = [issue for issue in result.validation_issues 
                      if issue.field_name == 'bank_account']
        assert len(bank_issues) == 1
        assert bank_issues[0].severity == 'medium'
        assert 'Invalid bank account' in bank_issues[0].description
    
    def test_disability_pension_below_minimum_percentage(self):
        """Test disability pension with percentage below minimum"""
        application_data = {
            'applicant_name': 'Test Applicant',
            'date_of_birth': '1980-05-20',
            'disability_certificate': 'DISABILITY_CERT_123',
            'address': 'Village Raipur',
            'bank_account': '1234567890123',
            'aadhaar_number': '123456789012',
            'disability_percentage': 30  # Below minimum 40%
        }
        
        result = self.model.validate_application(
            application_id='APP007',
            scheme_type='disability_pension',
            operator_id='OP001',
            application_data=application_data
        )
        
        # Find disability percentage issue
        disability_issues = [issue for issue in result.validation_issues 
                           if issue.field_name == 'disability_percentage']
        assert len(disability_issues) == 1
        assert disability_issues[0].severity == 'high'
        assert 'below minimum' in disability_issues[0].description
    
    def test_old_age_pension_age_requirement(self):
        """Test old age pension with age below 60"""
        application_data = {
            'applicant_name': 'Test Applicant',
            'date_of_birth': '1980-01-01',  # Age ~44, below minimum 60
            'age_proof': 'AADHAAR_123',
            'address': 'Village Raipur',
            'bank_account': '1234567890123',
            'aadhaar_number': '123456789012'
        }
        
        result = self.model.validate_application(
            application_id='APP008',
            scheme_type='old_age_pension',
            operator_id='OP001',
            application_data=application_data
        )
        
        # Should have age-related issue
        age_issues = [issue for issue in result.validation_issues 
                     if issue.field_name == 'date_of_birth']
        assert len(age_issues) == 1
        assert age_issues[0].severity == 'critical'
    
    def test_corrective_guidance_generation(self):
        """Test generation of corrective guidance in Hindi and English"""
        application_data = {
            'applicant_name': 'Test Applicant',
            'date_of_birth': '1975-03-15',
            # Missing required fields
        }
        
        result = self.model.validate_application(
            application_id='APP009',
            scheme_type='widow_pension',
            operator_id='OP001',
            application_data=application_data
        )
        
        assert len(result.corrective_guidance) > 0
        
        # Check guidance structure
        for guidance in result.corrective_guidance:
            assert guidance.issue_id.startswith('ISS')
            assert len(guidance.guidance_text_hindi) > 0
            assert len(guidance.guidance_text_english) > 0
            assert len(guidance.suggested_action) > 0
            assert guidance.priority >= 1
    
    def test_guidance_prioritization(self):
        """Test that guidance is prioritized by severity"""
        application_data = {
            'applicant_name': 'Test Applicant',
            'date_of_birth': '2010-01-01',  # Critical: age below minimum
            'aadhaar_number': '12345',  # Medium: invalid format
            'spouse_death_certificate': '',  # High: missing field
            'address': 'Village Raipur',
            'bank_account': '1234567890123'
        }
        
        result = self.model.validate_application(
            application_id='APP010',
            scheme_type='widow_pension',
            operator_id='OP001',
            application_data=application_data
        )
        
        # Guidance should be sorted by priority (1 = highest)
        priorities = [g.priority for g in result.corrective_guidance]
        assert priorities == sorted(priorities)
        
        # Critical issues should have priority 1
        critical_guidance = [g for g in result.corrective_guidance if g.priority == 1]
        assert len(critical_guidance) > 0
    
    def test_risk_score_calculation(self):
        """Test risk score calculation based on issue weights"""
        application_data = {
            'applicant_name': 'Test Applicant',
            'date_of_birth': '2010-01-01',  # Critical: 0.40
            'annual_income': 150000,  # High: 0.25
            'aadhaar_number': '12345',  # Medium: 0.15
            'spouse_death_certificate': 'CERT_123',
            'address': 'Village Raipur',
            'bank_account': '1234567890123'
        }
        
        result = self.model.validate_application(
            application_id='APP011',
            scheme_type='widow_pension',
            operator_id='OP001',
            application_data=application_data
        )
        
        # Risk score should be sum of impacts (capped at 1.0)
        expected_risk = 0.40 + 0.25 + 0.15  # 0.80
        assert result.rejection_risk_score == pytest.approx(expected_risk, abs=0.01)
    
    def test_risk_score_capped_at_one(self):
        """Test that risk score is capped at 1.0"""
        application_data = {
            'applicant_name': '',  # Missing
            'date_of_birth': '2010-01-01',  # Critical
            'annual_income': 150000,  # High
            # Many missing fields to exceed 1.0
        }
        
        result = self.model.validate_application(
            application_id='APP012',
            scheme_type='widow_pension',
            operator_id='OP001',
            application_data=application_data
        )
        
        # Risk score should be capped at 1.0
        assert result.rejection_risk_score <= 1.0
    
    def test_unknown_scheme_type(self):
        """Test handling of unknown scheme type"""
        application_data = {
            'applicant_name': 'Test Applicant',
            'date_of_birth': '1975-03-15'
        }
        
        result = self.model.validate_application(
            application_id='APP013',
            scheme_type='unknown_scheme',
            operator_id='OP001',
            application_data=application_data
        )
        
        # Should have an issue for unknown scheme type
        scheme_issues = [issue for issue in result.validation_issues 
                        if issue.field_name == 'scheme_type']
        assert len(scheme_issues) == 1
        assert scheme_issues[0].severity == 'high'
    
    def test_date_of_birth_formats(self):
        """Test handling of different date of birth formats"""
        # Test with string format
        application_data = {
            'applicant_name': 'Test Applicant',
            'date_of_birth': '1975-03-15',
            'spouse_death_certificate': 'CERT_123',
            'address': 'Village Raipur',
            'bank_account': '1234567890123',
            'aadhaar_number': '123456789012'
        }
        
        result = self.model.validate_application(
            application_id='APP014',
            scheme_type='widow_pension',
            operator_id='OP001',
            application_data=application_data
        )
        
        # Should not have date format issues
        date_issues = [issue for issue in result.validation_issues 
                      if issue.field_name == 'date_of_birth']
        assert len(date_issues) == 0
    
    def test_aadhaar_with_spaces_and_dashes(self):
        """Test Aadhaar number with spaces and dashes"""
        application_data = {
            'applicant_name': 'Test Applicant',
            'date_of_birth': '1975-03-15',
            'spouse_death_certificate': 'CERT_123',
            'address': 'Village Raipur',
            'bank_account': '1234567890123',
            'aadhaar_number': '1234-5678-9012'  # Valid with dashes
        }
        
        result = self.model.validate_application(
            application_id='APP015',
            scheme_type='widow_pension',
            operator_id='OP001',
            application_data=application_data
        )
        
        # Should not have Aadhaar format issues
        aadhaar_issues = [issue for issue in result.validation_issues 
                         if issue.field_name == 'aadhaar_number']
        assert len(aadhaar_issues) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
