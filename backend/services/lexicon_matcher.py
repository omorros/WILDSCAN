import re
from rapidfuzz import fuzz


class LexiconMatcher:
    def __init__(self, lexicon_entries: list[dict]):
        self.entries = lexicon_entries

    def match(self, text: str) -> list[dict]:
        text_lower = text.lower()
        results = []

        for entry in self.entries:
            if self._has_false_positive_context(text_lower, entry):
                continue

            if entry["code_word"].lower() in text_lower:
                if self._check_context_required(text_lower, entry):
                    results.append(self._make_result(entry, "exact", entry["confidence"]))
                    continue

            obfuscation_match = False
            for variant in entry.get("obfuscation_variants", []):
                if variant.lower() in text_lower:
                    if self._check_context_required(text_lower, entry):
                        results.append(self._make_result(entry, "obfuscation", entry["confidence"] * 0.95))
                        obfuscation_match = True
                        break
            if obfuscation_match:
                continue

            if len(entry["code_word"]) >= 4:
                fuzzy_result = self._fuzzy_match(text_lower, entry)
                if fuzzy_result:
                    results.append(fuzzy_result)

        return results

    def _has_false_positive_context(self, text: str, entry: dict) -> bool:
        for fp_context in entry.get("false_positive_contexts", []):
            if fp_context.lower() in text:
                return True
        return False

    def _check_context_required(self, text: str, entry: dict) -> bool:
        required = entry.get("context_required", [])
        if not required:
            return True
        return any(ctx.lower() in text for ctx in required)

    def _fuzzy_match(self, text: str, entry: dict) -> dict | None:
        code_word = entry["code_word"].lower()
        word_len = len(code_word)
        for i in range(len(text) - word_len + 1):
            window = text[i:i + word_len]
            ratio = fuzz.ratio(code_word, window)
            if ratio >= 80 and ratio < 100:
                if self._check_context_required(text, entry):
                    return self._make_result(entry, "fuzzy", entry["confidence"] * (ratio / 100))
        return None

    def _make_result(self, entry: dict, match_type: str, confidence: float) -> dict:
        return {
            "id": entry["id"],
            "code_word": entry["code_word"],
            "species_scientific": entry.get("species_scientific"),
            "product_type": entry.get("product_type"),
            "match_type": match_type,
            "confidence": round(confidence, 3),
        }
