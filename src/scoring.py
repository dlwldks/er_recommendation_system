from __future__ import annotations
from typing import Dict
import numpy as np
import pandas as pd

from src.config import SEVERITY_WEIGHTS, AVERAGE_TRAVEL_SPEED_KMH, GOLDEN_TIME_MINUTES
from src.geo_utils import haversine_distance_km


def estimate_travel_time_min(distance_km: float) -> float:
    return (distance_km / AVERAGE_TRAVEL_SPEED_KMH) * 60.0


def estimate_total_time(distance_km: float, waiting_min: float) -> float:
    travel_min = estimate_travel_time_min(distance_km)
    return travel_min + waiting_min


def compute_distance_and_time_features(
    candidate_df: pd.DataFrame,
    patient_lat: float,
    patient_lon: float,
) -> pd.DataFrame:
    df = candidate_df.copy()

    distances = []
    travel_times = []
    total_times = []

    for _, row in df.iterrows():
        distance_km = haversine_distance_km(
            patient_lat,
            patient_lon,
            float(row["latitude"]),
            float(row["longitude"]),
        )
        travel_min = estimate_travel_time_min(distance_km)
        total_time = estimate_total_time(distance_km, float(row["estimated_wait_min"]))

        distances.append(distance_km)
        travel_times.append(travel_min)
        total_times.append(total_time)

    df["distance_km"] = distances
    df["travel_time_min"] = travel_times
    df["total_time_min"] = total_times
    return df


def _minmax_normalize(series: pd.Series, reverse: bool = False) -> pd.Series:
    s = series.astype(float)
    min_v = s.min()
    max_v = s.max()

    if np.isclose(max_v, min_v):
        base = pd.Series(np.ones(len(s)), index=s.index)
    else:
        base = (s - min_v) / (max_v - min_v)

    if reverse:
        base = 1.0 - base

    return base.clip(0.0, 1.0)


def normalize_features(df: pd.DataFrame, required_department: str, severity: str) -> pd.DataFrame:
    result = df.copy()

    result["distance_score"] = _minmax_normalize(result["distance_km"], reverse=True)
    result["waiting_score"] = _minmax_normalize(result["estimated_wait_min"], reverse=True)
    result["hospital_score_norm"] = _minmax_normalize(result["hospital_score"], reverse=False)

    result["specialty_score"] = result["departments"].apply(
        lambda x: 1.0 if required_department.lower() in str(x).lower() else 0.7
    )

    golden_time = GOLDEN_TIME_MINUTES[severity]
    result["urgency_fit_score"] = result["total_time_min"].apply(
        lambda x: 1.0 if x <= golden_time else max(0.0, 1.0 - ((x - golden_time) / golden_time))
    )

    return result


def score_hospitals(df: pd.DataFrame, severity: str) -> pd.DataFrame:
    weights: Dict[str, float] = SEVERITY_WEIGHTS[severity]
    result = df.copy()

    result["final_score"] = (
        result["distance_score"] * weights["distance_score"]
        + result["waiting_score"] * weights["waiting_score"]
        + result["specialty_score"] * weights["specialty_score"]
        + result["hospital_score_norm"] * weights["hospital_score_norm"]
        + result["urgency_fit_score"] * weights["urgency_fit_score"]
    )

    return result.sort_values(by="final_score", ascending=False).reset_index(drop=True)