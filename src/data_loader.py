from __future__ import annotations
import pandas as pd


def load_hospital_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    expected_columns = {
        "hospital_id",
        "hospital_name",
        "latitude",
        "longitude",
        "is_open",
        "departments",
        "er_available",
        "trauma_available",
        "capacity_available",
        "estimated_wait_min",
        "hospital_score",
        "severe_case_supported",
    }
    _validate_columns(df, expected_columns, "hospital_data")
    return df


def load_patient_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    expected_columns = {
        "patient_id",
        "symptoms",
        "latitude",
        "longitude",
        "age",
        "heart_rate",
        "systolic_bp",
        "spo2",
        "consciousness",
    }
    _validate_columns(df, expected_columns, "patient_data")
    return df


def load_symptom_department_map(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    expected_columns = {"symptom", "department", "weight"}
    _validate_columns(df, expected_columns, "symptom_department_map")
    return df


def _validate_columns(df: pd.DataFrame, expected_columns: set, name: str) -> None:
    missing = expected_columns - set(df.columns)
    if missing:
        raise ValueError(f"[{name}] Missing columns: {missing}")