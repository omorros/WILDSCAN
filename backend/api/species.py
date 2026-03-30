from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.database import get_db

router = APIRouter(prefix="/api/species", tags=["species"])

@router.get("")
async def list_species(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT sr.id, sr.scientific_name, sr.common_name, sr.cites_appendix, sr.iucn_status,
               sr.population_trend, sr.range_countries, sr.typical_products
        FROM species_ref sr ORDER BY sr.common_name
    """))
    return {"species": [dict(row) for row in result.mappings()]}

@router.get("/{species_id}")
async def get_species(species_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM species_ref WHERE id = :id"), {"id": species_id})
    row = result.mappings().first()
    if not row:
        return {"error": "Species not found"}
    return dict(row)
