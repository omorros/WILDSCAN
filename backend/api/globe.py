from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.database import get_db

router = APIRouter(prefix="/api/globe", tags=["globe"])

@router.get("")
async def get_globe_data(db: AsyncSession = Depends(get_db)):
    detections_result = await db.execute(text("""
        SELECT l.id, l.platform, l.title_original, l.title_translated,
               ST_X(l.location_point) as lng, ST_Y(l.location_point) as lat,
               la.risk_score, la.alert_tier, la.species_matches
        FROM listings l
        JOIN listing_analysis la ON la.listing_id = l.id
        WHERE l.location_point IS NOT NULL AND la.risk_score > 0
    """))
    detection_features = []
    for row in detections_result.mappings():
        species_matches = row["species_matches"] or []
        detection_features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [row["lng"], row["lat"]]},
            "properties": {
                "id": str(row["id"]), "platform": row["platform"],
                "title": row["title_translated"] or row["title_original"],
                "risk_score": row["risk_score"], "alert_tier": row["alert_tier"],
                "species": species_matches[0]["common_name"] if species_matches else None,
            },
        })
    routes_result = await db.execute(text("""
        SELECT species_group, origin_region, destination_region, activity_level,
               ST_AsGeoJSON(route_geometry)::json as geometry
        FROM trafficking_routes
    """))
    route_features = []
    for row in routes_result.mappings():
        route_features.append({
            "type": "Feature", "geometry": row["geometry"],
            "properties": {"species_group": row["species_group"], "origin": row["origin_region"],
                          "destination": row["destination_region"], "activity_level": row["activity_level"]},
        })
    stats_result = await db.execute(text("""
        SELECT COUNT(*) as total_detections,
               COUNT(*) FILTER (WHERE alert_tier = 'red') as red,
               COUNT(*) FILTER (WHERE alert_tier = 'amber') as amber,
               COUNT(*) FILTER (WHERE alert_tier = 'yellow') as yellow
        FROM listing_analysis WHERE risk_score > 0
    """))
    stats_row = stats_result.mappings().first()
    countries_result = await db.execute(text("SELECT COUNT(DISTINCT platform) as cnt FROM listings WHERE id IN (SELECT listing_id FROM listing_analysis WHERE risk_score > 0)"))
    countries_count = countries_result.scalar() or 0
    return {
        "detections": {"type": "FeatureCollection", "features": detection_features},
        "routes": {"type": "FeatureCollection", "features": route_features},
        "stats": {"total_detections": stats_row["total_detections"] if stats_row else 0, "red": stats_row["red"] if stats_row else 0,
                  "amber": stats_row["amber"] if stats_row else 0, "yellow": stats_row["yellow"] if stats_row else 0, "countries": countries_count},
    }
