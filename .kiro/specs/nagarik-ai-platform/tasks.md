# Implementation Plan: NagarikAI Platform - Hackathon MVP

## Overview

This is a streamlined implementation plan for building a working prototype of the NagarikAI Platform for Hackathon 2026. The MVP focuses on demonstrating the three core AI capabilities with simplified implementations and mock data, prioritizing demo-ability over production readiness.

**MVP Scope:**
- Beneficiary Discovery Engine with basic entity matching (demo with sample data)
- Grievance Intelligence Layer with mBERT classification (pre-trained model)
- CSC Operator Assistant with rejection risk prediction (simple rule-based model)
- Single web interface combining all three features
- Mock databases with realistic sample data

**Out of Scope for MVP:**
- Production-grade security and encryption
- Offline mobile app capabilities
- Full RBAC and audit logging
- Auto-scaling and performance optimization
- Property-based testing (focus on demo functionality)

The implementation prioritizes speed and demo impact over completeness.

## Tasks

- [ ] 1. Set up basic project structure and mock data
  - [x] 1.1 Initialize Python FastAPI project with basic structure
    - Create project structure: backend/ and frontend/ directories
    - Set up Python virtual environment with FastAPI, uvicorn
    - Create simple in-memory data store (Python dictionaries) for demo
    - Add CORS middleware for local development
    - _Requirements: 12.1_

  - [x] 1.2 Create mock databases with sample data
    - Generate 50 sample civil death records (CSV format)
    - Generate 50 sample ration card records with some matching names
    - Generate 50 sample Aadhaar records
    - Generate 100 sample historical grievances in Hindi with department labels
    - Generate 50 sample historical applications with rejection outcomes
    - _Requirements: 1.1, 3.1, 6.1_

  - [x] 1.3 Create basic data models (Pydantic schemas)
    - Create EnrollmentCase, Grievance, ApplicationValidation schemas
    - Create API request/response models
    - Keep models simple without encryption or complex validation
    - _Requirements: 2.1, 5.1, 6.1_

- [ ] 2. Implement simplified Entity Resolver for beneficiary discovery
  - [x] 2.1 Create basic fuzzy matching for entity resolution
    - Implement simple name matching using fuzzywuzzy library
    - Match on name similarity (threshold > 70%)
    - Calculate basic confidence score based on name match percentage
    - Return top 3 matches per death record
    - _Requirements: 1.2, 9.1, 9.2_

  - [x] 2.2 Create Beneficiary Discovery Engine API
    - Create POST /api/beneficiary/discover endpoint
    - Accept death record as input
    - Use Entity Resolver to find matches across mock databases
    - Return list of potential beneficiaries with confidence scores
    - Generate simple eligibility reasoning text
    - _Requirements: 1.1, 1.3, 1.4_

- [ ] 3. Implement Grievance Intelligence with pre-trained model
  - [x] 3.1 Set up mBERT classifier for Hindi text
    - Use pre-trained multilingual BERT from Hugging Face
    - Create simple classification layer for 5 departments: Revenue, Health, Education, Social Welfare, Infrastructure
    - Fine-tune on mock grievance data (or use zero-shot classification)
    - Keep model lightweight for demo purposes
    - _Requirements: 3.1, 3.2_

  - [x] 3.2 Create Grievance Intelligence API
    - Create POST /api/grievance/submit endpoint
    - Accept Hindi/English grievance text
    - Classify using mBERT model
    - Calculate simple SLA prediction (fixed duration per department)
    - Return classification, confidence, predicted SLA
    - _Requirements: 3.1, 3.3, 3.4_

  - [x] 3.3 Implement basic auto-escalation logic
    - Create GET /api/grievance/check-escalations endpoint
    - Check mock grievances against SLA deadlines
    - Return list of grievances needing escalation
    - Simple rule: if current_time > sla_deadline, escalate
    - _Requirements: 4.1, 4.2_

- [ ] 4. Implement CSC Operator Assistant with rule-based validation
  - [x] 4.1 Create rule-based rejection risk model
    - Define validation rules for common issues:
      - Missing required fields (high risk)
      - Age below minimum (critical risk)
      - Income above threshold (high risk)
      - Document mismatch (medium risk)
    - Calculate risk score: count of issues weighted by severity
    - Generate corrective guidance messages in Hindi and English
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 4.2 Create CSC Operator Assistant API
    - Create POST /api/application/validate endpoint
    - Accept application data and documents
    - Run validation rules
    - Return rejection risk score (0-1) and list of issues with guidance
    - Prioritize guidance by severity
    - _Requirements: 6.1, 6.5, 7.1, 7.2, 7.3_

- [ ] 5. Build unified web interface for demo
  - [x] 5.1 Create React web app with three main sections
    - Initialize React project with Vite and TypeScript
    - Create three tabs: Beneficiary Discovery, Grievance Portal, Operator Assistant
    - Set up basic routing and navigation
    - Add simple styling with Tailwind CSS or Material-UI
    - _Requirements: 2.1, 3.1, 6.1_

  - [x] 5.2 Implement Beneficiary Discovery UI
    - Create form to input death record details
    - Display discovered beneficiaries in a table with confidence scores
    - Show eligibility reasoning for each match
    - Add visual indicators for confidence levels (high/medium/low)
    - _Requirements: 1.1, 1.3, 1.4_

  - [x] 5.3 Implement Grievance Portal UI
    - Create form to submit grievance in Hindi/English
    - Display classification result with department and confidence
    - Show predicted SLA timeline
    - Create simple status tracking view
    - Add mock escalation alerts display
    - _Requirements: 3.1, 3.3, 3.4, 4.1, 5.1_

  - [x] 5.4 Implement CSC Operator Assistant UI
    - Create application form with common fields (name, age, income, documents)
    - Display rejection risk score with color-coded indicator
    - Show validation issues in a list with severity badges
    - Display corrective guidance in both Hindi and English
    - Update risk score in real-time as user fixes issues
    - _Requirements: 6.1, 6.2, 6.5, 7.1, 7.2_

- [ ] 6. Add demo dashboard and analytics
  - [x] 6.1 Create simple analytics dashboard
    - Display mock metrics: enrollments discovered, grievances resolved, applications validated
    - Show simple bar charts for trends (use Chart.js or Recharts)
    - Add basic geographic distribution (simple table by district)
    - Use mock data to populate all metrics
    - _Requirements: 15.1, 15.2, 15.3_

- [x] 7. Polish and prepare for demo
  - [x] 7.1 Add Hindi language support for UI
    - Add Hindi translations for key UI elements
    - Implement language toggle (English/Hindi)
    - Ensure Hindi text displays correctly in all components
    - _Requirements: 2.4, 5.5, 7.1_

  - [x] 7.2 Create demo script and sample data
    - Prepare 3-5 demo scenarios showing each feature
    - Create sample inputs that produce good results
    - Document the demo flow and talking points
    - Test end-to-end demo flow multiple times
    - _Requirements: All_

  - [x] 7.3 Add visual polish and branding
    - Add NagarikAI logo and branding
    - Improve UI styling and responsiveness
    - Add loading states and animations
    - Create landing page explaining the platform
    - _Requirements: All_

  - [x] 7.4 Deploy demo to cloud platform
    - Deploy backend to Heroku, Railway, or similar
    - Deploy frontend to Vercel or Netlify
    - Ensure demo is accessible via public URL
    - Test deployment thoroughly
    - _Requirements: 12.4_

- [x] 8. Create presentation materials
  - [x] 8.1 Prepare hackathon presentation
    - Create slide deck covering problem, solution, architecture, demo
    - Include screenshots of all three features
    - Highlight AI/ML components (mBERT, entity resolution, risk prediction)
    - Prepare 5-minute pitch and 10-minute detailed presentation
    - _Requirements: All_

  - [x] 8.2 Record demo video
    - Record 2-3 minute video showing all features
    - Demonstrate beneficiary discovery with sample death record
    - Show grievance classification and routing
    - Demonstrate application validation with risk scoring
    - Add voiceover explaining each feature
    - _Requirements: All_

## Notes

- This MVP focuses on demonstrating the three core AI capabilities with simplified implementations
- Use mock data throughout - no need for real database connections
- Pre-trained models are sufficient - no need for custom training
- Single web interface is easier to demo than multiple apps
- Prioritize visual polish and demo-ability over code quality
- Target completion: 2-3 days for core features, 1 day for polish and presentation
- All property-based tests and production features are deferred post-hackathon

- [ ] 9. Implement CSC Operator Assistant Enhancements (Requirements 16–21)
  - [x] 9.1 Implement Local_NLP_Model for offline field anomaly detection
    - Create `backend/models/local_nlp_model.py` with `LocalNLPModel` class
    - Implement `parse_field` method covering format errors, implausible values, and cross-field inconsistencies for all supported scheme types
    - Implement `detect_anomalies` method scanning all fields in an application
    - Implement `supported_schemes` method returning the list of covered scheme types
    - Inference must complete in < 200 ms per field; fall back to regex rules if model unavailable
    - _Requirements: 16.1, 16.2, 16.3, 16.4_

  - [ ]* 9.2 Write property test for Local_NLP_Model anomaly detection
    - **Property 32: Local NLP Anomaly Detection Coverage** — for any anomalous field value and supported scheme, `detect_anomalies` returns at least one `FieldAnomaly` referencing the specific `field_name`
    - **Property 33: Local NLP Scheme Coverage** — for every scheme in `supported_schemes()`, `detect_anomalies` returns a result without error
    - **Validates: Requirements 16.1, 16.2, 16.3, 16.4**

  - [x] 9.3 Add offline-to-online reconciliation endpoint
    - Add `POST /api/application/reconcile-anomalies` endpoint in `backend/main.py`
    - Accept local anomaly flags from the device and merge with server-side `Rejection_Risk_Model` result
    - Return updated `rejection_risk_score` within 3 seconds of connectivity restoration
    - _Requirements: 16.5_

  - [ ]* 9.4 Write property test for offline-to-online reconciliation
    - **Property 34: Offline-to-Online Risk Score Reconciliation** — after `sync_deferred_data` completes, server-side score ≥ offline-only score when the same issues are present
    - **Validates: Requirements 16.5**

  - [x] 9.5 Implement Rejection_Pattern_Analyzer
    - Create `backend/models/rejection_pattern_analyzer.py` with `RejectionPatternAnalyzer` class and `RejectionPattern` dataclass
    - Implement `compute_rejection_frequencies` aggregating `Historical_Applications_DB` (applications CSV) per `(field_name, scheme_type)` pair; `rejection_frequency_score = rejected_count / total_applications`
    - Implement `get_high_risk_fields(scheme_type, threshold=0.3)` returning fields sorted descending by score, capped at 10 entries
    - Implement `export_csv(scheme_type)` returning a valid CSV string
    - Schedule refresh every 24 hours; store `last_refreshed` on each `RejectionPattern`
    - _Requirements: 17.1, 17.2, 17.4, 17.5_

  - [x] 9.6 Add Rejection_Pattern_Dashboard API endpoints
    - Add `GET /api/rejection-patterns/{scheme_type}` returning top-10 high-risk fields sorted by `rejection_frequency_score` descending
    - Add `GET /api/rejection-patterns/{scheme_type}/export` returning CSV download
    - _Requirements: 17.2, 17.5_

  - [ ]* 9.7 Write property tests for Rejection_Pattern_Analyzer
    - **Property 35: Rejection Frequency Score Correctness** — `rejection_frequency_score == rejected_count / total_applications` and value in `[0.0, 1.0]`
    - **Property 36: Rejection Pattern Dashboard Ordering** — `get_high_risk_fields` returns at most 10 entries sorted descending by score
    - **Property 37: High-Risk Field Highlighting Threshold** — all fields with score > 0.3 appear in result; no field with score ≤ 0.3 appears
    - **Property 38: Rejection Pattern Data Freshness** — `last_refreshed` is no more than 24 hours before current time
    - **Property 39: Rejection Pattern CSV Round-Trip** — `export_csv` output parses back to equivalent records
    - **Validates: Requirements 17.1, 17.2, 17.3, 17.4, 17.5**

  - [x] 9.8 Implement Eligibility_Inference_Engine
    - Create `backend/models/eligibility_inference_engine.py` with `EligibilityInferenceEngine` class and `DocumentMetadata` / `EligibilitySignal` dataclasses
    - Implement `extract_metadata(document_bytes, document_type)` extracting `document_type`, `issue_date`, `issuing_authority`, `validity_status`; never write raw bytes to disk
    - Implement `infer_eligibility(metadata, scheme_type)` returning `eligibility_status` and bilingual ineligibility reason using `RejectionRiskModel` feature set
    - Implement `discard_session_data(session_id)` purging all in-memory raw data within 60 seconds; wire to a watchdog timer
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5_

  - [x] 9.9 Add document metadata API endpoint
    - Add `POST /api/application/infer-eligibility` in `backend/main.py` accepting multipart document upload
    - Call `extract_metadata` then `infer_eligibility`; return `EligibilitySignal` with bilingual reason if ineligible
    - Ensure raw document bytes are not stored in any response field or database row
    - _Requirements: 18.1, 18.2, 18.3_

  - [ ]* 9.10 Write property tests for Eligibility_Inference_Engine
    - **Property 40: Document Metadata Extraction Completeness** — `extract_metadata` returns non-null `document_type`, `issue_date`, `issuing_authority`, `validity_status` for supported document types
    - **Property 41: Ineligibility Reason Bilingual Completeness** — when `eligibility_status == 'ineligible'`, both Hindi and English reason strings are non-empty
    - **Property 42: Raw Document Data Non-Persistence** — after session closure, no database row contains raw image bytes or OCR text for that `session_id`
    - **Validates: Requirements 18.1, 18.3, 18.4, 18.5**

  - [x] 9.11 Implement Guidance_Interface backend
    - Create `backend/models/guidance_interface.py` with `GuidanceInterface` class and `GuidanceQuery` / `GuidanceResponse` / `TranscriptionResult` dataclasses
    - Implement `handle_query` supporting intents: `field_definition`, `document_list`, `eligibility_criteria`, `rejection_reasons`; respond in `hi` or `chhattisgarhi` matching operator language setting; target latency < 3 seconds
    - Implement `transcribe_voice(audio_bytes, language)` returning transcription within 2 seconds
    - Pre-populate cached responses for common intents per scheme type during sync for offline/Lite_Mode use
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.6_

  - [x] 9.12 Add Guidance_Interface API endpoints
    - Add `POST /api/guidance/query` accepting `GuidanceQuery` and returning `GuidanceResponse`
    - Add `POST /api/guidance/transcribe` accepting audio bytes and returning `TranscriptionResult`
    - _Requirements: 19.1, 19.2, 19.4_

  - [ ]* 9.13 Write property tests for Guidance_Interface
    - **Property 43: Guidance Response Contextual Reference** — `referenced_field` equals `active_field` and `referenced_scheme` equals `scheme_type` in every response
    - **Property 44: Guidance Intent Coverage** — all four intents return non-empty `response_text` for every supported scheme type
    - **Property 45: Guidance Language Fidelity** — when `language` is `'hi'` or `'chhattisgarhi'`, `response_text` is in the requested language
    - **Validates: Requirements 19.2, 19.3, 19.6**

  - [x] 9.14 Implement Stall_Risk_Predictor
    - Create `backend/models/stall_risk_predictor.py` with `StallRiskPredictor` class and `StallRiskAssessment` dataclass
    - Implement `compute_stall_risk` using validation issue count/severity, time elapsed, scheme SLA data, and operator approval rate; return score in `[0, 1]` with bilingual stall reason
    - Implement `get_triage_queue(threshold=0.6)` returning applications with score > 0.6 sorted descending
    - Implement `refresh_all` recomputing scores for all in-progress applications; schedule every 30 minutes
    - _Requirements: 20.1, 20.2, 20.3, 20.4_

  - [x] 9.15 Add Stall_Risk_Predictor API endpoints
    - Add `GET /api/triage-queue` returning current `Triage_Queue` sorted by `stall_risk_score` descending with bilingual stall reasons
    - Add `POST /api/application/{application_id}/stall-risk` computing and returning `StallRiskAssessment` for a single application
    - Wire `refresh_all` to a background scheduler (APScheduler or Celery beat) running every 30 minutes
    - _Requirements: 20.2, 20.3, 20.4, 20.5_

  - [ ]* 9.16 Write property tests for Stall_Risk_Predictor
    - **Property 46: Stall Risk Score Bounds** — `stall_risk_score` is in `[0.0, 1.0]` for any application
    - **Property 47: Triage Queue Threshold and Ordering** — `get_triage_queue(0.6)` returns exactly applications with score > 0.6, sorted descending
    - **Property 48: Triage Queue Bilingual Stall Reason** — both `primary_stall_reason_hindi` and `primary_stall_reason_english` are non-empty for every queue entry
    - **Property 49: Stall Risk Score Freshness** — `computed_at` is no more than 30 minutes before current time
    - **Property 50: Triage Queue Removal After Resolution** — after issue resolution and `refresh_all`, resolved application no longer appears in queue
    - **Validates: Requirements 20.1, 20.2, 20.3, 20.4, 20.5**

  - [x] 9.17 Implement Offline_Cache_Manager
    - Create `backend/models/offline_cache_manager.py` with `OfflineCacheManager` class and `OfflineCacheManifest` dataclass
    - Implement `get_cache_manifest` returning current model version, checksum, last sync timestamp, and `is_stale` flag
    - Implement `is_cache_stale(max_age_hours=72)` returning `True` if `last_sync_timestamp` is older than 72 hours
    - Implement `get_connectivity_mode(bandwidth_kbps)` returning `'Online'`, `'Lite_Mode'` (< 50 kbps), or `'Offline'` (0 kbps)
    - Implement `sync_deferred_data` uploading deferred calls and downloading fresh model/pattern data within 60 seconds
    - Implement `apply_staleness_penalty(raw_confidence)` returning `max(0.0, raw_confidence - 0.10)` when stale, else unchanged; clamp to `[0.0, 1.0]`
    - _Requirements: 21.1, 21.2, 21.5, 21.6_

  - [x] 9.18 Add connectivity status and cache API endpoints
    - Add `GET /api/cache/manifest` returning `OfflineCacheManifest` including `connectivity_mode` and `last_sync_timestamp`
    - Add `POST /api/cache/sync` triggering `sync_deferred_data` and returning `SyncResult`
    - _Requirements: 21.4, 21.5_

  - [ ]* 9.19 Write property tests for Offline_Cache_Manager
    - **Property 51: Offline Cache Validity Window** — when `is_stale = False`, `detect_anomalies` and `infer_eligibility` return results without network errors
    - **Property 52: Lite_Mode Activation Threshold** — `get_connectivity_mode` returns `'Lite_Mode'` for bandwidth in `(0, 50)` kbps and `'Online'` for bandwidth ≥ 50 kbps
    - **Property 53: Core Features Available in Lite_Mode** — field anomaly detection, eligibility inference, and corrective guidance each return valid results in `Lite_Mode`
    - **Property 54: Staleness Confidence Penalty** — `apply_staleness_penalty(c)` returns `max(0.0, c - 0.10)` when stale and `c` unchanged when fresh
    - **Validates: Requirements 21.1, 21.2, 21.3, 21.5, 21.6**

  - [x] 9.20 Build Rejection_Pattern_Dashboard UI component
    - Add `RejectionPatternDashboard` component in `frontend/src/pages/OperatorAssistant.tsx` (or a new `RejectionPatterns.tsx` page)
    - Fetch top-10 high-risk fields from `GET /api/rejection-patterns/{scheme_type}` and render as a ranked table with `rejection_frequency_score` bar indicators
    - Add CSV export button wired to `GET /api/rejection-patterns/{scheme_type}/export`
    - _Requirements: 17.2, 17.5_

  - [x] 9.21 Add inline high-risk field highlighting to the application form
    - In `frontend/src/pages/OperatorAssistant.tsx`, fetch rejection patterns on scheme type selection
    - Highlight fields with `rejection_frequency_score > 0.3` with a visual indicator before the operator enters data
    - _Requirements: 17.3_

  - [x] 9.22 Build Guidance_Interface overlay UI component
    - Create `frontend/src/components/GuidanceOverlay.tsx` as a slide-in panel anchored to the right side of the form
    - Support text chat input and voice input (Web Speech API); display transcription for confirmation before sending
    - Render `GuidanceResponse.response_text` in the operator's language; keep overlay accessible without navigating away from the form
    - _Requirements: 19.1, 19.4, 19.5_

  - [x] 9.23 Build Triage_Queue UI component
    - Create `frontend/src/components/TriageQueue.tsx` displaying in-progress applications with `stall_risk_score > 0.6` sorted descending
    - Show `primary_stall_reason_hindi` and `primary_stall_reason_english` for each entry
    - Auto-refresh every 2 minutes; remove resolved applications from the list within 2 minutes of update
    - _Requirements: 20.2, 20.3, 20.5_

  - [x] 9.24 Add connectivity status indicator and Lite_Mode banner
    - Add a persistent status bar in `frontend/src/App.tsx` (or layout component) showing current mode (`Online`, `Lite_Mode`, `Offline`) and `last_sync_timestamp`
    - In `Lite_Mode`, disable non-essential UI elements (real-time charts, analytics calls) and show a banner
    - Display staleness warning when cache is older than 72 hours and reduce displayed confidence values by 10 percentage points in the UI
    - _Requirements: 21.2, 21.4, 21.6_

- [x] 10. Checkpoint — Ensure all CSC Operator Assistant Enhancement tests pass
  - Ensure all tests pass, ask the user if questions arise.
