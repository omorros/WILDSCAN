import uuid
import asyncio
import random
from datetime import datetime
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.database import get_db, async_session
from backend.api.detections import broadcast_detection, broadcast_scan_event

router = APIRouter(prefix="/api/scan", tags=["scan"])

class ScanRequest(BaseModel):
    marketplace: str = "olx.th"
    region: str = "TH"
    search_queries: list[str] = ["antiques", "collectibles", "traditional medicine"]


async def stream_demo_detections(job_id: str):
    """Background task: query demo detections and stream them via WebSocket."""
    import logging
    logger = logging.getLogger("scan")
    logger.warning(f"[SCAN] Background task started for job {job_id}")
    try:
        async with async_session() as db:
            result = await db.execute(text("""
                SELECT l.id, l.platform, l.title_original, l.title_translated,
                       l.price_amount, l.price_currency, l.images, l.post_date, l.location_text,
                       ST_X(l.location_point) as lng, ST_Y(l.location_point) as lat,
                       la.risk_score, la.alert_tier, la.species_matches, la.signal_breakdown,
                       la.code_word_matches, la.image_classification
                FROM listings l JOIN listing_analysis la ON la.listing_id = l.id
                WHERE la.alert_tier IN ('red', 'amber', 'yellow')
            """))
            rows = [dict(r) for r in result.mappings()]
            random.shuffle(rows)
            logger.warning(f"[SCAN] Fetched {len(rows)} detections from DB (shuffled)")

            total = len(rows)
            flagged = sum(1 for r in rows if r["alert_tier"] in ("red", "amber", "yellow"))

            # Build-up phase: simulate scanning
            await asyncio.sleep(5)

            # Build all detections and send as one batch
            detections = []
            for i, row in enumerate(rows):
                species_matches = row["species_matches"] or []
                top_species = species_matches[0] if species_matches else {}
                code_word_matches = row["code_word_matches"] or []
                image_class = row["image_classification"] or {}

                detections.append({
                    "id": str(row["id"]),
                    "platform": row["platform"],
                    "title_original": row["title_original"],
                    "title_translated": row["title_translated"],
                    "risk_score": row["risk_score"],
                    "alert_tier": row["alert_tier"],
                    "species": top_species.get("scientific_name"),
                    "cites_appendix": top_species.get("cites_appendix"),
                    "location": {
                        "lat": row["lat"],
                        "lng": row["lng"],
                        "text": row["location_text"],
                    } if row["lat"] else None,
                    "images": row["images"] or [],
                    "post_date": str(row["post_date"]) if row["post_date"] else None,
                    "signal_breakdown": row["signal_breakdown"] or {},
                    "code_word_count": len(code_word_matches),
                    "image_product": image_class.get("predicted_product", ""),
                })

            logger.warning(f"[SCAN] Sending batch of {total} detections")
            await broadcast_scan_event({
                "type": "scan_batch",
                "detections": detections,
                "total": total,
                "flagged": flagged,
            })

            await db.execute(text("""
                UPDATE scan_jobs SET status = 'completed', listings_found = :total,
                       listings_flagged = :flagged, completed_at = :now
                WHERE id = :id
            """), {"id": job_id, "total": total, "flagged": flagged, "now": datetime.utcnow()})
            await db.commit()

            await broadcast_scan_event({
                "type": "scan_complete",
                "total": total,
                "flagged": flagged,
            })
    except Exception as e:
        logger.error(f"[SCAN] Background task FAILED: {e}", exc_info=True)
        try:
            async with async_session() as db:
                await db.execute(text("""
                    UPDATE scan_jobs SET status = 'failed', error_message = :err, completed_at = :now
                    WHERE id = :id
                """), {"id": job_id, "err": str(e), "now": datetime.utcnow()})
                await db.commit()
        except Exception:
            pass
        await broadcast_scan_event({"type": "scan_complete", "total": 0, "flagged": 0})


@router.post("/start")
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    job_id = str(uuid.uuid4())
    proxy_country = {"olx.th": "TH", "chotot.com": "VN"}.get(request.marketplace, "TH")
    await db.execute(text("""
        INSERT INTO scan_jobs (id, marketplace, region, proxy_country, status, search_queries, started_at)
        VALUES (:id, :marketplace, :region, :proxy_country, 'running', :queries, :started_at)
    """), {"id": job_id, "marketplace": request.marketplace, "region": request.region,
           "proxy_country": proxy_country, "queries": request.search_queries, "started_at": datetime.utcnow()})
    await db.commit()

    background_tasks.add_task(stream_demo_detections, job_id)
    return {"job_id": job_id, "status": "running"}


@router.get("/jobs")
async def list_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT id, marketplace, region, proxy_country, status, listings_found, listings_passed_triage, listings_flagged,
               started_at, completed_at, error_message, created_at FROM scan_jobs ORDER BY created_at DESC LIMIT 20
    """))
    return {"jobs": [dict(row) for row in result.mappings()]}


@router.get("/jobs/{job_id}")
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM scan_jobs WHERE id = :id"), {"id": job_id})
    row = result.mappings().first()
    if not row:
        return {"error": "Job not found"}
    return dict(row)
