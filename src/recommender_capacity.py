from __future__ import annotations
from typing import Dict, List, Tuple
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


def initialize_capacity_state(hospitals_df: pd.DataFrame) -> Dict[str, int]:
    """
    병원별 남은 capacity 상태를 초기화한다.
    """
    capacity_state: Dict[str, int] = {}
    for _, row in hospitals_df.iterrows():
        hospital_id = str(row["hospital_id"])
        max_capacity = int(row.get("max_capacity", 1))
        capacity_state[hospital_id] = max_capacity
    return capacity_state


def apply_capacity_filter(
    candidates_df: pd.DataFrame,
    capacity_state: Dict[str, int],
) -> pd.DataFrame:
    """
    남은 capacity가 1 이상인 병원만 유지한다.
    """
    df = candidates_df.copy()
    df = df[df["hospital_id"].astype(str).map(lambda x: capacity_state.get(x, 0) > 0)]
    return df.reset_index(drop=True)


def assign_single_patient_with_capacity(
    patient_row: pd.Series,
    hospitals_df: pd.DataFrame,
    symptom_map_df: pd.DataFrame,
    capacity_state: Dict[str, int],
    top_k: int = 3,
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    환자 1명을 capacity-aware 방식으로 추천/배정한다.
    rank 1 병원이 실제 배정 병원이 되며, 해당 병원의 capacity를 1 감소시킨다.
    """
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

    candidates = apply_capacity_filter(candidates, capacity_state)

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
                    "remaining_capacity_after_assignment": None,
                    "explanation": "남은 수용 capacity를 고려했을 때 조건을 만족하는 병원을 찾지 못했습니다.",
                }
            ]
        ), capacity_state

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

    # rank 1 실제 배정
    assigned_hospital_id = str(ranked.iloc[0]["hospital_id"])
    capacity_state[assigned_hospital_id] = max(0, capacity_state[assigned_hospital_id] - 1)

    ranked["remaining_capacity_after_assignment"] = ranked["hospital_id"].astype(str).map(
        lambda x: capacity_state.get(x, 0)
    )

    ranked["explanation"] = ranked.apply(
        lambda row: generate_explanation(
            row=row,
            required_department=required_department,
            severity=severity,
        ),
        axis=1,
    )

    # rank 1 설명에 capacity 정보 추가
    ranked.loc[ranked["rank"] == 1, "explanation"] = ranked.loc[
        ranked["rank"] == 1, "explanation"
    ] + ranked.loc[ranked["rank"] == 1, "remaining_capacity_after_assignment"].apply(
        lambda x: f" 실제 배정 후 남은 수용 가능 인원은 {int(x)}명입니다."
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
        "remaining_capacity_after_assignment",
        "explanation",
    ]

    return ranked[result_columns], capacity_state


def recommend_for_all_patients_with_capacity(
    patients_df: pd.DataFrame,
    hospitals_df: pd.DataFrame,
    symptom_map_df: pd.DataFrame,
    top_k: int = 3,
    sort_by_severity_first: bool = True,
) -> pd.DataFrame:
    """
    전체 환자를 capacity-aware 방식으로 순차 배정한다.

    sort_by_severity_first=True이면
    critical -> severe -> moderate -> mild 순으로 우선 배정한다.
    """
    working_patients_df = patients_df.copy()

    if sort_by_severity_first:
        severity_priority = {
            "critical": 0,
            "severe": 1,
            "moderate": 2,
            "mild": 3,
        }

        tmp_rows = []
        for _, row in working_patients_df.iterrows():
            patient = preprocess_patient_row(row)
            sev = classify_severity(patient)
            row_dict = row.to_dict()
            row_dict["severity_for_order"] = sev
            row_dict["severity_order"] = severity_priority.get(sev, 99)
            tmp_rows.append(row_dict)

        working_patients_df = pd.DataFrame(tmp_rows).sort_values(
            by=["severity_order", "patient_id"],
            ascending=[True, True],
        ).reset_index(drop=True)

        working_patients_df = working_patients_df.drop(columns=["severity_for_order", "severity_order"])

    outputs: List[pd.DataFrame] = []
    capacity_state = initialize_capacity_state(hospitals_df)

    for _, patient_row in working_patients_df.iterrows():
        rec_df, capacity_state = assign_single_patient_with_capacity(
            patient_row=patient_row,
            hospitals_df=hospitals_df,
            symptom_map_df=symptom_map_df,
            capacity_state=capacity_state,
            top_k=top_k,
        )
        outputs.append(rec_df)

    return pd.concat(outputs, ignore_index=True)