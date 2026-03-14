# NagarikAI Platform - Data Models

This directory contains Pydantic schemas for the NagarikAI Platform API.

## Overview

The data models are organized into the following modules:

### Common Models (`common.py`)
- **Address**: Address information for beneficiaries
- **SourceRecord**: Reference to source records from external databases

### Enrollment Models (`enrollment.py`)
- **EnrollmentCase**: Main model for beneficiary enrollment cases
- **EnrollmentCaseCreate**: Request model for creating enrollment cases
- **EnrollmentCaseResponse**: Response model for enrollment operations

**Validates**: Requirements 2.1

### Grievance Models (`grievance.py`)
- **Grievance**: Main model for citizen grievances
- **GrievanceCreate**: Request model for submitting grievances
- **GrievanceResponse**: Response model for grievance operations
- **StatusTransition**: Record of status changes in grievance lifecycle

**Validates**: Requirements 5.1

### Validation Models (`validation.py`)
- **ApplicationValidation**: Main model for application validation results
- **ApplicationValidationCreate**: Request model for validating applications
- **ApplicationValidationResponse**: Response model for validation operations
- **ValidationIssue**: Individual validation issue in an application
- **CorrectionGuidance**: Guidance for correcting validation issues

**Validates**: Requirements 6.1

## Usage

Import models from the `models` package:

```python
from models import (
    EnrollmentCase,
    Grievance,
    ApplicationValidation,
    Address,
    SourceRecord
)
```

## Design Principles

1. **Simple and Clean**: Models are kept simple without encryption or complex validation logic
2. **Type Safety**: All fields are properly typed using Python type hints
3. **Validation**: Basic validation using Pydantic's built-in validators
4. **Documentation**: Each model includes field descriptions and examples
5. **API-Ready**: Separate request/response models for API operations

## Testing

Run the model tests:

```bash
python test_models.py
```

## Notes

- All timestamps use UTC timezone
- Confidence scores are constrained to [0.0, 1.0] range
- Status fields use predefined string values (not enums for simplicity)
- Models include example data in their Config for API documentation
