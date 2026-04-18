> **DEPRECATED by docs/REZERO-2026-04-18.md.** 이 문서는 Opus 4.6 이 2026-04-17 에 쌓은 설계 stack 의 일부다. 2026-04-18 Re:Zero 로 전면 격하. 참조 목적으로만 보존.

---
id: priorities-v1
status: active
created: 2026-04-17
derived-from: docs/experiment-3way-2026-04-17.md
---

# Design Priorities — 설계 우선순위 (tier 구조)

**핵심 관점**: oh-my-brain이 실제 운영에서 깨진 원인은 속도나 성능 문제가 아니었다. 3MB vault의 3-layer search는 충분히 빠르다. 문제는 **정합성·진실성·추적가능성** — 검색이 돌아와도 그 답이 지금의 진실인지 신뢰할 수 없다면 시스템이 무의미하다.

따라서 설계 결정 시 다음 우선순위를 **순서대로** 적용한다. 상위 tier가 위협받으면 하위 tier는 무조건 양보한다.

---

## Tier 0 — Integrity invariants (깨지면 시스템이 "거짓말하는 시스템")

이것들이 깨지면 속도·편의는 무의미하다. 다른 모든 것보다 우선.

### P0.1 Truth singularity (진실 단일성)
**규칙**: 현재 유효한 claim은 검색 시 **하나만** 반환되어야 한다. 갱신 시 이전 entry는 `supersedes` 체인에 기록되고 **물리적으로 `superseded/`로 이동**한다.

**왜 P0**: 원본 vault에서 "LLM 최종 결정"이 3일 간격으로 3개 entry로 쌓이고 모두 active 상태였다. 검색이 어느 것을 반환할지 예측 불가 → 진실이 중첩 → 시스템이 거짓말하는 상태와 동등.

**깨질 때 징후**: `superseded/` 디렉토리가 비어있는데 `type=decision`이 같은 topic에 여러 개.

### P0.2 Traceability (추적가능성)
**규칙**: 모든 entry의 `source:` 필드는 `~/omb/source/` 하위의 실존 파일로 resolve되어야 한다. 깨진 링크는 write 거부.

**왜 P0**: claim의 근거가 추적 불가하면 LLM이 지어낸 것과 사용자가 가져온 것을 구별할 수 없다. 신뢰 기반 붕괴.

**깨질 때 징후**: `omb health`가 source coverage 0%인데 "healthy" 반환 (2026-04-17 실측).

### P0.3 Immutable source (원본 불변)
**규칙**: `~/omb/source/` 파일은 한 번 들어오면 수정 금지. 정정은 새 source로 supersede.

**왜 P0**: ground truth가 흔들리면 rebuildable 약속이 의미 없다.

### P0.4 Rebuildable + proven (재생성 가능하며 실증됨)
**규칙**: source만으로 vault를 재생성할 수 있어야 하며, 이는 **분기별로 실제 테스트**한다. 테스트 안 한 약속은 죽은 약속.

**왜 P0**: "언젠가 재생성 가능"은 실제로는 불가능한 상태. 실증 cadence가 없으면 P0.2와 P0.3가 조용히 무너진다.

---

## Tier 1 — Enforcement (Tier 0를 기계로 지키는 층)

Tier 0는 사람이나 convention으로 지켜지지 않는다 (2026-04-17이 증명). 도구가 강제해야 한다.

### P1.1 Discipline as code (규율은 코드다, 문서가 아니다)
**규칙**: 모든 write 경로(ingest, edit, supersede)는 machine-checked contract를 통과해야 한다. 문서로만 적힌 규칙은 존재하지 않는 규칙으로 간주.

**구현**: `docs/ingest-contract-v2.md` C1–C6. 위반 시 non-zero exit.

### P1.2 Health fails loudly (health는 시끄럽게 실패한다)
**규칙**: Tier 0 invariant 중 하나라도 위반되면 `omb health`는 non-healthy 분류 + 위반 지점 명시. 전역 요약으로 넘기지 않는다.

**구현**: source coverage < 95% → `critical`. superseded/ 비어있으면 `warning`. naming conformance < 95% → `warning`. 

### P1.3 Merge requires normalize (통합은 normalize 후에)
**규칙**: view 통합, 대량 import, 다른 시스템에서 knowledge 가져올 때 **normalize 단계 필수**. naming/frontmatter/source 검증 통과해야 entries/에 진입 가능.

**왜**: 2026-04-15 lattice/cairn/owl → akasha 수렴에서 이 단계를 스킵한 대가를 2주 후에 치렀다.

---

## Tier 2 — Quality (있으면 좋은, 없어도 시스템은 산다)

### P2.1 Atomic ~500 tok claim (1 파일 = 1 주장)
**규칙**: entry 본문은 coherent 1 주장, ~500 토큰 내. 초과 시 분할.

### P2.2 Evidence blocks (근거 블록)
**규칙**: body에 `## Why it matters` + `## Evidence` 섹션 필수. 대안 비교 + 검증 방법 포함.

### P2.3 Graph edges suggested (관계 제안)
**규칙**: 신규 entry는 최소 1개 관련 entry를 `edges:`에 제시 (첫 entry 예외).

### P2.4 Compiled narratives fresh (내러티브 최신화)
**규칙**: topic 내 신규 entry가 쌓이면 해당 `compiled/<topic>.md` 재생성 스케줄. 분기별 1회 이상.

---

## Tier 3 — Performance (최후 고려)

인덱스 로딩 속도, 검색 latency, 저장 용량. 지금 규모(636 entries, 3MB)에선 문제 없음. Tier 0–2를 희생해서 이 층을 최적화하지 않는다.

---

## 결정 규칙

설계/운영 의사결정 시 적용:

1. **충돌하면 상위 tier 우선**. 속도를 위해 supersede 생략? 금지. Tier 0가 Tier 3를 이긴다.
2. **P0는 MVP에서도 완성되어야 한다**. Tier 1–3는 점진적 구현 허용.
3. **새 기능은 모든 상위 tier와 호환되어야 통과**. 호환 안 되면 설계 재검토.
4. **"나중에 고치지"는 Tier 0에 적용 안 됨**. 지금 못 지키면 기능 취소.

---

## 2026-04-17 현황 대비 적용

| tier | 원칙 | 현재 상태 | 필요 조치 |
|---|---|---|---|
| P0.1 | Truth singularity | **위반** (superseded/ 0개, duplicate 18 topics) | `omb supersede` CLI + AUDIT 리뷰 |
| P0.2 | Traceability | **위반** (source 0%, 실험 후 41.8%) | 나머지 370개는 source에 없는 claim — 삭제 또는 source 확보 |
| P0.3 | Immutable source | 유지됨 | — |
| P0.4 | Rebuildable proven | **위반** (실증 0회) | Q2 실증 테스트 스케줄 |
| P1.1 | Discipline as code | **미구현** | `omb ingest --validate` + contract v2 통합 |
| P1.2 | Health fails loudly | **미구현** (healthy 거짓말) | `omb health` 로직 강화 |
| P1.3 | Merge requires normalize | 암묵적 — 명시 필요 | `omb import --normalize` 게이트 |
| P2.1 | Atomic | 대체로 준수 | — |
| P2.2 | Evidence | 부분 준수 (최근만) | contract에서 강제 |
| P2.3 | Graph edges | 53% orphan | ingest 시 자동 제안 |
| P2.4 | Compiled fresh | homelab만 최신 | 분기 재컴파일 스케줄 |
| P3.x | Performance | 양호 | — |

---

**이 우선순위는 모든 설계 결정의 상위 문서다.** ATLAS/view-contract/source-layer-spec/ingest-contract는 이 tier에 따라 정렬되고, 충돌 시 이 문서가 이긴다.
