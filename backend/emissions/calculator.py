import numpy as np
import pandas as pd
from typing import Optional
from dataclasses import dataclass


@dataclass
class EmissionFactors:
    co2_per_m3_natural_gas: float = 2.34
    ch4_gwp: float = 28.0
    n2o_gwp: float = 265.0
    flare_combustion_efficiency: float = 0.98
    methane_destruction_efficiency: float = 0.995
    default_heating_value_mj_per_m3: float = 38.0


class EmissionCalculator:
    def __init__(self, factors: Optional[EmissionFactors] = None):
        self.factors = factors or EmissionFactors()

    def calculate_co2_from_flaring(
        self,
        flare_volume_m3: np.ndarray,
        gas_composition_methane: np.ndarray,
        combustion_efficiency: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        if combustion_efficiency is None:
            combustion_efficiency = np.full_like(
                flare_volume_m3, self.factors.flare_combustion_efficiency
            )

        combusted_volume = flare_volume_m3 * combustion_efficiency
        co2_emissions = combusted_volume * self.factors.co2_per_m3_natural_gas
        co2_emissions *= gas_composition_methane

        return co2_emissions

    def calculate_methane_slip(
        self,
        flare_volume_m3: np.ndarray,
        methane_fraction: np.ndarray,
        combustion_efficiency: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        if combustion_efficiency is None:
            combustion_efficiency = np.full_like(
                flare_volume_m3, self.factors.flare_combustion_efficiency
            )

        uncombusted = flare_volume_m3 * (1 - combustion_efficiency)
        methane_slip = uncombusted * methane_fraction
        return methane_slip

    def calculate_co2_equivalent(
        self,
        co2_direct: np.ndarray,
        methane_slip: np.ndarray,
        nox_emissions: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        co2e = co2_direct + (methane_slip * self.factors.ch4_gwp)
        if nox_emissions is not None:
            co2e += nox_emissions * self.factors.n2o_gwp * 0.001
        return co2e

    def calculate_emission_intensity(
        self,
        co2_equivalent: np.ndarray,
        production_volume: np.ndarray,
    ) -> np.ndarray:
        intensity = co2_equivalent / (production_volume + 1e-8)
        return intensity

    def calculate_energy_wasted(
        self,
        flare_volume_m3: np.ndarray,
        heating_value: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        if heating_value is None:
            heating_value = np.full_like(
                flare_volume_m3, self.factors.default_heating_value_mj_per_m3
            )
        energy_mj = flare_volume_m3 * heating_value
        return energy_mj

    def batch_calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        co2_direct = self.calculate_co2_from_flaring(
            df["flare_gas_volume"].values,
            df["methane_ratio"].values,
        )

        methane_slip = self.calculate_methane_slip(
            df["flare_gas_volume"].values,
            df["methane_ratio"].values,
        )

        nox = df["nox_emission_level"].values if "nox_emission_level" in df.columns else None
        co2e = self.calculate_co2_equivalent(co2_direct, methane_slip, nox)

        production = df["production_rate"].values if "production_rate" in df.columns else np.ones(len(df))
        intensity = self.calculate_emission_intensity(co2e, production)

        heating = df["heating_value"].values if "heating_value" in df.columns else None
        energy_wasted = self.calculate_energy_wasted(df["flare_gas_volume"].values, heating)

        results = pd.DataFrame({
            "co2_direct_tonnes": co2_direct / 1000,
            "methane_slip_kg": methane_slip,
            "co2_equivalent_tonnes": co2e / 1000,
            "emission_intensity_kg_per_bbl": intensity,
            "energy_wasted_mj": energy_wasted,
            "energy_wasted_mwh": energy_wasted / 3600,
        })

        return results
