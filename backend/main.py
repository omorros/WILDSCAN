import asyncio
import sys

# Fix for Windows ProactorEventLoop incompatibility with async DB drivers
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from backend.config import settings
from backend.api import globe, detections, scan, intel, species, lexicon, feedback

app = FastAPI(title="WILDSCAN", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "static", "images")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static/images", StaticFiles(directory=static_dir), name="images")

app.include_router(globe.router)
app.include_router(detections.router)
app.include_router(scan.router)
app.include_router(intel.router)
app.include_router(species.router)
app.include_router(lexicon.router)
app.include_router(feedback.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
