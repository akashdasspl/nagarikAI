"""
Unit tests for EligibilityInferenceEngine.
Validates: Requirements 18.1, 18.2, 18.3, 18.4, 18.5
"""
import time
import uuid
from datetime import date, timedelta

import pytest

from models.eligibility_inference_engine import (
    DocumentMetadata,
    EligibilityInferenceEngine,
    EligibilitySignal,
)

SUPPORTED_DOC_TYPES = [
    "aadhaar",
    "ration_card",
    "death_certificate",
    "income_certificate",
    "disability_certificate",
    "age_proof",
    "bank_passbook",
]


@pytest.fixture
def engine():
    return EligibilityInferenceEngine()


# ---------------------------------------------------------------------------
# extract_metadata
# ---------------------------------------------------------------------------

class TestExtractMetadata:
    def test_returns_document_metadata_instance(self, engine):
        meta = engine.extract_metadata(b"fake-bytes", "aadhaar")
        assert isinstance(meta, DocumentMetadata)

    def test_document_type_preserved(self, engine):
        for doc_type in SUPPORTED_DOC_TYPES:
            meta = engine.extract_metadata(b"x", doc_type)
            assert meta.document_type == doc_type

    def test_issuing_authority_non_empty(self, engine):
        for doc_type in SUPPORTED_DOC_TYPES:
            meta = engine.extract_metadata(b"x", doc_type)
            assert meta.issuing_authority, f"Empty authority for {doc_type}"

    def test_known_issuing_authorities(self, engine):
        expected = {
            "aadhaar": "UIDAI",
            "ration_card": "Food & Civil Supplies Department",
            "death_certificate": "Municipal Corporation / Gram Panchayat",
            "income_certificate": "Revenue Department",
            "disability_certificate": "Chief Medical Officer",
            "age_proof": "Municipal Corporation",
            "bank_passbook": "Bank",
        }
        for doc_type, authority in expected.items():
            meta = engine.extract_metadata(b"x", doc_type)
            assert meta.issuing_authority == authority

    def test_issue_date_is_approximately_two_years_ago(self, engine):
        meta = engine.extract_metadata(b"x", "aadhaar")
        assert meta.issue_date is not None
        delta = (date.today() - meta.issue_date).days
        # Allow ±10 days around 730 days
        assert 720 <= delta <= 740

    def test_validity_status_is_valid(self, engine):
        for doc_type in SUPPORTED_DOC_TYPES:
            meta = engine.extract_metadata(b"x", doc_type)
            assert meta.validity_status == "valid"

    def test_bytes_not_in_metadata(self, engine):
        raw = b"sensitive-document-bytes"
        meta = engine.extract_metadata(raw, "aadhaar")
        # DocumentMetadata must not expose raw bytes
        assert not hasattr(meta, "bytes")
        assert not hasattr(meta, "raw")

    def test_auto_generates_session_id_and_stores_in_memory(self, engine):
        engine.extract_metadata(b"data", "aadhaar")
        # At least one session should be stored
        assert len(engine._session_store) >= 1

    def test_caller_supplied_session_id_is_used(self, engine):
        sid = "test-session-123"
        engine.extract_metadata(b"data", "aadhaar", session_id=sid)
        assert sid in engine._session_store

    def test_unknown_doc_type_returns_fallback_authority(self, engine):
        meta = engine.extract_metadata(b"x", "unknown_doc")
        assert meta.issuing_authority  # non-empty fallback


# ---------------------------------------------------------------------------
# infer_eligibility
# ---------------------------------------------------------------------------

class TestInferEligibility:
    def _meta(self, doc_type="aadhaar", validity="valid", issue_date=None):
        if issue_date is None:
            issue_date = date.today() - timedelta(days=730)
        return DocumentMetadata(
            document_type=doc_type,
            issue_date=issue_date,
            issuing_authority="UIDAI",
            validity_status=validity,
        )

    def test_returns_eligibility_signal(self, engine):
        sig = engine.infer_eligibility(self._meta(), "ration_card")
        assert isinstance(sig, EligibilitySignal)

    def test_expired_document_is_ineligible(self, engine):
        meta = self._meta(validity="expired")
        sig = engine.infer_eligibility(meta, "ration_card")
        assert sig.eligibility_status == "ineligible"

    def test_expired_document_has_bilingual_reason(self, engine):
        meta = self._meta(validity="expired")
        sig = engine.infer_eligibility(meta, "ration_card")
        assert sig.ineligibility_reason_hindi
        assert sig.ineligibility_reason_english

    def test_none_issue_date_returns_unknown(self, engine):
        meta = self._meta(issue_date=None)
        meta.issue_date = None
        sig = engine.infer_eligibility(meta, "ration_card")
        assert sig.eligibility_status == "unknown"

    def test_document_older_than_5_years_is_ineligible(self, engine):
        old_date = date.today() - timedelta(days=365 * 6)
        meta = self._meta(issue_date=old_date)
        sig = engine.infer_eligibility(meta, "ration_card")
        assert sig.eligibility_status == "ineligible"

    def test_bank_passbook_not_flagged_for_age(self, engine):
        old_date = date.today() - timedelta(days=365 * 6)
        meta = self._meta(doc_type="bank_passbook", issue_date=old_date)
        sig = engine.infer_eligibility(meta, "ration_card")
        # bank_passbook is exempt from the 5-year rule
        assert sig.eligibility_status == "eligible"

    def test_widow_pension_requires_death_certificate(self, engine):
        meta = self._meta(doc_type="aadhaar")
        sig = engine.infer_eligibility(meta, "widow_pension")
        assert sig.eligibility_status == "ineligible"

    def test_widow_pension_with_death_certificate_is_eligible(self, engine):
        meta = self._meta(doc_type="death_certificate")
        sig = engine.infer_eligibility(meta, "widow_pension")
        assert sig.eligibility_status == "eligible"

    def test_disability_pension_requires_disability_certificate(self, engine):
        meta = self._meta(doc_type="aadhaar")
        sig = engine.infer_eligibility(meta, "disability_pension")
        assert sig.eligibility_status == "ineligible"

    def test_disability_pension_with_correct_doc_is_eligible(self, engine):
        meta = self._meta(doc_type="disability_certificate")
        sig = engine.infer_eligibility(meta, "disability_pension")
        assert sig.eligibility_status == "eligible"

    def test_old_age_pension_requires_age_proof(self, engine):
        meta = self._meta(doc_type="aadhaar")
        sig = engine.infer_eligibility(meta, "old_age_pension")
        assert sig.eligibility_status == "ineligible"

    def test_old_age_pension_with_age_proof_is_eligible(self, engine):
        meta = self._meta(doc_type="age_proof")
        sig = engine.infer_eligibility(meta, "old_age_pension")
        assert sig.eligibility_status == "eligible"

    def test_scholarship_requires_age_proof(self, engine):
        meta = self._meta(doc_type="aadhaar")
        sig = engine.infer_eligibility(meta, "scholarship")
        assert sig.eligibility_status == "ineligible"

    def test_scheme_without_doc_requirement_is_eligible(self, engine):
        meta = self._meta(doc_type="aadhaar")
        sig = engine.infer_eligibility(meta, "ration_card")
        assert sig.eligibility_status == "eligible"

    def test_confidence_in_valid_range(self, engine):
        meta = self._meta()
        sig = engine.infer_eligibility(meta, "ration_card")
        assert 0.0 <= sig.confidence <= 1.0

    def test_ineligible_signal_has_non_empty_bilingual_reasons(self, engine):
        meta = self._meta(validity="expired")
        sig = engine.infer_eligibility(meta, "ration_card")
        assert sig.ineligibility_reason_hindi != ""
        assert sig.ineligibility_reason_english != ""

    def test_eligible_signal_has_empty_reasons(self, engine):
        meta = self._meta(doc_type="death_certificate")
        sig = engine.infer_eligibility(meta, "widow_pension")
        assert sig.ineligibility_reason_hindi == ""
        assert sig.ineligibility_reason_english == ""

    def test_metadata_used_is_preserved(self, engine):
        meta = self._meta()
        sig = engine.infer_eligibility(meta, "ration_card")
        assert sig.metadata_used is meta

    def test_session_id_is_set(self, engine):
        meta = self._meta()
        sig = engine.infer_eligibility(meta, "ration_card", session_id="sess-42")
        assert sig.session_id == "sess-42"

    def test_auto_session_id_generated_when_not_provided(self, engine):
        meta = self._meta()
        sig = engine.infer_eligibility(meta, "ration_card")
        assert sig.session_id  # non-empty


# ---------------------------------------------------------------------------
# discard_session_data
# ---------------------------------------------------------------------------

class TestDiscardSessionData:
    def test_manual_discard_removes_session(self, engine):
        sid = "discard-test"
        engine.extract_metadata(b"data", "aadhaar", session_id=sid)
        assert sid in engine._session_store
        engine.discard_session_data(sid)
        assert sid not in engine._session_store

    def test_discard_nonexistent_session_is_safe(self, engine):
        # Should not raise
        engine.discard_session_data("nonexistent-session")

    def test_watchdog_timer_discards_within_60_seconds(self, engine):
        """
        Verify the watchdog fires. We use a very short timer by patching
        the timeout to 0.1 s to keep the test fast.
        """
        import threading as _threading
        import models.eligibility_inference_engine as _mod

        original_timer = _mod.threading.Timer

        class FastTimer(_threading.Timer):
            def __init__(self, interval, function, args=None, kwargs=None):
                super().__init__(0.1, function, args=args, kwargs=kwargs)

        _mod.threading.Timer = FastTimer

        try:
            sid = "watchdog-test-" + str(uuid.uuid4())
            engine.extract_metadata(b"data", "aadhaar", session_id=sid)
            assert sid in engine._session_store
            time.sleep(0.5)  # wait for fast timer
            assert sid not in engine._session_store
        finally:
            _mod.threading.Timer = original_timer

    def test_raw_bytes_not_accessible_after_discard(self, engine):
        sid = "privacy-test"
        engine.extract_metadata(b"sensitive", "aadhaar", session_id=sid)
        engine.discard_session_data(sid)
        assert sid not in engine._session_store
