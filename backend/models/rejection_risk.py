"""
Rule-based rejection risk model for application validation
Validates: Requirements 6.1, 6.2, 6.3
"""
from typing import Dict, List, Any, Tuple
from datetime import date, datetime
from .validation import ValidationIssue, CorrectionGuidance, ApplicationValidation


class RejectionRiskModel:
    """
    Rule-based model for predicting application rejection risk.
    
    This model validates applications against common rejection criteria
    and generates corrective guidance in Hindi and English.
    """
    
    # Severity weights for risk calculation
    SEVERITY_WEIGHTS = {
        'critical': 0.40,
        'high': 0.25,
        'medium': 0.15,
        'low': 0.05
    }
    
    # Scheme-specific validation rules
    SCHEME_RULES = {
        'widow_pension': {
            'required_fields': ['applicant_name', 'date_of_birth', 'spouse_death_certificate', 
                              'address', 'bank_account', 'aadhaar_number'],
            'min_age': 18,
            'max_income': 100000,  # Annual income in INR
        },
        'disability_pension': {
            'required_fields': ['applicant_name', 'date_of_birth', 'disability_certificate',
                              'address', 'bank_account', 'aadhaar_number'],
            'min_age': 18,
            'min_disability_percentage': 40,
            'max_income': 120000,
        },
        'old_age_pension': {
            'required_fields': ['applicant_name', 'date_of_birth', 'age_proof',
                              'address', 'bank_account', 'aadhaar_number'],
            'min_age': 60,
            'max_income': 80000,
        },
        'ration_card': {
            'required_fields': ['applicant_name', 'date_of_birth', 'address',
                              'family_members', 'income_certificate', 'aadhaar_number'],
            'min_age': 18,
            'max_income': 150000,
        },
        'bpl_card': {
            'required_fields': ['applicant_name', 'date_of_birth', 'address',
                              'family_members', 'income_certificate', 'aadhaar_number'],
            'min_age': 18,
            'max_income': 50000,
        }
    }
    
    def __init__(self):
        """Initialize the rejection risk model."""
        pass
    
    def validate_application(
        self,
        application_id: str,
        scheme_type: str,
        operator_id: str,
        application_data: Dict[str, Any]
    ) -> ApplicationValidation:
        """
        Validate an application and calculate rejection risk.
        
        Args:
            application_id: Unique application identifier
            scheme_type: Type of scheme being applied for
            operator_id: ID of the CSC operator
            application_data: Application form data to validate
            
        Returns:
            ApplicationValidation with risk score, issues, and guidance
        """
        validation_issues = []
        
        # Get scheme-specific rules
        scheme_rules = self.SCHEME_RULES.get(scheme_type, {})
        if not scheme_rules:
            # Unknown scheme type - treat as high risk
            validation_issues.append(ValidationIssue(
                field_name='scheme_type',
                issue_type='invalid_format',
                severity='high',
                impact_on_risk=0.25,
                description=f'Unknown scheme type: {scheme_type}'
            ))
        else:
            # Run validation rules
            validation_issues.extend(self._check_required_fields(application_data, scheme_rules))
            validation_issues.extend(self._check_age_requirements(application_data, scheme_rules))
            validation_issues.extend(self._check_income_requirements(application_data, scheme_rules))
            validation_issues.extend(self._check_document_validity(application_data, scheme_rules))
        
        # Calculate rejection risk score
        rejection_risk_score = self._calculate_risk_score(validation_issues)
        
        # Generate corrective guidance
        corrective_guidance = self._generate_guidance(validation_issues)
        
        return ApplicationValidation(
            application_id=application_id,
            scheme_type=scheme_type,
            rejection_risk_score=rejection_risk_score,
            validation_issues=validation_issues,
            corrective_guidance=corrective_guidance,
            validated_at=datetime.utcnow(),
            operator_id=operator_id
        )
    
    def _check_required_fields(
        self,
        application_data: Dict[str, Any],
        scheme_rules: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Check for missing required fields (high risk)."""
        issues = []
        required_fields = scheme_rules.get('required_fields', [])
        
        # Get documents object if it exists
        documents = application_data.get('documents', {})
        
        for field in required_fields:
            # Check if field exists in application_data
            field_value = application_data.get(field)
            
            # Special handling for document fields - check both the field and the documents checkbox
            if field in ['spouse_death_certificate', 'disability_certificate', 'age_proof', 'income_certificate']:
                # Map field names to document checkbox names
                doc_mapping = {
                    'spouse_death_certificate': 'death_certificate',
                    'disability_certificate': 'disability_certificate',
                    'age_proof': 'age_proof',
                    'income_certificate': 'income_certificate'
                }
                doc_checkbox = doc_mapping.get(field, field)
                
                # Check if document checkbox is checked
                if documents.get(doc_checkbox):
                    continue  # Document is marked as submitted
            
            # Special handling for aadhaar_number - check both field and checkbox
            if field == 'aadhaar_number':
                if documents.get('aadhaar') or field_value:
                    continue  # Aadhaar is marked as submitted or number is provided
            
            # Special handling for family_members - this is optional if not provided
            if field == 'family_members':
                # For now, skip this validation if not provided
                # In a real system, this would be a required list of family members
                continue
            
            # Check if field has a value
            if not field_value:
                issues.append(ValidationIssue(
                    field_name=field,
                    issue_type='missing',
                    severity='high',
                    impact_on_risk=0.25,
                    description=f'Required field {field} is missing'
                ))
        
        return issues
    
    def _check_age_requirements(
        self,
        application_data: Dict[str, Any],
        scheme_rules: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Check age requirements (critical risk if below minimum)."""
        issues = []
        
        if 'date_of_birth' not in application_data or not application_data['date_of_birth']:
            return issues  # Already caught by required fields check
        
        try:
            # Parse date of birth
            dob = application_data['date_of_birth']
            if isinstance(dob, str):
                dob = datetime.strptime(dob, '%Y-%m-%d').date()
            elif isinstance(dob, datetime):
                dob = dob.date()
            
            # Calculate age
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            # Check minimum age
            min_age = scheme_rules.get('min_age')
            if min_age and age < min_age:
                issues.append(ValidationIssue(
                    field_name='date_of_birth',
                    issue_type='invalid_format',
                    severity='critical',
                    impact_on_risk=0.40,
                    description=f'Age {age} is below minimum requirement of {min_age} years'
                ))
        except (ValueError, TypeError) as e:
            issues.append(ValidationIssue(
                field_name='date_of_birth',
                issue_type='invalid_format',
                severity='high',
                impact_on_risk=0.25,
                description=f'Invalid date of birth format: {str(e)}'
            ))
        
        return issues
    
    def _check_income_requirements(
        self,
        application_data: Dict[str, Any],
        scheme_rules: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Check income requirements (high risk if above threshold)."""
        issues = []
        
        max_income = scheme_rules.get('max_income')
        if not max_income:
            return issues
        
        # Check for income in multiple possible field names
        income = application_data.get('annual_income') or application_data.get('income')
        if income is None:
            return issues  # Income not provided or not required
        
        try:
            income = float(income)
            if income > max_income:
                issues.append(ValidationIssue(
                    field_name='annual_income',
                    issue_type='exceeds_threshold',
                    severity='high',
                    impact_on_risk=0.25,
                    description=f'Income {income} exceeds maximum threshold of {max_income}'
                ))
        except (ValueError, TypeError):
            issues.append(ValidationIssue(
                field_name='annual_income',
                issue_type='invalid_format',
                severity='medium',
                impact_on_risk=0.15,
                description='Invalid income format'
            ))
        
        return issues
    
    def _check_document_validity(
        self,
        application_data: Dict[str, Any],
        scheme_rules: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Check for document mismatches (medium risk)."""
        issues = []
        
        # Check Aadhaar number format (12 digits)
        aadhaar = application_data.get('aadhaar_number')
        if aadhaar:
            aadhaar_str = str(aadhaar).replace(' ', '').replace('-', '')
            if not aadhaar_str.isdigit() or len(aadhaar_str) != 12:
                issues.append(ValidationIssue(
                    field_name='aadhaar_number',
                    issue_type='invalid_format',
                    severity='medium',
                    impact_on_risk=0.15,
                    description='Invalid Aadhaar number format (must be 12 digits)'
                ))
        
        # Check bank account number format
        bank_account = application_data.get('bank_account')
        if bank_account:
            bank_account_str = str(bank_account).replace(' ', '')
            if not bank_account_str.isdigit() or len(bank_account_str) < 9 or len(bank_account_str) > 18:
                issues.append(ValidationIssue(
                    field_name='bank_account',
                    issue_type='invalid_format',
                    severity='medium',
                    impact_on_risk=0.15,
                    description='Invalid bank account number format'
                ))
        
        # Check disability percentage for disability pension
        if scheme_rules.get('min_disability_percentage'):
            disability_pct = application_data.get('disability_percentage')
            if disability_pct is not None:
                try:
                    disability_pct = float(disability_pct)
                    min_pct = scheme_rules['min_disability_percentage']
                    if disability_pct < min_pct:
                        issues.append(ValidationIssue(
                            field_name='disability_percentage',
                            issue_type='invalid_format',
                            severity='high',
                            impact_on_risk=0.25,
                            description=f'Disability percentage {disability_pct}% is below minimum of {min_pct}%'
                        ))
                except (ValueError, TypeError):
                    issues.append(ValidationIssue(
                        field_name='disability_percentage',
                        issue_type='invalid_format',
                        severity='medium',
                        impact_on_risk=0.15,
                        description='Invalid disability percentage format'
                    ))
        
        return issues
    
    def _calculate_risk_score(self, validation_issues: List[ValidationIssue]) -> float:
        """
        Calculate rejection risk score based on validation issues.
        
        Risk score is the sum of impact_on_risk values, capped at 1.0.
        """
        if not validation_issues:
            return 0.0
        
        total_risk = sum(issue.impact_on_risk for issue in validation_issues)
        return min(total_risk, 1.0)
    
    def _generate_guidance(
        self,
        validation_issues: List[ValidationIssue]
    ) -> List[CorrectionGuidance]:
        """
        Generate corrective guidance for validation issues.
        
        Provides guidance in both Hindi and English, prioritized by severity.
        """
        guidance_list = []
        
        # Guidance templates for common issues
        guidance_templates = {
            'applicant_name': {
                'hindi': 'कृपया आवेदक का पूरा नाम दर्ज करें',
                'english': 'Please enter the applicant\'s full name',
                'action': 'Enter complete name as per Aadhaar card'
            },
            'date_of_birth': {
                'hindi': 'कृपया जन्म तिथि सही प्रारूप में दर्ज करें (YYYY-MM-DD)',
                'english': 'Please enter date of birth in correct format (YYYY-MM-DD)',
                'action': 'Verify date of birth from Aadhaar or birth certificate'
            },
            'spouse_death_certificate': {
                'hindi': 'कृपया पति/पत्नी का मृत्यु प्रमाण पत्र अपलोड करें',
                'english': 'Please upload spouse\'s death certificate',
                'action': 'Upload death certificate from civil records'
            },
            'disability_certificate': {
                'hindi': 'कृपया विकलांगता प्रमाण पत्र अपलोड करें',
                'english': 'Please upload disability certificate',
                'action': 'Upload valid disability certificate from medical authority'
            },
            'age_proof': {
                'hindi': 'कृपया आयु प्रमाण दस्तावेज अपलोड करें',
                'english': 'Please upload age proof document',
                'action': 'Upload Aadhaar card or birth certificate'
            },
            'address': {
                'hindi': 'कृपया पूरा पता दर्ज करें',
                'english': 'Please enter complete address',
                'action': 'Enter address with village, block, district, and pincode'
            },
            'bank_account': {
                'hindi': 'कृपया बैंक खाता संख्या सही प्रारूप में दर्ज करें',
                'english': 'Please enter bank account number in correct format',
                'action': 'Verify bank account number from passbook'
            },
            'aadhaar_number': {
                'hindi': 'कृपया 12 अंकों का आधार नंबर दर्ज करें',
                'english': 'Please enter 12-digit Aadhaar number',
                'action': 'Enter Aadhaar number without spaces or dashes'
            },
            'family_members': {
                'hindi': 'कृपया परिवार के सदस्यों की जानकारी दर्ज करें',
                'english': 'Please enter family members information',
                'action': 'List all family members with their details'
            },
            'income_certificate': {
                'hindi': 'कृपया आय प्रमाण पत्र अपलोड करें',
                'english': 'Please upload income certificate',
                'action': 'Upload income certificate from revenue department'
            },
            'annual_income': {
                'hindi': 'कृपया वार्षिक आय सही प्रारूप में दर्ज करें',
                'english': 'Please enter annual income in correct format',
                'action': 'Enter annual income as per income certificate'
            },
            'disability_percentage': {
                'hindi': 'कृपया विकलांगता प्रतिशत सही प्रारूप में दर्ज करें',
                'english': 'Please enter disability percentage in correct format',
                'action': 'Enter disability percentage as per medical certificate'
            }
        }
        
        # Priority mapping (lower number = higher priority)
        severity_priority = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4
        }
        
        for idx, issue in enumerate(validation_issues):
            field_name = issue.field_name
            template = guidance_templates.get(field_name, {
                'hindi': f'कृपया {field_name} को ठीक करें',
                'english': f'Please correct {field_name}',
                'action': f'Review and correct {field_name}'
            })
            
            # Add specific guidance for age and income issues
            if 'age' in issue.description.lower() or 'below minimum' in issue.description:
                template = {
                    'hindi': f'आवेदक की आयु न्यूनतम आवश्यकता से कम है। कृपया जन्म तिथि की जांच करें।',
                    'english': f'Applicant age is below minimum requirement. Please verify date of birth.',
                    'action': 'Verify date of birth and ensure applicant meets age criteria'
                }
            elif 'income' in issue.description.lower() and 'exceeds' in issue.description:
                template = {
                    'hindi': f'वार्षिक आय अधिकतम सीमा से अधिक है। यह योजना के लिए पात्र नहीं हो सकता।',
                    'english': f'Annual income exceeds maximum threshold. May not be eligible for this scheme.',
                    'action': 'Verify income certificate and check eligibility criteria'
                }
            
            guidance_list.append(CorrectionGuidance(
                issue_id=f'ISS{idx+1:03d}',
                guidance_text_hindi=template['hindi'],
                guidance_text_english=template['english'],
                suggested_action=template['action'],
                priority=severity_priority.get(issue.severity, 4)
            ))
        
        # Sort by priority (ascending)
        guidance_list.sort(key=lambda g: g.priority)
        
        return guidance_list
