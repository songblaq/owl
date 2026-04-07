# Doc First 적용 예시 v0

작성일: 2026-04-04
상태: 예시

## 목적

Doc First와 Agent CLI First가 실제로 어떻게 연결되는지 한 번의 적용 사례로 설명한다.

## 시나리오

주제: `agent-cli-first · doc-first` 운영 원칙을 새 프로젝트/브레인 체계에 편입한다.

## 1. 판단 문서화

먼저 현재 workspace의 자원을 조사했다.
대상은 다음과 같았다.

- `docs/`: 설계/정책/계획
- `tasks/`: 실행 단위
- `reports/`: 결과와 증적
- `knowledge/`: 장기 지식
- `memory/`: 운영 기억
- `openclaw_report/`: 경량 브리핑
- `projects/agent-cli-spec`: 기존 Agent CLI 철학 문서

이 조사 결과를 바탕으로 `doc-first`를 독립 철학이 아니라 기존 문서 기반 운영 습관의 상위 명문화로 해석했다.

## 2. 설계 문서화

다음 문서를 작성했다.

- `docs/doc-first-operating-principle-v0.md`
- `docs/agent-cli-doc-first-operating-principle-v0.md`
- `docs/operating-principles-index-v0.md`

이 단계는 실행 전에 개념과 관계를 확정하는 설계 단계다.

## 3. 작업 문서화

실제 작업 항목은 다음으로 분해할 수 있었다.

- 합본 상위 원칙 작성
- 인덱스 작성
- brain compiled 요약 반영
- README 링크 반영
- MEMORY 장기 기억 반영
- 적용 예시와 템플릿 작성

즉 작업은 설명이 아니라 문서와 파일 변경 단위로 분해됐다.

## 4. 실행

실행 중에는 다음 원칙을 적용했다.

- 문서 생성과 링크 반영은 Doc First 실행
- 반복 가능한 구조화 산출은 Agent Brain 문서 계약에 맞춤
- 향후 반복 가능한 항목은 CLI/도구화 후보로 남김

이번 작업은 완전한 CLI-only가 아니라 Hybrid에 가깝다.

- LLM: 철학 정리, 관계 정의, 구조 해석
- 파일 작업 도구: 문서 생성, 편집, 링크 반영

## 5. 결과 문서화

실행 결과는 다음 위치에 남겼다.

- 프로젝트 원칙 문서: `~/_/projects/agent-brain/docs/`
- brain compiled 요약: `~/.agents/brain/compiled/`
- 장기 기억 반영: `MEMORY.md`

즉 결과가 채팅 답변으로만 끝나지 않고 실제 파일 증적으로 남았다.

## 6. 승격 판단

이번 작업의 승격 결과는 다음과 같다.

- 단순 대화 → 운영 원칙 문서
- 개별 원칙 → 상위 통합 원칙
- 개별 산출 → 운영 원칙 인덱스
- 세션 맥락 → 장기 기억 반영

## 한 줄 해석

이 예시는 다음 흐름을 보여준다.

```text
조사 -> 설계 문서화 -> 작업 분해 -> 실행 -> 결과 증적화 -> 장기 원칙 승격
```

즉 Doc First는 문서를 먼저 쓰는 버릇이 아니라, 운영 전체를 문서 객체 중심으로 굴리는 방식이다.
