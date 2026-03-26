from __future__ import annotations
from typing import List
import pandas as pd


def parse_symptoms(symptom_text: str) -> List[str]:
    if pd.isna(symptom_text):
        return []
    return [s.strip().lower() for s in str(symptom_text).split(";") if s.strip()]


def preprocess_patient_row(patient_row: pd.Series) -> dict:
    patient = patient_row.to_dict()
    patient["symptom_list"] = parse_symptoms(patient.get("symptoms", ""))
    patient["consciousness"] = str(patient.get("consciousness", "alert")).strip().lower()
    return patient