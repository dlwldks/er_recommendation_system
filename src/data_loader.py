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
        "max_capacity",
    }
    _validate_columns(df, expected_columns, "hospital_data")

    df["hospital_id"] = df["hospital_id"].astype(str)
    df["hospital_name"] = df["hospital_name"].astype(str)
    df["departments"] = df["departments"].fillna("").astype(str)

    numeric_columns = [
        "latitude",
        "longitude",
        "is_open",
        "er_available",
        "trauma_available",
        "capacity_available",
        "estimated_wait_min",
        "hospital_score",
        "severe_case_supported",
        "max_capacity",
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

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

    df["patient_id"] = df["patient_id"].astype(str)
    df["symptoms"] = df["symptoms"].fillna("").astype(str)
    df["consciousness"] = df["consciousness"].fillna("alert").astype(str)

    numeric_columns = [
        "latitude",
        "longitude",
        "age",
        "heart_rate",
        "systolic_bp",
        "spo2",
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def load_symptom_department_map(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    expected_columns = {"symptom", "department", "weight"}
    _validate_columns(df, expected_columns, "symptom_department_map")

    df["symptom"] = df["symptom"].astype(str).str.strip().str.lower()
    df["department"] = df["department"].astype(str).str.strip().str.lower()
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")

    return df


def _validate_columns(df: pd.DataFrame, expected_columns: set, name: str) -> None:
    missing = expected_columns - set(df.columns)
    if missing:
        raise ValueError(f"[{name}] Missing columns: {missing}")