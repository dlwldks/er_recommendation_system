from __future__ import annotations
from typing import Dict, List


CRITICAL_SIGNS = {
    "loss of consciousness",
    "head trauma",
    "severe bleeding",
    "cardiac arrest",
}

SEVERE_SIGNS = {
    "chest pain",
    "shortness of breath",
    "stroke symptoms",
    "high fever with confusion",
}

MODERATE_SIGNS = {
    "vomiting",
    "abdominal pain",
    "fracture suspicion",
    "high fever",
}

MILD_SIGNS = {
    "cough",
    "ankle pain",
    "swelling",
    "headache",
}


def classify_severity(patient: Dict) -> str:
    symptoms: List[str] = patient.get("symptom_list", [])
    spo2 = float(patient.get("spo2", 100))
    sbp = float(patient.get("systolic_bp", 120))
    hr = float(patient.get("heart_rate", 80))
    consciousness = str(patient.get("consciousness", "alert")).lower()

    if consciousness in {"pain", "unresponsive", "verbal"} and "loss of consciousness" in symptoms:
        return "critical"

    if any(sym in CRITICAL_SIGNS for sym in symptoms):
        return "critical"

    if spo2 < 90 or sbp < 90:
        return "critical"

    if any(sym in SEVERE_SIGNS for sym in symptoms):
        return "severe"

    if spo2 < 94 or hr >= 120:
        return "severe"

    if any(sym in MODERATE_SIGNS for sym in symptoms):
        return "moderate"

    if any(sym in MILD_SIGNS for sym in symptoms):
        return "mild"

    return "moderate"