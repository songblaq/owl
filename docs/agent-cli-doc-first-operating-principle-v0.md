# Agent CLI First + Doc First Operating Principle

작성일: 2026-04-04
상태: v0 (합본 상위 원칙)

## 목적

Agent CLI First와 Doc First를 상위 운영 원칙으로 통합 정의한다.
이 문서는 두 원칙의 관계와 전체 체계를 설명하며, 에이전트 운영의 근간이 된다.

## 전체 계획

### 1. 상위 철학: Doc First
- 판단, 설계, 작업, 결과를 문서 객체로 다루고 그 문서를 운영 계약과 증적으로 사용한다.
- 문서 생애주기: 아이디어 → 설계 → 작업 → 실행 → 결과 → 장기 지식 승격

### 2. 실행 원칙: Agent CLI First
- 문서화된 반복 실행 영역을 CLI 계약으로 외부화한다.
- LLM은 해석·판단·추론에 집중하고, 절차화된 실행은 CLI로 위임한다.

### 3. 관계: 계층 구조
```
Doc First (상위 운영 원칙)
  ↓
문서화 → 패턴 식별 → 스펙 정제
  ↓
Agent CLI First (하위 실행 원칙)
CLI 계약화 → 실행 → 결과 문서화 (Doc First로 귀환)
```

## 세부 원칙

### Doc First 세부
1. 중요한 판단/구조 변경 → 설계 문서화 (`docs/`)
2. 실행 단위 → 작업 문서화 (`tasks/`)
3. 실행 결과 → 증적 문서화 (`reports/`)
4. 장기 가치 → 지식 승격 (`knowledge/`, `compiled/concept.md`)
5. 현재 맥락 → 브리핑/기억 (`memory/`, `openclaw_report/`)

### Agent CLI First 세부
1. 작업 분류: CLI-only / LLM-only / Hybrid
2. CLI-only → 기존 CLI 우선
3. Hybrid → 단계별 CLI/LLM 분리
4. 반복 패턴 → Feature/Job/Workflow/Adapter CLI 승격

### 통합 운영 규칙
1. 새 작업 시작 시 Doc First 계약 문서 작성
2. 실행 중 반복 패턴 발견 시 Agent CLI 후보 기록
3. CLI 승격 시 Doc First 스펙 문서로 계약화
4. 모든 변경은 문서 검증 후 실행
5. 결과는 Doc First 증적으로 남기고 필요 시 CLI 개선

## 문서 생애주기 (통합)
```
판단 → Doc First 설계 문서
   ↓
작업 분해 → Doc First 작업 문서
   ↓
실행 계획 → Agent CLI 계약 (Hybrid 시)
   ↓
실행 → Agent CLI 실행
   ↓
결과 → Doc First 증적 문서
   ↓
승격 → 장기 지식 또는 CLI 개선
```

## owl 편입
- 이 문서는 `Operating Principle` 핵심
- 연결: `docs/doc-first-operating-principle-v0.md`, `docs/agent-cli-operating-principle-summary-v0.md`
- 인덱스: `docs/operating-principles-index-v0.md`

## 요약
Doc First는 문서를 운영의 근간으로, Agent CLI First는 그 실행 계약으로 작동한다. 둘은 분리되지 않고 하나의 루프를 이룬다.
