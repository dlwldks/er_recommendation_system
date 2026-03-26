from __future__ import annotations
import pandas as pd


def filter_candidate_hospitals(
    hospitals_df: pd.DataFrame,
    required_department: str,
    severity: str,
) -> pd.DataFrame:
    """
    하드 필터링:
    1) 운영 중
    2) 응급실 이용 가능
    3) 수용 가능
    4) 진료과 적합
    5) 중증이면 severe_case_supported 필요
    """
    df = hospitals_df.copy()

    df = df[df["is_open"] == 1]
    df = df[df["capacity_available"] == 1]

    if severity in {"critical", "severe"}:
        df = df[df["er_available"] == 1]

    df = df[
        df["departments"].fillna("").str.lower().str.contains(required_department.lower(), regex=False)
        | df["departments"].fillna("").str.lower().str.contains("emergency_medicine", regex=False)
    ]

    if severity in {"critical", "severe"}:
        df = df[df["severe_case_supported"] == 1]

    return df.reset_index(drop=True)