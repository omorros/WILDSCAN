import pytest
from backend.services.lexicon_matcher import LexiconMatcher


@pytest.fixture
def lexicon_entries():
    return [
        {
            "id": 1,
            "code_word": "งาช้าง",
            "language": "th",
            "species_scientific": "Loxodonta africana",
            "product_type": "ivory_raw",
            "confidence": 0.95,
            "context_required": [],
            "false_positive_contexts": [],
            "obfuscation_variants": ["งา.ช้าง", "งาช-าง"],
        },
        {
            "id": 2,
            "code_word": "งา",
            "language": "th",
            "species_scientific": "Loxodonta africana",
            "product_type": "ivory_raw",
            "confidence": 0.60,
            "context_required": ["แกะสลัก", "แท้", "ช้าง", "เก่า", "โบราณ"],
            "false_positive_contexts": ["งาดำ", "เมล็ดงา", "น้ำมันงา"],
            "obfuscation_variants": [],
        },
        {
            "id": 3,
            "code_word": "white gold",
            "language": "en",
            "species_scientific": "Loxodonta africana",
            "product_type": "ivory_raw",
            "confidence": 0.70,
            "context_required": ["carving", "antique", "tusk", "old"],
            "false_positive_contexts": ["white gold ring", "white gold necklace", "jewelry", "karat", "18k", "14k"],
            "obfuscation_variants": ["wh1te gold", "whitegold"],
        },
        {
            "id": 4,
            "code_word": "bone carving",
            "language": "en",
            "species_scientific": "Loxodonta africana",
            "product_type": "ivory_carved",
            "confidence": 0.50,
            "context_required": ["antique", "Asian", "Chinese", "Japanese", "netsuke", "figure"],
            "false_positive_contexts": ["bone china", "dog bone", "dinosaur bone"],
            "obfuscation_variants": [],
        },
    ]


@pytest.fixture
def matcher(lexicon_entries):
    return LexiconMatcher(lexicon_entries)


class TestExactMatch:
    def test_exact_match_thai(self, matcher):
        text = "ขายงาช้างแกะสลัก สวยมาก ราคาถูก"
        results = matcher.match(text)
        assert len(results) >= 1
        match = next(r for r in results if r["code_word"] == "งาช้าง")
        assert match["match_type"] == "exact"
        assert match["confidence"] == 0.95

    def test_no_match(self, matcher):
        text = "selling a nice phone case, good condition"
        results = matcher.match(text)
        assert len(results) == 0


class TestFuzzyMatch:
    def test_fuzzy_levenshtein(self, matcher):
        text = "selling whlte gold antique carving"
        results = matcher.match(text)
        assert len(results) >= 1
        match = next(r for r in results if r["code_word"] == "white gold")
        assert match["match_type"] == "fuzzy"

    def test_obfuscation_variant(self, matcher):
        text = "งา.ช้าง แกะสลัก ราคาดี"
        results = matcher.match(text)
        assert len(results) >= 1
        match = next(r for r in results if r["code_word"] == "งาช้าง")
        assert match["match_type"] == "obfuscation"


class TestContextGuards:
    def test_context_required_present(self, matcher):
        text = "งา แท้ แกะสลัก ราคาดี"
        results = matcher.match(text)
        assert any(r["code_word"] == "งา" for r in results)

    def test_context_required_absent(self, matcher):
        text = "งา อร่อยมาก"
        results = matcher.match(text)
        assert not any(r["code_word"] == "งา" for r in results)

    def test_false_positive_context_blocks(self, matcher):
        text = "beautiful bone china teapot, antique Asian"
        results = matcher.match(text)
        assert not any(r["code_word"] == "bone carving" for r in results)

    def test_false_positive_context_absent_allows(self, matcher):
        text = "antique bone carving, Asian figure"
        results = matcher.match(text)
        assert any(r["code_word"] == "bone carving" for r in results)
