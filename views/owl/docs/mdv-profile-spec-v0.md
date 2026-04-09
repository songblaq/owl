# MDV Profile Spec v0

작성일: 2026-04-03
상태: 설계 초안

## 1. 목적

MDV가 KIB를 어떤 관점 묶음으로 바라볼지 초기 프로파일을 정의한다.

---

## 2. 공통 원칙

- profile은 고정 taxonomy가 아니라 실용적 관점 묶음이다.
- 같은 자료가 여러 profile에 동시에 속할 수 있다.
- profile은 분류보다 활용 목적을 더 중시한다.

---

## 3. 초기 프로파일

### Research View
중점:
- 조사 가치
- 근거 수준
- 후속 탐색 필요성
- 비교 대상 존재 여부

대표 차원 예:
- research relevance
- evidence strength
- novelty
- uncertainty
- follow-up value

### Prompt View
중점:
- 프롬프트 자산화 가능성
- 재사용성
- 에이전트 작업 적합성

대표 차원 예:
- prompt relevance
- reuse potential
- instruction density
- workflow affinity

### Community View
중점:
- 커뮤니티 신호
- 대화성 자료의 가치
- 반복 등장 여부

대표 차원 예:
- signal strength
- trend velocity
- anecdotal density
- repetition frequency

### General Meta View
중점:
- 전반적 위치 파악
- source 유형 구분
- 상태 추적

대표 차원 예:
- source type
- status
- trust level
- volatility

---

## 4. 운영 원칙

- 처음엔 4개 프로파일만 사용한다.
- 자주 쓰지 않는 profile은 만들지 않는다.
- 차원 값은 정밀 점수보다 가벼운 수준으로 시작한다.
- 반복 사용 패턴이 확인되면 세분화한다.
