# Health Check Spec v0

작성일: 2026-04-03
상태: 보완 초안

## 1. 목적

Karpathy가 말한 linting / health checks를 owl 운영 규칙으로 구체화한다.

---

## 2. 점검 항목

### 2.1 데이터 불일치
- 서로 다른 문서 간 정보 충돌
- 오래된 정보와 최신 정보의 차이
- 이름/용어 표기 불일치

### 2.2 누락 데이터
- summary는 있으나 출처 링크가 없음
- concept 문서는 있으나 관련 source가 부족함
- article 후보는 있으나 compiled 문서가 없음

### 2.3 연결 후보
- 연관성이 높은 문서 간 연결 누락
- 동일 주제군 내 index 부재
- concept 문서로 승격할 후보 존재

### 2.4 새 문서 후보
- raw source가 충분히 쌓였지만 summary가 없음
- 여러 summary가 있지만 concept 문서가 없음
- 반복 질문이 많지만 report 문서가 없음

---

## 3. missing data 보완 원칙

- 누락이 확인되면 web search 나 추가 source 탐색으로 보완 후보를 찾을 수 있다.
- 보완은 원본을 덮어쓰지 않고, source 추가 또는 compiled 보강으로 처리한다.
- 누락 보완 작업도 문서화한다.

---

## 4. 운영 원칙

- health check는 지식 베이스 품질 유지의 정규 루프다.
- 문제 발견만 하고 끝내지 않고, 보완 또는 후보 문서로 연결한다.
- 반복되는 결함은 규칙 수정으로 이어져야 한다.
- 현재 최소 구현은 `src/brain_health_check.py` 이다.
- 예시 실행: `python3 src/brain_health_check.py`

## 5. 현재 최소 검사 항목

- summary 없는 raw source
- 관련 항목/관련 자료가 없는 compiled 문서
- outputs 링크가 없거나 깨진 report 문서
- concept 후보(같은 관련 항목이 여러 summary에 반복되지만 concept가 없음)
- index 후보(같은 subject compiled 문서가 여러 개지만 index가 없음)
- orphan concept (다른 compiled 문서에서 들어오는 링크가 전혀 없는 concept)
- stale index (entry index 역할을 하기엔 링크 수가 너무 적거나 깨진 링크가 있는 index)
- weak backlink (summary/report가 다른 compiled 문서를 전혀 가리키지 않는 상태)

## 6. 성숙도 관점에서의 해석

- health check가 clean이라고 해서 곧바로 성숙한 위키는 아니다.
- 최소 성숙 기준은 다음을 함께 본다.
  - 구조 존재 여부
  - raw→compiled 대응률
  - report→outputs filing 비율
  - concept/index 진입점 존재 여부
  - cross-link 밀도와 orphan 문서 비율
- 따라서 health check는 단순 파일 유무 검사에서 시작하되, 점차 링크 품질과 탐색성 검사로 확장한다.
