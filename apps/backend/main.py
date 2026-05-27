import logging
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import engine, Base
from routers import health, farmers, villages, crops, sensors, alerts, stats

logging.basicConfig(
    stream=sys.stdout,
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sanliurfa Agricultural Cooperative API",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PREFIX = "/api/v1"
app.include_router(health.router, prefix=PREFIX, tags=["health"])
app.include_router(farmers.router, prefix=PREFIX, tags=["farmers"])
app.include_router(villages.router, prefix=PREFIX, tags=["villages"])
app.include_router(crops.router, prefix=PREFIX, tags=["crops"])
app.include_router(sensors.router, prefix=PREFIX, tags=["sensors"])
app.include_router(alerts.router, prefix=PREFIX, tags=["alerts"])
app.include_router(stats.router, prefix=PREFIX, tags=["stats"])


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured")

    if os.getenv("RUN_SEED", "").lower() == "true":
        from seed.seed import run_seed
        run_seed(engine)
        logger.info("Seed completed")
