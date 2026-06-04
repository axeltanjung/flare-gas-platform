import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import argparse


class FlareGasDataGenerator:
    def __init__(self, n_rows: int = 150000, seed: int = 42):
        self.n_rows = n_rows
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.facilities = [f"FAC-{str(i).zfill(3)}" for i in range(1, 16)]
        self.flare_stacks = [f"FS-{str(i).zfill(2)}" for i in range(1, 6)]

    def generate_timestamps(self) -> pd.Series:
        start_date = datetime(2021, 1, 1)
        end_date = datetime(2024, 12, 31)
        total_seconds = int((end_date - start_date).total_seconds())
        random_seconds = np.sort(self.rng.integers(0, total_seconds, size=self.n_rows))
        timestamps = pd.to_datetime([start_date + timedelta(seconds=int(s)) for s in random_seconds])
        return timestamps

    def generate_operational_features(self, timestamps: pd.Series) -> pd.DataFrame:
        n = self.n_rows
        hour_of_day = timestamps.hour
        day_of_year = timestamps.dayofyear
        month = timestamps.month

        seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * day_of_year / 365)
        diurnal_factor = 1 + 0.15 * np.sin(2 * np.pi * (hour_of_day - 6) / 24)

        gas_pressure = self.rng.normal(45, 8, n) * seasonal_factor
        gas_pressure = np.clip(gas_pressure, 10, 120)

        gas_flow_rate = self.rng.gamma(4, 50, n) * diurnal_factor
        gas_flow_rate = np.clip(gas_flow_rate, 5, 800)

        methane_ratio = self.rng.beta(8, 2, n)
        ethane_ratio = self.rng.beta(3, 7, n) * (1 - methane_ratio)
        propane_ratio = 1 - methane_ratio - ethane_ratio
        propane_ratio = np.clip(propane_ratio, 0, 1)

        combustion_temperature = self.rng.normal(850, 120, n)
        combustion_temperature = np.clip(combustion_temperature, 400, 1400)

        ambient_temperature = 25 + 15 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        ambient_temperature += self.rng.normal(0, 5, n)

        wind_speed = self.rng.weibull(2, n) * 5
        wind_speed = np.clip(wind_speed, 0, 35)

        humidity = self.rng.beta(4, 3, n) * 100

        return pd.DataFrame({
            "gas_pressure": gas_pressure,
            "gas_flow_rate": gas_flow_rate,
            "methane_ratio": methane_ratio,
            "ethane_ratio": ethane_ratio,
            "propane_ratio": propane_ratio,
            "combustion_temperature": combustion_temperature,
            "ambient_temperature": ambient_temperature,
            "wind_speed": wind_speed,
            "humidity": humidity,
        })

    def generate_process_features(self, operational: pd.DataFrame) -> pd.DataFrame:
        n = self.n_rows

        upstream_pressure = operational["gas_pressure"] * self.rng.uniform(1.2, 2.0, n)
        separator_pressure = operational["gas_pressure"] * self.rng.uniform(0.6, 0.9, n)
        compressor_load = self.rng.beta(5, 3, n) * 100
        valve_opening_pct = self.rng.beta(3, 2, n) * 100
        maintenance_status = self.rng.choice(
            ["NORMAL", "SCHEDULED", "UNSCHEDULED", "EMERGENCY"],
            n,
            p=[0.85, 0.08, 0.05, 0.02],
        )
        production_rate = self.rng.gamma(5, 200, n)
        production_rate = np.clip(production_rate, 50, 5000)

        return pd.DataFrame({
            "upstream_pressure": upstream_pressure,
            "separator_pressure": separator_pressure,
            "compressor_load": compressor_load,
            "valve_opening_percentage": valve_opening_pct,
            "maintenance_status": maintenance_status,
            "production_rate": production_rate,
        })

    def generate_energy_features(self, operational: pd.DataFrame) -> pd.DataFrame:
        n = self.n_rows

        heating_value = (
            operational["methane_ratio"] * 55.5
            + operational["ethane_ratio"] * 51.9
            + operational["propane_ratio"] * 50.3
        )
        heating_value += self.rng.normal(0, 2, n)

        energy_content = operational["gas_flow_rate"] * heating_value / 1000
        fuel_gas_ratio = self.rng.beta(3, 5, n)

        return pd.DataFrame({
            "energy_content_of_gas": energy_content,
            "heating_value": heating_value,
            "fuel_gas_ratio": fuel_gas_ratio,
        })

    def generate_environmental_features(self, operational: pd.DataFrame) -> pd.DataFrame:
        n = self.n_rows

        co2_concentration = self.rng.normal(400, 50, n)
        co2_concentration += operational["gas_flow_rate"] * 0.05
        co2_concentration = np.clip(co2_concentration, 300, 900)

        nox_level = self.rng.gamma(2, 15, n)
        nox_level += operational["combustion_temperature"] * 0.01
        nox_level = np.clip(nox_level, 0, 200)

        methane_slip = self.rng.exponential(0.02, n)
        methane_slip = np.clip(methane_slip, 0, 0.15)

        emission_factor = self.rng.normal(2.5, 0.5, n)
        emission_factor = np.clip(emission_factor, 1.0, 5.0)

        return pd.DataFrame({
            "co2_concentration": co2_concentration,
            "nox_emission_level": nox_level,
            "methane_slip_rate": methane_slip,
            "emission_factor": emission_factor,
        })

    def generate_operational_events(self, timestamps: pd.Series) -> pd.DataFrame:
        n = self.n_rows
        hour = timestamps.hour

        startup_prob = np.where((hour >= 5) & (hour <= 8), 0.03, 0.005)
        shutdown_prob = np.where((hour >= 20) & (hour <= 23), 0.03, 0.005)

        startup_event = self.rng.binomial(1, startup_prob)
        shutdown_event = self.rng.binomial(1, shutdown_prob)
        emergency_relief = self.rng.binomial(1, 0.008, n)
        maintenance_window = self.rng.binomial(1, 0.04, n)
        abnormal_flag = self.rng.binomial(1, 0.06, n)

        return pd.DataFrame({
            "startup_event": startup_event,
            "shutdown_event": shutdown_event,
            "emergency_relief_event": emergency_relief,
            "maintenance_window": maintenance_window,
            "abnormal_operation_flag": abnormal_flag,
        })

    def generate_targets(
        self,
        operational: pd.DataFrame,
        process: pd.DataFrame,
        energy: pd.DataFrame,
        environmental: pd.DataFrame,
        events: pd.DataFrame,
    ) -> pd.DataFrame:
        n = self.n_rows

        base_volume = (
            operational["gas_flow_rate"] * 0.4
            + operational["gas_pressure"] * 0.8
            + process["compressor_load"] * 0.3
            - process["valve_opening_percentage"] * 0.15
            + energy["energy_content_of_gas"] * 0.02
        )

        event_multiplier = (
            1
            + events["startup_event"] * 1.5
            + events["shutdown_event"] * 1.2
            + events["emergency_relief_event"] * 3.0
            + events["abnormal_operation_flag"] * 0.8
        )

        flare_gas_volume = base_volume * event_multiplier
        flare_gas_volume += self.rng.normal(0, 15, n)
        flare_gas_volume = np.clip(flare_gas_volume, 0, None)

        spike_mask = self.rng.random(n) < 0.02
        flare_gas_volume[spike_mask] *= self.rng.uniform(2, 5, spike_mask.sum())

        co2_equivalent = (
            flare_gas_volume
            * environmental["emission_factor"]
            * (1 + environmental["methane_slip_rate"] * 25)
        )
        co2_equivalent += self.rng.normal(0, 10, n)
        co2_equivalent = np.clip(co2_equivalent, 0, None)

        risk_score = (
            0.3 * (operational["gas_pressure"] / 120)
            + 0.25 * (operational["gas_flow_rate"] / 800)
            + 0.2 * events["emergency_relief_event"]
            + 0.15 * events["abnormal_operation_flag"]
            + 0.1 * (environmental["methane_slip_rate"] / 0.15)
        )
        risk_score += self.rng.normal(0, 0.05, n)
        risk_score = np.clip(risk_score, 0, 1)
        flare_event_risk = (risk_score > 0.55).astype(int)

        emission_intensity = co2_equivalent / (process["production_rate"] + 1)
        emission_intensity = np.clip(emission_intensity, 0, 50)

        compliance_score = (
            0.4 * (emission_intensity / 50)
            + 0.3 * (flare_gas_volume / flare_gas_volume.max())
            + 0.3 * risk_score
        )
        compliance_risk = pd.cut(
            compliance_score,
            bins=[0, 0.3, 0.6, 1.01],
            labels=["LOW", "MEDIUM", "HIGH"],
        )

        return pd.DataFrame({
            "flare_gas_volume": np.round(flare_gas_volume, 2),
            "co2_emission_equivalent": np.round(co2_equivalent, 2),
            "flare_event_risk": flare_event_risk,
            "emission_intensity_index": np.round(emission_intensity, 4),
            "compliance_risk_level": compliance_risk,
        })

    def inject_data_quality_issues(self, df: pd.DataFrame) -> pd.DataFrame:
        n = len(df)
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            missing_mask = self.rng.random(n) < 0.015
            df.loc[missing_mask, col] = np.nan

        for col in ["gas_pressure", "gas_flow_rate", "combustion_temperature"]:
            if col in df.columns:
                outlier_mask = self.rng.random(n) < 0.005
                df.loc[outlier_mask, col] *= self.rng.uniform(3, 6, outlier_mask.sum())

        time_index = np.arange(n) / n
        drift_cols = ["gas_flow_rate", "co2_concentration", "emission_factor"]
        for col in drift_cols:
            if col in df.columns:
                drift = time_index * df[col].std() * 0.3
                df[col] = df[col] + drift

        return df

    def generate(self) -> pd.DataFrame:
        print(f"Generating {self.n_rows:,} rows of synthetic flare gas data...")

        timestamps = self.generate_timestamps()
        facility_ids = self.rng.choice(self.facilities, self.n_rows)
        flare_stack_ids = self.rng.choice(self.flare_stacks, self.n_rows)

        operational = self.generate_operational_features(timestamps)
        process = self.generate_process_features(operational)
        energy = self.generate_energy_features(operational)
        environmental = self.generate_environmental_features(operational)
        events = self.generate_operational_events(timestamps)
        targets = self.generate_targets(operational, process, energy, environmental, events)

        df = pd.concat(
            [
                pd.DataFrame({
                    "timestamp": timestamps,
                    "facility_id": facility_ids,
                    "flare_stack_id": flare_stack_ids,
                }),
                operational,
                process,
                energy,
                environmental,
                events,
                targets,
            ],
            axis=1,
        )

        df = self.inject_data_quality_issues(df)
        print(f"Dataset generated: {df.shape[0]} rows, {df.shape[1]} columns")
        return df

    def save(self, df: pd.DataFrame, output_dir: str = "./data"):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        csv_path = output_path / "flare_gas_dataset.csv"
        df.to_csv(csv_path, index=False)
        print(f"Saved dataset to {csv_path}")

        meta = {
            "dataset_name": "Synthetic Flare Gas Emissions Dataset",
            "version": "1.0.0",
            "n_rows": len(df),
            "n_columns": len(df.columns),
            "date_range": f"{df['timestamp'].min()} to {df['timestamp'].max()}",
            "facilities": len(df["facility_id"].unique()),
            "features": list(df.columns),
            "targets": [
                "flare_gas_volume",
                "co2_emission_equivalent",
                "flare_event_risk",
                "emission_intensity_index",
                "compliance_risk_level",
            ],
            "missing_rate": f"{df.isnull().mean().mean():.2%}",
        }

        import json
        meta_path = output_path / "dataset_metadata.json"
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2, default=str)
        print(f"Saved metadata to {meta_path}")

        return csv_path


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic flare gas dataset")
    parser.add_argument("--rows", type=int, default=150000, help="Number of rows")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", type=str, default="./data", help="Output directory")
    args = parser.parse_args()

    generator = FlareGasDataGenerator(n_rows=args.rows, seed=args.seed)
    df = generator.generate()
    generator.save(df, args.output)

    print("\nDataset Summary:")
    print(f"  Shape: {df.shape}")
    print(f"  Memory: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    print(f"  Missing values: {df.isnull().sum().sum():,}")
    print(f"\nTarget distributions:")
    print(f"  Flare volume: mean={df['flare_gas_volume'].mean():.1f}, std={df['flare_gas_volume'].std():.1f}")
    print(f"  CO2 equivalent: mean={df['co2_emission_equivalent'].mean():.1f}")
    print(f"  Event risk: {df['flare_event_risk'].mean():.2%} positive")
    print(f"  Compliance: {df['compliance_risk_level'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()
