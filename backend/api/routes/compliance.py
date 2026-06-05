from fastapi import APIRouter, HTTPException, Query
import pandas as pd
from pathlib import Path

from backend.models.schemas import ComplianceStatusResponse
from backend.emissions.compliance import ComplianceChecker
from backend.utils.config import get_settings

router = APIRouter()


@router.get("/status", response_model=ComplianceStatusResponse)
async def get_compliance_status(
    facility_id: str = Query(..., description="Facility ID to check"),
):
    try:
        settings = get_settings()
        data_path = Path(settings.data_path) / "flare_gas_dataset.csv"

        if not data_path.exists():
            raise HTTPException(status_code=404, detail="Dataset not found")

        df = pd.read_csv(data_path, parse_dates=["timestamp"])
        facility_data = df[df["facility_id"] == facility_id]

        if facility_data.empty:
            raise HTTPException(status_code=404, detail=f"Facility {facility_id} not found")

        checker = ComplianceChecker()
        report = checker.generate_compliance_report(facility_data, facility_id)

        return ComplianceStatusResponse(
            facility_id=facility_id,
            compliance_score=report["compliance_score"],
            status=report["status"],
            violations=report["violation_summary"],
            recommendations=report["recommendations"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance check failed: {str(e)}")
