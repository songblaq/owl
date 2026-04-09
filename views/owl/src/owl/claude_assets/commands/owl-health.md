---
description: Run owl vault health check and propose prioritized fixes
---

!`owl health --json`

위 health check 결과(JSON)를 해석하고 우선순위 fix 계획을 작성하세요.

이 vault 는 Karpathy 식 **LLM-maintained wiki** 입니다. 8개 무결성 규칙은 wiki 의 구조 건강을 측정합니다:
- `missing-summary-for-raw` (high) — raw 가 있는데 대응 summary 없음
- `report-broken-output-link` (high) — report 가 존재하지 않는 outputs/* 참조
- `index-broken-link` (high) — index 가 깨진 링크
- `compiled-missing-related` (medium) — `관련 항목:` 섹션 누락
- `report-missing-output-links` (medium) — report 에 outputs 링크 없음
- `orphan-concept` (medium) — concept 에 inbound link 없음
- `concept-candidate-missing` / `index-candidate-missing` / `weak-backlinks` / `stale-index-link-density` (low)

해석 작업은 **owl-health 서브에이전트**에 위임하세요 (`Task` tool, subagent_type="owl-health"). 서브에이전트가 정책 문서를 참조하면서 우선순위 fix 계획을 작성합니다.

서브에이전트 결과를 받으면:
1. **High severity 이슈**부터 사용자에게 보여주기
2. 각 이슈 그룹마다 owl-librarian 또는 owl-compiler 호출 제안
3. 사용자 승인 시 해당 서브에이전트로 실제 fix 작업 위임
4. fix 후 `owl health` 재실행해 delta 보고

**중요**: 직접 edit 하지 말고 항상 적절한 owl-* 서브에이전트를 통해 작업하세요. 정책 일관성을 위함입니다.
