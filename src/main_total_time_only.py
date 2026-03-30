from __future__ import annotations

import os
import pandas as pd

from src.config import Paths, TOP_K
from src.data_loader import (
    load_hospital_data,
    load_patient_data,
    load_symptom_department_map,
)
from src.recommender_baseline import recommend_for_all_patients_baseline
from src.visualization import plot_recommendation_scatter


def main() -> None:
    paths = Paths()
    model_name = "total_time_only"

    hospitals_df = load_hospital_data(paths.hospital_data)
    patients_df = load_patient_data(paths.patient_data)
    symptom_map_df = load_symptom_department_map(paths.symptom_map_data)

    results_df = recommend_for_all_patients_baseline(
        patients_df=patients_df,
        hospitals_df=hospitals_df,
        symptom_map_df=symptom_map_df,
        baseline_type=model_name,
        top_k=TOP_K,
    )

    model_output_dir = os.path.join("outputs", model_name)
    os.makedirs(model_output_dir, exist_ok=True)

    csv_output_path = os.path.join(model_output_dir, "recommendations.csv")
    img_output_path = os.path.join(model_output_dir, "recommendation_scatter.png")

    results_df.to_csv(csv_output_path, index=False, encoding="utf-8-sig")

    display_cols = [
        "patient_id",
        "rank",
        "severity",
        "required_department",
        "hospital_name",
        "distance_km",
        "estimated_wait_min",
        "total_time_min",
        "final_score",
    ]

    display_df = results_df[display_cols].copy()

    for col in ["distance_km", "estimated_wait_min", "total_time_min"]:
        display_df[col] = pd.to_numeric(display_df[col], errors="coerce").round(2)

    display_df["final_score"] = pd.to_numeric(
        display_df["final_score"],
        errors="coerce",
    ).round(6)

    plot_recommendation_scatter(
        hospitals_df=hospitals_df,
        patients_df=patients_df,
        recommendations_df=results_df,
        output_path=img_output_path,
        model_name=model_name,
    )

    print("\n=== Total-Time-Only Recommendation Results (Summary) ===")
    print(display_df.to_string(index=False))

    print(f"\nSaved detailed results to: {csv_output_path}")
    print(f"Saved scatter plot to: {img_output_path}")


if __name__ == "__main__":
    main()