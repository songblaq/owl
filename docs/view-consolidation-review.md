---
id: view-consolidation-review
status: draft-for-review
created: 2026-04-14
question: "3개 view를 모두 유지하는 게 최선인가? 잃는 것은 없는가?"
---

# View 통합 검토 — 리뷰 요청 문서

## 배경

oh-my-brain은 현재 3개 view를 운영 중:
- **owl** (192 entries, 1.2MB) — 내러티브 문서, TF-IDF, Claude Code 통합
- **facet** (217 entries, 948KB) — 원자 claim, 14 shard, ALIASES.tsv 121개
- **lattice** (169 entries, 676KB) — 원자 claim, typed edges 243개, graph 검색

동일한 128개 raw source를 3개 view가 각자 독립 처리한다.

---

## 질문: "3개를 합치면 잃는 것이 없는가?"

### 직관적 답변

7가지 조합(단독 3, 쌍 3, 전체 1)을 피처 커버리지로만 비교하면:

| 조합 | 검색 | 관계 | LLM통합 | 브라우징 | Claude Code | 공백 |
|---|---|---|---|---|---|---|
| owl 단독 | ★★★ | ✗ | ★★ | ✅ | ✅ | 관계, disambiguation |
| facet 단독 | ★★★★ | ✗ | ★★★★ | ✗ | ✗ | 관계, 내러티브, CC |
| lattice 단독 | ★★★★ | ✅ | ★★ | ✗ | ✗ | disambig, 내러티브, CC |
| owl+facet | ★★★★ | ✗ | ★★★★ | ✅ | ✅ | 관계만 |
| owl+lattice | ★★★★ | ✅ | ★★★ | ✅ | ✅ | disambiguation만 |
| facet+lattice | ★★★★★ | ✅ | ★★★★ | ✗ | ✗ | 내러티브, CC |
| **owl+facet+lattice** | ★★★★★ | ✅ | ★★★★ | ✅ | ✅ | **없음** |

피처 커버리지 기준으로는 3개 전체가 "잃는 것 없음"으로 보인다.

---

## 반론: 실제로는 잃는 것이 있다

### 1. 쓰기 비용 3배

raw source 1개 추가 시 3개 view에 각각 처리해야 한다.

실측:
- orbit-scheduler-concepts-raw.md → owl 9개 파일, lattice 5개 entries 생성
- 동일 정보가 최소 14개 파일로 분산

결과: 에이전트 투입 시간, API 비용, 검토 비용이 3배.

### 2. 검색 결과 중복

`omb search "orbit r4 scoring"` → 3개 view에서 총 9개 결과 반환.
`omb search "karpathy llm wiki"` → 15개 결과 반환.

같은 개념에 대해 owl이 말하는 것과 facet이 말하는 것, lattice가 말하는 것이 미묘하게 다를 수 있다.
LLM은 15개 결과를 읽고 중복 제거 + 합성을 해야 한다. 이것은 추가 토큰 비용이고 일관성 위험이다.

### 3. 정보 권위 모호성

동일 raw source에서 3개 view가 독립적으로 해석한 경우:
- owl의 "orbit-r4-scoring-concept.md" ← 내러티브 해석
- facet의 "orbit-r4-dispatch-engine.md" ← 원자 claim 해석
- lattice의 "orbit-r4-scoring" ← 관계 포함 claim

셋이 미묘하게 다른 말을 할 때 어느 것이 권위 있는가? 기준이 없다.

### 4. 유지보수 3중화

- owl health: 196 issues 상시 감지 → 대응 필요
- facet coverage: 128 sources 추적
- lattice coverage: 128 sources 추적

새 raw 추가 시 3개 view 모두 업데이트되었는지 확인해야 한다.
health issue가 owl에만 뜨고 facet/lattice는 모를 수도 있다.

### 5. 인지 부담

"이 정보를 어디서 찾아야 하나?" → 3곳 중 하나.
"이 정보를 어디에 써야 하나?" → 3곳 모두.

단일 view라면 "어디에 쓸지"는 자명하다.

---

## 통합 비용 vs 분산 비용 비교

### 3개 유지 시 비용
- raw 1개 추가: 에이전트 3세트 실행 (owl compile + facet ingest + lattice ingest)
- 검색: 결과 15개 중복 제거
- 유지보수: 3개 health 시스템 모니터링
- 일관성: 동일 사실의 3가지 표현 관리

### 2개 유지 시 비용 (예: owl + facet)
- 잃는 것: graph 1-hop 확장 (lattice 고유)
- 얻는 것: 쓰기 비용 2/3, 검색 결과 2/3, 유지보수 2/3
- 보완: facet에 `edges:` 필드 추가 (20줄 코드)로 관계 표현 일부 흡수

---

## 핵심 질문 (리뷰 요청)

1. **피처 커버리지 vs 운영 비용** — "3개가 모든 피처를 커버한다"는 말은 맞지만, 운영 비용의 3중화가 그 피처 가치를 상회하는가?

2. **graph expansion의 실제 가치** — lattice의 graph 1-hop 확장이 실제 쿼리에서 얼마나 자주, 얼마나 결정적으로 도움이 되는가? 벤치마크에서는 Q3(filing loop)에서 100점이었으나 이 쿼리 유형이 얼마나 빈번한가?

3. **ALIASES vs graph 우선순위** — disambiguation(facet)과 graph expansion(lattice)이 동시에 필요한 쿼리가 존재하는가? 아니면 대부분의 쿼리는 둘 중 하나만 필요한가?

4. **통합 임계점** — view 수가 늘어날수록 "검색 결과 합성" 자체가 하나의 인지 작업이 된다. 3개가 그 임계점을 넘는가?

---

## 잠정 의견

"3개를 합치면 잃는 것이 없다"는 피처 관점에서만 맞다.
운영 관점에서는 **쓰기 3배, 검색 노이즈 3배, 유지보수 3배**를 치른다.

이 비용을 감수할 만큼 lattice의 graph 기능이 일상적으로 필요한가가 핵심 판단 기준이다.

필자 의견: **owl + facet (2개)가 현실적 최선.**
- facet에 optional `edges:` 필드 추가로 관계 표현 부분 흡수
- graph 검색은 포기하되, 필요 시 lattice를 실험적으로 병행

---

*리뷰 요청: 위 분석에서 빠진 비용이나 잘못된 가정이 있는가?*
