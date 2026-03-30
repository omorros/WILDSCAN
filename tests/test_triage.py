import pytest
from backend.agents.triage import triage_listing


LEXICON_ENTRIES = [
    {"code_word": "งาช้าง", "language": "th", "confidence": 0.95, "context_required": [], "false_positive_contexts": [], "obfuscation_variants": []},
    {"code_word": "ivory", "language": "en", "confidence": 0.90, "context_required": [], "false_positive_contexts": [], "obfuscation_variants": []},
]


class TestTriageCodeWordMatch:
    def test_passes_on_code_word_match(self):
        listing = {
            "title": "ขายงาช้างแกะสลัก",
            "description": "สวยมาก ราคาถูก",
            "platform_category": "electronics",
            "seller_listing_count": 500,
            "seller_join_date": "2020-01-01",
        }
        result = triage_listing(listing, LEXICON_ENTRIES)
        assert result["passed"] is True
        assert result["reason"] == "code_word_match"
        assert "งาช้าง" in result["fast_match_code_words"]


class TestTriageCategoryFilter:
    def test_passes_high_risk_category(self):
        listing = {
            "title": "beautiful old artifact",
            "description": "from my collection",
            "platform_category": "antiques",
            "seller_listing_count": 5,
            "seller_join_date": "2026-03-01",
        }
        result = triage_listing(listing, LEXICON_ENTRIES)
        assert result["passed"] is True
        assert result["reason"] == "high_risk_category"

    def test_triaged_out_low_risk_category(self):
        listing = {
            "title": "iPhone 15 Pro Max",
            "description": "brand new sealed",
            "platform_category": "electronics",
            "seller_listing_count": 50,
            "seller_join_date": "2023-01-01",
        }
        result = triage_listing(listing, LEXICON_ENTRIES)
        assert result["passed"] is False
        assert result["reason"] == "triaged_out"


class TestTriageEdgeCases:
    def test_no_category_defaults_to_pass(self):
        listing = {
            "title": "mystery item",
            "description": "",
            "platform_category": None,
            "seller_listing_count": None,
            "seller_join_date": None,
        }
        result = triage_listing(listing, LEXICON_ENTRIES)
        assert result["passed"] is True
