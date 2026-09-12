"""
NirmaanAI Forecasting Service Layer
Phase 9: Production & Energy Forecasting

Exposes real-time API services for:
1. Energy Demand Forecasting (multi-horizon hourly active power and energy)
2. Downstream Tariff & Cost Estimation (Peak ₹12.50 vs Base ₹8.50 per kWh)
3. Operational Peak Demand Alerts
4. Daily Production Volume & Throughput Projection

Maintains strict separation:
Forecast (kW) -> Tariff Classification -> Rupee Cost Estimation -> Operational Alert.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from src.utils.config_loader import get_project_root
from src.utils.logger import logger


class HourlyEnergyForecast(BaseModel):
    timestamp: datetime
    hour: int
    predicted_kw: float
    predicted_kwh: float
    is_peak_tariff: bool
    tariff_rate_inr: float
    estimated_cost_inr: float


class EnergyForecastRequest(BaseModel):
    start_time: datetime = Field(description="Start timestamp for forecast horizon")
    horizon_hours: int = Field(default=24, ge=1, le=168, description="Forecast horizon in hours")
    recent_power_history: Optional[List[float]] = Field(
        default=None,
        description="Recent hourly power readings for autoregressive conditioning (up to 168 hours)"
    )


class EnergyForecastResponse(BaseModel):
    start_time: datetime
    horizon_hours: int
    total_predicted_kwh: float
    peak_predicted_kwh: float
    base_predicted_kwh: float
    peak_kwh_ratio: float
    total_estimated_cost_inr: float
    peak_load_warning: bool
    operational_recommendation: str
    hourly_forecasts: List[HourlyEnergyForecast]


class ProductionForecastRequest(BaseModel):
    target_date: datetime
    planned_units: int = Field(default=1200, ge=1)
    is_afternoon_shift_heavy: bool = False


class ProductionForecastResponse(BaseModel):
    target_date: datetime
    planned_units: int
    predicted_completed_units: float
    estimated_fulfillment_rate: float
    schedule_risk_level: str
    operational_advisory: str


class ForecastingService:
    """Production & Energy Forecasting Service managing inference and downstream calculations."""

    def __init__(self, model_artifact_path: Optional[Union[str, Path]] = None):
        root = get_project_root()
        path = Path(model_artifact_path) if model_artifact_path else root / "models" / "forecasting" / "forecaster_champion.joblib"
        
        if not path.exists():
            raise FileNotFoundError(f"Forecasting model artifact not found at: {path}")

        logger.info(f"Loading forecasting artifacts from {path}")
        artifacts = joblib.load(path)
        self.plant_model = artifacts.get("plant_energy_champion")
        self.prod_model = artifacts.get("production_champion")
        self.feature_names_plant = artifacts.get("feature_names_plant", [])
        self.feature_names_prod = artifacts.get("feature_names_prod", [])
        
        tariffs = artifacts.get("tariff_assumptions", {})
        self.base_tariff = tariffs.get("base_tariff_inr", 8.50)
        self.peak_tariff = tariffs.get("peak_tariff_inr", 12.50)

    def forecast_plant_energy(self, request: EnergyForecastRequest) -> EnergyForecastResponse:
        """
        Forecasts hourly plant power demand, applies tariff rules, and computes INR expenditure.
        Strict 4-stage pipeline:
        1. Model forecast (kW)
        2. Tariff classification (Peak 18:00 - 22:00)
        3. Rupee cost projection
        4. Operational alert generation
        """
        start = request.start_time
        horizon = request.horizon_hours
        hourly_records: List[HourlyEnergyForecast] = []

        total_kwh = 0.0
        peak_kwh = 0.0
        base_kwh = 0.0
        total_cost = 0.0

        for h in range(horizon):
            ts = start + timedelta(hours=h)
            hour_of_day = ts.hour
            dow = ts.weekday()
            is_weekend = int(dow >= 5)
            is_peak = (18 <= hour_of_day < 22)
            tariff_rate = self.peak_tariff if is_peak else self.base_tariff

            # Feature synthesis for step
            sin_hour = np.sin(2.0 * np.pi * hour_of_day / 24.0)
            cos_hour = np.cos(2.0 * np.pi * hour_of_day / 24.0)
            sin_dow = np.sin(2.0 * np.pi * dow / 7.0)
            cos_dow = np.cos(2.0 * np.pi * dow / 7.0)

            # Default baseline estimates if no external history supplied
            lag_1h = 60.0  # Nominal multi-machine power baseline
            lag_2h = 60.0
            lag_3h = 60.0
            lag_24h = 60.0
            lag_168h = 60.0
            roll_6h = 60.0
            roll_24h = 60.0
            roll_std_24h = 2.5

            if request.recent_power_history and len(request.recent_power_history) > 0:
                hist = request.recent_power_history
                lag_1h = hist[-1]
                lag_2h = hist[-2] if len(hist) >= 2 else lag_1h
                lag_3h = hist[-3] if len(hist) >= 3 else lag_2h
                lag_24h = hist[-24] if len(hist) >= 24 else lag_1h
                lag_168h = hist[-168] if len(hist) >= 168 else lag_24h
                roll_6h = float(np.mean(hist[-6:])) if len(hist) >= 6 else lag_1h
                roll_24h = float(np.mean(hist[-24:])) if len(hist) >= 24 else lag_1h
                roll_std_24h = float(np.std(hist[-24:])) if len(hist) >= 24 else 2.0

            feat_dict = {
                "hour": hour_of_day,
                "day_of_week": dow,
                "is_weekend": is_weekend,
                "sin_hour": sin_hour,
                "cos_hour": cos_hour,
                "sin_dow": sin_dow,
                "cos_dow": cos_dow,
                "lag_1h": lag_1h,
                "lag_2h": lag_2h,
                "lag_3h": lag_3h,
                "lag_24h": lag_24h,
                "lag_168h": lag_168h,
                "rolling_mean_6h": roll_6h,
                "rolling_mean_24h": roll_24h,
                "rolling_std_24h": roll_std_24h
            }

            feat_vec = np.array([[feat_dict.get(k, 0.0) for k in self.feature_names_plant]])
            pred_kw = float(self.plant_model.predict(feat_vec)[0])

            # Hourly energy in kWh = avg kW * 1h
            pred_kwh = pred_kw * 1.0
            hour_cost = pred_kwh * tariff_rate

            total_kwh += pred_kwh
            total_cost += hour_cost
            if is_peak:
                peak_kwh += pred_kwh
            else:
                base_kwh += pred_kwh

            hourly_records.append(
                HourlyEnergyForecast(
                    timestamp=ts,
                    hour=hour_of_day,
                    predicted_kw=round(pred_kw, 2),
                    predicted_kwh=round(pred_kwh, 2),
                    is_peak_tariff=is_peak,
                    tariff_rate_inr=tariff_rate,
                    estimated_cost_inr=round(hour_cost, 2)
                )
            )

        peak_ratio = peak_kwh / total_kwh if total_kwh > 0 else 0.0
        peak_warning = peak_ratio > 0.25

        if peak_warning:
            rec = "CRITICAL: Over 25% of energy demand falls in peak tariff window (18:00 - 22:00 at ₹12.50/kWh). Recommend rescheduling heavy batch jobs to morning or night shift."
        else:
            rec = "NOMINAL: Electricity consumption within scheduled tariff envelope. Peak tariff exposure is manageable."

        return EnergyForecastResponse(
            start_time=start,
            horizon_hours=horizon,
            total_predicted_kwh=round(total_kwh, 2),
            peak_predicted_kwh=round(peak_kwh, 2),
            base_predicted_kwh=round(base_kwh, 2),
            peak_kwh_ratio=round(peak_ratio, 4),
            total_estimated_cost_inr=round(total_cost, 2),
            peak_load_warning=peak_warning,
            operational_recommendation=rec,
            hourly_forecasts=hourly_records
        )

    def forecast_production_throughput(self, request: ProductionForecastRequest) -> ProductionForecastResponse:
        """Forecasts daily completed unit volume and assesses schedule adherence risk."""
        planned = request.planned_units
        dow = request.target_date.weekday()
        is_weekend = int(dow >= 5)

        feat_dict = {
            "total_planned_jobs": 10,
            "total_planned_units": planned,
            "lag_completed_1d": planned * 0.98,
            "lag_completed_7d": planned * 0.97,
            "prior_completion_rate_3d": 0.98,
            "day_of_week": dow,
            "is_weekend": is_weekend
        }
        feat_vec = np.array([[feat_dict.get(k, 0.0) for k in self.feature_names_prod]])
        pred_units = float(self.prod_model.predict(feat_vec)[0])

        fulfillment_rate = pred_units / planned if planned > 0 else 0.0
        if fulfillment_rate < 0.90:
            risk = "HIGH_RISK"
            advisory = "Forecast indicates <90% planned batch completion. Upstream maintenance or line congestion may constrain shift delivery."
        elif fulfillment_rate < 0.96:
            risk = "MODERATE_RISK"
            advisory = "Slight completion shortfall projected. Buffer capacity is recommended."
        else:
            risk = "LOW_RISK"
            advisory = "Target completion volume aligned with historical throughput capacity."

        return ProductionForecastResponse(
            target_date=request.target_date,
            planned_units=planned,
            predicted_completed_units=round(pred_units, 1),
            estimated_fulfillment_rate=round(fulfillment_rate, 4),
            schedule_risk_level=risk,
            operational_advisory=advisory
        )
