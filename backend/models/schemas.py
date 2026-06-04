from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class ComplianceLevel(str, Enum)
    LOW = LOW
    MEDIUM = MEDIUM
    HIGH = HIGH


class PredictionInput(BaseModel)
    gas_pressure float = Field(..., ge=0, description=Gas pressure in kPa)
    gas_flow_rate float = Field(..., ge=0, description=Gas flow rate in m3h)
    methane_ratio float = Field(..., ge=0, le=1)
    ethane_ratio float = Field(..., ge=0, le=1)
    propane_ratio float = Field(..., ge=0, le=1)
    combustion_temperature float = Field(..., ge=200)
    ambient_temperature float
    wind_speed float = Field(..., ge=0)
    humidity float = Field(..., ge=0, le=100)
    upstream_pressure float = Field(..., ge=0)
    separator_pressure float = Field(..., ge=0)
    compressor_load float = Field(..., ge=0, le=100)
    valve_opening_percentage float = Field(..., ge=0, le=100)
    maintenance_status str = Field(default=NORMAL)
    production_rate float = Field(..., ge=0)
    energy_content_of_gas Optional[float] = None
    heating_value Optional[float] = None
    fuel_gas_ratio Optional[float] = None
    co2_concentration Optional[float] = None
    nox_emission_level Optional[float] = None
    methane_slip_rate Optional[float] = None
    emission_factor Optional[float] = None
    startup_event int = Field(default=0, ge=0, le=1)
    shutdown_event int = Field(default=0, ge=0, le=1)
    emergency_relief_event int = Field(default=0, ge=0, le=1)
    maintenance_window int = Field(default=0, ge=0, le=1)
    abnormal_operation_flag int = Field(default=0, ge=0, le=1)


class FlareVolumeResponse(BaseModel)
    predicted_volume_m3 float
    confidence_interval_lower float
    confidence_interval_upper float
    model_version str = xgboost-v1.0


class EmissionPredictionResponse(BaseModel)
    co2_equivalent_tonnes float
    direct_co2_tonnes float
    methane_slip_kg float
    emission_intensity float
    energy_wasted_mwh float
    model_version str = lightgbm-v1.0


class RiskPredictionResponse(BaseModel)
    risk_probability float
    risk_label str
    threshold_used float
    contributing_factors List[Dict[str, Any]]


class EmissionReportRequest(BaseModel)
    facility_id Optional[str] = None
    start_date Optional[str] = None
    end_date Optional[str] = None
    period str = D


class EmissionReportResponse(BaseModel)
    summary Dict[str, Any]
    facility_breakdown List[Dict[str, Any]]
    compliance Dict[str, Any]
    trend_data List[Dict[str, Any]]


class ComplianceStatusResponse(BaseModel)
    facility_id str
    compliance_score float
    status str
    violations List[Dict[str, Any]]
    recommendations List[str]


class ExplainResponse(BaseModel)
    expected_value float
    top_drivers List[Dict[str, Any]]
    operational_insights List[str]


class FacilityResponse(BaseModel)
    facility_id str
    total_co2e_tonnes float
    total_flare_volume float
    avg_emission_intensity float
    compliance_status str
    risk_events int
    record_count int


class HealthResponse(BaseModel)
    status str
    version str
    models_loaded Dict[str, bool]
    timestamp str


class BatchPredictionInput(BaseModel)
    records List[PredictionInput]


class OptimizationSuggestion(BaseModel)
    category str
    suggestion str
    estimated_reduction_pct float
    priority str
    affected_metric str
