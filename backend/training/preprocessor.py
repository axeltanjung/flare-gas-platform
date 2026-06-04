import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from typing import Tuple, Dict, List
import joblib
from pathlib import Path


class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.feature_columns: List[str] = []
        self.numeric_columns: List[str] = []
        self.categorical_columns: List[str] = []

    @property
    def target_columns(self) -> List[str]:
        return [
            "flare_gas_volume",
            "co2_emission_equivalent",
            "flare_event_risk",
            "emission_intensity_index",
            "compliance_risk_level",
        ]

    @property
    def drop_columns(self) -> List[str]:
        return ["timestamp", "facility_id", "flare_stack_id"]

    def load_data(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path, parse_dates=["timestamp"])
        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

        categorical_cols = df.select_dtypes(include=["object", "category"]).columns
        for col in categorical_cols:
            if col not in self.drop_columns and col not in self.target_columns:
                df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else "UNKNOWN")

        return df

    def encode_categoricals(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        categorical_cols = ["maintenance_status"]

        for col in categorical_cols:
            if col in df.columns:
                if fit:
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col].astype(str))
                    self.label_encoders[col] = le
                else:
                    le = self.label_encoders[col]
                    df[col] = df[col].map(
                        lambda x: le.transform([str(x)])[0]
                        if str(x) in le.classes_
                        else -1
                    )

        return df

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if "timestamp" in df.columns:
            df["hour"] = df["timestamp"].dt.hour
            df["day_of_week"] = df["timestamp"].dt.dayofweek
            df["month"] = df["timestamp"].dt.month
            df["day_of_year"] = df["timestamp"].dt.dayofyear
            df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
            df["is_night"] = ((df["hour"] < 6) | (df["hour"] > 22)).astype(int)

        if "gas_pressure" in df.columns and "gas_flow_rate" in df.columns:
            df["pressure_flow_ratio"] = df["gas_pressure"] / (df["gas_flow_rate"] + 1)
            df["pressure_flow_product"] = df["gas_pressure"] * df["gas_flow_rate"]

        if "combustion_temperature" in df.columns and "ambient_temperature" in df.columns:
            df["temp_delta"] = df["combustion_temperature"] - df["ambient_temperature"]

        if all(c in df.columns for c in ["upstream_pressure", "separator_pressure"]):
            df["pressure_drop"] = df["upstream_pressure"] - df["separator_pressure"]

        if "compressor_load" in df.columns and "valve_opening_percentage" in df.columns:
            df["load_valve_interaction"] = df["compressor_load"] * df["valve_opening_percentage"] / 100

        return df

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        feature_df = df.drop(
            columns=[c for c in self.drop_columns + self.target_columns if c in df.columns],
            errors="ignore",
        )
        self.feature_columns = list(feature_df.columns)
        self.numeric_columns = list(feature_df.select_dtypes(include=[np.number]).columns)
        return feature_df

    def scale_features(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        if fit:
            df[self.numeric_columns] = self.scaler.fit_transform(df[self.numeric_columns])
        else:
            df[self.numeric_columns] = self.scaler.transform(df[self.numeric_columns])
        return df

    def preprocess(
        self, data_path: str, test_size: float = 0.2, scale: bool = False
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        df = self.load_data(data_path)
        df = self.handle_missing_values(df)
        df = self.engineer_features(df)
        df = self.encode_categoricals(df, fit=True)

        targets = df[self.target_columns].copy()
        if "compliance_risk_level" in targets.columns:
            compliance_le = LabelEncoder()
            targets["compliance_risk_level"] = compliance_le.fit_transform(
                targets["compliance_risk_level"].astype(str)
            )
            self.label_encoders["compliance_risk_level"] = compliance_le

        features = self.prepare_features(df)

        if scale:
            features = self.scale_features(features, fit=True)

        X_train, X_test, y_train, y_test = train_test_split(
            features, targets, test_size=test_size, random_state=42
        )

        return X_train, X_test, y_train, y_test

    def save(self, path: str):
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.scaler, save_path / "scaler.joblib")
        joblib.dump(self.label_encoders, save_path / "label_encoders.joblib")
        joblib.dump(self.feature_columns, save_path / "feature_columns.joblib")

    def load(self, path: str):
        load_path = Path(path)
        self.scaler = joblib.load(load_path / "scaler.joblib")
        self.label_encoders = joblib.load(load_path / "label_encoders.joblib")
        self.feature_columns = joblib.load(load_path / "feature_columns.joblib")
