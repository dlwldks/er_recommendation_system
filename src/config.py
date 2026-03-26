from dataclasses import dataclass
from typing import Dict


@dataclass
class Paths:
    hospital_data: str = "data/hospitals.csv"
    patient_data: str = "data/patients.csv"
    symptom_map_data: str = "data/symptom_department_map.csv"
    output_path: str = "outputs/recommendations.csv"


SEVERITY_WEIGHTS: Dict[str, Dict[str, float]] = {
    "critical": {
        "distance_score": 0.30,
        "waiting_score": 0.20,
        "specialty_score": 0.15,
        "hospital_score_norm": 0.10,
        "urgency_fit_score": 0.25,
    },
    "severe": {
        "distance_score": 0.27,
        "waiting_score": 0.23,
        "specialty_score": 0.18,
        "hospital_score_norm": 0.12,
        "urgency_fit_score": 0.20,
    },
    "moderate": {
        "distance_score": 0.22,
        "waiting_score": 0.26,
        "specialty_score": 0.22,
        "hospital_score_norm": 0.15,
        "urgency_fit_score": 0.15,
    },
    "mild": {
        "distance_score": 0.18,
        "waiting_score": 0.28,
        "specialty_score": 0.24,
        "hospital_score_norm": 0.20,
        "urgency_fit_score": 0.10,
    },
}

GOLDEN_TIME_MINUTES: Dict[str, int] = {
    "critical": 30,
    "severe": 60,
    "moderate": 120,
    "mild": 240,
}

AVERAGE_TRAVEL_SPEED_KMH = 40.0
TOP_K = 3