# Rule Source Spec v0

작성일: 2026-04-03
상태: 초안

## 1. 목적

에이전트 운영 계약, 규칙 문서, 원칙 문서처럼 정책적 성격이 강한 source를 owl 안에서 어떻게 다룰지 정의한다.

---

## 2. 정의

Rule Source는 사실 데이터이면서 동시에 운영 원칙 추출의 근거가 되는 source다.

예:
- operating contract
- workflow rules
- safety rules
- response policy
- formatting policy

---

## 3. 처리 방식

### 3.1 Raw 보관
원문은 raw source로 보관한다.

### 3.2 Compiled 요약
핵심 규칙과 적용 가능한 원칙을 compiled summary로 만든다.

### 3.3 현재 운영 반영
현재 에이전트의 메모리/정체성/운영 문서에 반영 가능한 항목은 별도로 기록한다.

예:
- `docs/agent-cli-operating-principle-summary-v0.md`
  - CLI First를 전역 운영 원칙으로 축약한 compiled summary
  - 작업을 CLI-only / LLM-only / Hybrid로 구분하는 분류 기준 포함

### 3.4 경계 유지
- source 자체와 현재 운영 반영 결과는 구분한다.
- 타 에이전트의 페르소나, 기억, 사용자 프로필은 그대로 복제하지 않는다.
- 규칙과 원칙만 추출 대상으로 삼는다.

---

## 4. 목적 효과

이 규칙은 외부 운영 계약을 단순 참고로 끝내지 않고, owl 안에서 재사용 가능한 정책 source 로 관리하게 한다.
