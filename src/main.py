from __future__ import annotations
import os

from src.config import Paths, TOP_K
from src.data_loader import (
    load_hospital_data,
    load_patient_data,
    load_symptom_department_map,
)
from src.recommender import recommend_for_all_patients


def main() -> None:
    paths = Paths()

    hospitals_df = load_hospital_data(paths.hospital_data)
    patients_df = load_patient_data(paths.patient_data)
    symptom_map_df = load_symptom_department_map(paths.symptom_map_data)

    results_df = recommend_for_all_patients(
        patients_df=patients_df,
        hospitals_df=hospitals_df,
        symptom_map_df=symptom_map_df,
        top_k=TOP_K,
    )

    os.makedirs(os.path.dirname(paths.output_path), exist_ok=True)
    results_df.to_csv(paths.output_path, index=False, encoding="utf-8-sig")

    print("=== Recommendation Results ===")
    print(results_df[["patient_id", "hospital_name", "final_score", "explanation"]].to_string(index=False))
    print(f"\nSaved to: {paths.output_path}")


if __name__ == "__main__":
    main()