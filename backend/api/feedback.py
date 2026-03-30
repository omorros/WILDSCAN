from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.database import get_db

router = APIRouter(tags=["feedback"])

class ReviewRequest(BaseModel):
    verdict: str
    notes: str = ""
    false_positive_trigger: str | None = None
    false_positive_context: str | None = None
    reviewer: str = "investigator"

@router.post("/api/detections/{detection_id}/review")
async def review_detection(detection_id: str, request: ReviewRequest, db: AsyncSession = Depends(get_db)):
    await db.execute(text("""
        INSERT INTO listing_reviews (listing_id, verdict, notes, false_positive_trigger, false_positive_context, reviewer)
        VALUES (:listing_id, :verdict, :notes, :trigger, :context, :reviewer)
    """), {"listing_id": detection_id, "verdict": request.verdict, "notes": request.notes,
           "trigger": request.false_positive_trigger, "context": request.false_positive_context, "reviewer": request.reviewer})
    if request.verdict == "false_positive" and request.false_positive_trigger and request.false_positive_context:
        await db.execute(text("UPDATE code_word_lexicon SET false_positive_contexts = array_append(false_positive_contexts, :context) WHERE code_word = :trigger"),
                        {"trigger": request.false_positive_trigger, "context": request.false_positive_context})
    if request.verdict == "true_positive":
        analysis = await db.execute(text("SELECT code_word_matches FROM listing_analysis WHERE listing_id = :id"), {"id": detection_id})
        row = analysis.mappings().first()
        if row and row["code_word_matches"]:
            for match in row["code_word_matches"]:
                await db.execute(text("UPDATE code_word_lexicon SET detection_count = detection_count + 1 WHERE code_word = :word"), {"word": match.get("code_word", "")})
    await db.commit()
    return {"status": "reviewed", "verdict": request.verdict}
