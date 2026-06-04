from fastapi import APIRouter, HTTPException
from backend.models.schemas import PredictionInput, ExplainResponse
from backend.services.prediction_service import prediction_service

router = APIRouter()


@router.post("/emission", response_model=ExplainResponse)
async def explain_emission_prediction(input_data: PredictionInput):
    try:
        result = prediction_service.explain_prediction(
            input_data.model_dump(), model_type="lightgbm"
        )
        return ExplainResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


@router.post("/flare-volume", response_model=ExplainResponse)
async def explain_flare_volume(input_data: PredictionInput):
    try:
        result = prediction_service.explain_prediction(
            input_data.model_dump(), model_type="xgboost"
        )
        return ExplainResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")
