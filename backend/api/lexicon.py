from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.database import get_db

router = APIRouter(prefix="/api/lexicon", tags=["lexicon"])

@router.get("")
async def list_lexicon(language: str | None = None, db: AsyncSession = Depends(get_db)):
    where = "WHERE status = 'verified'"
    params = {}
    if language:
        where += " AND language = :language"; params["language"] = language
    result = await db.execute(text(f"SELECT cwl.*, sr.scientific_name, sr.common_name FROM code_word_lexicon cwl LEFT JOIN species_ref sr ON cwl.species_id = sr.id {where} ORDER BY cwl.language, cwl.code_word"), params)
    return {"lexicon": [dict(row) for row in result.mappings()]}

@router.get("/proposed")
async def list_proposed(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM proposed_code_words ORDER BY created_at DESC LIMIT 50"))
    return {"proposed": [dict(row) for row in result.mappings()]}
