import base64
import json
import os

from openai import AsyncOpenAI
from backend.config import settings


openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

VISION_PROMPT = """You are a wildlife product identification specialist. Analyze this marketplace product image. Identify if the product is or contains material from a CITES-listed species.

Products to check for: ivory (raw and carved), pangolin scales, rhino horn, tiger parts (bone, skin, teeth), tortoiseshell, shahtoosh wool, bear bile, coral, exotic birds (live), reptiles (live and products), shark fin, hornbill casque, rosewood.

Return ONLY valid JSON:
{
  "product_detected": bool,
  "predicted_product": "string or null",
  "predicted_species_scientific": "string or null",
  "confidence": float,
  "visual_evidence": "string describing what you see",
  "alternative_explanations": "string describing what else this could be"
}"""


async def analyze_images(listing: dict) -> dict:
    images = listing.get("images_local", []) or listing.get("images", [])
    if not images:
        return {
            "primary_classification": {
                "product_detected": False, "predicted_product": None, "predicted_species": None,
                "confidence": 0.0, "visual_evidence": "No images available", "alternative_explanations": None,
            },
            "per_image_results": [],
            "image_risk_score": 0.0,
        }

    per_image_results = []
    for img_path in images[:3]:
        result = await _classify_image(img_path)
        if result:
            per_image_results.append(result)

    if per_image_results:
        primary = max(per_image_results, key=lambda r: r.get("confidence", 0))
    else:
        primary = {
            "product_detected": False, "predicted_product": None, "predicted_species": None,
            "confidence": 0.0, "visual_evidence": "Image analysis failed", "alternative_explanations": None,
        }

    image_risk_score = primary.get("confidence", 0.0) if primary.get("product_detected") else 0.0
    return {
        "primary_classification": primary,
        "per_image_results": per_image_results,
        "image_risk_score": image_risk_score,
    }


async def _classify_image(image_path: str) -> dict | None:
    if not settings.openai_api_key:
        return None
    try:
        if image_path.startswith("/static/") or image_path.startswith("C:"):
            if image_path.startswith("/static/"):
                abs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), image_path.lstrip("/"))
            else:
                abs_path = image_path
            with open(abs_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
            image_content = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}}
        else:
            image_content = {"type": "image_url", "image_url": {"url": image_path}}

        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": [{"type": "text", "text": VISION_PROMPT}, image_content]}],
            temperature=0,
            max_tokens=500,
        )
        result = json.loads(response.choices[0].message.content)
        if "predicted_species_scientific" in result:
            result["predicted_species"] = result.pop("predicted_species_scientific")
        return result
    except Exception:
        return None
