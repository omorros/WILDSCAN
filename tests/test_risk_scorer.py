import pytest
from backend.agents.risk_scorer import score_listing


class TestSignalScoring:
    def test_max_score_red_alert(self):
        signals = {
            "code_word_confidence": "exact",
            "cites_appendix": "I",
            "iucn_status": "EN",
            "seizure_correlation": "high",
            "geographic_risk": "high",
            "seller_behavior": "multiple_wildlife",
            "price_signal": "within_range",
            "image_evidence": "high",
            "text_image_agreement": True,
        }
        result = score_listing(signals)
        assert result["risk_score"] >= 80
        assert result["alert_tier"] == "red"

    def test_zero_score_clear(self):
        signals = {
            "code_word_confidence": "none",
            "cites_appendix": None,
            "iucn_status": "LC",
            "seizure_correlation": "none",
            "geographic_risk": "low",
            "seller_behavior": "established",
            "price_signal": "unknown",
            "image_evidence": "none",
            "text_image_agreement": False,
        }
        result = score_listing(signals)
        assert result["risk_score"] < 40
        assert result["alert_tier"] == "clear"

    def test_amber_tier(self):
        signals = {
            "code_word_confidence": "fuzzy",
            "cites_appendix": "II",
            "iucn_status": "VU",
            "seizure_correlation": "medium",
            "geographic_risk": "medium",
            "seller_behavior": "new_account",
            "price_signal": "anomalous",
            "image_evidence": "medium",
            "text_image_agreement": False,
        }
        result = score_listing(signals)
        assert 60 <= result["risk_score"] < 80
        assert result["alert_tier"] == "amber"


class TestSignalBreakdown:
    def test_breakdown_has_all_signals(self):
        signals = {
            "code_word_confidence": "exact",
            "cites_appendix": "I",
            "iucn_status": "CR",
            "seizure_correlation": "high",
            "geographic_risk": "high",
            "seller_behavior": "multiple_wildlife",
            "price_signal": "within_range",
            "image_evidence": "high",
            "text_image_agreement": True,
        }
        result = score_listing(signals)
        breakdown = result["signal_breakdown"]
        assert "code_word" in breakdown
        assert "cites" in breakdown
        assert "iucn" in breakdown
        assert "seizure" in breakdown
        assert "geographic" in breakdown
        assert "seller" in breakdown
        assert "price" in breakdown
        assert "image" in breakdown
        for key, val in breakdown.items():
            assert "score" in val
            assert "max" in val


class TestHardOverrides:
    def test_trade_suspension_forces_min_80(self):
        signals = {
            "code_word_confidence": "none",
            "cites_appendix": "I",
            "iucn_status": "LC",
            "seizure_correlation": "none",
            "geographic_risk": "low",
            "seller_behavior": "established",
            "price_signal": "unknown",
            "image_evidence": "none",
            "text_image_agreement": False,
            "trade_suspension_active": True,
        }
        result = score_listing(signals)
        assert result["risk_score"] >= 80
        assert result["hard_override_applied"] is True

    def test_appendix_i_source_country_image_forces_min_65(self):
        signals = {
            "code_word_confidence": "none",
            "cites_appendix": "I",
            "iucn_status": "LC",
            "seizure_correlation": "none",
            "geographic_risk": "high",
            "seller_behavior": "established",
            "price_signal": "unknown",
            "image_evidence": "high",
            "text_image_agreement": False,
        }
        result = score_listing(signals)
        assert result["risk_score"] >= 65


class TestAgreementBonus:
    def test_agreement_bonus_applied(self):
        signals = {
            "code_word_confidence": "exact",
            "cites_appendix": "I",
            "iucn_status": "EN",
            "seizure_correlation": "none",
            "geographic_risk": "low",
            "seller_behavior": "established",
            "price_signal": "unknown",
            "image_evidence": "high",
            "text_image_agreement": True,
        }
        result = score_listing(signals)
        assert result["agreement_bonus"] == 5

    def test_no_agreement_bonus_without_both(self):
        signals = {
            "code_word_confidence": "exact",
            "cites_appendix": "I",
            "iucn_status": "EN",
            "seizure_correlation": "none",
            "geographic_risk": "low",
            "seller_behavior": "established",
            "price_signal": "unknown",
            "image_evidence": "none",
            "text_image_agreement": False,
        }
        result = score_listing(signals)
        assert result["agreement_bonus"] == 0
