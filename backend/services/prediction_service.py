import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from backend.utils.config import get_settings
from backend.utils.logger import logger
from backend.training.preprocessor import DataPreprocessor
from backend.emissions.engine import EmissionEngine
from backend.explainability.shap_explainer import SHAPExplainer


class PredictionService:
    def __init__(self):
        self.settings = get_settings()
        self.model_path = Path(self.settings.model_path)
        self.data_path = Path(self.settings.data_path)
        self.preprocessor = DataPreprocessor()
        self.emission_engine = EmissionEngine()
        self.xgb_model = None
        self.lgb_model = None
        self.clf_model = None
        self.clf_threshold = 0.5
        self.explainer = None
        self._loaded = False

    def load_models(self):
        try:
            self.preprocessor.load(str(self.model_path))
            self.xgb_model = joblib.load(self.model_path / "xgboost_flare_volume.joblib")
            self.lgb_model = joblib.load(self.model_path / "lightgbm_emissions.joblib")
            self.clf_model = joblib.load(self.model_path / "classifier_risk.joblib")
            self.clf_threshold = joblib.load(self.model_path / "optimal_threshold.joblib")
            self._loaded = True
            logger.info("All models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            self._loaded = False

    @property
    def models_loaded(self) -> Dict[str, bool]:
        return {
            "xgboost_flare_volume": self.xgb_model is not None,
            "lightgbm_emissions": self.lgb_model is not None,
            "classifier_risk": self.clf_model is not None,
            "preprocessor": self._loaded,
        }

    def _prepare_input(self, input_data: Dict) -> pd.DataFrame:
        df = pd.DataFrame([input_data])

        categorical_cols = ["maintenance_status"]
        for col in categorical_cols:
            if col in df.columns and col in self.preprocessor.label_encoders:
                le = self.preprocessor.label_encoders[col]
                df[col] = df[col].map(
                    lambda x: le.transform([str(x)])[0]
                    if str(x) in le.classes_ else 0
                )

        df["hour"] = 12
        df["day_of_week"] = 3
        df["month"] = 6
        df["day_of_year"] = 180
        df["is_weekend"] = 0
        df["is_night"] = 0

        if "gas_pressure" in df.columns and "gas_flow_rate" in df.columns:
            df["pressure_flow_ratio"] = df["gas_pressure"] / (df["gas_flow_rate"] + 1)
            df["pressure_flow_product"] = df["gas_pressure"] * df["gas_flow_rate"]

        if "combustion_temperature" in df.columns and "ambient_temperature" in df.columns:
            df["temp_delta"] = df["combustion_temperature"] - df["ambient_temperature"]

        if "upstream_pressure" in df.columns and "separator_pressure" in df.columns:
            df["pressure_drop"] = df["upstream_pressure"] - df["separator_pressure"]

        if "compressor_load" in df.columns and "valve_opening_percentage" in df.columns:
            df["load_valve_interaction"] = df["compressor_load"] * df["valve_opening_percentage"] / 100

        expected_features = self.preprocessor.feature_columns
        for col in expected_features:
            if col not in df.columns:
                df[col] = 0

        df = df[expected_features]
        return df

    def predict_flare_volume(self, input_data: Dict) -> Dict:
        if self.xgb_model is None:
            raise RuntimeError("XGBoost model not loaded")

        X = self._prepare_input(input_data)
        prediction = float(self.xgb_model.predict(X)[0])
        prediction = max(0, prediction)

        std_estimate = prediction * 0.1
        return {
            "predicted_volume_m3": round(prediction, 2),
            "confidence_interval_lower": round(prediction - 1.96 * std_estimate, 2),
            "confidence_interval_upper": round(prediction + 1.96 * std_estimate, 2),
            "model_version": "xgboost-v1.0",
        }

    def predict_emissions(self, input_data: Dict) -> Dict:
        if self.lgb_model is None:
            raise RuntimeError("LightGBM model not loaded")

        X = self._prepare_input(input_data)
        co2e_prediction = float(self.lgb_model.predict(X)[0])
        co2e_prediction = max(0, co2e_prediction)

        methane_ratio = input_data.get("methane_ratio", 0.85)
        flow_rate = input_data.get("gas_flow_rate", 100)
        direct_co2 = co2e_prediction * 0.85
        methane_slip = flow_rate * (1 - 0.98) * methane_ratio
        heating_value = input_data.get("heating_value", 38.0)
        energy_wasted = flow_rate * heating_value / 3600

        production_rate = input_data.get("production_rate", 1000)
        intensity = co2e_prediction / (production_rate + 1e-8)

        return {
            "co2_equivalent_tonnes": round(co2e_prediction / 1000, 4),
            "direct_co2_tonnes": round(direct_co2 / 1000, 4),
            "methane_slip_kg": round(methane_slip, 4),
            "emission_intensity": round(intensity, 6),
            "energy_wasted_mwh": round(energy_wasted, 4),
            "model_version": "lightgbm-v1.0",
        }

    def predict_risk(self, input_data: Dict) -> Dict:
        if self.clf_model is None:
            raise RuntimeError("Classification model not loaded")

        X = self._prepare_input(input_data)
        probability = float(self.clf_model.predict_proba(X)[0][1])
        risk_label = "HIGH" if probability >= self.clf_threshold else "LOW"

        contributing_factors = []
        if input_data.get("gas_pressure", 0) > 80:
            contributing_factors.append({"factor": "High gas pressure", "impact": "high"})
        if input_data.get("emergency_relief_event", 0) == 1:
            contributing_factors.append({"factor": "Emergency relief active", "impact": "critical"})
        if input_data.get("abnormal_operation_flag", 0) == 1:
            contributing_factors.append({"factor": "Abnormal operation detected", "impact": "high"})
        if input_data.get("compressor_load", 0) > 80:
            contributing_factors.append({"factor": "High compressor load", "impact": "medium"})

        return {
            "risk_probability": round(probability, 4),
            "risk_label": risk_label,
            "threshold_used": self.clf_threshold,
            "contributing_factors": contributing_factors,
        }

    def explain_prediction(self, input_data: Dict, model_type: str = "xgboost") -> Dict:
        X = self._prepare_input(input_data)

        model = self.xgb_model if model_type == "xgboost" else self.lgb_model
        if model is None:
            raise RuntimeError(f"{model_type} model not loaded")

        explainer = SHAPExplainer(model=model, model_type="tree")
        explainer.initialize()
        result = explainer.explain_single(X)

        insights = []
        for contrib in result["contributions"][:5]:
            feature = contrib["feature"]
            shap_val = contrib["shap_value"]
            direction = "increases" if shap_val > 0 else "decreases"
            insights.append(
                f"{feature} {direction} prediction by {abs(shap_val):.2f}"
            )

        return {
            "expected_value": result["expected_value"],
            "top_drivers": result["contributions"][:10],
            "operational_insights": insights,
        }


prediction_service = PredictionService()
