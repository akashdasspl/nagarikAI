"""
Eligibility Inference Engine for pre-submission document metadata analysis.
Validates: Requirements 18.1, 18.2, 18.3, 18.4, 18.5
"""
from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, Optional

from .rejection_risk import RejectionRiskModel


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class DocumentMetadata:
    """Derived metadata extracted from a document (no raw bytes stored)."""
    document_type: str
    issue_date: Optional[date]
    issuing_authority: str
    validity_status: str  # 'valid' | 'expired' | 'unknown'


@dataclass
class EligibilitySignal:
    """Pre-submission eligibility inference result."""
    session_id: str
    scheme_type: str
    eligibility_status: str  # 'eligible' | 'ineligible' | 'unknown'
    ineligibility_reason_hindi: str
    ineligibility_reason_english: str
    confidence: float
    metadata_used: DocumentMetadata


# ---------------------------------------------------------------------------
# Issuing authority map
# ---------------------------------------------------------------------------

_ISSUING_AUTHORITIES: Dict[str, str] = {
    "aadhaar": "UIDAI",
    "ration_card": "Food & Civil Supplies Department",
    "death_certificate": "Municipal Corporation / Gram Panchayat",
    "income_certificate": "Revenue Department",
    "disability_certificate": "Chief Medical Officer",
    "age_proof": "Municipal Corporation",
    "bank_passbook": "Bank",
}

# Scheme → required document type(s)
_SCHEME_REQUIRED_DOCS: Dict[str, str] = {
    "widow_pension": "death_certificate",
    "disability_pension": "disability_certificate",
    "old_age_pension": "age_proof",
    "scholarship": "age_proof",
}


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class EligibilityInferenceEngine:
    """
    Extracts eligibility-relevant metadata from document bytes (in-memory only)
    and infers a pre-submission eligibility signal for a given scheme type.

    Raw document bytes are NEVER written to disk and are purged from memory
    within 60 seconds of session closure via a watchdog timer.
    """

    def __init__(self) -> None:
        # {session_id: {'bytes': bytes, 'created_at': datetime, '_timer': Timer}}
        self._session_store: Dict[str, dict] = {}
        self._lock = threading.Lock()
        self._risk_model = RejectionRiskModel()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_metadata(
        self,
        document_bytes: bytes,
        document_type: str,
        session_id: Optional[str] = None,
    ) -> DocumentMetadata:
        """
        Extract eligibility-relevant metadata from document bytes.

        Raw bytes are stored in-memory only, keyed by session_id.
        They are NEVER written to disk.

        Args:
            document_bytes: Raw document bytes (kept in-memory only).
            document_type: One of the supported document types.
            session_id: Optional caller-supplied session identifier.
                        A new UUID is generated when omitted.

        Returns:
            DocumentMetadata with simulated extraction results.
        """
        if session_id is None:
            session_id = str(uuid.uuid4())

        # Store bytes in-memory and arm the watchdog timer
        self._store_session(session_id, document_bytes)

        # Simulate metadata extraction (MVP — no real OCR)
        metadata = self._simulate_extraction(document_type)
        return metadata

    def infer_eligibility(
        self,
        metadata: DocumentMetadata,
        scheme_type: str,
        session_id: Optional[str] = None,
    ) -> EligibilitySignal:
        """
        Infer a pre-submission eligibility signal from document metadata.

        Args:
            metadata: DocumentMetadata returned by extract_metadata.
            scheme_type: Target welfare scheme.
            session_id: Optional session identifier for correlation.

        Returns:
            EligibilitySignal with bilingual ineligibility reason when applicable.
        """
        if session_id is None:
            session_id = str(uuid.uuid4())

        status, reason_hi, reason_en, confidence = self._apply_eligibility_rules(
            metadata, scheme_type
        )

        return EligibilitySignal(
            session_id=session_id,
            scheme_type=scheme_type,
            eligibility_status=status,
            ineligibility_reason_hindi=reason_hi,
            ineligibility_reason_english=reason_en,
            confidence=confidence,
            metadata_used=metadata,
        )

    def discard_session_data(self, session_id: str) -> None:
        """
        Immediately purge all in-memory raw data for the given session.

        A watchdog timer also calls this automatically 60 seconds after
        the session is created, so callers need not call it explicitly.
        """
        with self._lock:
            entry = self._session_store.pop(session_id, None)
            if entry:
                timer: Optional[threading.Timer] = entry.get("_timer")
                if timer is not None:
                    timer.cancel()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _store_session(self, session_id: str, document_bytes: bytes) -> None:
        """Store bytes in-memory and arm a 60-second watchdog timer."""
        with self._lock:
            # Cancel any existing timer for this session
            existing = self._session_store.get(session_id)
            if existing:
                t = existing.get("_timer")
                if t:
                    t.cancel()

            timer = threading.Timer(60.0, self.discard_session_data, args=(session_id,))
            timer.daemon = True
            timer.start()

            self._session_store[session_id] = {
                "bytes": document_bytes,
                "created_at": datetime.utcnow(),
                "_timer": timer,
            }

    def _simulate_extraction(self, document_type: str) -> DocumentMetadata:
        """
        Simulate OCR-based metadata extraction for MVP purposes.

        Returns plausible metadata without touching disk.
        """
        authority = _ISSUING_AUTHORITIES.get(document_type, "Government Authority")
        issue_date = (datetime.utcnow() - timedelta(days=730)).date()  # ~2 years ago
        validity_status = "valid"

        # bank_passbook doesn't expire in the traditional sense
        if document_type == "bank_passbook":
            validity_status = "valid"

        return DocumentMetadata(
            document_type=document_type,
            issue_date=issue_date,
            issuing_authority=authority,
            validity_status=validity_status,
        )

    def _apply_eligibility_rules(
        self,
        metadata: DocumentMetadata,
        scheme_type: str,
    ) -> tuple[str, str, str, float]:
        """
        Apply eligibility rules and return (status, reason_hi, reason_en, confidence).
        """
        # Rule 1: expired document
        if metadata.validity_status == "expired":
            return (
                "ineligible",
                "दस्तावेज़ की अवधि समाप्त हो गई है",
                "Document expired",
                0.95,
            )

        # Rule 2: unknown issue date → unknown eligibility
        if metadata.issue_date is None:
            return (
                "unknown",
                "दस्तावेज़ की जारी तिथि अज्ञात है",
                "Document issue date is unknown",
                0.50,
            )

        # Rule 3: document too old (> 5 years for most docs)
        age_years = (date.today() - metadata.issue_date).days / 365.25
        if age_years > 5 and metadata.document_type != "bank_passbook":
            return (
                "ineligible",
                "दस्तावेज़ 5 वर्ष से अधिक पुराना है और संभवतः अमान्य है",
                "Document is older than 5 years and may be invalid",
                0.80,
            )

        # Rule 4: scheme-specific document type check
        required_doc = _SCHEME_REQUIRED_DOCS.get(scheme_type)
        if required_doc and metadata.document_type != required_doc:
            reason_en = (
                f"Scheme '{scheme_type}' requires a {required_doc.replace('_', ' ')}, "
                f"but a {metadata.document_type.replace('_', ' ')} was provided"
            )
            reason_hi = (
                f"योजना '{scheme_type}' के लिए {required_doc.replace('_', ' ')} आवश्यक है, "
                f"लेकिन {metadata.document_type.replace('_', ' ')} प्रदान किया गया"
            )
            return ("ineligible", reason_hi, reason_en, 0.90)

        # All checks passed
        return ("eligible", "", "", 0.85)
