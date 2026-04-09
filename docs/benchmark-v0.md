# Benchmark v0 — owl vs cairn

작성일: 2026-04-09
상태: v0 (첫 full-migration 완료 직후)

## 0. Context

2026-04-09 단일 세션에서 owl vault (192 compiled docs, ~2026-04-03 ~ 2026-04-08 누적) 전체를 cairn vault 로 마이그레이션. 결과 244 cairn atomic entries. 이 문서는 두 시스템을 6축에서 비교 측정한 첫 벤치마크.

## 1. 마이그레이션 개요

| 항목 | owl | cairn |
|---|---|---|
| 마이그레이션 전 docs | 192 compiled (+ 60 raw) | 0 |
| 마이그레이션 후 | (그대로) | **244 atomic entries** |
| 확장 비율 | 1.0x (원본) | **1.27x** (192→244) |
| 유형 분포 | 5 kinds (summary/note/report/concept/index) | 5 types (claim 93 / fact 82 / procedure 41 / preference 25 / open-question 3) |
| 작성 방식 | Karpathy LLM Wiki 패턴, 인간+LLM hybrid | LLM-first, atomic units |
| 마이그레이션 시간 | 원본 작성: ~며칠 (여러 세션) | **~35 분 (parallel subagents, 17 batches × 5 parallel)** |

## 2. 차원 1 — Storage density

### 측정

| 지표 | owl (compiled/) | cairn (entries/) | 비교 |
|---|---|---|---|
| 파일 수 | 192 | **244** | +27% |
| 총 크기 | 1.2M | **976K** | **-19%** |
| 평균 파일 크기 | 3005 bytes | **1255 bytes** | -58% |
| 평균 lines/file | 63 | **19** | -70% |

### 해석

- **cairn 이 파일 수는 더 많지만 총 크기는 작음**. 이는 atomicity 가 실제 정보 밀도를 높였음을 의미 — owl 의 긴 doc 안에 있던 메타 섹션 (관련 자료, 다음 작업, 반복 헤더) 이 마이그레이션 과정에서 필수 핵심 claim 만 남도록 distill 됨
- **평균 파일이 cairn 쪽이 2.4x 작음**. LLM 이 한 번에 다룰 수 있는 단위가 더 잘 게 쪼개짐
- owl 의 total overhead 가 raw 파일, index 파일, report 구조 등으로 인해 더 큼

**승자**: cairn (더 밀집, 더 작은 원자 단위)

## 3. 차원 2 — Retrieval cost (wall-clock)

### 측정 (5 queries × 2 systems)

| query | owl (s) | cairn (s) | 차이 |
|---|---|---|---|
| `karpathy llm wiki` | 0.150 | **0.090** | **cairn 40% 빠름** |
| `smart gym rep counting` | 0.089 | **0.068** | cairn 24% 빠름 |
| `content factory pipeline` | 0.084 | **0.069** | cairn 18% 빠름 |
| `deos canonical` | 0.093 | **0.073** | cairn 22% 빠름 |
| `filing loop` | 0.087 | **0.073** | cairn 16% 빠름 |
| **평균** | **0.101** | **0.075** | **cairn 26% 빠름** |

### 해석

- cairn 이 평균 ~25-30% 빠름
- 이유 1: cairn 의 파일이 평균 2.4x 작아서 per-file read 가 빠름
- 이유 2: cairn 의 파일 수가 많지만 python rglob + text processing 이 여전히 선형이고 총 바이트가 작아서 cairn 총 처리량 적음
- 이유 3: owl 은 compiled + raw 둘 다 스캔 (결과에 raw 파일 등장). cairn 은 entries/ 만

**승자**: cairn (일관되게 빠름)

## 4. 차원 3 — Search quality (top-3 precision)

### Query 1: "karpathy llm wiki"

| 순위 | owl top-3 (score) | cairn top-3 (score) |
|---|---|---|
| 1 | karpathy-llm-wiki-gist-summary.md (55) | wiki-maintenance-near-zero-cost-for-llm (31) |
| 2 | karpathy-llm-wiki-gist-raw.md (46) | human-llm-role-split (30) |
| 3 | karpathy-wiki-compiler-workflow-raw.md (41) | llm-maintained-wiki-right-pattern (30) |

**관찰**: owl 의 top-3 는 *같은 raw 의 여러 버전* 을 반환 (summary + raw + 다른 raw). 실질 정보는 1 개. cairn 은 *3 개의 서로 다른 atomic claims* 반환. **cairn 이 더 유용**.

### Query 2: "smart gym rep counting"

| 순위 | owl top-3 (score) | cairn top-3 (score) |
|---|---|---|
| 1 | smart-gym-research-papers-raw.md (45) | **smart-gym-rep-counting-state-machine** (53) |
| 2 | smart-gym-architecture-concept.md (41) | smart-gym-confidence-score-formula (30) |
| 3 | smart-gym-experiment-status-summary.md (40) | smart-gym-accuracy-vs-flow-positioning (26) |

**관찰**: owl 은 "rep counting" 주제를 *부분* 포함하는 넓은 docs 를 반환 (research papers, architecture, status). cairn 은 *정확히 rep counting* 을 다루는 atomic entries 를 반환. **cairn top hit 이 owl top hit 보다 score 더 높고 더 specific**.

### Query 3: "content factory pipeline"

| 순위 | owl top-3 (score) | cairn top-3 (score) |
|---|---|---|
| 1 | content-factory-pipeline-templates-index.md (49) | **content-factory-pipeline-maturity-distribution** (36) |
| 2 | content-factory-pipeline-templates-raw.md (47) | content-factory-canonical-definition (35) |
| 3 | deos-content-factory-integration-report.md (43) | content-factory-truth-split (32) |

**관찰**: owl 의 top 2 가 같은 주제의 "index + raw" 쌍. cairn 은 3 개의 독립 측면 (maturity / definition / truth split). **cairn 이 더 diverse**.

**승자**: cairn (top-3 가 더 specific + diverse + non-duplicative)

## 5. 차원 4 — Session startup cost

### owl

세션 시작 시 vault 의 전체 구조를 파악하려면:
- `owl search` 를 여러 번 실행해야 함
- 또는 `ls ~/owl-vault/compiled/` 로 파일명 리스트만 봄
- **전체 TOC 가 없음**. LLM 은 무엇이 있는지 탐색적으로 발견해야 함

### cairn

```bash
cat ~/cairn-vault/INDEX.md
```

1 파일 로드로 **244 entries 의 id + type + topics + summary + confidence** 를 모두 확보.

| 지표 | 값 |
|---|---|
| INDEX.md 크기 | 80K, 260 lines |
| 단일 read 로 얻는 정보 | 244 entries 의 TOC 완전 |
| 세션 시작 비용 | 1 tool call, ~1 단일 file read |

### 해석

cairn 의 INDEX.md 는 fresh agent 설계의 핵심이자 실제 구현. 세션 시작 시 이 파일 1 개로 전체 vault 의 *topography* 를 확보. 다음 retrieval 은 이미 알고 있는 id 기반 targeted read.

owl 에는 이 layer 가 없음. 매 query 마다 full-corpus scan.

**승자**: cairn (카테고리적 승리 — owl 에 동등 기능 없음)

## 6. 차원 5 — Write cost (이관 작업 비용)

### 측정

**cairn 마이그레이션 방식** (2026-04-09 단일 세션):
- 17 batches × ~10 owl docs each
- 배치당 parallel 5 subagents (일부 배치), 나머지는 여러 라운드
- 실행 시간: 약 30-40 분
- 결과: 244 atomic entries

**owl 원본 작성 방식** (참고):
- 수동 작성, 여러 세션, 며칠에 걸쳐
- 각 compiled doc 이 owl-compiler 또는 사람 작성
- 결과: 192 compiled docs

### 해석

- cairn 의 **atomic + See also 없음** 설계가 parallel batch 마이그레이션을 가능하게 함
- 각 subagent 가 독립적으로 1 owl doc 을 N cairn entries 로 변환. 다른 subagent 의 작업을 알 필요 없음 (cross-link 이 없으므로)
- owl 은 본질적으로 sequential — 각 compiled doc 이 기존 docs 와의 관련성 확인 필요
- **cairn 은 write throughput 이 월등히 높음** (parallel 가능 덕분)

### Trade-off

cairn 의 parallel migration 은 가끔 semantic 중복을 생성함 (여러 subagent 가 비슷한 claim 을 각자 만듦). 이번 마이그레이션에서:
- ~5-10 건의 중복 감지 (subagent 가 보고) 
- 각 subagent 가 `ls` 로 기존 entries 확인하여 부분 회피
- Total collision: ~15-20 건 추정, 대부분 `-alt` suffix 로 해결

완벽하지 않지만 *실용적으로 작동*.

**승자**: cairn (설계가 parallel 을 지원함)

## 7. 차원 6 — Write ergonomics (LLM 관점)

### cairn

- 단위가 작음 → 각 LLM 작업의 scope 명확
- frontmatter 가 strict → 형식 실수 적음
- body ~400 token cap → over-writing 유도 없음
- topic tags 가 load-bearing → LLM 이 의식적으로 분류하게 됨
- See also 없음 → cross-link 실수 걱정 0

### owl

- compiled doc 이 큼 → 한 번의 LLM call 로 많은 맥락 필요
- `관련 항목:` 헤더 + 본문 cross-link 은 LLM 판단 부담
- 5 kind 분류 (summary/note/concept/index/report) 가 가끔 애매
- raw 를 읽으면서 compiled 를 쓰는 패턴이 context 많이 소비

### 해석

**cairn 쪽이 LLM 에게 가벼움**. 단위 작업이 명확하고, 실수 여지가 적고, 병렬화 가능.

owl 쪽은 더 "wiki-like" — 사람이 browse 하는 것도 염두에 두면 owl 의 장점이 있음. 하지만 본질이 LLM-first 라면 cairn 이 더 자연스러움.

**승자**: cairn (LLM-first 목적에 더 부합)

## 8. 종합 비교

| 차원 | owl | cairn | 승자 |
|---|---|---|---|
| Storage density | 192 files, 1.2M, 63 lines/file | 244 files, 976K, 19 lines/file | **cairn** |
| Retrieval speed (avg) | 0.101s | 0.075s | **cairn** (26% 빠름) |
| Search top-3 precision | duplicate-heavy, broader | specific, diverse | **cairn** |
| Session startup | no TOC | INDEX.md (1 file) | **cairn** |
| Write throughput | sequential (며칠) | parallel (30-40분) | **cairn** |
| LLM write ergonomics | wiki-like, heavier | atomic, lighter | **cairn** |

**6/6 cairn 승**. 단 aspects not measured:
- 인간이 Obsidian 에서 browse 하기 좋은가 — owl 이 단연 우위
- long-term maintenance (1년 후에도 의미 유지) — 미검증
- 실제 사용자가 "정말 더 잘 쓴다" 는 주관 경험 — 미검증
- 다른 LLM 모델 (Sonnet vs Opus vs GPT-4) 간의 차이 — 미검증

## 9. 놀라움

### 예상했던 것

- cairn 이 더 밀집하고 빠를 것 (예상대로)
- cairn 의 top-3 가 더 specific 할 것 (예상대로)
- cairn parallel migration 이 가능할 것 (예상대로)

### 놀라웠던 것

1. **cairn 의 총 바이트가 더 작음** — 파일 수가 27% 더 많은데도. Atomicity 가 자연 압축 효과. 메타 섹션 (관련 자료, 다음 작업 등) 이 사라진 영향.
2. **cairn 의 parallel migration 이 예상보다 깨끗함** — 17 subagent 배치에서 semantic 중복이 겨우 ~15-20 건. 각 subagent 가 `ls` 로 기존 확인한 덕분.
3. **owl search 가 top-3 에 raw + compiled 혼재** — 같은 주제의 "raw 원문" 과 "compiled summary" 가 둘 다 top 에 등장. cairn 은 entries/ 만 보므로 더 깔끔.
4. **244 entries 규모에서도 INDEX.md 가 80K (260 lines)** — 예상보다 작음. 8k 토큰 sharding trigger 까지 꽤 여유. 500+ entries 까지도 single INDEX.md 가능할 듯.

## 10. 한계

### 이번 벤치마크가 측정하지 못한 것

1. **실제 LLM query quality** — "이 질문에 owl/cairn 을 통해 얻은 답변이 얼마나 정확/유용한가" 는 정성 판단 필요. 이번엔 top-3 path 만 비교.
2. **Real Claude Code session 에서의 ergonomics** — 실제 일상 사용에서 어느 쪽이 편한가
3. **Drift / maintenance** — 1개월, 3개월, 6개월 후에도 vault 가 건강한가
4. **Write cost at scale** — 다음 owl compile/ingest 이벤트 시 cairn 에는 어떤 비용이 드는가
5. **Cross-machine behavior** — WebDAV sync 아래에서 cairn 이 어떻게 동작하는가

### 마이그레이션의 결함

- **중복 체크가 완벽하지 않음** — 244 entries 중 ~5-10 건 정도는 semantic 중복일 가능성. 수동 audit 필요
- **Topic tag 표준화 안 됨** — subagent 들이 각자 판단한 topic 이라 일관성 낮음 (e.g., `kb` vs `knowledge-base`)
- **Body 400 token cap 일부 초과** — 몇 entries 는 약간 넘음. 수동 재작성 또는 자동 split 필요
- **Language mixing** — 일부 entry 가 Korean + English 혼재. 검색에는 영향 없지만 스타일 일관성 ↓

## 11. 권고

### cairn 을 primary 로 전환할까?

**아직 아님**. 이유:
1. 벤치마크는 mechanical 측면 (speed, density) 측정. *usage quality* 는 미검증
2. owl 은 투자가 크고 (200+ docs, 여러 cleanup 거침), Obsidian 통합이 있음
3. cairn 은 아직 *실사용* 안 해봄. 내일 실제 Claude Code 세션에서 cairn 을 "external knowledge" 로 써보기 전엔 확신 불가

### 바로 할 수 있는 것

1. **owl 에 INDEX.md 도입** — cairn 의 가장 큰 이점 하나를 owl 이 흡수 가능. owl-librarian 이 주기적으로 INDEX.md 유지
2. **cairn 을 Claude Code 의 second knowledge source 로 연결** — 현재는 owl 만 global 설정됨. cairn 도 비슷하게 `~/.claude/agents/cairn-*.md`, `~/.claude/commands/cairn-*.md` 심링크
3. **1주일간 실사용** — 다음 세션들에서 의식적으로 cairn 도 쿼리해 비교
4. **cairn 의 중복 정리 + topic 표준화** — 실사용 전 수동 pass

### 장기

- **6개월 후 재벤치마크** — cairn 과 owl 어느 쪽이 실제로 더 사용되고 있는지
- **Hybrid 가능성** — owl 의 Obsidian 친화 + cairn 의 INDEX/atomic 장점 합치기
- **cairn 을 public 으로 공개할지** — 외부 사용자가 fresh-agent-design-based KB 를 써보면 어떨지

## 12. 결론 (정직하게)

**Mechanical 측면에서 cairn 이 owl 을 6/6 으로 이김**. Atomic unit + flat directory + INDEX.md + no See also 조합은 LLM-first 목적에 예상대로 잘 맞음. 마이그레이션 자체가 parallel 로 30-40 분만에 완료된 게 가장 강력한 증거 — *owl 설계 하에서는 불가능한 일*.

**그러나**:
- 이 벤치마크는 1 세션 + 1 마이그레이션 기반. *사용 경험* 은 미검증
- owl 의 Obsidian 통합과 인간 가독성은 여기 측정 안 됨
- cairn 의 중복/언어 혼재/topic 비표준화 같은 품질 이슈는 아직 cleanup 필요

**다음 단계는 숫자가 아니라 실 사용**. cairn 을 실제 Claude Code 세션들에 투입해 1주일 써보고, 그 때 다시 이 문서를 보강해야 v1 benchmark 가 될 수 있음.
