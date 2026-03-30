# src/visualization_comparison.py
# ------------------------------------------------------------
# 모델 비교 결과를 시각화하는 파일
# - 평균 총 소요시간 비교 바차트
# - 평균 대기시간 비교 바차트
# - 특정 병원 집중도 비교 바차트
# - 활용 병원 수 비교 바차트
# - 병원별 환자 배정 분포 그래프 저장
# ------------------------------------------------------------

from __future__ import annotations

import os

import matplotlib.pyplot as plt
import pandas as pd


def save_comparison_bar_chart(
    metrics_df: pd.DataFrame,
    output_path: str,
    metric_col: str,
    title: str,
    ylabel: str,
) -> None:
    if metrics_df.empty or metric_col not in metrics_df.columns:
        return

    plot_df = metrics_df.copy()
    plot_df = plot_df.sort_values(by=metric_col, ascending=True).reset_index(drop=True)

    plt.figure(figsize=(10, 6))
    plt.bar(plot_df["model_name"], plot_df[metric_col])
    plt.title(title)
    plt.xlabel("Model")
    plt.ylabel(ylabel)
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def save_assignment_distribution_chart(
    assignment_df: pd.DataFrame,
    output_path: str,
) -> None:
    if assignment_df.empty:
        return

    pivot_df = assignment_df.pivot_table(
        index="hospital_name",
        columns="model_name",
        values="assigned_patients",
        aggfunc="sum",
        fill_value=0,
    )

    if pivot_df.empty:
        return

    pivot_df = pivot_df.sort_index()

    ax = pivot_df.plot(
        kind="bar",
        figsize=(12, 7),
        rot=25,
    )

    ax.set_title("Hospital Assignment Distribution by Model")
    ax.set_xlabel("Hospital")
    ax.set_ylabel("Assigned Patients")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def save_all_comparison_plots(
    metrics_df: pd.DataFrame,
    assignment_df: pd.DataFrame,
    output_dir: str,
) -> None:
    os.makedirs(output_dir, exist_ok=True)

    save_comparison_bar_chart(
        metrics_df=metrics_df,
        output_path=os.path.join(output_dir, "avg_total_time_comparison.png"),
        metric_col="avg_total_time_min",
        title="Average Total Time by Model",
        ylabel="Average Total Time (min)",
    )

    save_comparison_bar_chart(
        metrics_df=metrics_df,
        output_path=os.path.join(output_dir, "avg_wait_time_comparison.png"),
        metric_col="avg_wait_min",
        title="Average Wait Time by Model",
        ylabel="Average Wait Time (min)",
    )

    save_comparison_bar_chart(
        metrics_df=metrics_df,
        output_path=os.path.join(output_dir, "max_concentration_ratio_comparison.png"),
        metric_col="max_concentration_ratio",
        title="Hospital Concentration Ratio by Model",
        ylabel="Max Concentration Ratio",
    )

    save_comparison_bar_chart(
        metrics_df=metrics_df,
        output_path=os.path.join(output_dir, "unique_assigned_hospitals_comparison.png"),
        metric_col="unique_assigned_hospitals",
        title="Number of Assigned Hospitals by Model",
        ylabel="Unique Assigned Hospitals",
    )

    save_assignment_distribution_chart(
        assignment_df=assignment_df,
        output_path=os.path.join(output_dir, "hospital_assignment_distribution.png"),
    )