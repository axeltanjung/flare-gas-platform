from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from backend.utils.config import get_settings
from backend.utils.logger import logger
from backend.services.prediction_service import prediction_service
from backend.api.routes import predict, emissions, compliance, explain, facilities


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FlareGas Intelligence Platform...")
    prediction_service.load_models()
    yield
    logger.info("Shutting down FlareGas Intelligence Platform...")


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered Flare Gas Prediction & Emission Intelligence Platform for ESG Reporting",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, prefix="/predict", tags=["Predictions"])
app.include_router(emissions.router, prefix="/emission", tags=["Emissions"])
app.include_router(compliance.router, prefix="/compliance", tags=["Compliance"])
app.include_router(explain.router, prefix="/explain", tags=["Explainability"])
app.include_router(facilities.router, prefix="/facility", tags=["Facilities"])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "models_loaded": prediction_service.models_loaded,
        "timestamp": datetime.utcnow().isoformat(),
    }
