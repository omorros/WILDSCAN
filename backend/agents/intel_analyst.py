import json
from anthropic import AsyncAnthropic

from backend.config import settings


anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)

SYSTEM_PROMPT = """You are a wildlife trafficking intelligence analyst working for an international enforcement coordination center. You receive structured detection data from automated monitoring systems.

Rules:
- Cite specific signal scores and evidence
- Distinguish high-confidence findings from inferences
- Recommend concrete next steps with relevant jurisdictions
- Reference applicable laws (CITES, national wildlife protection acts)
- Always note alternative explanations
- Be precise about confidence levels"""


def _safe_json(obj) -> str:
    """Serialize to JSON, handling UUID/date/memoryview types."""
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception:
        return "{}"


async def generate_brief(detection: dict) -> dict:
    if not settings.anthropic_api_key:
        return _fallback_brief(detection)

    user_content = f"""Analyze this wildlife trafficking detection and generate a structured intelligence brief.

Detection Data:
- Platform: {detection.get('platform', 'unknown')}
- Title (original): {detection.get('title_original', '')}
- Title (translated): {detection.get('title_translated', '')}
- Location: {detection.get('location_text', 'unknown')}
- Risk Score: {detection.get('risk_score', 0)}/100
- Alert Tier: {detection.get('alert_tier', 'unknown')}
- Signal Breakdown: {_safe_json(detection.get('signal_breakdown', {}))}
- Species Matches: {_safe_json(detection.get('species_matches', []))}
- Code Word Matches: {_safe_json(detection.get('code_word_matches', []))}
- Geographic Risk: {_safe_json(detection.get('geographic_risk', {}))}
- Seizure Correlations: {_safe_json(detection.get('seizure_correlations', []))}
- Image Analysis: {_safe_json(detection.get('image_classification', {}))}

Return ONLY valid JSON with these fields, no other text:
{{
  "executive_summary": "2-3 sentence summary",
  "risk_assessment": "detailed risk assessment paragraph",
  "key_evidence": [{{"evidence_type": "string", "description": "string", "confidence": "high/medium/low", "source": "string"}}],
  "species_profile": "conservation context paragraph",
  "legal_framework": [{{"jurisdiction": "string", "applicable_law": "string", "offense_classification": "string"}}],
  "recommended_actions": ["action 1", "action 2"],
  "confidence_statement": "overall confidence assessment",
  "alternative_explanations": ["explanation 1"]
}}"""

    try:
        response = await anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
        text = response.content[0].text.strip()
        # Handle case where Claude wraps JSON in markdown code block
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)
    except Exception as e:
        print(f"[intel_analyst] Brief generation failed: {type(e).__name__}: {e}")
        return _fallback_brief(detection)


async def stream_chat(detection: dict, chat_history: list[dict], question: str):
    if not settings.anthropic_api_key:
        yield "Chat unavailable — no Anthropic API key configured."
        return

    messages = [
        {"role": "user", "content": f"Here is the detection case data for context:\n{json.dumps(detection, indent=2, default=str)}\n\nI'll now ask questions about this case."},
        {"role": "assistant", "content": "I've reviewed the detection data. I'm ready to answer questions about this case, provide analysis, or discuss enforcement options."},
    ]
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    async with anthropic_client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            yield text


def _fallback_brief(detection: dict) -> dict:
    return {
        "executive_summary": f"Detection scored {detection.get('risk_score', 0)}/100 ({detection.get('alert_tier', 'unknown')}) on {detection.get('platform', 'unknown')}.",
        "risk_assessment": "Automated brief — LLM unavailable.",
        "key_evidence": [],
        "species_profile": "",
        "legal_framework": [],
        "recommended_actions": ["Manual review recommended"],
        "confidence_statement": "Automated assessment only",
        "alternative_explanations": [],
    }
