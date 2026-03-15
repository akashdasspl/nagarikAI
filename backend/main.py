"""
NagarikAI Platform - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from models import (
    EnrollmentCase,
    EnrollmentCaseCreate,
    EnrollmentCaseResponse,
    Grievance,
    GrievanceCreate,
    GrievanceResponse,
    EscalationCheckResponse,
    ApplicationValidation,
    ApplicationValidationCreate,
    ApplicationValidationResponse,
    DeathRecordInput,
    PotentialBeneficiary,
    BeneficiaryDiscoveryResponse,
    SourceRecord,
)
from models.entity_resolver import EntityResolver
from models.grievance_classifier import get_classifier
from models.rejection_risk import RejectionRiskModel
from models.reconcile import (
    LocalAnomalyInput,
    MergedIssue,
    ReconcileAnomaliesRequest,
    ReconcileAnomaliesResponse,
    SEVERITY_WEIGHTS as _SEVERITY_WEIGHTS,
    reconcile as _reconcile_logic,
)
from models.rejection_pattern_analyzer import RejectionPatternAnalyzer
from models.eligibility_inference_engine import (
    EligibilityInferenceEngine,
    EligibilitySignal,
    DocumentMetadata,
)
from models.guidance_interface import (
    GuidanceInterface,
    GuidanceQuery,
    GuidanceResponse,
    TranscriptionResult,
)
from models.stall_risk_predictor import StallRiskPredictor
from models.offline_cache_manager import OfflineCacheManager
from datetime import datetime, timedelta
from dataclasses import asdict
import uuid


# Initialize FastAPI app
app = FastAPI(
    title="NagarikAI Platform",
    description="AI-Powered Citizen Service Intelligence Platform for Chhattisgarh e-District",
    version="0.1.0"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory data stores for demo
mock_data = {
    "civil_death_records": [],
    "ration_card_records": [],
    "aadhaar_records": [],
    "grievances": [],
    "applications": [],
    "enrollments": []
}

# Initialize Entity Resolver with correct data directory
import os
data_dir = "data" if os.path.exists("data") else "backend/data"
entity_resolver = EntityResolver(data_dir=data_dir)

# Initialize Grievance Classifier
grievance_classifier = get_classifier()

# Initialize Rejection Risk Model
rejection_risk_model = RejectionRiskModel()

# Initialize Rejection Pattern Analyzer
rejection_pattern_analyzer = RejectionPatternAnalyzer()

# Initialize Eligibility Inference Engine
eligibility_engine = EligibilityInferenceEngine()

# Initialize Guidance Interface
guidance_interface = GuidanceInterface()

# Initialize Stall Risk Predictor
stall_risk_predictor = StallRiskPredictor()

# Initialize Offline Cache Manager
cache_manager = OfflineCacheManager()

# ---------------------------------------------------------------------------
# Seed demo data for Triage Queue (so it shows entries on first load)
# ---------------------------------------------------------------------------
_demo_submitted_at = datetime.utcnow() - timedelta(hours=80)
stall_risk_predictor.add_application(
    application_id="APP-DEMO-001",
    application_data={"applicant_name": "रामलाल यादव", "scheme_type": "widow_pension"},
    validation_issues=[{"severity": "critical"}, {"severity": "high"}],
    scheme_type="widow_pension",
    submitted_at=_demo_submitted_at,
    operator_id="OP004",
)
stall_risk_predictor.add_application(
    application_id="APP-DEMO-002",
    application_data={"applicant_name": "सुनीता देवी", "scheme_type": "old_age_pension"},
    validation_issues=[{"severity": "high"}],
    scheme_type="old_age",
    submitted_at=datetime.utcnow() - timedelta(hours=100),
    operator_id="OP002",
)
stall_risk_predictor.add_application(
    application_id="APP-DEMO-003",
    application_data={"applicant_name": "अशोक कुमार", "scheme_type": "disability_pension"},
    validation_issues=[{"severity": "critical"}],
    scheme_type="disability_pension",
    submitted_at=datetime.utcnow() - timedelta(hours=110),
    operator_id="OP004",
)


# ---------------------------------------------------------------------------
# Pydantic models for Rejection Pattern Dashboard
# ---------------------------------------------------------------------------

class RejectionPatternItem(BaseModel):
    field_name: str
    scheme_type: str
    rejected_count: int
    total_applications: int
    rejection_frequency_score: float
    last_refreshed: datetime


class RejectionPatternListResponse(BaseModel):
    scheme_type: str
    patterns: List[RejectionPatternItem]


class EligibilitySignalResponse(BaseModel):
    session_id: str
    scheme_type: str
    eligibility_status: str
    ineligibility_reason_hindi: str
    ineligibility_reason_english: str
    confidence: float
    document_type: str
    issuing_authority: str
    validity_status: str


# ---------------------------------------------------------------------------
# Pydantic models for Guidance Interface
# ---------------------------------------------------------------------------

class GuidanceQueryRequest(BaseModel):
    intent: str
    scheme_type: str
    active_field: str
    language: str
    question_text: str = ""


class GuidanceResponseModel(BaseModel):
    intent: str
    scheme_type: str
    referenced_field: str
    referenced_scheme: str
    response_text: str
    language: str


class TranscriptionResponse(BaseModel):
    transcription: str
    language: str
    confidence: float


# ---------------------------------------------------------------------------
# Pydantic models for Stall Risk Predictor
# ---------------------------------------------------------------------------

class StallRiskRequest(BaseModel):
    application_data: Dict[str, Any]
    validation_issues: List[Dict[str, Any]]
    scheme_type: str
    submitted_at: str  # ISO datetime string
    operator_id: str


# ---------------------------------------------------------------------------
# Pydantic models for Offline Cache Manager
# ---------------------------------------------------------------------------

class OfflineCacheManifestResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    model_version: str
    checksum: str
    last_sync_timestamp: str  # ISO string
    is_stale: bool
    connectivity_mode: str


class SyncResultResponse(BaseModel):
    success: bool
    synced_at: str  # ISO string
    deferred_calls_uploaded: int
    models_updated: bool
    error_message: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "NagarikAI Platform API",
        "version": "0.1.0"
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "data_stores": {
            "civil_death_records": len(mock_data["civil_death_records"]),
            "ration_card_records": len(mock_data["ration_card_records"]),
            "aadhaar_records": len(mock_data["aadhaar_records"]),
            "grievances": len(mock_data["grievances"]),
            "applications": len(mock_data["applications"]),
            "enrollments": len(mock_data["enrollments"])
        }
    }


@app.post("/api/beneficiary/discover", response_model=BeneficiaryDiscoveryResponse)
async def discover_beneficiaries(death_record: DeathRecordInput):
    """
    Discover potential beneficiaries from a death record
    
    Uses Entity Resolver to match across ration card and Aadhaar databases
    to identify potential widow pension or dependent beneficiaries.
    
    Validates: Requirements 1.1, 1.3, 1.4
    """
    try:
        # Convert death record to dict for entity resolver
        death_record_dict = {
            'record_id': death_record.record_id,
            'name': death_record.name,
            'father_name': death_record.father_name,
            'date_of_death': str(death_record.date_of_death),
            'age': death_record.age,
            'gender': death_record.gender,
            'district': death_record.district,
            'village': death_record.village
        }
        
        # Use Entity Resolver to find matches across databases
        target_databases = ['ration_card', 'aadhaar']
        matches = entity_resolver.resolve_entity(death_record_dict, target_databases)
        
        # Convert matches to potential beneficiaries
        beneficiaries = []
        
        for match in matches:
            # Determine relationship and scheme based on deceased gender and match
            if death_record.gender == 'M':
                # Male deceased - look for spouse (widow pension)
                relationship = "spouse"
                scheme_type = "widow_pension"
                reasoning = f"Matched deceased spouse '{death_record.name}' in {match.target_database} records with {match.confidence_score:.0%} confidence. Eligible for widow pension scheme."
                
                # Extract beneficiary name from matched fields
                if match.target_database == 'ration_card':
                    # For ration card, we need to infer spouse name
                    # In a real system, we'd have family member data
                    beneficiary_name = f"Spouse of {death_record.name}"
                else:
                    # For Aadhaar, use the matched name
                    beneficiary_name = match.matched_fields.get('name', ('', ''))[1]
                    
            elif death_record.gender == 'F':
                # Female deceased - look for dependents (orphan support, elderly care)
                relationship = "dependent"
                scheme_type = "dependent_support"
                reasoning = f"Matched deceased family member '{death_record.name}' in {match.target_database} records with {match.confidence_score:.0%} confidence. Potential dependents may be eligible for support schemes."
                beneficiary_name = f"Dependents of {death_record.name}"
            else:
                relationship = "family_member"
                scheme_type = "family_support"
                reasoning = f"Matched deceased person '{death_record.name}' in {match.target_database} records with {match.confidence_score:.0%} confidence."
                beneficiary_name = f"Family of {death_record.name}"
            
            # Create source record
            source_record = SourceRecord(
                record_id=match.target_record_id,
                database=match.target_database,
                matched_fields={
                    k: {'source': v[0], 'target': v[1]} 
                    for k, v in match.matched_fields.items()
                },
                confidence_score=match.confidence_score
            )
            
            # Create potential beneficiary
            beneficiary = PotentialBeneficiary(
                beneficiary_name=beneficiary_name,
                relationship=relationship,
                scheme_type=scheme_type,
                confidence_score=match.confidence_score,
                eligibility_reasoning=reasoning,
                source_records=[source_record]
            )
            
            beneficiaries.append(beneficiary)
        
        # Sort beneficiaries by confidence score (descending) - Validates Requirement 1.4
        beneficiaries.sort(key=lambda b: b.confidence_score, reverse=True)
        
        # Prepare response
        response = BeneficiaryDiscoveryResponse(
            success=True,
            message=f"Found {len(beneficiaries)} potential beneficiaries" if beneficiaries else "No potential beneficiaries found",
            death_record_id=death_record.record_id,
            deceased_name=death_record.name,
            beneficiaries=beneficiaries,
            total_found=len(beneficiaries)
        )
        
        return response
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Data file not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error discovering beneficiaries: {str(e)}"
        )


@app.post("/api/beneficiary/search-by-aadhaar", response_model=BeneficiaryDiscoveryResponse)
async def search_by_aadhaar(aadhaar_request: Dict[str, str]):
    """
    Search for a person by Aadhaar number and find their family members
    
    Uses Entity Resolver to find the person in Aadhaar database, then searches
    for family members in Ration Card database to identify potential beneficiaries
    for various welfare schemes.
    """
    try:
        aadhaar_number = aadhaar_request.get('aadhaar_number')
        
        if not aadhaar_number or len(aadhaar_number) != 12:
            raise HTTPException(
                status_code=400,
                detail="Valid 12-digit Aadhaar number is required"
            )
        
        # Load Aadhaar records to find the person
        aadhaar_records = entity_resolver.load_csv_data("aadhaar_records.csv")
        
        # Find the person by Aadhaar number
        person_record = None
        for record in aadhaar_records:
            if record.get('aadhaar_number') == aadhaar_number:
                person_record = record
                break
        
        if not person_record:
            return BeneficiaryDiscoveryResponse(
                success=True,
                message="No record found for this Aadhaar number",
                death_record_id=aadhaar_number,
                deceased_name="",
                beneficiaries=[],
                total_found=0
            )
        
        # Search for family members in Ration Card database
        ration_records = entity_resolver.load_csv_data("ration_card_records.csv")
        
        # Calculate age once (outside the loop)
        dob_str = person_record.get('date_of_birth', '')
        age = 0
        if dob_str:
            try:
                from datetime import datetime
                dob = datetime.strptime(dob_str, '%Y-%m-%d')
                today = datetime.now()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            except:
                age = int(person_record.get('age', 0))
        else:
            age = int(person_record.get('age', 0))
        
        gender = person_record.get('gender', '')
        
        # Determine eligible schemes once (not per ration card)
        eligible_schemes = []
        
        if age >= 60:
            eligible_schemes.append({
                'scheme': 'old_age_pension',
                'reason': f"Person is {age} years old, eligible for Old Age Pension (60+ years)"
            })
        
        if gender == 'F' and age >= 18:
            eligible_schemes.append({
                'scheme': 'widow_pension',
                'reason': f"Female family member, may be eligible for Widow Pension if spouse is deceased"
            })
        
        # Find the best matching ration card for each scheme
        scheme_best_matches = {}  # scheme_type -> (confidence, ration_record)
        
        # Find ration cards where this person might be listed
        for ration_record in ration_records:
            # Calculate name similarity
            name_similarity = entity_resolver.calculate_name_similarity(
                person_record.get('name', ''),
                ration_record.get('head_of_family', '')
            )
            
            # Calculate location similarity
            person_location = f"{person_record.get('village', '')} {person_record.get('district', '')}"
            ration_location = f"{ration_record.get('village', '')} {ration_record.get('district', '')}"
            location_similarity = entity_resolver.calculate_location_similarity(
                person_location,
                ration_location
            )
            
            # If there's a match (name + location), this is likely their family
            if name_similarity >= 0.7 and location_similarity >= 0.7:
                confidence = (name_similarity + location_similarity) / 2
                
                # Check for age-based schemes
                for scheme_info in eligible_schemes:
                    scheme_type = scheme_info['scheme']
                    if scheme_type not in scheme_best_matches or confidence > scheme_best_matches[scheme_type][0]:
                        scheme_best_matches[scheme_type] = (confidence, ration_record, scheme_info)
                
                # Check BPL eligibility from ration card type
                if ration_record.get('card_type') == 'BPL':
                    scheme_type = 'bpl_card'
                    scheme_info = {
                        'scheme': scheme_type,
                        'reason': "Family has BPL ration card, eligible for BPL benefits"
                    }
                    if scheme_type not in scheme_best_matches or confidence > scheme_best_matches[scheme_type][0]:
                        scheme_best_matches[scheme_type] = (confidence, ration_record, scheme_info)
        
        # Create beneficiary entries from best matches
        beneficiaries = []
        for scheme_type, (confidence, ration_record, scheme_info) in scheme_best_matches.items():
            source_record = SourceRecord(
                record_id=ration_record.get('card_number', ''),
                database='ration_card',
                matched_fields={
                    'name': {'source': person_record.get('name', ''), 'target': ration_record.get('head_of_family', '')},
                    'village': {'source': person_record.get('village', ''), 'target': ration_record.get('village', '')},
                    'district': {'source': person_record.get('district', ''), 'target': ration_record.get('district', '')}
                },
                confidence_score=confidence
            )
            
            beneficiary = PotentialBeneficiary(
                beneficiary_name=person_record.get('name', ''),
                relationship="self",
                scheme_type=scheme_info['scheme'],
                confidence_score=confidence,
                eligibility_reasoning=scheme_info['reason'],
                source_records=[source_record],
                contact_info={
                    'aadhaar_id': aadhaar_number,
                    'address': f"{person_record.get('village', '')}, {person_record.get('district', '')}"
                }
            )
            
            beneficiaries.append(beneficiary)
        
        # Sort by confidence score
        beneficiaries.sort(key=lambda b: b.confidence_score, reverse=True)
        
        response = BeneficiaryDiscoveryResponse(
            success=True,
            message=f"Found {len(beneficiaries)} potential scheme eligibilities" if beneficiaries else "Person found but no scheme eligibilities identified",
            death_record_id=aadhaar_number,
            deceased_name=person_record.get('name', ''),
            beneficiaries=beneficiaries,
            total_found=len(beneficiaries)
        )
        
        return response
        
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Data file not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching by Aadhaar: {str(e)}"
        )


@app.post("/api/grievance/submit", response_model=GrievanceResponse)
async def submit_grievance(grievance_data: GrievanceCreate):
    """
    Submit a new grievance for classification and routing
    
    Accepts Hindi or English grievance text, classifies it using mBERT,
    predicts SLA, and creates a grievance record.
    
    Validates: Requirements 3.1, 3.3, 3.4
    """
    try:
        # Validate language
        if grievance_data.language not in ['hi', 'en', 'chhattisgarhi']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {grievance_data.language}. Supported: 'hi', 'en', 'chhattisgarhi'"
            )
        
        # Validate grievance text
        if not grievance_data.text or not grievance_data.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Grievance text cannot be empty"
            )
        
        # Classify grievance using mBERT classifier
        category, confidence, sla_hours = grievance_classifier.classify(
            grievance_data.text,
            grievance_data.language
        )
        
        # Generate unique grievance ID
        grievance_id = str(uuid.uuid4())
        
        # Calculate SLA deadline
        submitted_at = datetime.now(datetime.UTC) if hasattr(datetime, 'UTC') else datetime.utcnow()
        sla_deadline = submitted_at + timedelta(hours=sla_hours)
        
        # Create grievance record
        grievance = Grievance(
            grievance_id=grievance_id,
            citizen_id=grievance_data.citizen_id,
            text=grievance_data.text,
            language=grievance_data.language,
            category=category,
            classification_confidence=confidence,
            predicted_sla=sla_hours,
            assigned_department=category,  # Department matches category
            assigned_officer_id=None,  # Not assigned yet
            status="submitted",
            escalation_level=0,
            submitted_at=submitted_at,
            sla_deadline=sla_deadline,
            resolved_at=None,
            status_history=[]
        )
        
        # Store in mock data store
        mock_data["grievances"].append(grievance.model_dump())
        
        # Prepare response
        response = GrievanceResponse(
            success=True,
            message=f"Grievance submitted successfully. Routed to {category} department.",
            grievance=grievance
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting grievance: {str(e)}"
        )


@app.get("/api/grievance/check-escalations", response_model=EscalationCheckResponse)
async def check_escalations():
    """
    Check grievances for SLA deadline breaches and identify those needing escalation
    
    Scans all unresolved grievances in the mock data store and identifies those
    that have exceeded their SLA deadline. Simple rule: if current_time > sla_deadline, escalate.
    
    Validates: Requirements 4.1, 4.2
    """
    try:
        # Get current time
        current_time = datetime.now(datetime.UTC) if hasattr(datetime, 'UTC') else datetime.utcnow()
        
        # Get all grievances from mock data store
        all_grievances = mock_data["grievances"]
        
        # Filter for unresolved grievances (not in 'resolved' status)
        unresolved_statuses = ["submitted", "assigned", "in_progress", "escalated"]
        unresolved_grievances = [
            g for g in all_grievances 
            if g.get("status") in unresolved_statuses
        ]
        
        # Check each grievance against SLA deadline
        grievances_needing_escalation = []
        
        for grievance_dict in unresolved_grievances:
            # Parse the SLA deadline
            sla_deadline = grievance_dict.get("sla_deadline")
            
            # Handle both datetime objects and ISO string formats
            if isinstance(sla_deadline, str):
                # Parse ISO format string
                sla_deadline = datetime.fromisoformat(sla_deadline.replace('Z', '+00:00'))
            
            # Check if current time exceeds SLA deadline
            if current_time > sla_deadline:
                # Convert dict to Grievance model for response
                grievance = Grievance(**grievance_dict)
                grievances_needing_escalation.append(grievance)
        
        # Sort by how overdue they are (most overdue first)
        grievances_needing_escalation.sort(
            key=lambda g: current_time - g.sla_deadline,
            reverse=True
        )
        
        # Prepare response
        response = EscalationCheckResponse(
            success=True,
            message=f"Checked {len(unresolved_grievances)} unresolved grievances. Found {len(grievances_needing_escalation)} needing escalation.",
            total_checked=len(unresolved_grievances),
            escalations_needed=len(grievances_needing_escalation),
            grievances=grievances_needing_escalation
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking escalations: {str(e)}"
        )


@app.post("/api/application/validate", response_model=ApplicationValidationResponse)
async def validate_application(validation_request: ApplicationValidationCreate):
    """
    Validate application data and predict rejection risk
    
    Accepts application data and documents, runs validation rules using the
    rejection risk model, and returns rejection risk score (0-1) with a list
    of issues and corrective guidance prioritized by severity.
    
    Validates: Requirements 6.1, 6.5, 7.1, 7.2, 7.3
    """
    try:
        # Validate required fields in request
        if not validation_request.application_id:
            raise HTTPException(
                status_code=400,
                detail="application_id is required"
            )
        
        if not validation_request.scheme_type:
            raise HTTPException(
                status_code=400,
                detail="scheme_type is required"
            )
        
        if not validation_request.operator_id:
            raise HTTPException(
                status_code=400,
                detail="operator_id is required"
            )
        
        if not validation_request.application_data:
            raise HTTPException(
                status_code=400,
                detail="application_data is required"
            )
        
        # Run validation using the rejection risk model
        validation_result = rejection_risk_model.validate_application(
            application_id=validation_request.application_id,
            scheme_type=validation_request.scheme_type,
            operator_id=validation_request.operator_id,
            application_data=validation_request.application_data
        )
        
        # Store validation result in mock data store for demo purposes
        mock_data["applications"].append({
            "application_id": validation_request.application_id,
            "scheme_type": validation_request.scheme_type,
            "operator_id": validation_request.operator_id,
            "rejection_risk_score": validation_result.rejection_risk_score,
            "validated_at": validation_result.validated_at.isoformat(),
            "issues_count": len(validation_result.validation_issues)
        })
        
        # Prepare response message
        if validation_result.rejection_risk_score == 0.0:
            message = "Application validation successful. No issues found."
        elif validation_result.rejection_risk_score < 0.3:
            message = f"Application validation complete. Low rejection risk ({validation_result.rejection_risk_score:.2f}). {len(validation_result.validation_issues)} minor issues found."
        elif validation_result.rejection_risk_score < 0.6:
            message = f"Application validation complete. Medium rejection risk ({validation_result.rejection_risk_score:.2f}). {len(validation_result.validation_issues)} issues found."
        else:
            message = f"Application validation complete. High rejection risk ({validation_result.rejection_risk_score:.2f}). {len(validation_result.validation_issues)} critical issues found."
        
        # Prepare response
        response = ApplicationValidationResponse(
            success=True,
            message=message,
            validation=validation_result
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error validating application: {str(e)}"
        )


# ---------------------------------------------------------------------------
# Severity weights used for score derivation from merged anomaly list
# ---------------------------------------------------------------------------
_SEVERITY_WEIGHTS = {
    "critical": 0.40,
    "high": 0.25,
    "medium": 0.15,
    "low": 0.05,
}


@app.post("/api/application/reconcile-anomalies", response_model=ReconcileAnomaliesResponse)
async def reconcile_anomalies(request: ReconcileAnomaliesRequest):
    """
    Offline-to-online reconciliation endpoint.

    Accepts local anomaly flags captured while the device was offline, runs the
    server-side Rejection_Risk_Model on the supplied application data, merges
    both sets of issues (deduplicating by field_name + anomaly_type), and
    returns an updated rejection_risk_score.

    Validates: Requirements 16.5
    """
    try:
        # 1. Run server-side RejectionRiskModel
        server_validation = rejection_risk_model.validate_application(
            application_id="reconcile-" + str(uuid.uuid4()),
            scheme_type=request.scheme_type,
            operator_id="system",
            application_data=request.application_data,
        )

        # 2. Convert server validation issues to MergedIssue list
        server_issues = [
            MergedIssue(
                field_name=vi.field_name,
                anomaly_type=vi.issue_type,
                description=vi.description or "",
                severity=vi.severity,
                source="server",
            )
            for vi in server_validation.validation_issues
        ]

        # 3. Merge, deduplicate, and recalculate score
        return _reconcile_logic(
            server_score=server_validation.rejection_risk_score,
            server_issues=server_issues,
            local_anomalies=request.local_anomalies,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reconciling anomalies: {str(e)}",
        )


@app.get("/api/rejection-patterns/{scheme_type}", response_model=RejectionPatternListResponse)
async def get_rejection_patterns(scheme_type: str):
    """
    Return top-10 high-risk fields for the given scheme type, sorted by
    rejection_frequency_score descending.

    Validates: Requirements 17.2, 17.5
    """
    try:
        patterns = rejection_pattern_analyzer.get_high_risk_fields(scheme_type, threshold=0.0)
        items = [
            RejectionPatternItem(
                field_name=p.field_name,
                scheme_type=p.scheme_type,
                rejected_count=p.rejected_count,
                total_applications=p.total_applications,
                rejection_frequency_score=p.rejection_frequency_score,
                last_refreshed=p.last_refreshed,
            )
            for p in patterns
        ]
        return RejectionPatternListResponse(scheme_type=scheme_type, patterns=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rejection patterns: {str(e)}")


@app.get("/api/rejection-patterns/{scheme_type}/export")
async def export_rejection_patterns(scheme_type: str):
    """
    Export rejection pattern data for the given scheme type as a CSV download.

    Validates: Requirements 17.2, 17.5
    """
    try:
        csv_data = rejection_pattern_analyzer.export_csv(scheme_type)
        filename = f"rejection_patterns_{scheme_type}.csv"
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting rejection patterns: {str(e)}")


@app.post("/api/application/infer-eligibility", response_model=EligibilitySignalResponse)
async def infer_eligibility(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    scheme_type: str = Form(...),
    session_id: Optional[str] = Form(None),
):
    """
    Pre-submission document eligibility inference.

    Accepts a multipart document upload, extracts metadata (in-memory only),
    and infers a pre-submission eligibility signal for the given scheme type.
    Raw document bytes are never stored in any response field or database row.

    Validates: Requirements 18.1, 18.2, 18.3
    """
    try:
        document_bytes = await file.read()

        metadata: DocumentMetadata = eligibility_engine.extract_metadata(
            document_bytes, document_type, session_id=session_id
        )

        effective_session_id = session_id or str(uuid.uuid4())
        signal: EligibilitySignal = eligibility_engine.infer_eligibility(
            metadata, scheme_type, session_id=effective_session_id
        )

        return EligibilitySignalResponse(
            session_id=signal.session_id,
            scheme_type=signal.scheme_type,
            eligibility_status=signal.eligibility_status,
            ineligibility_reason_hindi=signal.ineligibility_reason_hindi,
            ineligibility_reason_english=signal.ineligibility_reason_english,
            confidence=signal.confidence,
            document_type=signal.metadata_used.document_type,
            issuing_authority=signal.metadata_used.issuing_authority,
            validity_status=signal.metadata_used.validity_status,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inferring eligibility: {str(e)}")


@app.post("/api/guidance/query", response_model=GuidanceResponseModel)
async def guidance_query(request: GuidanceQueryRequest):
    """
    Return contextual guidance for a CSC operator query.

    Accepts a GuidanceQueryRequest (intent, scheme_type, active_field, language,
    optional question_text) and returns a multilingual guidance response served
    from the in-memory cache (sub-3-second latency).

    Validates: Requirements 19.1, 19.2
    """
    try:
        query = GuidanceQuery(
            intent=request.intent,
            scheme_type=request.scheme_type,
            active_field=request.active_field,
            language=request.language,
            question_text=request.question_text,
        )
        result: GuidanceResponse = guidance_interface.handle_query(query)
        return GuidanceResponseModel(
            intent=result.intent,
            scheme_type=result.scheme_type,
            referenced_field=result.referenced_field,
            referenced_scheme=result.referenced_scheme,
            response_text=result.response_text,
            language=result.language,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing guidance query: {str(e)}")


@app.post("/api/guidance/transcribe", response_model=TranscriptionResponse)
async def guidance_transcribe(
    audio: UploadFile = File(...),
    language: str = Form(...),
):
    """
    Transcribe operator voice input to text.

    Accepts a multipart audio file upload and a language code ('hi' or
    'chhattisgarhi'), and returns the transcription result.

    Validates: Requirements 19.4
    """
    try:
        audio_bytes = await audio.read()
        result: TranscriptionResult = guidance_interface.transcribe_voice(audio_bytes, language)
        return TranscriptionResponse(
            transcription=result.transcription,
            language=result.language,
            confidence=result.confidence,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")


@app.get("/api/triage-queue")
async def get_triage_queue():
    """
    Return current Triage_Queue sorted by stall_risk_score descending with
    bilingual stall reasons.

    Validates: Requirements 20.2, 20.3
    """
    try:
        queue = stall_risk_predictor.get_triage_queue(threshold=0.6)
        result = []
        for assessment in queue:
            d = asdict(assessment)
            d["computed_at"] = assessment.computed_at.isoformat()
            result.append(d)
        return {"triage_queue": result, "total": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching triage queue: {str(e)}")


@app.post("/api/application/{application_id}/stall-risk")
async def compute_stall_risk(application_id: str, request: StallRiskRequest):
    """
    Compute and return StallRiskAssessment for a single application.

    Validates: Requirements 20.2, 20.4, 20.5
    """
    try:
        submitted_at = datetime.fromisoformat(request.submitted_at)
        assessment = stall_risk_predictor.add_application(
            application_id=application_id,
            application_data=request.application_data,
            validation_issues=request.validation_issues,
            scheme_type=request.scheme_type,
            submitted_at=submitted_at,
            operator_id=request.operator_id,
        )
        d = asdict(assessment)
        d["computed_at"] = assessment.computed_at.isoformat()
        return d
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid request data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing stall risk: {str(e)}")


@app.post("/api/application/{application_id}/resolve")
async def resolve_application(application_id: str):
    """
    Mark an application as resolved, removing it from the triage queue.

    Validates: Requirements 20.5
    """
    try:
        stall_risk_predictor.resolve_application(application_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resolving application: {str(e)}")


@app.get("/api/cache/manifest", response_model=OfflineCacheManifestResponse)
async def get_cache_manifest(bandwidth_kbps: float = 100.0):
    """
    Return the current offline cache manifest including connectivity mode and
    last sync timestamp.

    Validates: Requirements 21.4, 21.5
    """
    try:
        manifest = cache_manager.get_cache_manifest(bandwidth_kbps)
        d = asdict(manifest)
        d["last_sync_timestamp"] = manifest.last_sync_timestamp.isoformat()
        return d
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cache manifest: {str(e)}")


@app.post("/api/cache/sync", response_model=SyncResultResponse)
async def sync_cache():
    """
    Trigger deferred data synchronisation and return the result.

    Validates: Requirements 21.4, 21.5
    """
    try:
        result = cache_manager.sync_deferred_data()
        d = asdict(result)
        d["synced_at"] = result.synced_at.isoformat()
        return d
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing cache: {str(e)}")
