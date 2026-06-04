from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pandas as pd
from pathlib import Path

from backend.models.schemas import EmissionReportResponse
from backend.services.prediction_service import prediction_service
from backend.utils.config import get_settings

router = APIRouter()


@router.get("/report", response_model=EmissionReportResponse)
async def get_emission_report(
    facility_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    period: str = Query("D", description="Aggregation period: H, D, W, M"),
):
    try:
        settings = get_settings()
        data_path = Path(settings.data_path) / "flare_gas_dataset.csv"

        if not data_path.exists():
            raise HTTPException(status_code=404, detail="Dataset not found")

        df = pd.read_csv(data_path, parse_dates=["timestamp"])

        if facility_id:
            df = df[df["facility_id"] == facility_id]
            if df.empty:
                raise HTTPException(status_code=404, detail=f"Facility {facility_id} not found")

        if start_date:
            df = df[df["timestamp"] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df["timestamp"] <= pd.to_datetime(end_date)]

        engine = prediction_service.emission_engine
        report = engine.process_batch(df)
        trend = engine.get_emission_trend(df, period=period)

        return EmissionReportResponse(
            summary=report["summary"],
            facility_breakdown=report["facility_breakdown"],
            compliance=report["compliance"],
            trend_data=trend.to_dict(orient="records") if not trend.empty else [],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
