from fastapi import APIRouter, HTTPException
from backend.models.schemas import (
    PredictionInput,
    FlareVolumeResponse,
    EmissionPredictionResponse,
    RiskPredictionResponse,
)
from backend.services.prediction_service import prediction_service

router = APIRouter()


@router.post("/flare-volume", response_model=FlareVolumeResponse)
async def predict_flare_volume(input_data: PredictionInput):
    try:
        result = prediction_service.predict_flare_volume(input_data.model_dump())
        return FlareVolumeResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/emissions", response_model=EmissionPredictionResponse)
async def predict_emissions(input_data: PredictionInput):
    try:
        result = prediction_service.predict_emissions(input_data.model_dump())
        return EmissionPredictionResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/risk", response_model=RiskPredictionResponse)
async def predict_risk(input_data: PredictionInput):
    try:
        result = prediction_service.predict_risk(input_data.model_dump())
        return RiskPredictionResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
