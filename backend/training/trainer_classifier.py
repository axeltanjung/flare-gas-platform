import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    precision_recall_curve,
    f1_score,
    confusion_matrix,
)
from sklearn.model_selection import GridSearchCV
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import mlflow
import joblib
from pathlib import Path
from typing import Dict, Optional, Tuple


class ClassificationTrainer:
    def __init__(self, experiment_name: str = "flare-gas-classification"):
        self.experiment_name = experiment_name
        self.model: Optional[GradientBoostingClassifier] = None
        self.best_params: Dict = {}
        self.metrics: Dict = {}
        self.optimal_threshold: float = 0.5
        self.classification_report: Optional[Dict] = None

    def get_default_params(self) -> Dict:
        return {
            "n_estimators": 400,
            "max_depth": 6,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "min_samples_split": 10,
            "min_samples_leaf": 5,
            "random_state": 42,
        }

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        handle_imbalance: bool = True,
        hyperparameter_tuning: bool = False,
    ) -> GradientBoostingClassifier:
        if handle_imbalance:
            smote = SMOTE(random_state=42, sampling_strategy=0.5)
            X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
        else:
            X_resampled, y_resampled = X_train, y_train

        if hyperparameter_tuning:
            self.model = self._train_with_tuning(X_resampled, y_resampled)
        else:
            params = self.get_default_params()
            self.model = GradientBoostingClassifier(**params)
            self.model.fit(X_resampled, y_resampled)
            self.best_params = params

        probabilities = self.model.predict_proba(X_test)[:, 1]
        self.optimal_threshold = self._find_optimal_threshold(y_test, probabilities)
        predictions = (probabilities >= self.optimal_threshold).astype(int)

        self.metrics = self._compute_metrics(y_test, predictions, probabilities)
        self.classification_report = classification_report(y_test, predictions, output_dict=True)

        return self.model

    def _train_with_tuning(
        self, X_train: pd.DataFrame, y_train: pd.Series
    ) -> GradientBoostingClassifier:
        param_grid = {
            "max_depth": [4, 6, 8],
            "learning_rate": [0.01, 0.05, 0.1],
            "n_estimators": [200, 400, 600],
            "subsample": [0.7, 0.8, 0.9],
        }
        base_model = GradientBoostingClassifier(random_state=42)
        grid = GridSearchCV(
            base_model,
            param_grid,
            cv=3,
            scoring="f1",
            n_jobs=-1,
            verbose=0,
        )
        grid.fit(X_train, y_train)
        self.best_params = grid.best_params_
        return grid.best_estimator_

    def _find_optimal_threshold(
        self, y_true: pd.Series, probabilities: np.ndarray
    ) -> float:
        precisions, recalls, thresholds = precision_recall_curve(y_true, probabilities)
        f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-8)
        optimal_idx = np.argmax(f1_scores)
        return float(thresholds[optimal_idx]) if optimal_idx < len(thresholds) else 0.5

    def _compute_metrics(
        self, y_true: pd.Series, y_pred: np.ndarray, y_prob: np.ndarray
    ) -> Dict:
        cm = confusion_matrix(y_true, y_pred)
        return {
            "accuracy": float((y_pred == y_true).mean()),
            "f1_score": float(f1_score(y_true, y_pred)),
            "roc_auc": float(roc_auc_score(y_true, y_prob)),
            "precision": float(cm[1, 1] / (cm[1, 1] + cm[0, 1] + 1e-8)),
            "recall": float(cm[1, 1] / (cm[1, 1] + cm[1, 0] + 1e-8)),
            "optimal_threshold": self.optimal_threshold,
            "true_positives": int(cm[1, 1]),
            "false_positives": int(cm[0, 1]),
            "true_negatives": int(cm[0, 0]),
            "false_negatives": int(cm[1, 0]),
        }

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        return self.model.predict_proba(X)[:, 1]

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        probabilities = self.predict_proba(X)
        return (probabilities >= self.optimal_threshold).astype(int)

    def log_to_mlflow(self, run_name: str = "classification-risk"):
        mlflow.set_experiment(self.experiment_name)
        with mlflow.start_run(run_name=run_name):
            mlflow.log_params(self.best_params)
            mlflow.log_metrics(self.metrics)
            mlflow.sklearn.log_model(self.model, "model")
            mlflow.log_param("optimal_threshold", self.optimal_threshold)

    def save(self, path: str):
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, save_path / "classifier_risk.joblib")
        joblib.dump(self.metrics, save_path / "classifier_metrics.joblib")
        joblib.dump(self.optimal_threshold, save_path / "optimal_threshold.joblib")

    def load(self, path: str):
        load_path = Path(path)
        self.model = joblib.load(load_path / "classifier_risk.joblib")
        self.metrics = joblib.load(load_path / "classifier_metrics.joblib")
        self.optimal_threshold = joblib.load(load_path / "optimal_threshold.joblib")
