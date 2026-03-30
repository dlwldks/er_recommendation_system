# src/main_comparison.py
# ------------------------------------------------------------
# 각 모델의 recommendations.csv를 불러와 비교 결과를 생성하는 실행 파일
# 저장 위치: outputs/comparison/
# 생성 파일:
# - model_comparison_metrics.csv
# - hospital_assignment_distribution.csv
# - patient_level_comparison.csv
# - 각종 비교 그래프 png
# ------------------------------------------------------------

from __future__ import annotations

import os

from src.evaluation import compare_multiple_models
from src.visualization_comparison import save_all_comparison_plots


def main() -> None:
    outputs_dir = "outputs"
    comparison_dir = os.path.join(outputs_dir, "comparison")
    os.makedirs(comparison_dir, exist_ok=True)

    model_names = [
        "distance_only",
        "total_time_only",
        "proposed",
        "capacity_aware",
        "severity_adaptive",
    ]

    metrics_df, assignment_df, patient_level_df = compare_multiple_models(
        outputs_dir=outputs_dir,
        model_names=model_names,
    )

    metrics_csv_path = os.path.join(comparison_dir, "model_comparison_metrics.csv")
    assignment_csv_path = os.path.join(comparison_dir, "hospital_assignment_distribution.csv")
    patient_level_csv_path = os.path.join(comparison_dir, "patient_level_comparison.csv")

    metrics_df.to_csv(metrics_csv_path, index=False, encoding="utf-8-sig")
    assignment_df.to_csv(assignment_csv_path, index=False, encoding="utf-8-sig")
    patient_level_df.to_csv(patient_level_csv_path, index=False, encoding="utf-8-sig")

    save_all_comparison_plots(
        metrics_df=metrics_df,
        assignment_df=assignment_df,
        output_dir=comparison_dir,
    )

    print("\n=== Model Comparison Metrics ===")
    print(metrics_df.to_string(index=False))

    print("\n=== Hospital Assignment Distribution ===")
    if assignment_df.empty:
        print("No assignment distribution data.")
    else:
        print(assignment_df.to_string(index=False))

    print("\n=== Patient-Level Comparison ===")
    if patient_level_df.empty:
        print("No patient-level comparison data.")
    else:
        print(patient_level_df.to_string(index=False))

    print(f"\nSaved model comparison metrics to: {metrics_csv_path}")
    print(f"Saved hospital assignment distribution to: {assignment_csv_path}")
    print(f"Saved patient-level comparison to: {patient_level_csv_path}")
    print(f"Saved comparison plots to: {comparison_dir}")


if __name__ == "__main__":
    main()