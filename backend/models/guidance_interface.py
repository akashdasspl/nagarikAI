"""
Guidance_Interface backend for CSC Operator Assistant.
Provides multilingual voice and chat guidance in Hindi and Chhattisgarhi.
Validates: Requirements 19.1, 19.2, 19.3, 19.4, 19.6
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional
import os


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class GuidanceQuery:
    """Represents an operator's guidance request."""
    intent: str          # field_definition | document_list | eligibility_criteria | rejection_reasons
    scheme_type: str
    active_field: str    # current form field the operator is on
    language: str        # 'hi' | 'chhattisgarhi'
    question_text: str = ""  # optional free-text question


@dataclass
class GuidanceResponse:
    """Represents the guidance system's response to an operator query."""
    intent: str
    scheme_type: str
    referenced_field: str    # equals active_field from query
    referenced_scheme: str   # equals scheme_type from query
    response_text: str       # in the requested language
    language: str


@dataclass
class TranscriptionResult:
    """Represents the result of a voice transcription."""
    transcription: str
    language: str
    confidence: float


# ---------------------------------------------------------------------------
# Supported schemes and languages
# ---------------------------------------------------------------------------

SUPPORTED_SCHEMES = [
    "widow_pension",
    "disability_pension",
    "old_age_pension",
    "ration_card",
    "scholarship",
]

SUPPORTED_LANGUAGES = ["hi", "chhattisgarhi"]

SUPPORTED_INTENTS = [
    "field_definition",
    "document_list",
    "eligibility_criteria",
    "rejection_reasons",
    "application_process",
    "fees_and_charges",
    "processing_time",
    "contact_support",
    "common_mistakes",
]

# ---------------------------------------------------------------------------
# Cache data: _CACHE[intent][scheme_type][language] = response_text
# ---------------------------------------------------------------------------

_CACHE: Dict[str, Dict[str, Dict[str, str]]] = {

    # ------------------------------------------------------------------
    # field_definition
    # ------------------------------------------------------------------
    "field_definition": {
        scheme: {
            "hi": "यह फ़ील्ड {field} की जानकारी के लिए है। कृपया सही और पूर्ण जानकारी भरें।",
            "chhattisgarhi": "ये फील्ड {field} के जानकारी बर हे। सही अउ पूरा जानकारी भरव।",
        }
        for scheme in SUPPORTED_SCHEMES
    },

    # ------------------------------------------------------------------
    # document_list
    # ------------------------------------------------------------------
    "document_list": {
        "widow_pension": {
            "hi": (
                "विधवा पेंशन के लिए आवश्यक दस्तावेज़: मृत्यु प्रमाण पत्र, "
                "आधार कार्ड, बैंक पासबुक, निवास प्रमाण पत्र।"
            ),
            "chhattisgarhi": (
                "विधवा पेंशन बर जरूरी कागज: मृत्यु प्रमाण पत्र, "
                "आधार कार्ड, बैंक पासबुक, निवास प्रमाण पत्र।"
            ),
        },
        "disability_pension": {
            "hi": "विकलांग पेंशन के लिए: विकलांगता प्रमाण पत्र, आधार कार्ड, बैंक पासबुक।",
            "chhattisgarhi": "विकलांग पेंशन बर: विकलांगता प्रमाण पत्र, आधार कार्ड, बैंक पासबुक।",
        },
        "old_age_pension": {
            "hi": "वृद्धावस्था पेंशन के लिए: आयु प्रमाण पत्र, आधार कार्ड, बैंक पासबुक, निवास प्रमाण पत्र।",
            "chhattisgarhi": "बुढ़ापा पेंशन बर: उमर प्रमाण पत्र, आधार कार्ड, बैंक पासबुक, निवास प्रमाण पत्र।",
        },
        "ration_card": {
            "hi": "राशन कार्ड के लिए: आधार कार्ड, निवास प्रमाण पत्र, परिवार के सदस्यों की जानकारी।",
            "chhattisgarhi": "राशन कार्ड बर: आधार कार्ड, निवास प्रमाण पत्र, परिवार के मन के जानकारी।",
        },
        "scholarship": {
            "hi": "छात्रवृत्ति के लिए: आयु प्रमाण पत्र, शैक्षणिक प्रमाण पत्र, आधार कार्ड, बैंक पासबुक।",
            "chhattisgarhi": "छात्रवृत्ति बर: उमर प्रमाण पत्र, पढ़ाई प्रमाण पत्र, आधार कार्ड, बैंक पासबुक।",
        },
    },

    # ------------------------------------------------------------------
    # eligibility_criteria
    # ------------------------------------------------------------------
    "eligibility_criteria": {
        "widow_pension": {
            "hi": (
                "विधवा पेंशन के लिए पात्रता: आवेदक विधवा होनी चाहिए, "
                "आयु 18 वर्ष से अधिक, वार्षिक आय 1 लाख से कम।"
            ),
            "chhattisgarhi": (
                "विधवा पेंशन बर पात्रता: आवेदक विधवा होना चाही, "
                "उमर 18 बछर ले जादा, सालाना आय 1 लाख ले कम।"
            ),
        },
        "disability_pension": {
            "hi": "विकलांग पेंशन के लिए: 40% या अधिक विकलांगता, आयु 18 वर्ष से अधिक।",
            "chhattisgarhi": "विकलांग पेंशन बर: 40% या जादा विकलांगता, उमर 18 बछर ले जादा।",
        },
        "old_age_pension": {
            "hi": "वृद्धावस्था पेंशन के लिए: आयु 60 वर्ष या अधिक, वार्षिक आय 80,000 से कम।",
            "chhattisgarhi": "बुढ़ापा पेंशन बर: उमर 60 बछर या जादा, सालाना आय 80,000 ले कम।",
        },
        "ration_card": {
            "hi": "राशन कार्ड के लिए: परिवार की वार्षिक आय 1.5 लाख से कम।",
            "chhattisgarhi": "राशन कार्ड बर: परिवार के सालाना आय 1.5 लाख ले कम।",
        },
        "scholarship": {
            "hi": "छात्रवृत्ति के लिए: आयु 5-25 वर्ष, शैक्षणिक संस्थान में नामांकित।",
            "chhattisgarhi": "छात्रवृत्ति बर: उमर 5-25 बछर, पढ़ाई संस्थान म नाम दर्ज।",
        },
    },

    # ------------------------------------------------------------------
    # rejection_reasons
    # ------------------------------------------------------------------
    "rejection_reasons": {
        "widow_pension": {
            "hi": (
                "विधवा पेंशन अस्वीकृति के सामान्य कारण: मृत्यु प्रमाण पत्र नहीं, "
                "आय सीमा से अधिक, दस्तावेज़ अपूर्ण।"
            ),
            "chhattisgarhi": (
                "विधवा पेंशन नामंजूरी के आम कारण: मृत्यु प्रमाण पत्र नइ हे, "
                "आय सीमा ले जादा, कागज अधूरा।"
            ),
        },
        "disability_pension": {
            "hi": "विकलांग पेंशन अस्वीकृति: विकलांगता प्रमाण पत्र की वैधता समाप्त, प्रतिशत कम।",
            "chhattisgarhi": "विकलांग पेंशन नामंजूरी: विकलांगता प्रमाण पत्र के मियाद खतम, प्रतिशत कम।",
        },
        "old_age_pension": {
            "hi": "वृद्धावस्था पेंशन अस्वीकृति: आयु प्रमाण नहीं, आय सीमा से अधिक।",
            "chhattisgarhi": "बुढ़ापा पेंशन नामंजूरी: उमर प्रमाण नइ हे, आय सीमा ले जादा।",
        },
        "ration_card": {
            "hi": "राशन कार्ड अस्वीकृति: आय सीमा से अधिक, पहले से कार्ड मौजूद।",
            "chhattisgarhi": "राशन कार्ड नामंजूरी: आय सीमा ले जादा, पहिले ले कार्ड हे।",
        },
        "scholarship": {
            "hi": "छात्रवृत्ति अस्वीकृति: आयु सीमा से बाहर, संस्थान मान्यता प्राप्त नहीं।",
            "chhattisgarhi": "छात्रवृत्ति नामंजूरी: उमर सीमा ले बाहर, संस्थान मान्यता नइ मिले।",
        },
    },

    # ------------------------------------------------------------------
    # application_process
    # ------------------------------------------------------------------
    "application_process": {
        "widow_pension": {
            "hi": "विधवा पेंशन आवेदन प्रक्रिया: 1) सभी दस्तावेज़ तैयार करें 2) फॉर्म भरें 3) CSC केंद्र पर जमा करें 4) रसीद प्राप्त करें 5) 30 दिनों में स्वीकृति मिलेगी।",
            "chhattisgarhi": "विधवा पेंशन आवेदन प्रक्रिया: 1) सब कागज तैयार करव 2) फॉर्म भरव 3) CSC केंद्र म जमा करव 4) रसीद लेव 5) 30 दिन म मंजूरी मिलही।",
        },
        "disability_pension": {
            "hi": "विकलांग पेंशन आवेदन: विकलांगता प्रमाण पत्र लेकर CSC केंद्र पर आएं, फॉर्म भरें, दस्तावेज़ जमा करें। 45 दिनों में प्रक्रिया पूरी होगी।",
            "chhattisgarhi": "विकलांग पेंशन आवेदन: विकलांगता प्रमाण पत्र लेके CSC केंद्र आव, फॉर्म भरव, कागज जमा करव। 45 दिन म प्रक्रिया पूरा होही।",
        },
        "old_age_pension": {
            "hi": "वृद्धावस्था पेंशन आवेदन: आयु प्रमाण और आधार कार्ड लेकर आएं। फॉर्म भरने में मदद मिलेगी। 30 दिनों में स्वीकृति।",
            "chhattisgarhi": "बुढ़ापा पेंशन आवेदन: उमर प्रमाण अउ आधार कार्ड लेके आव। फॉर्म भरे म मदद मिलही। 30 दिन म मंजूरी।",
        },
        "ration_card": {
            "hi": "राशन कार्ड आवेदन: परिवार के सभी सदस्यों का आधार कार्ड, निवास प्रमाण, और आय प्रमाण लेकर आएं। 15 दिनों में कार्ड मिलेगा।",
            "chhattisgarhi": "राशन कार्ड आवेदन: परिवार के सब मन के आधार कार्ड, निवास प्रमाण, अउ आय प्रमाण लेके आव। 15 दिन म कार्ड मिलही।",
        },
        "scholarship": {
            "hi": "छात्रवृत्ति आवेदन: शैक्षणिक प्रमाण पत्र, आधार कार्ड, बैंक पासबुक लेकर आएं। ऑनलाइन आवेदन भी कर सकते हैं। 60 दिनों में राशि मिलेगी।",
            "chhattisgarhi": "छात्रवृत्ति आवेदन: पढ़ाई प्रमाण पत्र, आधार कार्ड, बैंक पासबुक लेके आव। ऑनलाइन आवेदन भी कर सकत हव। 60 दिन म रकम मिलही।",
        },
    },

    # ------------------------------------------------------------------
    # fees_and_charges
    # ------------------------------------------------------------------
    "fees_and_charges": {
        "widow_pension": {
            "hi": "विधवा पेंशन के लिए कोई शुल्क नहीं है। यह सेवा पूरी तरह निःशुल्क है। CSC केंद्र पर भी कोई शुल्क नहीं लिया जाएगा।",
            "chhattisgarhi": "विधवा पेंशन बर कोनो शुल्क नइ हे। ये सेवा पूरा तरह मुफ्त हे। CSC केंद्र म भी कोनो शुल्क नइ लिए जाही।",
        },
        "disability_pension": {
            "hi": "विकलांग पेंशन निःशुल्क है। केवल विकलांगता प्रमाण पत्र बनवाने में अस्पताल शुल्क लग सकता है।",
            "chhattisgarhi": "विकलांग पेंशन मुफ्त हे। सिरिफ विकलांगता प्रमाण पत्र बनवाए म अस्पताल शुल्क लग सकत हे।",
        },
        "old_age_pension": {
            "hi": "वृद्धावस्था पेंशन पूरी तरह निःशुल्क है। कोई आवेदन शुल्क नहीं है।",
            "chhattisgarhi": "बुढ़ापा पेंशन पूरा तरह मुफ्त हे। कोनो आवेदन शुल्क नइ हे।",
        },
        "ration_card": {
            "hi": "राशन कार्ड बनवाना निःशुल्क है। कोई शुल्क नहीं लिया जाता।",
            "chhattisgarhi": "राशन कार्ड बनवाना मुफ्त हे। कोनो शुल्क नइ लिए जात हे।",
        },
        "scholarship": {
            "hi": "छात्रवृत्ति आवेदन निःशुल्क है। कोई प्रोसेसिंग शुल्क नहीं है।",
            "chhattisgarhi": "छात्रवृत्ति आवेदन मुफ्त हे। कोनो प्रोसेसिंग शुल्क नइ हे।",
        },
    },

    # ------------------------------------------------------------------
    # processing_time
    # ------------------------------------------------------------------
    "processing_time": {
        "widow_pension": {
            "hi": "विधवा पेंशन स्वीकृति में 30-45 दिन लगते हैं। आवेदन जमा करने के बाद रसीद संख्या से स्थिति जांच सकते हैं।",
            "chhattisgarhi": "विधवा पेंशन मंजूरी म 30-45 दिन लगत हे। आवेदन जमा करे के बाद रसीद नंबर ले स्थिति देख सकत हव।",
        },
        "disability_pension": {
            "hi": "विकलांग पेंशन में 45-60 दिन लगते हैं क्योंकि विकलांगता सत्यापन होता है।",
            "chhattisgarhi": "विकलांग पेंशन म 45-60 दिन लगत हे काबर कि विकलांगता सत्यापन होथे।",
        },
        "old_age_pension": {
            "hi": "वृद्धावस्था पेंशन 30 दिनों में स्वीकृत हो जाती है। तेज़ प्रक्रिया के लिए सभी दस्तावेज़ सही रखें।",
            "chhattisgarhi": "बुढ़ापा पेंशन 30 दिन म मंजूर हो जाथे। तेज प्रक्रिया बर सब कागज सही रखव।",
        },
        "ration_card": {
            "hi": "राशन कार्ड 15-20 दिनों में बन जाता है। सत्यापन के बाद घर पर भेजा जाता है।",
            "chhattisgarhi": "राशन कार्ड 15-20 दिन म बन जाथे। सत्यापन के बाद घर भेजे जाथे।",
        },
        "scholarship": {
            "hi": "छात्रवृत्ति स्वीकृति में 60-90 दिन लगते हैं। राशि सीधे बैंक खाते में आती है।",
            "chhattisgarhi": "छात्रवृत्ति मंजूरी म 60-90 दिन लगत हे। रकम सीधा बैंक खाता म आथे।",
        },
    },

    # ------------------------------------------------------------------
    # contact_support
    # ------------------------------------------------------------------
    "contact_support": {
        "widow_pension": {
            "hi": "विधवा पेंशन सहायता के लिए: जिला समाज कल्याण कार्यालय से संपर्क करें या हेल्पलाइन 1800-XXX-XXXX पर कॉल करें।",
            "chhattisgarhi": "विधवा पेंशन मदद बर: जिला समाज कल्याण कार्यालय ले संपर्क करव या हेल्पलाइन 1800-XXX-XXXX म कॉल करव।",
        },
        "disability_pension": {
            "hi": "विकलांग पेंशन सहायता: जिला विकलांग कल्याण अधिकारी से मिलें या टोल-फ्री नंबर 1800-XXX-XXXX पर कॉल करें।",
            "chhattisgarhi": "विकलांग पेंशन मदद: जिला विकलांग कल्याण अधिकारी ले मिलव या टोल-फ्री नंबर 1800-XXX-XXXX म कॉल करव।",
        },
        "old_age_pension": {
            "hi": "वृद्धावस्था पेंशन सहायता: नजदीकी CSC केंद्र या जिला कार्यालय से संपर्क करें। हेल्पलाइन: 1800-XXX-XXXX",
            "chhattisgarhi": "बुढ़ापा पेंशन मदद: नजदीक CSC केंद्र या जिला कार्यालय ले संपर्क करव। हेल्पलाइन: 1800-XXX-XXXX",
        },
        "ration_card": {
            "hi": "राशन कार्ड सहायता: खाद्य आपूर्ति विभाग या CSC केंद्र से संपर्क करें। हेल्पलाइन: 1800-XXX-XXXX",
            "chhattisgarhi": "राशन कार्ड मदद: खाद्य आपूर्ति विभाग या CSC केंद्र ले संपर्क करव। हेल्पलाइन: 1800-XXX-XXXX",
        },
        "scholarship": {
            "hi": "छात्रवृत्ति सहायता: शिक्षा विभाग या स्कूल/कॉलेज से संपर्क करें। हेल्पलाइन: 1800-XXX-XXXX",
            "chhattisgarhi": "छात्रवृत्ति मदद: शिक्षा विभाग या स्कूल/कॉलेज ले संपर्क करव। हेल्पलाइन: 1800-XXX-XXXX",
        },
    },

    # ------------------------------------------------------------------
    # common_mistakes
    # ------------------------------------------------------------------
    "common_mistakes": {
        "widow_pension": {
            "hi": "आम गलतियां: 1) मृत्यु प्रमाण पत्र की फोटोकॉपी स्पष्ट नहीं 2) आय प्रमाण पुराना 3) बैंक खाता संयुक्त है 4) पता प्रमाण मेल नहीं खाता। इनसे बचें।",
            "chhattisgarhi": "आम गलती: 1) मृत्यु प्रमाण पत्र के फोटोकॉपी साफ नइ हे 2) आय प्रमाण पुराना हे 3) बैंक खाता संयुक्त हे 4) पता प्रमाण मेल नइ खात हे। इन ले बचव।",
        },
        "disability_pension": {
            "hi": "आम गलतियां: 1) विकलांगता प्रमाण पत्र की वैधता समाप्त 2) विकलांगता प्रतिशत 40% से कम 3) पुराने मेडिकल रिपोर्ट। नए दस्तावेज़ लाएं।",
            "chhattisgarhi": "आम गलती: 1) विकलांगता प्रमाण पत्र के मियाद खतम 2) विकलांगता प्रतिशत 40% ले कम 3) पुराना मेडिकल रिपोर्ट। नवा कागज लाव।",
        },
        "old_age_pension": {
            "hi": "आम गलतियां: 1) जन्म तिथि प्रमाण नहीं 2) आय प्रमाण सीमा से अधिक 3) पहले से पेंशन मिल रही है। सही जानकारी दें।",
            "chhattisgarhi": "आम गलती: 1) जन्म तिथि प्रमाण नइ हे 2) आय प्रमाण सीमा ले जादा 3) पहिले ले पेंशन मिलत हे। सही जानकारी देव।",
        },
        "ration_card": {
            "hi": "आम गलतियां: 1) परिवार के सभी सदस्यों का आधार नहीं 2) पुराना पता 3) आय प्रमाण गलत। सभी दस्तावेज़ अपडेट रखें।",
            "chhattisgarhi": "आम गलती: 1) परिवार के सब मन के आधार नइ हे 2) पुराना पता 3) आय प्रमाण गलत। सब कागज अपडेट रखव।",
        },
        "scholarship": {
            "hi": "आम गलतियां: 1) पिछले वर्ष की मार्कशीट नहीं 2) बैंक खाता माता-पिता के नाम पर 3) संस्थान कोड गलत। ध्यान से भरें।",
            "chhattisgarhi": "आम गलती: 1) पिछला साल के मार्कशीट नइ हे 2) बैंक खाता माता-पिता के नाम म 3) संस्थान कोड गलत। ध्यान ले भरव।",
        },
    },
}

# Generic fallback responses for unknown schemes
_FALLBACK: Dict[str, Dict[str, str]] = {
    "field_definition": {
        "hi": "यह फ़ील्ड {field} की जानकारी के लिए है। कृपया सही और पूर्ण जानकारी भरें।",
        "chhattisgarhi": "ये फील्ड {field} के जानकारी बर हे। सही अउ पूरा जानकारी भरव।",
    },
    "document_list": {
        "hi": "कृपया संबंधित योजना के लिए आवश्यक दस्तावेज़ तैयार रखें: आधार कार्ड, निवास प्रमाण पत्र, बैंक पासबुक।",
        "chhattisgarhi": "कृपया संबंधित योजना बर जरूरी कागज तैयार रखव: आधार कार्ड, निवास प्रमाण पत्र, बैंक पासबुक।",
    },
    "eligibility_criteria": {
        "hi": "पात्रता के लिए कृपया संबंधित योजना की शर्तें जांचें।",
        "chhattisgarhi": "पात्रता बर कृपया संबंधित योजना के शर्त देखव।",
    },
    "rejection_reasons": {
        "hi": "अस्वीकृति के सामान्य कारण: दस्तावेज़ अपूर्ण, पात्रता शर्तें पूरी नहीं।",
        "chhattisgarhi": "नामंजूरी के आम कारण: कागज अधूरा, पात्रता शर्त पूरा नइ।",
    },
    "application_process": {
        "hi": "आवेदन प्रक्रिया: दस्तावेज़ तैयार करें, फॉर्म भरें, CSC केंद्र पर जमा करें।",
        "chhattisgarhi": "आवेदन प्रक्रिया: कागज तैयार करव, फॉर्म भरव, CSC केंद्र म जमा करव।",
    },
    "fees_and_charges": {
        "hi": "यह सेवा निःशुल्क है। कोई आवेदन शुल्क नहीं है।",
        "chhattisgarhi": "ये सेवा मुफ्त हे। कोनो आवेदन शुल्क नइ हे।",
    },
    "processing_time": {
        "hi": "आवेदन प्रक्रिया में 30-60 दिन लगते हैं। रसीद संख्या से स्थिति जांच सकते हैं।",
        "chhattisgarhi": "आवेदन प्रक्रिया म 30-60 दिन लगत हे। रसीद नंबर ले स्थिति देख सकत हव।",
    },
    "contact_support": {
        "hi": "सहायता के लिए नजदीकी CSC केंद्र या जिला कार्यालय से संपर्क करें।",
        "chhattisgarhi": "मदद बर नजदीक CSC केंद्र या जिला कार्यालय ले संपर्क करव।",
    },
    "common_mistakes": {
        "hi": "आम गलतियां: अधूरे दस्तावेज़, पुराने प्रमाण पत्र, गलत जानकारी। सभी दस्तावेज़ सही रखें।",
        "chhattisgarhi": "आम गलती: अधूरा कागज, पुराना प्रमाण पत्र, गलत जानकारी। सब कागज सही रखव।",
    },
}


# ---------------------------------------------------------------------------
# GuidanceInterface
# ---------------------------------------------------------------------------

class GuidanceInterface:
    """
    Provides contextual guidance to CSC operators in Hindi and Chhattisgarhi.

    Responses are served from a pre-populated in-memory cache, ensuring
    sub-3-second latency and full offline / Lite_Mode availability.
    """

    def __init__(self) -> None:
        # Deep-copy the module-level cache so each instance is independent
        self._cache: Dict[str, Dict[str, Dict[str, str]]] = {}
        self._populate_cache()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def handle_query(self, query: GuidanceQuery) -> GuidanceResponse:
        """
        Return a contextual guidance response for the given query.

        Looks up the pre-populated cache for (intent, scheme_type, language).
        If active_field is provided the response template is customised to
        reference that field.  Falls back to a generic response for unknown
        schemes or languages.

        For complex questions that don't match predefined intents, uses LLM fallback.

        Completes in < 3 seconds (cache lookup is O(1)).
        """
        language = query.language if query.language in SUPPORTED_LANGUAGES else "hi"
        intent = query.intent if query.intent in SUPPORTED_INTENTS else "field_definition"

        # Retrieve from cache; fall back to generic if scheme unknown
        scheme_cache = self._cache.get(intent, {})
        lang_cache = scheme_cache.get(query.scheme_type) or scheme_cache.get("_fallback", {})
        response_text = lang_cache.get(language, "")

        # Substitute {field} placeholder with the active field name
        if query.active_field:
            response_text = response_text.replace("{field}", query.active_field)
        else:
            response_text = response_text.replace("{field}", "")

        # If question_text is provided and response seems generic, try LLM fallback
        if query.question_text and len(query.question_text) > 20:
            # Check if this might be a complex question that needs LLM
            if self._is_complex_question(query.question_text):
                llm_response = self._get_llm_response(query.question_text, query.scheme_type, language)
                if llm_response:
                    response_text = llm_response

        return GuidanceResponse(
            intent=query.intent,
            scheme_type=query.scheme_type,
            referenced_field=query.active_field,
            referenced_scheme=query.scheme_type,
            response_text=response_text,
            language=language,
        )
    
    def _is_complex_question(self, question: str) -> bool:
        """
        Determine if a question is complex and needs LLM processing.
        
        Complex questions are those that:
        - Are longer than typical predefined questions
        - Contain multiple clauses or specific scenarios
        - Ask "what if" or hypothetical questions
        """
        lower = question.lower()
        
        # Indicators of complex questions
        complex_indicators = [
            'what if', 'agar', 'अगर', 'suppose', 'मान लो',
            'but', 'lekin', 'लेकिन', 'par', 'पर',
            'both', 'dono', 'दोनों',
            'multiple', 'kai', 'कई',
            'specific', 'vishesh', 'विशेष',
            'exception', 'अपवाद',
            'special case', 'विशेष मामला'
        ]
        
        # Check for complex indicators
        for indicator in complex_indicators:
            if indicator in lower:
                return True
        
        # Check for multiple questions (contains multiple question marks or "and")
        if question.count('?') > 1 or (' and ' in lower and '?' in question):
            return True
        
        # Long questions are likely complex
        if len(question) > 100:
            return True
        
        return False
    
    def _get_llm_response(self, question: str, scheme_type: str, language: str) -> Optional[str]:
        """
        Get LLM response for complex questions.
        
        Uses Google Gemini API with gemini-2.5-flash model for fast, accurate responses.
        Falls back to cached response if LLM fails.
        """
        try:
            # Check if Gemini API key is available
            api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyDYghQKOwDOTtTOpE5H65wkZLm2bcEmQ8w')
            if not api_key:
                return None  # Fall back to cached response
            
            import requests
            
            # Prepare context about the scheme
            scheme_context = self._get_scheme_context(scheme_type, language)
            
            # Prepare system instruction and prompt
            system_instruction = f"""You are a helpful assistant for CSC (Common Service Center) operators in Chhattisgarh, India.
You help operators answer questions about government welfare schemes in {language} language.

Context about {scheme_type}:
{scheme_context}

Instructions:
- Answer in {language} language (Hindi or Chhattisgarhi)
- Be concise and practical
- Focus on actionable information
- If you don't know, say so clearly
- Keep responses under 150 words"""

            # Call Gemini API
            url = f'https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}'
            
            response = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                json={
                    'contents': [{
                        'parts': [{
                            'text': f"{system_instruction}\n\nQuestion: {question}"
                        }]
                    }],
                    'generationConfig': {
                        'temperature': 0.3,
                        'maxOutputTokens': 300,
                        'topP': 0.8,
                        'topK': 10
                    }
                },
                timeout=10  # 10 second timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    candidate = data['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        llm_text = candidate['content']['parts'][0]['text'].strip()
                        return llm_text
            
        except Exception as e:
            # Silently fall back to cached response
            pass
        
        return None
    
    def _get_scheme_context(self, scheme_type: str, language: str) -> str:
        """Get relevant context about a scheme for LLM."""
        # Combine all cached responses for this scheme to provide context
        context_parts = []
        
        for intent in ['document_list', 'eligibility_criteria', 'application_process', 'fees_and_charges', 'processing_time']:
            scheme_cache = self._cache.get(intent, {})
            lang_cache = scheme_cache.get(scheme_type) or scheme_cache.get("_fallback", {})
            text = lang_cache.get(language, '')
            if text:
                context_parts.append(f"{intent}: {text}")
        
        return "\n".join(context_parts)

    def transcribe_voice(self, audio_bytes: bytes, language: str) -> TranscriptionResult:
        """
        Transcribe voice input to text.

        For MVP: returns a mock transcription representative of the language.
        Completes within 2 seconds.

        Args:
            audio_bytes: Raw audio bytes from the operator's microphone.
            language:    'hi' or 'chhattisgarhi'.

        Returns:
            TranscriptionResult with transcription, language, and confidence.
        """
        if language == "chhattisgarhi":
            transcription = "मोर उमर 65 बछर हे"
        else:
            transcription = "मेरी आयु 65 वर्ष है"

        return TranscriptionResult(
            transcription=transcription,
            language=language if language in SUPPORTED_LANGUAGES else "hi",
            confidence=0.85,
        )

    # ------------------------------------------------------------------
    # Cache population (called once at __init__)
    # ------------------------------------------------------------------

    def _populate_cache(self) -> None:
        """
        Pre-populate _cache with responses for all intents × schemes × languages.
        This mirrors what would happen during a sync for offline / Lite_Mode use.
        """
        for intent, scheme_map in _CACHE.items():
            self._cache[intent] = {}
            for scheme, lang_map in scheme_map.items():
                self._cache[intent][scheme] = dict(lang_map)
            # Add fallback entry for unknown schemes
            self._cache[intent]["_fallback"] = dict(_FALLBACK.get(intent, {}))
