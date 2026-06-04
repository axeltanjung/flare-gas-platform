import numpy as np
import pandas as pd
import shap
from typing import Dict, List, Optional, Any
import joblib
from pathlib import Path


class SHAPExplainer:
    def __init__(self, model: Any = None, model_type: str = "tree"):
        self.model = model
        self.model_type = model_type
        self.explainer: Optional[shap.Explainer] = None
        self.shap_values: Optional[np.ndarray] = None
        self.expected_value: Optional[float] = None

    def initialize(self, background_data: Optional[pd.DataFrame] = None):
        if self.model is None:
            raise ValueError("Model must be set before initialization")

        if self.model_type == "tree":
            self.explainer = shap.TreeExplainer(self.model)
        elif self.model_type == "linear":
            self.explainer = shap.LinearExplainer(self.model, background_data)
        else:
            if background_data is not None:
                self.explainer = shap.KernelExplainer(
                    self.model.predict, shap.sample(background_data, 100)
                )
            else:
                raise ValueError("Background data required for kernel explainer")

        self.expected_value = self.explainer.expected_value
        if isinstance(self.expected_value, np.ndarray):
            self.expected_value = float(self.expected_value[0])

    def explain(self, X: pd.DataFrame) -> Dict:
        if self.explainer is None:
            raise ValueError("Explainer not initialized. Call initialize() first.")

        self.shap_values = self.explainer.shap_values(X)

        if isinstance(self.shap_values, list):
            self.shap_values = self.shap_values[1]

        feature_importance = self._global_importance(X)
        top_drivers = self._top_drivers(X, n=10)

        return {
            "shap_values": self.shap_values,
            "expected_value": self.expected_value,
            "feature_importance": feature_importance,
            "top_drivers": top_drivers,
        }

    def explain_single(self, X_row: pd.DataFrame) -> Dict:
        if self.explainer is None:
            raise ValueError("Explainer not initialized")

        sv = self.explainer.shap_values(X_row)
        if isinstance(sv, list):
            sv = sv[1]

        contributions = pd.DataFrame({
            "feature": X_row.columns,
            "value": X_row.iloc[0].values,
            "shap_value": sv[0] if sv.ndim > 1 else sv,
            "abs_shap": np.abs(sv[0] if sv.ndim > 1 else sv),
        }).sort_values("abs_shap", ascending=False)

        return {
            "expected_value": self.expected_value,
            "contributions": contributions.to_dict(orient="records"),
            "prediction_breakdown": {
                "base_value": self.expected_value,
                "total_shap": float(contributions["shap_value"].sum()),
                "final_prediction": self.expected_value + float(contributions["shap_value"].sum()),
            },
        }

    def _global_importance(self, X: pd.DataFrame) -> pd.DataFrame:
        mean_abs_shap = np.abs(self.shap_values).mean(axis=0)
        fi = pd.DataFrame({
            "feature": X.columns,
            "mean_abs_shap": mean_abs_shap,
        }).sort_values("mean_abs_shap", ascending=False)
        fi["importance_pct"] = fi["mean_abs_shap"] / fi["mean_abs_shap"].sum() * 100
        return fi

    def _top_drivers(self, X: pd.DataFrame, n: int = 10) -> List[Dict]:
        fi = self._global_importance(X)
        top = fi.head(n)

        drivers = []
        for _, row in top.iterrows():
            feature = row["feature"]
            feature_idx = list(X.columns).index(feature)
            feature_shap = self.shap_values[:, feature_idx]

            drivers.append({
                "feature": feature,
                "importance": float(row["mean_abs_shap"]),
                "importance_pct": float(row["importance_pct"]),
                "mean_impact": float(feature_shap.mean()),
                "max_positive_impact": float(feature_shap.max()),
                "max_negative_impact": float(feature_shap.min()),
                "direction": "positive" if feature_shap.mean() > 0 else "negative",
            })

        return drivers

    def get_emission_drivers(self, X: pd.DataFrame) -> Dict:
        explanation = self.explain(X)

        emission_features = [
            "gas_flow_rate", "gas_pressure", "methane_ratio",
            "combustion_temperature", "compressor_load",
            "emission_factor", "methane_slip_rate",
        ]

        drivers = [
            d for d in explanation["top_drivers"]
            if d["feature"] in emission_features
        ]

        return {
            "emission_drivers": drivers,
            "total_drivers": explanation["top_drivers"],
            "operational_insight": self._generate_operational_insight(drivers),
        }

    def _generate_operational_insight(self, drivers: List[Dict]) -> List[str]:
        insights = []
        for d in drivers[:5]:
            feature = d["feature"]
            direction = d["direction"]
            importance = d["importance_pct"]

            if feature == "gas_flow_rate":
                insights.append(
                    f"Gas flow rate is the #{len(insights)+1} driver ({importance:.1f}% importance). "
                    f"Higher flow rates {'increase' if direction == 'positive' else 'decrease'} emissions."
                )
            elif feature == "gas_pressure":
                insights.append(
                    f"Gas pressure contributes {importance:.1f}% to prediction. "
                    "Optimize pressure regulation to reduce flaring."
                )
            elif feature == "combustion_temperature":
                insights.append(
                    f"Combustion temperature ({importance:.1f}% impact). "
                    "Ensure optimal temperature for complete combustion."
                )
            elif feature == "compressor_load":
                insights.append(
                    f"Compressor load drives {importance:.1f}% of variance. "
                    "Balance compressor scheduling with flare reduction."
                )
            else:
                insights.append(
                    f"{feature} contributes {importance:.1f}% to emission prediction "
                    f"(direction: {direction})."
                )

        return insights

    def save_explanations(self, path: str, X: pd.DataFrame):
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)

        fi = self._global_importance(X)
        fi.to_csv(save_path / "shap_feature_importance.csv", index=False)

        if self.shap_values is not None:
            joblib.dump(self.shap_values, save_path / "shap_values.joblib")
