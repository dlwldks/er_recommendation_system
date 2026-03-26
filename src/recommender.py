from __future__ import annotations
from typing import List
import pandas as pd

from src.preprocessing import preprocess_patient_row
from src.department import map_symptom_to_department
from src.severity import classify_severity
from src.filtering import filter_candidate_hospitals
from src.scoring import (
    compute_distance_and_time_features,
    normalize_features,
    score_hospitals,
)
from src.explanation import generate_explanation


def recommend_top_k(
    patient_row: pd.Series,
    hospitals_df: pd.DataFrame,
    symptom_map_df: pd.DataFrame,
    top_k: int = 3,
) -> pd.DataFrame:
    patient = preprocess_patient_row(patient_row)

    severity = classify_severity(patient)
    required_department, dept_scores = map_symptom_to_department(
        patient["symptom_list"], symptom_map_df
    )

    candidates = filter_candidate_hospitals(
        hospitals_df=hospitals_df,
        required_department=required_department,
        severity=severity,
    )

    if candidates.empty:
        return pd.DataFrame(
            [
                {
                    "rank": 1,
                    "patient_id": patient["patient_id"],
                    "severity": severity,
                    "required_department": required_department,
                    "hospital_id": None,
                    "hospital_name": "No available hospital",
                    "distance_km": None,
                    "travel_time_min": None,
                    "estimated_wait_min": None,
                    "total_time_min": None,
                    "distance_score": None,
                    "waiting_score": None,
                    "specialty_score": None,
                    "hospital_score_norm": None,
                    "urgency_fit_score": None,
                    "final_score": 0.0,
                    "explanation": "조건을 만족하는 병원을 찾지 못했습니다.",
                }
            ]
        )

    candidates = compute_distance_and_time_features(
        candidates,
        patient_lat=float(patient["latitude"]),
        patient_lon=float(patient["longitude"]),
    )

    candidates = normalize_features(
        candidates,
        required_department=required_department,
        severity=severity,
    )

    ranked = score_hospitals(candidates, severity=severity).head(top_k).copy()
    ranked = ranked.reset_index(drop=True)
    ranked["rank"] = ranked.index + 1

    ranked["patient_id"] = patient["patient_id"]
    ranked["severity"] = severity
    ranked["required_department"] = required_department
    ranked["department_score_details"] = str(dept_scores)

    ranked["explanation"] = ranked.apply(
        lambda row: generate_explanation(
            row=row,
            required_department=required_department,
            severity=severity,
        ),
        axis=1,
    )

    result_columns = [
        "rank",
        "patient_id",
        "severity",
        "required_department",
        "hospital_id",
        "hospital_name",
        "distance_km",
        "travel_time_min",
        "estimated_wait_min",
        "total_time_min",
        "distance_score",
        "waiting_score",
        "specialty_score",
        "hospital_score_norm",
        "urgency_fit_score",
        "final_score",
        "explanation",
    ]

    return ranked[result_columns]


def recommend_for_all_patients(
    patients_df: pd.DataFrame,
    hospitals_df: pd.DataFrame,
    symptom_map_df: pd.DataFrame,
    top_k: int = 3,
) -> pd.DataFrame:
    outputs: List[pd.DataFrame] = []

    for _, patient_row in patients_df.iterrows():
        rec_df = recommend_top_k(
            patient_row=patient_row,
            hospitals_df=hospitals_df,
            symptom_map_df=symptom_map_df,
            top_k=top_k,
        )
        outputs.append(rec_df)

    return pd.concat(outputs, ignore_index=True)