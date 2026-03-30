from __future__ import annotations

import pandas as pd


SEVERITY_WEIGHT_MAP = {
    "critical": {
        "distance_score": 0.25,
        "waiting_score": 0.20,
        "specialty_score": 0.15,
        "hospital_score_norm": 0.10,
        "urgency_fit_score": 0.30,
    },
    "severe": {
        "distance_score": 0.22,
        "waiting_score": 0.23,
        "specialty_score": 0.18,
        "hospital_score_norm": 0.12,
        "urgency_fit_score": 0.25,
    },
    "moderate": {
        "distance_score": 0.20,
        "waiting_score": 0.28,
        "specialty_score": 0.20,
        "hospital_score_norm": 0.17,
        "urgency_fit_score": 0.15,
    },
    "mild": {
        "distance_score": 0.15,
        "waiting_score": 0.30,
        "specialty_score": 0.20,
        "hospital_score_norm": 0.25,
        "urgency_fit_score": 0.10,
    },
}


def _ensure_score_columns(df: pd.DataFrame) -> pd.DataFrame:
    working_df = df.copy()

    required_cols = [
        "distance_score",
        "waiting_score",
        "specialty_score",
        "hospital_score_norm",
        "urgency_fit_score",
    ]

    for col in required_cols:
        if col not in working_df.columns:
            working_df[col] = 0.0

    return working_df


def score_hospitals_by_severity_adaptive(
    candidates_df: pd.DataFrame,
    severity: str,
) -> pd.DataFrame:
    working_df = _ensure_score_columns(candidates_df)

    weights = SEVERITY_WEIGHT_MAP.get(
        severity,
        SEVERITY_WEIGHT_MAP["moderate"],
    )

    working_df["final_score"] = (
        working_df["distance_score"] * weights["distance_score"]
        + working_df["waiting_score"] * weights["waiting_score"]
        + working_df["specialty_score"] * weights["specialty_score"]
        + working_df["hospital_score_norm"] * weights["hospital_score_norm"]
        + working_df["urgency_fit_score"] * weights["urgency_fit_score"]
    )

    working_df = working_df.sort_values(
        by=["final_score", "total_time_min", "distance_km"],
        ascending=[False, True, True],
    ).reset_index(drop=True)

    return working_df