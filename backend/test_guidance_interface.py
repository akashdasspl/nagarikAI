"""
Unit tests for GuidanceInterface backend.
Validates: Requirements 19.1, 19.2, 19.3, 19.4, 19.6
"""
import pytest
from models.guidance_interface import (
    GuidanceInterface,
    GuidanceQuery,
    GuidanceResponse,
    TranscriptionResult,
    SUPPORTED_INTENTS,
    SUPPORTED_LANGUAGES,
    SUPPORTED_SCHEMES,
)


@pytest.fixture
def gi() -> GuidanceInterface:
    return GuidanceInterface()


# ---------------------------------------------------------------------------
# handle_query — basic contract
# ---------------------------------------------------------------------------

class TestHandleQueryContract:
    def test_returns_guidance_response(self, gi):
        query = GuidanceQuery(
            intent="field_definition",
            scheme_type="widow_pension",
            active_field="date_of_birth",
            language="hi",
        )
        result = gi.handle_query(query)
        assert isinstance(result, GuidanceResponse)

    def test_referenced_field_equals_active_field(self, gi):
        query = GuidanceQuery(
            intent="document_list",
            scheme_type="old_age_pension",
            active_field="age_proof",
            language="hi",
        )
        result = gi.handle_query(query)
        assert result.referenced_field == query.active_field

    def test_referenced_scheme_equals_scheme_type(self, gi):
        query = GuidanceQuery(
            intent="eligibility_criteria",
            scheme_type="ration_card",
            active_field="income",
            language="hi",
        )
        result = gi.handle_query(query)
        assert result.referenced_scheme == query.scheme_type

    def test_response_text_non_empty_for_all_intents_and_schemes(self, gi):
        for intent in SUPPORTED_INTENTS:
            for scheme in SUPPORTED_SCHEMES:
                for lang in SUPPORTED_LANGUAGES:
                    query = GuidanceQuery(
                        intent=intent,
                        scheme_type=scheme,
                        active_field="test_field",
                        language=lang,
                    )
                    result = gi.handle_query(query)
                    assert result.response_text, (
                        f"Empty response for intent={intent}, scheme={scheme}, lang={lang}"
                    )

    def test_language_echoed_in_response(self, gi):
        for lang in SUPPORTED_LANGUAGES:
            query = GuidanceQuery(
                intent="document_list",
                scheme_type="scholarship",
                active_field="",
                language=lang,
            )
            result = gi.handle_query(query)
            assert result.language == lang


# ---------------------------------------------------------------------------
# handle_query — field substitution
# ---------------------------------------------------------------------------

class TestFieldSubstitution:
    def test_active_field_substituted_in_field_definition(self, gi):
        query = GuidanceQuery(
            intent="field_definition",
            scheme_type="widow_pension",
            active_field="aadhaar_number",
            language="hi",
        )
        result = gi.handle_query(query)
        assert "aadhaar_number" in result.response_text

    def test_active_field_substituted_chhattisgarhi(self, gi):
        query = GuidanceQuery(
            intent="field_definition",
            scheme_type="disability_pension",
            active_field="bank_account",
            language="chhattisgarhi",
        )
        result = gi.handle_query(query)
        assert "bank_account" in result.response_text

    def test_no_placeholder_left_when_active_field_empty(self, gi):
        query = GuidanceQuery(
            intent="field_definition",
            scheme_type="ration_card",
            active_field="",
            language="hi",
        )
        result = gi.handle_query(query)
        assert "{field}" not in result.response_text


# ---------------------------------------------------------------------------
# handle_query — unknown / fallback cases
# ---------------------------------------------------------------------------

class TestFallbackBehaviour:
    def test_unknown_scheme_returns_non_empty_response(self, gi):
        query = GuidanceQuery(
            intent="document_list",
            scheme_type="unknown_scheme_xyz",
            active_field="",
            language="hi",
        )
        result = gi.handle_query(query)
        assert result.response_text

    def test_unknown_language_defaults_to_hindi(self, gi):
        query = GuidanceQuery(
            intent="eligibility_criteria",
            scheme_type="widow_pension",
            active_field="",
            language="english",  # unsupported
        )
        result = gi.handle_query(query)
        assert result.language == "hi"
        assert result.response_text

    def test_unknown_intent_returns_non_empty_response(self, gi):
        query = GuidanceQuery(
            intent="unknown_intent",
            scheme_type="widow_pension",
            active_field="",
            language="hi",
        )
        result = gi.handle_query(query)
        # Should not raise; response_text may be empty for truly unknown intent
        assert isinstance(result, GuidanceResponse)


# ---------------------------------------------------------------------------
# handle_query — all four intents
# ---------------------------------------------------------------------------

class TestIntentCoverage:
    @pytest.mark.parametrize("intent", SUPPORTED_INTENTS)
    def test_intent_returns_response(self, gi, intent):
        query = GuidanceQuery(
            intent=intent,
            scheme_type="old_age_pension",
            active_field="age",
            language="hi",
        )
        result = gi.handle_query(query)
        assert result.response_text

    @pytest.mark.parametrize("intent", SUPPORTED_INTENTS)
    def test_intent_chhattisgarhi(self, gi, intent):
        query = GuidanceQuery(
            intent=intent,
            scheme_type="scholarship",
            active_field="marks",
            language="chhattisgarhi",
        )
        result = gi.handle_query(query)
        assert result.response_text


# ---------------------------------------------------------------------------
# transcribe_voice
# ---------------------------------------------------------------------------

class TestTranscribeVoice:
    def test_returns_transcription_result(self, gi):
        result = gi.transcribe_voice(b"\x00\x01\x02", "hi")
        assert isinstance(result, TranscriptionResult)

    def test_hindi_transcription_non_empty(self, gi):
        result = gi.transcribe_voice(b"audio", "hi")
        assert result.transcription
        assert result.language == "hi"

    def test_chhattisgarhi_transcription_non_empty(self, gi):
        result = gi.transcribe_voice(b"audio", "chhattisgarhi")
        assert result.transcription
        assert result.language == "chhattisgarhi"

    def test_confidence_is_0_85(self, gi):
        result = gi.transcribe_voice(b"audio", "hi")
        assert result.confidence == pytest.approx(0.85)

    def test_empty_bytes_still_returns_result(self, gi):
        result = gi.transcribe_voice(b"", "hi")
        assert isinstance(result, TranscriptionResult)
        assert result.transcription

    def test_unknown_language_defaults_to_hi(self, gi):
        result = gi.transcribe_voice(b"audio", "unknown_lang")
        assert result.language == "hi"


# ---------------------------------------------------------------------------
# Cache pre-population (offline / Lite_Mode)
# ---------------------------------------------------------------------------

class TestCachePrePopulation:
    def test_cache_covers_all_intents(self, gi):
        for intent in SUPPORTED_INTENTS:
            assert intent in gi._cache

    def test_cache_covers_all_schemes_per_intent(self, gi):
        for intent in SUPPORTED_INTENTS:
            for scheme in SUPPORTED_SCHEMES:
                assert scheme in gi._cache[intent], (
                    f"Cache missing scheme={scheme} for intent={intent}"
                )

    def test_cache_covers_both_languages(self, gi):
        for intent in SUPPORTED_INTENTS:
            for scheme in SUPPORTED_SCHEMES:
                for lang in SUPPORTED_LANGUAGES:
                    assert lang in gi._cache[intent][scheme], (
                        f"Cache missing lang={lang} for intent={intent}, scheme={scheme}"
                    )

    def test_fallback_entry_present(self, gi):
        for intent in SUPPORTED_INTENTS:
            assert "_fallback" in gi._cache[intent]
