from fastapi import APIRouter, HTTPException
import pandas as pd
from pathlib import Path

from backend.models.schemas import FacilityResponse
from backend.services.prediction_service import prediction_service
from backend.utils.config import get_settings

router = APIRouter()


@router.get("/{facility_id}", response_model=FacilityResponse)
async def get_facility_details(facility_id: str):
    try:
        settings = get_settings()
        data_path = Path(settings.data_path) / "flare_gas_dataset.csv"

        if not data_path.exists():
            raise HTTPException(status_code=404, detail="Dataset not found")

        df = pd.read_csv(data_path, parse_dates=["timestamp"])
        facility_data = df[df["facility_id"] == facility_id]

        if facility_data.empty:
            raise HTTPException(status_code=404, detail=f"Facility {facility_id} not found")

        total_co2e = float(facility_data["co2_emission_equivalent"].sum() / 1000)
        total_volume = float(facility_data["flare_gas_volume"].sum())
        avg_intensity = float(facility_data["emission_intensity_index"].mean())
        risk_events = int(facility_data["flare_event_risk"].sum())

        compliance_risk = facility_data["compliance_risk_level"].value_counts()
        if "HIGH" in compliance_risk and compliance_risk["HIGH"] > len(facility_data) * 0.1:
            compliance_status = "NON_COMPLIANT"
        elif "MEDIUM" in compliance_risk and compliance_risk["MEDIUM"] > len(facility_data) * 0.3:
            compliance_status = "WARNING"
        else:
            compliance_status = "COMPLIANT"

        return FacilityResponse(
            facility_id=facility_id,
            total_co2e_tonnes=round(total_co2e, 2),
            total_flare_volume=round(total_volume, 2),
            avg_emission_intensity=round(avg_intensity, 6),
            compliance_status=compliance_status,
            risk_events=risk_events,
            record_count=len(facility_data),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get facility: {str(e)}")
