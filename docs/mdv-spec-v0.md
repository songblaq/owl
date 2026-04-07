# MDV 명세 v0

작성일: 2026-04-03
상태: 설계 초안

## 1. 정의

MDV(Multi Dimension View)는 KIB의 raw/compiled 지식을 다양한 차원과 프로파일로 다시 해석하는 메타 뷰 계층이다.

핵심 아이디어는 다음과 같다.

- 같은 지식도 관점에 따라 다르게 읽힌다.
- 메타 뷰는 원본을 대체하지 않는다.
- 메타 뷰는 해석과 탐색을 돕는다.

---

## 2. MDV가 필요한 이유

카파시식 KIB만으로도 상당 부분은 가능하지만, 다음 경우에는 메타 관점이 필요해진다.

- 같은 자료를 research / prompt / community 같은 여러 관점으로 보고 싶을 때
- 반복적으로 같은 판단을 재사용하고 싶을 때
- 자료의 위치, 성격, 활용 가능성을 더 구조적으로 표현하고 싶을 때
- 장기 운영에서 분류와 탐색을 더 정교하게 하고 싶을 때

즉 MDV는 KIB를 대체하는 것이 아니라, **KIB를 재사용 가능한 관점으로 읽는 계층**이다.

---

## 3. MDV의 기능

### 3.1 Metadata Enrichment
- source type
- status
- trust level
- relevance
- volatility
같은 메타 정보를 부여한다.

### 3.2 Dimension Assignment
자료를 여러 차원 축 위에 위치시킨다.

예:
- research relevance
- prompt relevance
- evidence strength
- novelty
- signal strength

### 3.3 Relation Mapping
자료 간의 관계를 식별한다.

예:
- 관련 source
- 상위 개념
- 하위 개념
- 유사 자료
- 후속 조사 후보

### 3.4 Profile Views
특정 목적에 맞는 관점을 제공한다.

예:
- Research View
- Prompt View
- Community View
- General Meta View

---

## 4. MDV의 설계 원칙

- 원본을 직접 대체하지 않는다.
- 차원은 너무 많이 고정하지 않는다.
- 반복해서 유의미한 차원만 살아남게 한다.
- profile은 고정 taxonomy라기보다 실용적 묶음으로 시작한다.
- 필요 없으면 약화하거나 제거 가능해야 한다.

---

## 5. MDV의 초기 범위

초기에는 복잡한 독립 엔진보다 다음 정도로 시작한다.

- 간단한 메타데이터 필드
- 몇 개의 대표 차원
- 몇 개의 profile view
- markdown 또는 JSON 기반 뷰 산출물

즉 MDV는 초기에 거대한 그래프 데이터베이스가 아니라, **가벼운 해석 층**으로 시작한다.

---

## 6. MDV가 하지 않는 것

- raw 데이터의 주 저장소 역할
- compiled 문서의 본 저장소 역할
- 모든 것을 즉시 정량화하는 과도한 모델링

MDV는 구조보다 해석의 층이다.
