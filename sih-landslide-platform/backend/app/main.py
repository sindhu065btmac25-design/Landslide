import asyncio
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from api.routes import (
    alerts, analytics, feedback, health, infrastructure, risk, satellite, terrain, weather,
)
from core.config import get_settings
from core.logging import configure_logging, new_request_id, request_id_ctx
from schemas.common import Location
from services.risk.engine import RiskEngine

configure_logging()
logger = logging.getLogger("app")
settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version=settings.MODEL_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    token = request_id_ctx.set(new_request_id())
    try:
        response = await call_next(request)
    finally:
        request_id_ctx.reset(token)
    return response


for module in (health, weather, satellite, terrain, infrastructure, risk, alerts, feedback, analytics):
    app.include_router(module.router)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "model_version": settings.MODEL_VERSION,
        "demo_mode": settings.DEMO_MODE,
        "docs": "/docs",
    }


_engine = RiskEngine()


@app.websocket("/ws/risk")
async def ws_risk(websocket: WebSocket):
    """Streams a fresh risk assessment for a client-specified location every
    30s. Real deployment publishes from the Celery `update_risk` job via
    Redis pub/sub instead of recomputing per-connection."""
    await websocket.accept()
    try:
        init = await websocket.receive_json()
        location = Location(latitude=init["lat"], longitude=init["lon"], name=init.get("name"))
        while True:
            assessment = await _engine.assess(location)
            await websocket.send_json(
                {
                    "risk_score": assessment.risk_score,
                    "category": assessment.category,
                    "confidence": assessment.confidence,
                    "uncertainty": assessment.uncertainty,
                    "timestamp": assessment.timestamp.isoformat(),
                    "top_driver": assessment.drivers[0].factor if assessment.drivers else None,
                }
            )
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
