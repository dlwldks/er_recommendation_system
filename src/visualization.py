from __future__ import annotations
import os
import pandas as pd
import matplotlib.pyplot as plt


def plot_recommendation_scatter(
    hospitals_df: pd.DataFrame,
    patients_df: pd.DataFrame,
    recommendations_df: pd.DataFrame,
    output_path: str,
    model_name: str = "proposed",
) -> None:
    top1_df = recommendations_df[recommendations_df["rank"] == 1].copy()

    top1_df = top1_df.merge(
        patients_df[["patient_id", "latitude", "longitude"]],
        on="patient_id",
        how="left",
    )
    top1_df = top1_df.rename(
        columns={
            "latitude": "patient_latitude",
            "longitude": "patient_longitude",
        }
    )

    top1_df = top1_df.merge(
        hospitals_df[["hospital_id", "hospital_name", "latitude", "longitude"]],
        on=["hospital_id", "hospital_name"],
        how="left",
    )
    top1_df = top1_df.rename(
        columns={
            "latitude": "hospital_latitude",
            "longitude": "hospital_longitude",
        }
    )

    plt.figure(figsize=(10, 8))

    plt.scatter(
        hospitals_df["longitude"],
        hospitals_df["latitude"],
        label="Hospitals",
        alpha=0.8,
        s=100,
        marker="o",
    )

    plt.scatter(
        patients_df["longitude"],
        patients_df["latitude"],
        label="Patients",
        alpha=0.9,
        s=130,
        marker="*",
    )

    for _, row in top1_df.iterrows():
        if pd.notna(row["patient_longitude"]) and pd.notna(row["hospital_longitude"]):
            plt.plot(
                [row["patient_longitude"], row["hospital_longitude"]],
                [row["patient_latitude"], row["hospital_latitude"]],
                linestyle="--",
                alpha=0.7,
            )

    plt.scatter(
        top1_df["hospital_longitude"],
        top1_df["hospital_latitude"],
        label="Top-1 Recommended Hospitals",
        alpha=1.0,
        s=220,
        marker="o",
        facecolors="none",
        linewidths=2,
    )

    for _, row in patients_df.iterrows():
        plt.text(
            row["longitude"],
            row["latitude"],
            row["patient_id"],
            fontsize=9,
        )

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title(f"ER Recommendation Scatter Plot ({model_name})")
    plt.legend()
    plt.grid(True, alpha=0.3)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()