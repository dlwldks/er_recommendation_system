# src/evaluation.py
# ------------------------------------------------------------
# 모델별 추천 결과 CSV를 읽어서 비교 지표를 계산하는 파일
# - Top-1 추천 기준으로 모델 성능 비교
# - 평균 거리, 평균 대기시간, 평균 총 소요시간 계산
# - 특정 병원 쏠림 정도(max concentration) 계산
# - 병원별 환자 배정 분포 테이블 생성
# ------------------------------------------------------------

from __future__ import annotations

import os
from typing import Dict, List

import pandas as pd


def _safe_numeric_mean(series: pd.Series) -> float:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return 0.0
    return float(numeric.mean())


def _safe_numeric_std(series: pd.Series) -> float:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return 0.0
    return float(numeric.std(ddof=0))


def _top1_only(df: pd.DataFrame) -> pd.DataFrame:
    if "rank" not in df.columns:
        return df.copy()
    return df[df["rank"] == 1].copy()


def compute_model_metrics(
    recommendations_df: pd.DataFrame,
    model_name: str,
) -> Dict[str, float | int | str]:
    top1_df = _top1_only(recommendations_df)
    valid_top1_df = top1_df[top1_df["hospital_id"].notna()].copy()

    patient_count = int(top1_df["patient_id"].nunique()) if "patient_id" in top1_df.columns else len(top1_df)
    assigned_count = int(valid_top1_df["patient_id"].nunique()) if "patient_id" in valid_top1_df.columns else len(valid_top1_df)
    unassigned_count = max(patient_count - assigned_count, 0)

    avg_distance_km = _safe_numeric_mean(valid_top1_df.get("distance_km", pd.Series(dtype=float)))
    avg_wait_min = _safe_numeric_mean(valid_top1_df.get("estimated_wait_min", pd.Series(dtype=float)))
    avg_total_time_min = _safe_numeric_mean(valid_top1_df.get("total_time_min", pd.Series(dtype=float)))
    avg_final_score = _safe_numeric_mean(valid_top1_df.get("final_score", pd.Series(dtype=float)))

    hospital_distribution = (
        valid_top1_df["hospital_name"].value_counts(dropna=True)
        if "hospital_name" in valid_top1_df.columns
        else pd.Series(dtype=int)
    )

    unique_assigned_hospitals = int(hospital_distribution.shape[0])

    max_concentration_count = int(hospital_distribution.max()) if not hospital_distribution.empty else 0
    max_concentration_ratio = (
        float(max_concentration_count / assigned_count) if assigned_count > 0 else 0.0
    )

    assignment_std = _safe_numeric_std(hospital_distribution.astype(float)) if not hospital_distribution.empty else 0.0

    return {
        "model_name": model_name,
        "patient_count": patient_count,
        "assigned_count": assigned_count,
        "unassigned_count": unassigned_count,
        "avg_distance_km": round(avg_distance_km, 4),
        "avg_wait_min": round(avg_wait_min, 4),
        "avg_total_time_min": round(avg_total_time_min, 4),
        "avg_final_score": round(avg_final_score, 6),
        "unique_assigned_hospitals": unique_assigned_hospitals,
        "max_concentration_count": max_concentration_count,
        "max_concentration_ratio": round(max_concentration_ratio, 4),
        "assignment_std": round(assignment_std, 4),
    }


def build_hospital_assignment_table(
    recommendations_df: pd.DataFrame,
    model_name: str,
) -> pd.DataFrame:
    top1_df = _top1_only(recommendations_df)
    valid_top1_df = top1_df[top1_df["hospital_name"].notna()].copy()

    if valid_top1_df.empty:
        return pd.DataFrame(columns=["model_name", "hospital_name", "assigned_patients"])

    hospital_counts = (
        valid_top1_df.groupby("hospital_name")["patient_id"]
        .nunique()
        .reset_index(name="assigned_patients")
        .sort_values(by=["assigned_patients", "hospital_name"], ascending=[False, True])
        .reset_index(drop=True)
    )

    hospital_counts.insert(0, "model_name", model_name)
    return hospital_counts


def build_patient_level_comparison(
    model_result_map: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    환자별로 각 모델의 Top-1 추천 병원을 한 줄에 비교할 수 있는 테이블 생성
    """
    merged_df: pd.DataFrame | None = None

    for model_name, df in model_result_map.items():
        top1_df = _top1_only(df).copy()

        keep_cols = [
            "patient_id",
            "hospital_name",
            "severity",
            "required_department",
            "distance_km",
            "estimated_wait_min",
            "total_time_min",
            "final_score",
        ]
        available_cols = [col for col in keep_cols if col in top1_df.columns]
        model_df = top1_df[available_cols].copy()

        rename_map = {}
        for col in model_df.columns:
            if col != "patient_id":
                rename_map[col] = f"{model_name}_{col}"

        model_df = model_df.rename(columns=rename_map)

        if merged_df is None:
            merged_df = model_df
        else:
            merged_df = merged_df.merge(model_df, on="patient_id", how="outer")

    if merged_df is None:
        return pd.DataFrame()

    return merged_df.sort_values(by="patient_id").reset_index(drop=True)


def load_model_result_csv(outputs_dir: str, model_name: str) -> pd.DataFrame:
    csv_path = os.path.join(outputs_dir, model_name, "recommendations.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Result file not found: {csv_path}")
    return pd.read_csv(csv_path)


def compare_multiple_models(
    outputs_dir: str,
    model_names: List[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metrics_rows: List[Dict[str, float | int | str]] = []
    assignment_tables: List[pd.DataFrame] = []
    model_result_map: Dict[str, pd.DataFrame] = {}

    for model_name in model_names:
        df = load_model_result_csv(outputs_dir=outputs_dir, model_name=model_name)
        model_result_map[model_name] = df

        metrics_rows.append(
            compute_model_metrics(
                recommendations_df=df,
                model_name=model_name,
            )
        )

        assignment_tables.append(
            build_hospital_assignment_table(
                recommendations_df=df,
                model_name=model_name,
            )
        )

    metrics_df = pd.DataFrame(metrics_rows)

    if assignment_tables:
        assignment_df = pd.concat(assignment_tables, ignore_index=True)
    else:
        assignment_df = pd.DataFrame(columns=["model_name", "hospital_name", "assigned_patients"])

    patient_level_df = build_patient_level_comparison(model_result_map)

    return metrics_df, assignment_df, patient_level_df