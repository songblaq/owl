# Agent CLI Operating Principle Summary

작성일: 2026-04-04

## 목적

CLI First 운영 원칙을 에이전트 브레인 관점에서 요약한다.

## 핵심 원칙

CLI First는 모든 작업을 CLI로 대체하자는 뜻이 아니다.

정확한 의미는 다음과 같다.
- 절차화 가능하고 재현 가능한 실행은 CLI로 내린다.
- 해석, 판단, 추론, 전략 수립, 예외 대응은 LLM 레이어에 남긴다.
- 실제 작업은 CLI-only / LLM-only / Hybrid로 먼저 분류한다.

## 작업 분류

### CLI-only
- 파일 변환
- 정형 API 호출
- 상태 조회
- 빌드/테스트
- 반복 가능한 수집/동기화

### LLM-only
- 애매한 요구 해석
- 전략 설계
- 창의적 초안 작성
- 열린형 평가와 판단

### Hybrid
- LLM이 요청을 해석하고 CLI를 선택
- CLI가 데이터를 수집하고 LLM이 해석
- LLM이 계획하고 CLI가 실행한 뒤 LLM이 최종 정리

## 운영 규칙

1. 작업 전에 먼저 CLI-only / LLM-only / Hybrid를 분류한다.
2. CLI-only는 기존 CLI를 우선 찾는다.
3. Hybrid는 어느 단계가 CLI이고 어느 단계가 LLM인지 분리한다.
4. LLM-only를 억지로 CLI라고 주장하지 않는다.
5. 반복 작업은 Feature CLI / Job CLI / Workflow CLI / Adapter CLI 승격 후보로 기록한다.

## owl 편입 메모

이 문서는 owl에서 `Operating Principle` 및 `Rule Source` 계열 compiled summary로 취급할 수 있다.

권장 연결 대상:
- `docs/term-dictionary-v0.md`
- `docs/rule-source-spec-v0.md`
- 향후 운영 원칙 인덱스 또는 core concepts index

## 에이전트 브레인 반영 메모

이 원칙은 특정 작업용 스킬이 아니라 운영 원칙이다.
따라서 전역 규칙에서는 다음처럼 짧게 반영하는 것이 적절하다.

- 가능한 실행은 CLI로 내리고, 해석·판단·추론은 LLM에 남긴다.
- 작업은 먼저 CLI-only / LLM-only / Hybrid로 구분한다.
- Hybrid 작업은 단계별 책임을 분리한다.
