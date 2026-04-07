# Sample Compile Report — 2026-04-08

작성일: 2026-04-08
상태: v0 (완료)
선행: `plans/2026-04-08-post-finishing-continuation-v0.md` §5 (Phase I 계획)

## 0. 목적

84 missing-summary-for-raw 중 5개를 대표 sample 로 선정하여 **general-purpose 서브에이전트를 owl-compiler 지시사항으로 wrap** 해서 컴파일. 나머지 79 는 별도 세션 / batch 로 미룸.

## 1. 배경

- 84 missing-summary 중 *26 regular* (표준 naming), *58 atlas* (비표준 naming, `raw/atlas/` sub-tree)
- atlas 58 은 원래 ARIA 시스템에서 가져온 non-standard 파일 → 별도 exclusion 정책 필요 → 이번 범위 밖
- regular 26 에서 5 선정

## 2. 선정된 Sample 5개

| # | raw | 선정 이유 |
|---|---|---|
| 1 | `raw/2026-04-07-karpathy-llm-wiki-gist-raw.md` | owl 의 origin source. 최우선 |
| 2 | `raw/2026-04-04-openclaw-kb-system-design-raw.md` | OpenClaw 핵심 디자인 |
| 3 | `raw/2026-04-04-deos-specs-architecture-raw.md` | DE OS 아키텍처 |
| 4 | `raw/2026-04-04-smart-gym-experiment-protocol-raw.md` | 다양성 (연구/실험) |
| 5 | `raw/runtimes/2026-04-07-antigravity-runtime-raw.md` | runtimes/ 서브트리 대표 |

## 3. 실행 방식

- **Parallel**: 5개 Task tool 호출을 동시 발사
- **각 task 의 subagent_type**: `general-purpose` (현재 세션에서 owl-compiler 가 Task tool 에 직접 노출 안 됨)
- **Prompt 구조**: owl-compiler 의 역할/contract 를 embed (5 required headers + 4 body sections + hard constraints)
- **출력 검증**: 각 task 가 자체적으로 read-back 검증 + 보고

## 4. 결과 — 5개 summary 생성

| # | compiled file | Title |
|---|---|---|
| 1 | `compiled/2026-04-07-karpathy-llm-wiki-gist-summary.md` | Karpathy의 LLM Wiki — owl 프로젝트의 원천 정의 |
| 2 | `compiled/2026-04-04-openclaw-kb-system-design-summary.md` | OpenClaw LUCAKB 지식 베이스 시스템 설계 요약 |
| 3 | `compiled/2026-04-04-deos-specs-architecture-summary.md` | DE OS 스펙 아키텍처 요약 — 5계층 모델과 파이프라인 계약 |
| 4 | `compiled/2026-04-04-smart-gym-experiment-protocol-summary.md` | Smart Gym EXP-002: WiFi CSI 비접촉 운동 감지 실험 프로토콜 |
| 5 | `compiled/2026-04-07-antigravity-runtime-summary.md` | Antigravity 런타임: Gemini 기반 CLI 에이전트 요약 |

## 5. 품질 검증

각 task 가 스스로 verify:
- ✓ 5 required headers (상태/유형/출처/작성일/관련 항목) 모두 present
- ✓ 헤더 순서 정확
- ✓ 4 body sections (핵심 주장/맥락/인용·근거/후속 작업) 모두 작성
- ✓ 핵심 주장 3-10 bullets 범위 안
- ✓ raw 파일 절대 수정 안 함 (invariant 준수)
- ✓ 관련 항목 은 concept terms (file path 아님)

## 6. Health delta

| 지표 | Before | After | 변동 |
|---|---|---|---|
| total issues | 292 | 292 | 0 |
| high | 84 | **79** | **-5** ← 5 compiles removed 5 highs |
| medium | 95 | 95 | 0 |
| low | 113 | **118** | +5 |
| missing-summary-for-raw | 84 | **79** | **-5** ✓ |
| missing-required-headers | 63 | 63 | 0 (새 summaries 는 헤더 완비) |
| weak-backlinks | 82 | **87** | +5 ← 새 summaries 는 cross-link 없음 |

**해석**: 
- 5 high issue 가 5 low issue 로 교환됨 (severity 낮아짐)
- total 변동 0
- *정확한 진행* — 새 summaries 에 cross-references 추가하면 weak-backlinks 도 0 으로 감소 (다음 batch 작업)
- 사실상 5 high fix 완료

## 7. 관찰된 패턴 (다음 batch 에 적용)

### 7.1 general-purpose 가 owl-compiler 역할을 수행하는 데 효과적
- 5/5 task 모두 헤더/본문/검증 모두 정확
- Prompt 에 owl-compiler contract 를 명시하면 충실히 준수함
- 평균 duration: 70-108초 per task, total ~1.5-2분 (parallel)

### 7.2 각 summary 가 자연스럽게 *weak-backlinks* 발생
- 새 summary 는 다른 compiled doc 에 대한 cross-link 없이 만들어짐
- 다음 단계: owl-librarian 이 cross-link 을 추가 (batch weak-backlinks fix)
- 이는 *2-phase 분업* 의 자연스러운 결과: owl-compiler 는 content 생성, owl-librarian 은 linking

### 7.3 atlas sub-tree 는 별도 정책 필요
- 58/84 (69%) 가 `raw/atlas/` sub-tree 에서 나옴
- 비표준 naming: `ATLAS.md`, `core.part01.md` 등
- 옵션:
  - (a) health rule 에 `raw/atlas/` exclusion 추가
  - (b) atlas 파일을 owl 규칙에 맞게 rename
  - (c) atlas 를 별도 vault 로 분리
- 이번 세션 밖, 다음 결정

### 7.4 parallel limit
- Task tool 을 5 parallel 로 발사 → 모두 성공
- 더 많이 (10+) 시도해봐도 괜찮을 가능성 (다만 API cost 고려)

## 8. 나머지 79 raws 처리 전략

### 8.1 Regular 21 (= 26 - 5 사용)

```
raw/2026-04-04-ai-scaler-resource-pack-raw.md
raw/2026-04-04-content-factory-core-contract-raw.md
raw/2026-04-04-content-factory-pipeline-templates-raw.md
raw/2026-04-04-deos-ops-web-implementation-complete-raw.md
raw/2026-04-04-deos-ops-web-skeleton-review-raw.md
raw/2026-04-04-deos-session-state-snapshot-raw.md
raw/2026-04-04-deos-system-overview-raw.md
raw/2026-04-04-openclaw-director-comfyui-pipeline-raw.md
raw/2026-04-04-openclaw-orbit-agenthive-integration-raw.md
raw/2026-04-04-openclaw-qa-test-framework-raw.md
raw/2026-04-04-smart-gym-research-papers-raw.md
raw/2026-04-04-smart-gym-technical-strategy-raw.md
raw/2026-04-07-deos-local-content-factory-research-raw.md
raw/runtimes/2026-04-07-aria-runtimes-index-raw.md
raw/runtimes/2026-04-07-claude-app-runtime-raw.md
raw/runtimes/2026-04-07-codex-runtime-raw.md
raw/runtimes/2026-04-07-cowork-runtime-raw.md
raw/runtimes/2026-04-07-cursor-runtime-raw.md
raw/runtimes/2026-04-07-opencode-runtime-raw.md
raw/runtimes/2026-04-07-openjarvis-runtime-raw.md
raw/runtimes/2026-04-07-vscode-runtime-raw.md
```

Batch 처리 전략:
- 5 parallel × 5 rounds = 25 (1개 여유)
- 총 예상 시간: 10-15분 (네트워크/LLM 시간 포함)
- 또는 각각 개별 세션

### 8.2 Atlas 58 — 별도 결정

atlas sub-tree 에 대한 정책 결정 필요. 이 문서 §7.3 참조.

## 9. Commit 전략

이 보고서는 `plans/sample-compile-report-2026-04-08-v0.md` 로 project repo 에 commit.
새 summary 5개는 vault (git 외부) 에 있으므로 project commit 대상 아님.

## 10. 다음 세션 권장 input

이 문서 + `plans/2026-04-08-post-finishing-continuation-v0.md` + `docs/health-triage-playbook-v0.md` 를 input 으로 제공하면 새 세션이 즉시 batch 2 (regular 21) 를 이어갈 수 있음.
