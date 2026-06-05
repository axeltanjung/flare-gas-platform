import pandas as pd
from typing import Dict, List
from backend.emissions.calculator import EmissionCalculator
from backend.emissions.compliance import ComplianceChecker


class EmissionEngine:
    def __init__(self):
        self.calculator = EmissionCalculator()
        self.compliance = ComplianceChecker()

    def process_batch(self, df: pd.DataFrame) -> Dict:
        emission_results = self.calculator.batch_calculate(df)
        merged = pd.concat([df, emission_results], axis=1)

        summary = self._compute_summary(merged)
        facility_breakdown = self._facility_breakdown(merged)
        compliance_report = self.compliance.generate_compliance_report(merged)

        return {
            "summary": summary,
            "facility_breakdown": facility_breakdown,
            "compliance": compliance_report,
            "detailed_emissions": emission_results,
        }

    def _compute_summary(self, df: pd.DataFrame) -> Dict:
        return {
            "total_co2e_tonnes": float(df["co2_equivalent_tonnes"].sum()),
            "total_flare_volume_m3": float(df["flare_gas_volume"].sum()),
            "avg_emission_intensity": float(df["emission_intensity_kg_per_bbl"].mean()),
            "total_energy_wasted_mwh": float(df["energy_wasted_mwh"].sum()),
            "high_risk_events": int((df.get("flare_event_risk", pd.Series([0])) == 1).sum()),
            "avg_combustion_temp": float(df["combustion_temperature"].mean()) if "combustion_temperature" in df.columns else None,
            "total_methane_slip_tonnes": float(df["methane_slip_kg"].sum() / 1000),
        }

    def _facility_breakdown(self, df: pd.DataFrame) -> List:
        if "facility_id" not in df.columns:
            return []

        grouped = df.groupby("facility_id").agg({
            "co2_equivalent_tonnes": "sum",
            "flare_gas_volume": "sum",
            "emission_intensity_kg_per_bbl": "mean",
            "energy_wasted_mwh": "sum",
        }).reset_index()

        grouped = grouped.sort_values("co2_equivalent_tonnes", ascending=False)
        return grouped.to_dict(orient="records")

    def get_emission_trend(
        self, df: pd.DataFrame, period: str = "D"
    ) -> pd.DataFrame:
        if "timestamp" not in df.columns:
            return pd.DataFrame()

        emission_results = self.calculator.batch_calculate(df)
        merged = pd.concat([df[["timestamp"]], emission_results], axis=1)
        merged["timestamp"] = pd.to_datetime(merged["timestamp"])

        trend = merged.set_index("timestamp").resample(period).agg({
            "co2_equivalent_tonnes": "sum",
            "co2_direct_tonnes": "sum",
            "methane_slip_kg": "sum",
            "energy_wasted_mwh": "sum",
        }).reset_index()

        return trend

    def get_facility_report(
        self, df: pd.DataFrame, facility_id: str
    ) -> Dict:
        facility_data = df[df["facility_id"] == facility_id]
        if facility_data.empty:
            return {"error": f"Facility {facility_id} not found"}

        emission_results = self.calculator.batch_calculate(facility_data)
        compliance = self.compliance.generate_compliance_report(
            pd.concat([facility_data, emission_results], axis=1),
            facility_id=facility_id,
        )

        return {
            "facility_id": facility_id,
            "record_count": len(facility_data),
            "total_co2e_tonnes": float(emission_results["co2_equivalent_tonnes"].sum()),
            "avg_intensity": float(emission_results["emission_intensity_kg_per_bbl"].mean()),
            "total_energy_wasted_mwh": float(emission_results["energy_wasted_mwh"].sum()),
            "compliance": compliance,
        }
