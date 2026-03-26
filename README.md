# 🚑 ER Recommendation System (응급실 추천 시스템)

## 📌 프로젝트 개요

본 프로젝트는 환자의 증상, 위치, 응급도를 기반으로
가장 적절한 응급실을 추천하는 시스템이다.

단순 거리 기반 추천이 아닌,

* 진료과 적합성
* 응급도
* 이동 시간 + 대기 시간
* 병원 수용 능력

을 종합적으로 고려하여 **설명 가능한 추천(Explainable Recommendation)**을 제공한다.

---

## 🎯 목표

* 응급 상황에서 **최적의 병원 선택 자동화**
* 현실적인 조건(대기시간, 수용 능력 등)을 반영한 추천
* 추천 결과에 대한 **설명 가능성 확보**
* 병원 쏠림 현상을 해결하는 **capacity-aware 모델 구현**

---

## 🧠 모델 구조

### 1️⃣ Proposed Model

**Severity-Aware Filter-and-Rank Model**

#### 🔹 특징

* 증상 → 진료과 매핑
* 환자 상태 기반 응급도 분류
* 병원 필터링 (운영 여부, 진료 가능 여부 등)
* 거리 + 대기시간 기반 총 도달시간 계산
* 정규화 후 가중합 점수 계산
* Top-K 병원 추천
* 추천 이유 생성 (Explainable)

---

### 2️⃣ Capacity-Aware Model (확장 모델)

#### 🔹 핵심 아이디어

> 병원의 수용 가능 인원을 고려하여 환자를 분산 배정

#### 🔹 특징

* 병원별 `max_capacity` 설정
* 환자를 **순차적으로 배정**
* 배정 시 capacity 감소
* capacity가 0이면 해당 병원 제외
* 중증 환자 우선 배정 (`critical → severe → ...`)

#### 🔹 효과

* 특정 병원으로의 과도한 집중 방지
* 현실적인 응급실 운영 상황 반영

---

## ⚙️ 시스템 흐름

```
환자 데이터 입력
    ↓
증상 기반 진료과 추론
    ↓
응급도 분류
    ↓
병원 후보 필터링
    ↓
거리 + 대기시간 계산
    ↓
점수 계산 및 정렬
    ↓
(옵션) capacity 적용
    ↓
Top-K 추천 + 설명 생성
```

---

## 📊 데이터 구성

### 🏥 병원 데이터

* 위치 (위도, 경도)
* 진료과
* 응급실 운영 여부
* 대기시간
* 병원 점수
* 중증 대응 가능 여부
* 최대 수용 인원 (`max_capacity`)

---

### 🧑 환자 데이터

* 위치
* 증상
* 나이
* 심박수
* 혈압
* 산소포화도
* 의식 상태

---

### 🔗 증상-진료과 매핑

* symptom → department
* weight 기반 매칭

---

## 📈 시각화 (Visualization)

### 📍 Scatter Plot

* 병원 위치 (●)
* 환자 위치 (★)
* 추천 병원 (○ 강조)
* 환자 → 병원 연결선 (--)

---

### 예시

![example](outputs/proposed/recommendation_scatter.png)

---

## 🔍 주요 결과 분석

### ❗ 기존 모델 (Proposed)

* 대부분 환자가 동일 병원으로 집중
* 최적 병원에 대한 쏠림 현상 발생

```
P001 → H001
P002 → H001
P003 → H001
P004 → H001
```

---

### ✅ Capacity-Aware 적용 후

* 병원 수용 능력 고려
* 환자 분산 배정

```
P001 → H001
P003 → H001
P002 → H005
P004 → H004
```

---

## 🧪 실험 결과 해석

### Before

* 최적 병원 집중
* 현실성 부족

### After

* 분산 배정
* 응급실 과부하 완화
* 현실성 증가

---

## 📂 프로젝트 구조

```
src/
├─ main.py
├─ main_capacity.py
├─ recommender.py
├─ recommender_capacity.py
├─ visualization.py
├─ data_loader.py
├─ preprocessing.py
├─ scoring.py
├─ filtering.py
├─ explanation.py

data/
├─ hospitals.csv
├─ patients.csv
├─ symptom_map.csv

outputs/
├─ proposed/
│  ├─ recommendations.csv
│  └─ recommendation_scatter.png
├─ capacity_aware/
│  ├─ recommendations.csv
│  └─ recommendation_scatter.png
```

---

## 🚀 실행 방법

### 기본 모델

```bash
python -m src.main
```

### Capacity-Aware 모델

```bash
python -m src.main_capacity
```

---

## 💡 향후 개선 방향

* 병원 실시간 대기시간 API 연동
* 교통 상황 반영 (실시간 이동시간)
* LLM 기반 증상 이해
* 병원 추천 개인화
* Reinforcement Learning 기반 최적 배정
* Multi-agent 시스템 확장

---

## 🧠 핵심 기여 (Contribution)

* 응급도 + 진료과 + 거리 + 대기시간을 통합한 추천 모델
* 설명 가능한 추천 시스템 구현
* 병원 수용 능력을 고려한 capacity-aware 확장
* 시각화를 통한 직관적 결과 분석

---

## 🏁 결론

본 시스템은 단순 거리 기반 추천을 넘어
**현실적인 응급 의료 환경을 반영한 추천 시스템**으로 확장되었으며,

특히 **capacity-aware 모델**을 통해
병원 과밀 문제를 해결할 수 있는 가능성을 제시한다.
