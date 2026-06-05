from typing import Dict
import mlflow

from backend.training.preprocessor import DataPreprocessor
from backend.training.trainer_xgboost import XGBoostTrainer
from backend.training.trainer_lightgbm import LightGBMTrainer
from backend.training.trainer_classifier import ClassificationTrainer


class TrainingPipeline:
    def __init__(
        self,
        data_path: str = "./data/flare_gas_dataset.csv",
        model_path: str = "./models",
        mlflow_uri: str = "http://localhost:5000",
    ):
        self.data_path = data_path
        self.model_path = model_path
        self.preprocessor = DataPreprocessor()
        self.xgb_trainer = XGBoostTrainer()
        self.lgb_trainer = LightGBMTrainer()
        self.clf_trainer = ClassificationTrainer()

        try:
            mlflow.set_tracking_uri(mlflow_uri)
        except Exception:
            pass

    def run(self, hyperparameter_tuning: bool = False) -> Dict:
        print("=" * 60)
        print("FLARE GAS ML TRAINING PIPELINE")
        print("=" * 60)

        print("\n[1/5] Preprocessing data...")
        X_train, X_test, y_train, y_test = self.preprocessor.preprocess(self.data_path)
        self.preprocessor.save(self.model_path)
        print(f"  Train: {X_train.shape}, Test: {X_test.shape}")

        print("\n[2/5] Training XGBoost (Flare Volume Prediction)...")
        self.xgb_trainer.train(
            X_train,
            y_train["flare_gas_volume"],
            X_test,
            y_test["flare_gas_volume"],
            hyperparameter_tuning=hyperparameter_tuning,
        )
        self.xgb_trainer.save(self.model_path)
        print(f"  Metrics: {self.xgb_trainer.metrics}")

        print("\n[3/5] Training LightGBM (Emission Prediction)...")
        self.lgb_trainer.train(
            X_train,
            y_train["co2_emission_equivalent"],
            X_test,
            y_test["co2_emission_equivalent"],
            hyperparameter_tuning=hyperparameter_tuning,
        )
        self.lgb_trainer.save(self.model_path)
        print(f"  Metrics: {self.lgb_trainer.metrics}")

        print("\n[4/5] Training Classifier (Risk Prediction)...")
        self.clf_trainer.train(
            X_train,
            y_train["flare_event_risk"],
            X_test,
            y_test["flare_event_risk"],
            handle_imbalance=True,
            hyperparameter_tuning=hyperparameter_tuning,
        )
        self.clf_trainer.save(self.model_path)
        print(f"  Metrics: {self.clf_trainer.metrics}")

        print("\n[5/5] Logging to MLflow...")
        try:
            self.xgb_trainer.log_to_mlflow()
            self.lgb_trainer.log_to_mlflow()
            self.clf_trainer.log_to_mlflow()
            print("  MLflow logging complete")
        except Exception as e:
            print(f"  MLflow logging skipped: {e}")

        results = {
            "xgboost_metrics": self.xgb_trainer.metrics,
            "lightgbm_metrics": self.lgb_trainer.metrics,
            "classifier_metrics": self.clf_trainer.metrics,
            "feature_importance_xgb": self.xgb_trainer.feature_importance,
            "feature_importance_lgb": self.lgb_trainer.feature_importance,
        }

        print("\n" + "=" * 60)
        print("TRAINING COMPLETE")
        print("=" * 60)
        return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run ML training pipeline")
    parser.add_argument("--data", type=str, default="./data/flare_gas_dataset.csv")
    parser.add_argument("--models", type=str, default="./models")
    parser.add_argument("--mlflow-uri", type=str, default="http://localhost:5000")
    parser.add_argument("--tune", action="store_true", help="Enable hyperparameter tuning")
    args = parser.parse_args()

    pipeline = TrainingPipeline(
        data_path=args.data,
        model_path=args.models,
        mlflow_uri=args.mlflow_uri,
    )
    results = pipeline.run(hyperparameter_tuning=args.tune)

    print("\nFinal Results Summary:")
    for model_name in ["xgboost_metrics", "lightgbm_metrics", "classifier_metrics"]:
        print(f"\n  {model_name}:")
        for metric, value in results[model_name].items():
            print(f"    {metric}: {value:.4f}")


if __name__ == "__main__":
    main()
