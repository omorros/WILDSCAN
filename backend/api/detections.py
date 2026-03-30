import json
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.database import get_db

router = APIRouter(prefix="/api/detections", tags=["detections"])
ws_connections: list[WebSocket] = []

@router.get("")
async def list_detections(tier: str | None = None, species: str | None = None, platform: str | None = None,
                          limit: int = Query(50, le=200), offset: int = 0, db: AsyncSession = Depends(get_db)):
    where_clauses = ["la.risk_score > 0"]
    params = {"limit": limit, "offset": offset}
    if tier:
        where_clauses.append("la.alert_tier = :tier"); params["tier"] = tier
    if platform:
        where_clauses.append("l.platform = :platform"); params["platform"] = platform
    where_sql = " AND ".join(where_clauses)
    result = await db.execute(text(f"""
        SELECT l.id, l.platform, l.title_original, l.title_translated, l.price_amount, l.price_currency,
               l.images, l.images_local, l.post_date, l.location_text,
               ST_X(l.location_point) as lng, ST_Y(l.location_point) as lat,
               la.risk_score, la.alert_tier, la.species_matches, la.signal_breakdown, la.code_word_matches,
               EXISTS(SELECT 1 FROM intelligence_briefs ib WHERE ib.listing_id = l.id) as has_brief
        FROM listings l JOIN listing_analysis la ON la.listing_id = l.id
        WHERE {where_sql} ORDER BY la.risk_score DESC LIMIT :limit OFFSET :offset
    """), params)
    detections = []
    for row in result.mappings():
        species_matches = row["species_matches"] or []
        top_species = species_matches[0] if species_matches else {}
        detections.append({
            "id": str(row["id"]), "platform": row["platform"], "title_original": row["title_original"],
            "title_translated": row["title_translated"], "risk_score": row["risk_score"], "alert_tier": row["alert_tier"],
            "species": top_species.get("scientific_name"), "cites_appendix": top_species.get("cites_appendix"),
            "location": {"lat": row["lat"], "lng": row["lng"], "text": row["location_text"]} if row["lat"] else None,
            "images": row["images"] or [], "post_date": str(row["post_date"]) if row["post_date"] else None,
            "signal_breakdown": row["signal_breakdown"] or {}, "has_brief": row["has_brief"],
        })
    count_result = await db.execute(text(f"SELECT COUNT(*) FROM listings l JOIN listing_analysis la ON la.listing_id = l.id WHERE {where_sql}"), params)
    total = count_result.scalar()
    return {"detections": detections, "total": total, "filters_applied": {"tier": tier, "species": species, "platform": platform}}

@router.get("/stats")
async def detection_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT COUNT(*) FILTER (WHERE risk_score > 0) as total_detections,
               COUNT(*) FILTER (WHERE alert_tier = 'red') as red, COUNT(*) FILTER (WHERE alert_tier = 'amber') as amber,
               COUNT(*) FILTER (WHERE alert_tier = 'yellow') as yellow, COUNT(*) FILTER (WHERE alert_tier = 'clear') as clear_count,
               AVG(risk_score) FILTER (WHERE risk_score > 0) as avg_score FROM listing_analysis
    """))
    row = result.mappings().first()
    return dict(row) if row else {}

@router.get("/{detection_id}")
async def get_detection(detection_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT l.*, la.*, ST_X(l.location_point) as lng, ST_Y(l.location_point) as lat
        FROM listings l JOIN listing_analysis la ON la.listing_id = l.id WHERE l.id = :id
    """), {"id": detection_id})
    row = result.mappings().first()
    if not row:
        return {"error": "Detection not found"}
    brief_result = await db.execute(text("SELECT * FROM intelligence_briefs WHERE listing_id = :id ORDER BY generated_at DESC LIMIT 1"), {"id": detection_id})
    brief_row = brief_result.mappings().first()
    return {
        "id": str(row["id"]), "platform": row["platform"], "title_original": row["title_original"],
        "title_translated": row["title_translated"], "description_original": row["description_original"],
        "description_translated": row["description_translated"], "price_amount": row["price_amount"],
        "price_currency": row["price_currency"], "images": row["images"] or [], "images_local": row["images_local"] or [],
        "seller_id": row["seller_id"], "seller_name": row["seller_name"],
        "seller_join_date": str(row["seller_join_date"]) if row["seller_join_date"] else None,
        "seller_listing_count": row["seller_listing_count"],
        "location": {"lat": row["lat"], "lng": row["lng"], "text": row["location_text"]} if row["lat"] else None,
        "post_date": str(row["post_date"]) if row["post_date"] else None, "language": row["language"],
        "risk_score": row["risk_score"], "alert_tier": row["alert_tier"],
        "signal_breakdown": row["signal_breakdown"] or {}, "agreement_bonus": row["agreement_bonus"],
        "hard_override_applied": row["hard_override_applied"], "hard_override_reason": row["hard_override_reason"],
        "code_word_matches": row["code_word_matches"] or [], "linguistic_risk_score": row["linguistic_risk_score"],
        "analysis_method": row["analysis_method"], "image_classification": row["image_classification"] or {},
        "image_risk_score": row["image_risk_score"], "text_image_agreement": row["text_image_agreement"],
        "species_matches": row["species_matches"] or [], "geographic_risk": row["geographic_risk"] or {},
        "seizure_correlations": row["seizure_correlations"] or [],
        "brief": dict(brief_row) if brief_row else None,
    }

@router.websocket("/feed")
async def detection_feed(websocket: WebSocket):
    await websocket.accept()
    ws_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_connections.remove(websocket)

async def broadcast_detection(detection: dict):
    message = json.dumps(detection, default=str)
    for ws in ws_connections[:]:
        try:
            await ws.send_text(message)
        except Exception:
            ws_connections.remove(ws)

async def broadcast_scan_event(event: dict):
    """Broadcast a scan lifecycle event (e.g. scan_complete) to all WS clients."""
    message = json.dumps(event, default=str)
    for ws in ws_connections[:]:
        try:
            await ws.send_text(message)
        except Exception:
            ws_connections.remove(ws)
