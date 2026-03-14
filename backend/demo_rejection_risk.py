"""
Demo script for rejection risk model
Demonstrates validation of various application scenarios
"""
from models.rejection_risk import RejectionRiskModel
import json


def print_validation_result(title: str, result):
    """Pretty print validation result"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")
    print(f"\nApplication ID: {result.application_id}")
    print(f"Scheme Type: {result.scheme_type}")
    print(f"Rejection Risk Score: {result.rejection_risk_score:.2f} ({get_risk_level(result.rejection_risk_score)})")
    
    if result.validation_issues:
        print(f"\n📋 Validation Issues ({len(result.validation_issues)}):")
        for issue in result.validation_issues:
            severity_emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }
            print(f"  {severity_emoji.get(issue.severity, '⚪')} [{issue.severity.upper()}] {issue.field_name}")
            print(f"     Issue: {issue.issue_type}")
            print(f"     Impact: {issue.impact_on_risk:.2f}")
            print(f"     Description: {issue.description}")
    else:
        print("\n✅ No validation issues found!")
    
    if result.corrective_guidance:
        print(f"\n💡 Corrective Guidance ({len(result.corrective_guidance)}):")
        for guidance in result.corrective_guidance:
            print(f"\n  Priority {guidance.priority}: {guidance.issue_id}")
            print(f"     English: {guidance.guidance_text_english}")
            print(f"     Hindi: {guidance.guidance_text_hindi}")
            print(f"     Action: {guidance.suggested_action}")
    
    print(f"\n{'='*80}\n")


def get_risk_level(score: float) -> str:
    """Get risk level description"""
    if score >= 0.75:
        return "VERY HIGH RISK"
    elif score >= 0.50:
        return "HIGH RISK"
    elif score >= 0.25:
        return "MEDIUM RISK"
    elif score > 0:
        return "LOW RISK"
    else:
        return "NO RISK"


def main():
    """Run demo scenarios"""
    model = RejectionRiskModel()
    
    print("\n" + "="*80)
    print("  REJECTION RISK MODEL DEMO")
    print("  NagarikAI Platform - CSC Operator Assistant")
    print("="*80)
    
    # Scenario 1: Valid application with no issues
    print("\n\n🎯 SCENARIO 1: Valid Widow Pension Application")
    result1 = model.validate_application(
        application_id='APP001',
        scheme_type='widow_pension',
        operator_id='OP001',
        application_data={
            'applicant_name': 'Sita Devi',
            'date_of_birth': '1975-03-15',
            'spouse_death_certificate': 'DEATH_CERT_123',
            'address': 'Village Raipur, Block Raipur, District Raipur, Chhattisgarh',
            'bank_account': '1234567890123',
            'aadhaar_number': '123456789012',
            'annual_income': 50000
        }
    )
    print_validation_result("Valid Application - No Issues", result1)
    
    # Scenario 2: Missing required fields
    print("\n\n🎯 SCENARIO 2: Application with Missing Required Fields")
    result2 = model.validate_application(
        application_id='APP002',
        scheme_type='widow_pension',
        operator_id='OP001',
        application_data={
            'applicant_name': 'Radha Devi',
            'date_of_birth': '1980-05-20',
            # Missing: spouse_death_certificate, address, bank_account, aadhaar_number
        }
    )
    print_validation_result("Missing Required Fields", result2)
    
    # Scenario 3: Age below minimum (critical)
    print("\n\n🎯 SCENARIO 3: Applicant Age Below Minimum Requirement")
    result3 = model.validate_application(
        application_id='APP003',
        scheme_type='widow_pension',
        operator_id='OP001',
        application_data={
            'applicant_name': 'Minor Applicant',
            'date_of_birth': '2010-01-01',  # Age ~14
            'spouse_death_certificate': 'DEATH_CERT_456',
            'address': 'Village Bilaspur, District Bilaspur',
            'bank_account': '9876543210123',
            'aadhaar_number': '987654321098'
        }
    )
    print_validation_result("Age Below Minimum (Critical)", result3)
    
    # Scenario 4: Income above threshold
    print("\n\n🎯 SCENARIO 4: Income Above Maximum Threshold")
    result4 = model.validate_application(
        application_id='APP004',
        scheme_type='widow_pension',
        operator_id='OP001',
        application_data={
            'applicant_name': 'Wealthy Applicant',
            'date_of_birth': '1970-08-10',
            'spouse_death_certificate': 'DEATH_CERT_789',
            'address': 'Village Durg, District Durg',
            'bank_account': '5555666677778888',
            'aadhaar_number': '555566667777',
            'annual_income': 150000  # Above threshold
        }
    )
    print_validation_result("Income Above Threshold", result4)
    
    # Scenario 5: Multiple validation issues
    print("\n\n🎯 SCENARIO 5: Multiple Validation Issues (Complex Case)")
    result5 = model.validate_application(
        application_id='APP005',
        scheme_type='widow_pension',
        operator_id='OP001',
        application_data={
            'applicant_name': 'Complex Case',
            'date_of_birth': '2012-03-15',  # Critical: age below minimum
            'spouse_death_certificate': '',  # High: missing
            'address': 'Village Raigarh',
            'bank_account': 'INVALID',  # Medium: invalid format
            'aadhaar_number': '12345',  # Medium: invalid format
            'annual_income': 120000  # High: above threshold
        }
    )
    print_validation_result("Multiple Issues - Very High Risk", result5)
    
    # Scenario 6: Disability pension with low percentage
    print("\n\n🎯 SCENARIO 6: Disability Pension - Percentage Below Minimum")
    result6 = model.validate_application(
        application_id='APP006',
        scheme_type='disability_pension',
        operator_id='OP002',
        application_data={
            'applicant_name': 'Disability Applicant',
            'date_of_birth': '1985-06-15',
            'disability_certificate': 'DISABILITY_CERT_123',
            'address': 'Village Korba, District Korba',
            'bank_account': '1111222233334444',
            'aadhaar_number': '111122223333',
            'disability_percentage': 30  # Below minimum 40%
        }
    )
    print_validation_result("Disability Percentage Below Minimum", result6)
    
    # Scenario 7: Old age pension - valid
    print("\n\n🎯 SCENARIO 7: Old Age Pension - Valid Application")
    result7 = model.validate_application(
        application_id='APP007',
        scheme_type='old_age_pension',
        operator_id='OP003',
        application_data={
            'applicant_name': 'Senior Citizen',
            'date_of_birth': '1955-01-01',  # Age ~69
            'age_proof': 'AADHAAR_CARD',
            'address': 'Village Jagdalpur, District Bastar',
            'bank_account': '9999888877776666',
            'aadhaar_number': '999988887777',
            'annual_income': 40000
        }
    )
    print_validation_result("Valid Old Age Pension Application", result7)
    
    # Scenario 8: BPL card with income above threshold
    print("\n\n🎯 SCENARIO 8: BPL Card - Income Above Threshold")
    result8 = model.validate_application(
        application_id='APP008',
        scheme_type='bpl_card',
        operator_id='OP004',
        application_data={
            'applicant_name': 'BPL Applicant',
            'date_of_birth': '1990-04-20',
            'address': 'Village Rajnandgaon',
            'family_members': '4',
            'income_certificate': 'INCOME_CERT_123',
            'aadhaar_number': '444455556666',
            'annual_income': 75000  # Above BPL threshold of 50000
        }
    )
    print_validation_result("BPL Card - Income Too High", result8)
    
    print("\n" + "="*80)
    print("  DEMO COMPLETED")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
