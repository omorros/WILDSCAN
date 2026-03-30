import json
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from backend.config import settings
from backend.services.lexicon_matcher import LexiconMatcher


openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)


async def analyze_text(listing: dict, lexicon_entries: list[dict]) -> dict:
    text = f"{listing.get('title', '')} {listing.get('description', '')}"
    matcher = LexiconMatcher(lexicon_entries)
    code_word_matches = matcher.match(text)
    translation = await _translate(text, listing.get("language", "th"))
    analysis_method = "deterministic"
    max_confidence = max((m["confidence"] for m in code_word_matches), default=0)

    if 0.3 < max_confidence < 0.7 or (not code_word_matches and listing.get("triage_reason") == "high_risk_category"):
        claude_result = await _claude_code_word_assessment(text, translation)
        if claude_result:
            analysis_method = "llm_assisted"
            for item in claude_result.get("identified_products", []):
                code_word_matches.append({
                    "code_word": item.get("product", ""),
                    "species_scientific": item.get("species", ""),
                    "product_type": item.get("product", ""),
                    "match_type": "llm_novel",
                    "confidence": item.get("confidence", 0.5),
                })

    linguistic_risk = max((m["confidence"] for m in code_word_matches), default=0.0)
    return {
        "translation": translation,
        "code_word_matches": code_word_matches,
        "linguistic_risk_score": linguistic_risk,
        "analysis_method": analysis_method,
    }


async def _translate(text: str, source_language: str) -> str:
    if not settings.openai_api_key:
        return text
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Translate this marketplace listing to English. Preserve any unusual terms, slang, or code-like language. Return only the translation."},
                {"role": "user", "content": text},
            ],
            temperature=0,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return text


async def _claude_code_word_assessment(original: str, translation: str) -> dict | None:
    if not settings.anthropic_api_key:
        return None
    try:
        response = await anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""You are a wildlife trade linguistic analyst. Given this marketplace listing (original + translation), assess whether it contains indicators of wildlife trafficking. Consider code words, euphemisms, and contextual signals. Be precise about confidence.

Original: {original}
Translation: {translation}

Return ONLY valid JSON:
{{
  "is_suspicious": bool,
  "confidence": float,
  "reasoning": "string",
  "identified_products": [{{"product": "string", "species": "string", "confidence": float}}],
  "novel_code_words": [{{"word": "string", "language": "string", "proposed_species": "string", "evidence": "string"}}]
}}""",
            }],
        )
        return json.loads(response.content[0].text)
    except Exception:
        return None
