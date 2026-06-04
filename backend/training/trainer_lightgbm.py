import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV
import mlflow
import mlflow.lightgbm
import joblib
from pathlib import Path
from typing import Dict, Optional, Tuple


class LightGBMTrainer:
    def __init__(self, experiment_name: str = "flare-gas-lightgbm"):
        self.experiment_name = experiment_name
        self.model: Optional[lgb.LGBMRegressor] = None
        self.best_params: Dict = {}
        self.metrics: Dict = {}
        self.feature_importance: Optional[pd.DataFrame] = None
        self.uncertainty_estimates: Optional[np.ndarray] = None

    def get_default_params(self) -> Dict:
        return {
            "n_estimators": 600,
            "max_depth": 8,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "min_child_samples": 20,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "random_state": 42,
            "n_jobs": -1,
            "verbosity": -1,
        }

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        hyperparameter_tuning: bool = False,
    ) -> lgb.LGBMRegressor:
        if hyperparameter_tuning:
            self.model = self._train_with_tuning(X_train, y_train)
        else:
            params = self.get_default_params()
            self.model = lgb.LGBMRegressor(**params)
            self.model.fit(
                X_train,
                y_train,
                eval_set=[(X_test, y_test)],
            )
            self.best_params = params

        predictions = self.model.predict(X_test)
        self.metrics = self._compute_metrics(y_test, predictions)
        self.feature_importance = self._get_feature_importance(X_train.columns)
        self.uncertainty_estimates = self._estimate_uncertainty(X_test)

        return self.model

    def _train_with_tuning(
        self, X_train: pd.DataFrame, y_train: pd.Series
    ) -> lgb.LGBMRegressor:
        param_grid = {
            "max_depth": [6, 8, 10],
            "learning_rate": [0.01, 0.05, 0.1],
            "n_estimators": [400, 600, 800],
            "num_leaves": [31, 63, 127],
        }
        base_model = lgb.LGBMRegressor(random_state=42, n_jobs=-1, verbosity=-1)
        grid = GridSearchCV(
            base_model,
            param_grid,
            cv=3,
            scoring="neg_root_mean_squared_error",
            n_jobs=-1,
            verbose=0,
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
        importance_gain = self.model.booster_.feature_importance(importance_type="gain")
        importance_split = self.model.booster_.feature_importance(importance_type="split")

        fi_df = pd.DataFrame({
            "feature": feature_names,
            "importance_gain": importance_gain,
            "importance_split": importance_split,
        }).sort_values("importance_gain", ascending=False)

        return fi_df

    def _estimate_uncertainty(self, X: pd.DataFrame, n_iterations: int = 10) -> np.ndarray:
        predictions = []
        n_estimators = self.model.n_estimators_
        step = max(1, n_estimators // n_iterations)

        for i in range(step, n_estimators + 1, step):
            pred = self.model.predict(X, num_iteration=i)
            predictions.append(pred)

        predictions = np.array(predictions)
        uncertainty = np.std(predictions, axis=0)
        return uncertainty

    def predict_with_uncertainty(
        self, X: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray]:
        predictions = self.model.predict(X)
        uncertainty = self._estimate_uncertainty(X)
        return predictions, uncertainty

    def get_feature_interactions(
        self, X: pd.DataFrame, top_k: int = 10
    ) -> pd.DataFrame:
        fi = self.feature_importance
        if fi is None:
            return pd.DataFrame()

        top_features = fi.head(top_k)["feature"].tolist()
        interactions = []

        for i, f1 in enumerate(top_features):
            for f2 in top_features[i + 1:]:
                if f1 in X.columns and f2 in X.columns:
                    corr = X[f1].corr(X[f2])
                    interactions.append({
                        "feature_1": f1,
                        "feature_2": f2,
                        "correlation": corr,
                        "abs_correlation": abs(corr),
                    })

        return pd.DataFrame(interactions).sort_values("abs_correlation", ascending=False)

    def log_to_mlflow(self, run_name: str = "lightgbm-emissions"):
        mlflow.set_experiment(self.experiment_name)
        with mlflow.start_run(run_name=run_name):
            mlflow.log_params(self.best_params)
            mlflow.log_metrics(self.metrics)
            mlflow.lightgbm.log_model(self.model, "model")

    def save(self, path: str):
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, save_path / "lightgbm_emissions.joblib")
        joblib.dump(self.metrics, save_path / "lightgbm_metrics.joblib")
        if self.feature_importance is not None:
            self.feature_importance.to_csv(
                save_path / "lightgbm_feature_importance.csv", index=False
            )

    def load(self, path: str):
        load_path = Path(path)
        self.model = joblib.load(load_path / "lightgbm_emissions.joblib")
        self.metrics = joblib.load(load_path / "lightgbm_metrics.joblib")

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        return self.model.predict(X)
