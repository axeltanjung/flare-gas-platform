import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ComplianceThreshold:
    name: str
    metric: str
    max_value: float
    unit: str
    regulation: str


class ComplianceChecker:
    def __init__(self):
        self.thresholds: List[ComplianceThreshold] = [
            ComplianceThreshold(
                name="Daily Flare Volume Limit",
                metric="daily_flare_volume",
                max_value=50000,
                unit="m3/day",
                regulation="EPA 40 CFR 60",
            ),
            ComplianceThreshold(
                name="Emission Intensity Cap",
                metric="emission_intensity",
                max_value=20.0,
                unit="kg CO2e/bbl",
                regulation="EU ETS Phase IV",
            ),
            ComplianceThreshold(
                name="Methane Slip Limit",
                metric="methane_slip_rate",
                max_value=0.05,
                unit="fraction",
                regulation="OGMP 2.0",
            ),
            ComplianceThreshold(
                name="Combustion Efficiency",
                metric="combustion_efficiency",
                max_value=1.0,
                unit="fraction",
                regulation="World Bank Zero Flaring",
            ),
            ComplianceThreshold(
                name="Annual CO2 Equivalent",
                metric="annual_co2e",
                max_value=100000,
                unit="tonnes/year",
                regulation="Paris Agreement NDC",
            ),
        ]

    def check_compliance(self, df: pd.DataFrame) -> pd.DataFrame:
        violations = []

        for threshold in self.thresholds:
            if threshold.metric in df.columns:
                mask = df[threshold.metric] > threshold.max_value
                if mask.any():
                    violations.append({
                        "threshold_name": threshold.name,
                        "metric": threshold.metric,
                        "limit": threshold.max_value,
                        "unit": threshold.unit,
                        "regulation": threshold.regulation,
                        "violation_count": int(mask.sum()),
                        "violation_rate": float(mask.mean()),
                        "max_observed": float(df.loc[mask, threshold.metric].max()),
                        "mean_violation": float(df.loc[mask, threshold.metric].mean()),
                    })

        return pd.DataFrame(violations)

    def calculate_compliance_score(self, df: pd.DataFrame) -> float:
        scores = []

        for threshold in self.thresholds:
            if threshold.metric in df.columns:
                compliance_rate = (df[threshold.metric] <= threshold.max_value).mean()
                scores.append(compliance_rate)

        return float(np.mean(scores)) if scores else 1.0

    def generate_compliance_report(
        self, df: pd.DataFrame, facility_id: Optional[str] = None
    ) -> Dict:
        violations = self.check_compliance(df)
        score = self.calculate_compliance_score(df)

        if score >= 0.95:
            status = "COMPLIANT"
        elif score >= 0.8:
            status = "WARNING"
        else:
            status = "NON_COMPLIANT"

        report = {
            "facility_id": facility_id or "ALL",
            "compliance_score": round(score * 100, 1),
            "status": status,
            "total_records": len(df),
            "violation_summary": violations.to_dict(orient="records") if len(violations) > 0 else [],
            "recommendations": self._generate_recommendations(violations),
        }

        return report

    def _generate_recommendations(self, violations: pd.DataFrame) -> List[str]:
        recommendations = []

        if violations.empty:
            return ["All compliance thresholds met. Continue monitoring."]

        for _, v in violations.iterrows():
            if v["metric"] == "daily_flare_volume":
                recommendations.append(
                    f"Reduce daily flare volume. Current max: {v['max_observed']:.0f} m3/day "
                    f"exceeds limit of {v['limit']:.0f} m3/day. "
                    "Consider gas recovery or compression optimization."
                )
            elif v["metric"] == "emission_intensity":
                recommendations.append(
                    f"Emission intensity exceeds {v['limit']} {v['unit']}. "
                    "Optimize combustion efficiency and reduce methane slip."
                )
            elif v["metric"] == "methane_slip_rate":
                recommendations.append(
                    "Methane slip above threshold. Inspect flare tip, pilot gas supply, "
                    "and wind shielding systems."
                )

        return recommendations
