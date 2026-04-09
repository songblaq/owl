# OpenClaw 스킬 구조 원칙 계획 (2026-04-04)

## 목적
OpenClaw 스킬 구조를 `L0-doc / L1-call / L2-inner` 원칙으로 정리하고, OpenClaw 전용(`blaq-*`)과 범용 공통(`luca-*`) 스킬을 분리한다.

## 구조 원칙
- `L0-doc`: 지도/정책/레지스트리
- `L1-call`: 공개 표면
- `L2-inner`: 내부 재사용 구현
- `L1`은 `L1`을 호출하지 않는다.
- 공통은 `L2`로 올린다.
- 모든 `L2`는 하나 이상의 `L1`에 연결되어야 한다.

## 저장소 원칙
- 공용 canonical: `~/.agents/skills`
- OpenClaw runtime: `~/.openclaw/workspace/skills`
- `luca-*`는 canonical을 `.agents/skills`에 두고 runtime에서는 symlink 노출 모델을 우선 검토

## 후속 작업
1. `luca-*` 승격 대상 확정
2. symlink 운영 검증
3. orphan inner 점검
4. L0 hub 완성
5. category/role 2차 정제
