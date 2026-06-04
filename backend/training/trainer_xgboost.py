import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV
import mlflow
import mlflow.xgboost
import joblib
from pathlib import Path
from typing import Dict, Optional, Tuple


class XGBoostTrainer:
    def __init__(self, experiment_name: str = "flare-gas-xgboost"):
        self.experiment_name = experiment_name
        self.model: Optional[xgb.XGBRegressor] = None
        self.best_params: Dict = {}
        self.metrics: Dict = {}
        self.feature_importance: Optional[pd.DataFrame] = None

    def get_default_params(self) -> Dict:
        return {
            "n_estimators": 500,
            "max_depth": 8,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "min_child_weight": 5,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "random_state": 42,
            "n_jobs": -1,
            "tree_method": "hist",
        }

    def get_tuning_grid(self) -> Dict:
        return {
            "max_depth": [6, 8, 10],
            "learning_rate": [0.01, 0.05, 0.1],
            "n_estimators": [300, 500, 700],
            "subsample": [0.7, 0.8, 0.9],
            "colsample_bytree": [0.7, 0.8, 0.9],
        }

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        hyperparameter_tuning: bool = False,
    ) -> xgb.XGBRegressor:
        if hyperparameter_tuning:
            self.model = self._train_with_tuning(X_train, y_train)
        else:
            params = self.get_default_params()
            self.model = xgb.XGBRegressor(**params)
            self.model.fit(
                X_train,
                y_train,
                eval_set=[(X_test, y_test)],
                verbose=50,
            )
            self.best_params = params

        predictions = self.model.predict(X_test)
        self.metrics = self._compute_metrics(y_test, predictions)
        self.feature_importance = self._get_feature_importance(X_train.columns)

        return self.model

    def _train_with_tuning(
        self, X_train: pd.DataFrame, y_train: pd.Series
    ) -> xgb.XGBRegressor:
        base_model = xgb.XGBRegressor(
            random_state=42, n_jobs=-1, tree_method="hist"
        )
        grid = GridSearchCV(
            base_model,
            self.get_tuning_grid(),
            cv=3,
            scoring="neg_root_mean_squared_error",
            n_jobs=-1,
            verbose=1,
        )
        grid.fit(X_train, y_train)
        self.best_params = grid.best_params_
        return grid.best_estimator_

    def _compute_metrics(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict:
        return {
            "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "mae": float(mean_absolute_error(y_true, y_pred)),
            "r2": float(r2_score(y_true, y_pred)),
            "mape": float(np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100),
        }

    def _get_feature_importance(self, feature_names: pd.Index) -> pd.DataFrame:
        importance = self.model.feature_importances_
        fi_df = pd.DataFrame({
            "feature": feature_names,
            "importance": importance,
        }).sort_values("importance", ascending=False)
        return fi_df

    def log_to_mlflow(self, run_name: str = "xgboost-flare-volume"):
        mlflow.set_experiment(self.experiment_name)
        with mlflow.start_run(run_name=run_name):
            mlflow.log_params(self.best_params)
            mlflow.log_metrics(self.metrics)
            mlflow.xgboost.log_model(self.model, "model")

            if self.feature_importance is not None:
                fi_path = "/tmp/feature_importance.csv"
                self.feature_importance.to_csv(fi_path, index=False)
                mlflow.log_artifact(fi_path)

    def save(self, path: str):
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, save_path / "xgboost_flare_volume.joblib")
        joblib.dump(self.metrics, save_path / "xgboost_metrics.joblib")
        if self.feature_importance is not None:
            self.feature_importance.to_csv(
                save_path / "xgboost_feature_importance.csv", index=False
            )

    def load(self, path: str):
        load_path = Path(path)
        self.model = joblib.load(load_path / "xgboost_flare_volume.joblib")
        self.metrics = joblib.load(load_path / "xgboost_metrics.joblib")

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        return self.model.predict(X)
