import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.database import get_db
from backend.agents.intel_analyst import generate_brief, stream_chat

router = APIRouter(prefix="/api/intel", tags=["intelligence"])

@router.post("/brief/{detection_id}")
async def create_brief(detection_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT l.*, la.* FROM listings l JOIN listing_analysis la ON la.listing_id = l.id WHERE l.id = :id"), {"id": detection_id})
    row = result.mappings().first()
    if not row:
        return {"error": "Detection not found"}
    detection_data = dict(row)
    brief = await generate_brief(detection_data)
    await db.execute(text("""
        INSERT INTO intelligence_briefs (listing_id, brief_type, executive_summary, full_brief, recommended_actions, generated_by)
        VALUES (:listing_id, 'auto', :summary, :full_brief, :actions, 'claude-sonnet')
    """), {"listing_id": detection_id, "summary": brief.get("executive_summary", ""), "full_brief": json.dumps(brief), "actions": brief.get("recommended_actions", [])})
    await db.commit()
    return brief

class ChatRequest(BaseModel):
    detection_id: str
    question: str
    chat_history: list[dict] = []

@router.post("/chat")
async def chat_about_case(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT l.*, la.* FROM listings l JOIN listing_analysis la ON la.listing_id = l.id WHERE l.id = :detection_id"), {"detection_id": request.detection_id})
    row = result.mappings().first()
    if not row:
        return {"error": "Detection not found"}
    detection_data = dict(row)
    async def event_stream():
        async for chunk in stream_chat(detection_data, request.chat_history, request.question):
            yield f"data: {json.dumps({'text': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
