from __future__ import annotations
from collections import defaultdict
from typing import List, Tuple
import pandas as pd


def map_symptom_to_department(symptoms: List[str], symptom_map_df: pd.DataFrame) -> Tuple[str, dict]:
    """
    증상 목록으로부터 가장 적합한 진료과를 추론한다.
    가중치 합이 가장 높은 department를 선택한다.
    """
    dept_scores = defaultdict(float)

    for symptom in symptoms:
        matches = symptom_map_df[symptom_map_df["symptom"].str.lower() == symptom.lower()]
        for _, row in matches.iterrows():
            dept_scores[row["department"]] += float(row["weight"])

    if not dept_scores:
        return "emergency_medicine", {"emergency_medicine": 1.0}

    best_department = max(dept_scores, key=dept_scores.get)
    return best_department, dict(dept_scores)