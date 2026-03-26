제안 모델이 의도한 로직대로 작동하는지 확인하는 1차 기능 검증 실험

이 실험에서 고려한 요소

지금 모델은 이미 아래 요소를 고려하고 있어:

환자 증상
응급도(severity)
증상 기반 진료과 추론
병원 운영 여부
수용 가능 여부
응급실 가능 여부
중증 대응 가능 여부
환자-병원 거리
예상 대기시간
병원 점수
응급도 적합성(urgency fit)
설명 가능한 추천 결과

즉, 지금 baseline처럼 부르고 있었지만 정확히 말하면
**“제안 모델의 1차 실행 검증”**이야.

2. 그럼 진짜 baseline은 뭐냐

논문에서 baseline이라고 부를 건 보통 더 단순한 모델이야.

예를 들면:

Baseline A

Distance-Only

가장 가까운 병원 추천
Baseline B

Total-Time-Only

이동 + 대기시간 최소 병원 추천
Baseline C

Static-Weighted

고정 가중치 점수 모델
Proposed

Severity-Aware Filter-and-Rank