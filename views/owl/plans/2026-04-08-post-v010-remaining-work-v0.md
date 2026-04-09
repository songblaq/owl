# Post-v0.1.0 Remaining Work 계획 — 2026-04-08

작성일: 2026-04-08
상태: v0 (대규모, 다중 세션 예상)
선행:
- v0.1.0 릴리스 완료 (https://github.com/songblaq/owl/releases/tag/v0.1.0)
- 이전 계획: `plans/2026-04-08-post-finishing-continuation-v0.md`, `plans/sample-compile-report-2026-04-08-v0.md`

## 0. Context

v0.1.0 릴리스 후 남은 5 항목을 처리하기 위한 상세 계획. 총 예상 규모는 **5-12 시간, 2-4 세션** 분할 권장.

## 1. 5 항목 요약 + 현실 분석

| # | 항목 | Current count | 유형 | 단일 세션? |
|---|---|---|---|---|
| 1 | regular 21 raws batch compile | 21 items | LLM compile (parallel 가능) | ✓ (30-60 min) |
| 2 | atlas 58 정책 결정 | 58 items | 디자인 결정 + 구현 | ✓ (30-45 min) |
| 3 | 63 missing-required-headers | 43 heavy + 9 easy + 11 mid | Read+Edit (간단 mechanical) | △ (60-180 min) |
| 4 | 87 weak-backlinks batch | 58 summaries + 28 reports + 1 | 해석적 판단 (각 파일마다) | ✗ **multi-session** (2-4h) |
| 5 | 30 report-missing-output-links | 30 reports | 해석 + 정책 결정 | △ (60-120 min) |

## 2. 의존성 분석

```
2 (atlas 정책) ─┬→ 1 (regular compile)    ─┬→ 4 (backlinks)
                 │                            │
                 └→ 3 (headers fix)  ────────┘
                                              
                 5 (reports) — 독립
```

- **2 가 먼저**: atlas 정책이 바뀌면 3 (헤더 룰), 1 (compile 대상 리스트) 모두 영향받음
- **1 이 4 에 선행**: 새 summaries 가 backlinks 대상에 추가됨
- **3 이 4 에 선행**: 헤더 없는 docs 는 kind 추론 안 돼서 backlinks 룰이 약해짐
- **5 는 독립**: reports 처리는 다른 것과 안 엮임

## 3. 권장 실행 순서

```
Phase K (atlas)     → Phase L1 (compile 21) ┐
                    → Phase L2 (headers 63) ┘ → Phase M (backlinks 87) → Phase N (reports 30) → Phase O (검증)
```

L1 과 L2 는 독립적이라 *같은 세션에서 parallel* 가능. M 은 L 이후.

---

## 4. Phase K — Atlas 58 정책 결정

### 4.1 실황 (정찰 결과)

- 58 files 이 `raw/atlas/` 서브트리에 존재
- 구조: `ATLAS.md` (root) + `ctx/` + `pages/{orbit,infra,khala,security}/` + `indexes/` + `build/` + `manifest.json` + `meta/` + `views/`
- 출처: `~/.aria/atlas/` 에서 import (ARIA 의 "Constella System Knowledge Pack")
- ATLAS.md 첫 줄: *"Constella System Knowledge Pack"*, v1.0.0, 2026-03-23
- 특성: **자체 내부 구조 보유, 참조 자료 (reference pack), 개별 raw 가 아님**

### 4.2 4 옵션 비교

| 옵션 | 설명 | Pros | Cons |
|---|---|---|---|
| **A. 단순 exclusion** | health rule 에 `raw/atlas/` 제외 | 가장 간단, 1-line code change | atlas 가 wiki 와 완전 단절 |
| **B. Rename + 58 compile** | 파일명 owl 규격으로 변경 + 각 compile | 완전 통합 | 58 renames + 58 compiles = huge effort, 기존 구조 파괴 |
| **C. 별도 sub-vault** | `~/owl-vault/atlas/` 로 분리 | 깨끗한 경계 | 새 패턴 도입, vault 스키마 복잡화 |
| **D. 참조 인덱스 + exclusion** ★ | `compiled/atlas-external-reference-index.md` 1 파일 만들어서 atlas 구조 설명 + health rule exclusion | 간결, wiki 에 atlas 존재 인지, raw 무변경 | index 1 개 작성 필요 |

### 4.3 제 추천: **옵션 D**

이유:
1. Atlas 는 **외부 참조 자료** 이지 wiki 콘텐츠가 아님. 각 파일을 summary 로 만드는 게 의미 없음.
2. `compiled/atlas-external-reference-index.md` 한 개로 "atlas 가 뭐고 왜 vault 에 있는지" 를 설명하면 wiki 통합은 충분.
3. Health rule 에 `raw/atlas/` exclusion 은 1-line 코드 변경.
4. Raw 파일 무변경 (vault invariant 보존).

### 4.4 Steps

1. `src/owl/health.py` 의 `check_missing_summaries` 와 `raw_files` 에 `raw/atlas/` 제외 추가
   - 접근 1: `raw_files()` helper 가 `atlas/` 제외 (모든 룰에 영향)
   - 접근 2: `check_missing_summaries` 에만 제외 (타겟팅)
   - 추천: 접근 1 (일관성 우선, atlas 가 wiki 구조 밖에 있다는 철학 반영)
2. `compiled/atlas-external-reference-index.md` 작성
   - 제목: *"Atlas — Constella System Knowledge Pack (External Reference)"*
   - 필수 5 헤더 (유형: index, 출처: raw/atlas/ATLAS.md, 관련 항목: atlas, constella, external reference, knowledge pack, ARIA)
   - 본문: atlas 가 무엇인지, 왜 vault 에 있는지, 구조 (ATLAS.md + ctx/ + pages/), 어떻게 읽는지
3. `docs/health-check-spec-v0.md` 에 exclusion 추가 명시
4. `docs/folder-policy-v0.md` 에 atlas 예외 명시
5. `owl health` 재실행 → `missing-summary-for-raw: 79 → 21` 확인
6. 메모리 `feedback_vault_subtree_policy.md` 작성 (subtree exclusion 의 일반 패턴 박제)
7. commit + push

### 4.5 Risks

- Exclusion 이 atlas 안의 *진짜* missing summary 를 덮어쓸 가능성 → 그럴 가능성 매우 낮음 (atlas 자체가 자체 완결 reference)
- 미래에 atlas 같은 sub-tree 가 더 생기면? → exclusion 패턴을 더 일반화 (`raw/*/manifest.json` 존재하면 sub-tree 간주 같은 규칙)

### 4.6 Exit

- `owl health --json` 에서 missing-summary-for-raw 가 79 → **21** 로 감소
- compiled/atlas-external-reference-index.md 존재
- vault invariant 무손상
- commit 1개

---

## 5. Phase L1 — Regular 21 Raws Batch Compile

### 5.1 대상 (`plans/sample-compile-report-2026-04-08-v0.md §8.1` 참조)

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

### 5.2 실행 방식

- `plans/sample-compile-report-2026-04-08-v0.md` 의 Phase I 패턴 재사용
- **5 parallel × 5 rounds = 25 slot, 21 사용**
- 각 Task tool = general-purpose + owl-compiler contract embed (Phase I prompt 재사용)
- 각 compile 후 파일 존재 verify

### 5.3 Steps

1. 21 raws 를 주제별로 그룹화 (deos / content-factory / openclaw / smart-gym / runtimes / ai-scaler)
2. Round 1: 5 parallel 발사 (예: karpathy 이미 했으니 다른 groups 에서 1개씩)
3. 각 round 후 `owl health --json` 으로 missing-summary 감소 확인
4. Round 2-5 반복
5. 모두 끝나면 `plans/` 에 compile report v1 (Phase I 처럼)
6. commit + push

### 5.4 Risks

- 어떤 raw 는 길어서 (5000+ lines) 단일 Task 안 끝날 수 있음 → retry with increased token budget 또는 split
- LLM 이 헤더 순서 틀리는 경우 → self-verify 패턴 prompt 에 박혀 있음
- 특정 topic (예: runtimes) 가 거의 비슷해서 cross-reference 중복 → 괜찮음, librarian 이 나중에 dedupe

### 5.5 Exit

- 21 new summaries in `~/owl-vault/compiled/`
- missing-summary-for-raw 가 21 → **0** (Phase K + L1 합쳐서)
- high severity 가 79 → 58 (79 - 21, 다만 atlas exclusion 으로 이미 21 이 되어 있으면 21 → 0)
- commit 1개 (report + 이전 compile report 업데이트)

---

## 6. Phase L2 — 63 Missing-Required-Headers Fix

### 6.1 실황 (정찰 결과)

```
43 files: 5 헤더 모두 누락  (상태:, 유형:, 출처:, 작성일:, 관련 항목:)
 9 files: 관련 항목: 만 누락  (쉬운 fix)
 8 files: 4 헤더 누락  (상태: 없음, 나머지 4)
 2 files: 4 헤더 누락  (작성일: 없음, 나머지 4)
 1 file : 2 헤더 누락  (유형: + 작성일:)
---
63 total
```

### 6.2 카테고리별 전략

**A. 9 files with only `관련 항목:` missing** (쉬운):
- 각 파일 read → 본문에서 주요 개념 3-5개 추출 → `관련 항목:` 섹션 추가
- Mechanical, 파일당 1-2분
- 총: 9-18분

**B. 43 files with ALL headers missing** (어려운):
- 이 파일들은 옛 노트 format (예전 brain 시절) 일 가능성 높음
- 각 파일 read → 내용 보고 infer:
  - `상태:` = `compiled` (다 compiled/ 안에 있으므로)
  - `유형:` = 파일명 접미사에서 infer (`-summary.md` → `summary`, `-note.md` → `note` 등)
  - `출처:` = 파일명 slug 로부터 raw 추론 또는 `내부 작성` 명시
  - `작성일:` = 파일명 앞 `YYYY-MM-DD`
  - `관련 항목:` = 본문에서 추출 (가장 어려움)
- 파일당 3-5분
- 총: 129-215분 = 2-3.5시간

**C. 11 files with partial headers** (중간):
- 각자 sub-category 에 맞게 fix
- 파일당 2-3분
- 총: 22-33분

### 6.3 실행 방식 (권장)

**접근 1 — Python 스크립트 + LLM 검토 하이브리드** (가장 효율적):
```python
# For each file:
# 1. Read existing headers
# 2. Infer from filename (date, kind, slug)
# 3. Prepend missing headers with inferred values
# 4. Placeholder for 관련 항목: → to be filled by LLM batch
```

**접근 2 — Task tool + owl-librarian**:
- 5-10 parallel tasks 에 파일 리스트 분배
- 각 task 가 header inference + 관련 항목: 선정
- 시간 비슷하지만 품질 높음

**추천**: 접근 2 (품질 우선). 5 parallel × 13 rounds = 65 slot, 63 사용.

### 6.4 Steps (접근 2 기준)

1. 63 파일을 5 parallel batch 로 나눔 (13 files/batch 평균)
2. 각 batch 를 owl-librarian (or general-purpose wrap) 에 위임
3. Prompt: "이 N 파일의 missing headers 를 추가해라. 기존 본문 유지. 새 헤더는 파일 최상단에 삽입."
4. 각 batch 결과 verify: `owl health --json` 의 missing-required-headers 카운트 감소
5. 완료되면 commit

### 6.5 Risks

- `관련 항목:` 의 concept terms 선정이 어긋남 → LLM 에게 명확한 기준 (3-5 concepts, 본문 키워드 기반) 제공
- 일부 파일이 *의도적으로* 헤더 없음 (draft, raw-like) → grep 결과와 대조
- Edit 도구의 replace_all 실수 → 파일 단위로 edit

### 6.6 Exit

- missing-required-headers 가 63 → **0-5** (소수 의도적 예외 허용)
- 파일 변경은 vault 내부 (project commit 대상 아님)
- `plans/` 에 headers-fix-report 1개 (commit 대상)

---

## 7. Phase M — 87 Weak-Backlinks Batch (가장 큰 작업)

### 7.1 실황

- 87 = 58 summaries + 28 reports + 1 other
- 각 파일에 `compiled/...` cross-link 이 0
- L1 이 생성한 새 21 summaries 를 더하면 총 108 에 도달할 수 있음 (L1 후 수치)

### 7.2 현실 인식

- **이 작업이 가장 무겁다**. 각 파일마다:
  1. 본문 read
  2. 관련 주제 판단
  3. `owl search` 로 candidate 찾기
  4. 적절한 cross-link 1-3개 선정
  5. 본문에 `관련 자료` 섹션 추가 or 갱신
- 파일당 3-7 분 × 87-108 파일 = **4.5-13 시간**
- **단일 세션 불가**. 2-4 세션 분할 필요

### 7.3 Batch 분할 전략

- **Batch A (2 session)**: summaries 58 — 가장 많음. 반 (29) 씩 2 세션
- **Batch B (1 session)**: reports 28 — 덜 복잡
- **Batch C (0.5 session)**: other 1 + Batch A, B 의 overflow

### 7.4 각 Batch 의 실행 방식

1. 해당 group 의 파일 리스트 추출
2. 10 parallel × 3 rounds (30 파일/round 의 1/3)
3. 각 task 에 owl-librarian 프롬프트: "이 파일 read + `owl search` 로 candidate 3개 찾기 + best 1-2 선정 + 본문에 추가"
4. 각 task 결과 self-verify

### 7.5 Risks

- Cross-link 이 잘못 매핑 → LLM 판단 오류 → owl health 재실행으로 detect 힘듦 (dangling-link 는 없어서). human review 필요
- 어떤 파일은 정말 standalone 이라 cross-link 없는 게 정답 → 예외 처리

### 7.6 Exit

- weak-backlinks 가 87-108 → **20-40** (일부 의도적 standalone)
- 여러 commits (각 batch 1 commit)
- 새 `plans/backlinks-batch-report.md` 들

---

## 8. Phase N — 30 Reports Output Links Review

### 8.1 실황 (첫 5 sample)

```
compiled/2026-04-03-agent-brain-extended-health-check-report.md
compiled/2026-04-03-agent-brain-health-check-remediation-report.md
compiled/2026-04-03-agent-brain-health-check-report.md
compiled/2026-04-03-agent-brain-karpathy-alignment-report.md
compiled/2026-04-03-agent-brain-priority-query-report.md
```

- 모두 `agent-brain-*-report.md` 패턴 (옛 brain 시대 분석 리포트)
- 추측: 텍스트-only 분석 리포트, output (slide/figure/visual) 자체가 없음 — **output 안 만드는 게 디자인 의도**

### 8.2 전략

**옵션 A — 정책 변경**: `report-missing-output-links` 룰을 완화해서 *일부 report 는 텍스트-only OK* 처리. 새 frontmatter field `outputs-exempt: true` 같은 걸 체크
- Pros: 30 개 한번에 해결
- Cons: 룰이 덜 엄격해짐

**옵션 B — 개별 review**: 각 report 를 read, 진짜 output 있어야 하는지 판단, 없는 경우 삭제 or 수정
- Pros: 정확
- Cons: 30 × 5 min = 2.5h

**옵션 C — 하이브리드** ★: 모든 report 에 `outputs-exempt:` 추가 (간단 mechanical), 동시에 health.py 에 해당 frontmatter 존재 시 rule 건너뛰도록 수정
- Pros: 한번에 해결 + 미래 report 도 이 패턴 사용 가능
- Cons: 룰 설계 변경

### 8.3 추천: **옵션 C**

Steps:
1. `src/owl/health.py` 의 `check_report_outputs` 에 `outputs-exempt: true` frontmatter 체크 추가
2. 30 reports 에 `outputs-exempt: true` 추가 (Python 일괄)
3. `docs/compiled-format-spec-v0.md` 에 exempt field 문서화
4. `owl health` 재실행 → `report-missing-output-links` 감소
5. commit

### 8.4 Exit

- report-missing-output-links 가 30 → **0-3**
- commit 1-2개

---

## 9. Phase O — Final Verification

### 9.1 Goal

모든 Phase 완료 후 최종 health 상태 + v0.1.1 patch release 여부 결정

### 9.2 Steps

1. `owl health --json` 전체 상태 확인
2. 변화 정리 (before/after 표)
3. `plans/` 에 final-cleanup-report 작성
4. pyproject.toml version bump 여부 결정:
   - Health 규칙 변경 + playbook 발전 있으면 → **v0.1.1** 태그
   - 단순 데이터 정리만이면 → tag 없이 commit 만
5. (선택) v0.1.1 tag + release

### 9.3 Exit

- health 가 대부분 clean 또는 low severity 만 남음
- 전체 playbook 업데이트
- (선택) v0.1.1 release

---

## 10. 세션 분할 권장

| 세션 | Phases | 예상 시간 | 권장 주의사항 |
|---|---|---|---|
| **1** | K (atlas) + L1 (compile 21) | 1-2h | 가장 집중, dependencies 해제 |
| **2** | L2 (headers 63) | 2-3h | owl-librarian batch 집중 |
| **3** | M (backlinks batch A — summaries) | 2-3h | 가장 해석적 |
| **4** | M (backlinks batch B — reports) + N (reports exempt) | 2h | |
| **5** | O (verification + v0.1.1?) | 30min | 정리 |

**총 7.5-10.5 시간, 5 세션**. 다만 single long session 으로 1+2+3 은 가능 (5-8h).

## 11. 사용자 결정 포인트

이 계획 전체가 크기 때문에 아래 3가지 중 선택:

1. **Plan 전체 실행** — 한 세션에 Phase K+L1 만, 나머지 별도 세션
2. **Phase K 만** — atlas 정책만 결정 + 구현, 나머지는 다음 기회
3. **Cherry-pick** — 특정 Phase 만 골라서 진행 (예: Phase N 만 = report exempt 룰만)

저의 권장: **옵션 1**. Phase K + L1 이 의존성 해제에 가장 효과적이고, 1-2h 안에 완료 가능. 나머지 3 phases 는 해석적 작업이라 각자 별도 세션이 품질 우위.

## 12. 비계획 / 후속 고려

- **atlas 에 대한 *진짜* 활용**: 사용자가 atlas 내용을 owl 안에서 쿼리하고 싶다면 별도 "atlas-aware search" 기능 필요
- **자동 cross-linking tool**: weak-backlinks 를 반복 처리 하는 owl-auto-link CLI 또는 서브에이전트
- **CI 통합**: `owl health` 를 git hook / CI 로 실행
- **batch health fix 명령**: `owl fix weak-backlinks --sample 10` 같은 CLI 확장
