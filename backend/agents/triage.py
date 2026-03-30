HIGH_RISK_CATEGORIES = {
    "antiques", "collectibles", "traditional medicine", "pets",
    "exotic animals", "health", "art", "handicrafts", "jewelry",
    "medicine", "animals", "garden", "hobbies",
}

LOW_RISK_CATEGORIES = {
    "electronics", "vehicles", "clothing", "real estate", "jobs",
    "services", "automotive", "phones", "computers", "furniture",
    "appliances", "sports",
}


def triage_listing(listing: dict, lexicon_entries: list[dict]) -> dict:
    text = f"{listing.get('title', '')} {listing.get('description', '')}".lower()

    matched_words = []
    for entry in lexicon_entries:
        code_word = entry["code_word"].lower()
        if code_word in text:
            matched_words.append(entry["code_word"])

    if matched_words:
        return {
            "passed": True,
            "reason": "code_word_match",
            "fast_match_code_words": matched_words,
        }

    category = (listing.get("platform_category") or "").lower().strip()

    if not category:
        return {"passed": True, "reason": "high_risk_category", "fast_match_code_words": []}

    is_high_risk = any(cat in category for cat in HIGH_RISK_CATEGORIES)
    is_low_risk = any(cat in category for cat in LOW_RISK_CATEGORIES)

    if is_high_risk:
        return {"passed": True, "reason": "high_risk_category", "fast_match_code_words": []}

    if is_low_risk:
        return {"passed": False, "reason": "triaged_out", "fast_match_code_words": []}

    return {"passed": True, "reason": "high_risk_category", "fast_match_code_words": []}
