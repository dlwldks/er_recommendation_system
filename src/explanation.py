from __future__ import annotations
import pandas as pd


def generate_explanation(row: pd.Series, required_department: str, severity: str) -> str:
    reasons = []

    reasons.append(f"{required_department} 진료 가능")
    reasons.append(f"예상 이동거리 {row['distance_km']:.2f}km")
    reasons.append(f"예상 대기시간 {float(row['estimated_wait_min']):.0f}분")
    reasons.append(f"총 도달시간 {float(row['total_time_min']):.1f}분")

    if row["urgency_fit_score"] >= 0.8:
        reasons.append("응급도 기준에서 신속 대응 가능")
    elif row["urgency_fit_score"] >= 0.5:
        reasons.append("응급도 기준에서 수용 가능")
    else:
        reasons.append("응급도 기준에서 시간 여유가 적음")

    if row["specialty_score"] >= 1.0:
        reasons.append("증상과 직접적으로 관련된 진료과 보유")
    else:
        reasons.append("응급의학과 중심 대응 가능")

    if severity in {"critical", "severe"} and row.get("severe_case_supported", 0) == 1:
        reasons.append("중증 응급환자 대응 가능")

    reasons.append("동일 점수 병원 간에는 총 도달시간 기준으로 우선순위 결정")

    explanation = f"{row['hospital_name']} 추천 이유: " + ", ".join(reasons) + "."
    return explanation