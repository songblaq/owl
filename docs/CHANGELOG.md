# Changelog

omb 의 변경 이력. 2026-04-18 Re:Zero 이후로는 wiki 가 MAIN. 형식: [Keep a Changelog](https://keepachangelog.com/).

---

## [v3.3] - 2026-04-18 — input/brain/bench + UI 중립화

사용자 지시 두 개 반영:
1. "input / brain / bench 로 가고, brain 은 live / readonly 로" — 3단계 위계
2. "사용자는 wiki/akasha/오울이냐 그런거 몰라. 그냥 omb 를 쓴다" — 내부 용어 노출 금지

### Changed (경로)
- `~/omb/source/` → `~/omb/input/`
- `~/omb/live/` → `~/omb/brain/`
- `~/omb/live/wiki/` → `~/omb/brain/live/` (편집/축적)
- `~/omb/live/capsule/` → `~/omb/brain/readonly/` (읽기 전용 번들)
- `~/omb/bench/` 유지 (akasha + sandbox)
- `~/omb/brain/live/raw` symlink → `~/omb/input`

### Changed (UI 중립화)
- `omb status`: `wiki MAIN`, `live (SERVING)`, `bench (BENCHMARK only)` 같은 내부 라벨 제거. `brain/live 10 항목`, `brain/readonly 2 제품 번들`, `bench 2 도전자 (응답에 사용 안 함)` 로 경로 기반·한글 자연어
- `omb search`: `wiki search —` → `omb search —`, `── capsule: x ──` → `── 제품번들: x ──`
- `omb --help`: `wiki / capsule / akasha` 영어 라벨 빼고 "지식 / 제품 번들 / 벤치 하위 레이어" 한글 설명

### Changed (코드 path 상수)
- `wiki_ops.py` · `vault_ops.py` · `cli.py` (omb)
- `capsule/src/capsule/registry.py` · `capsule/cli.py`
- `akasha/src/akasha/ingestcmd.py` (상대경로 → 절대 `~/omb/input`)
- `tools/benchmark_vault.py` · `fix_sources.py` · `migrate_a.py` · `drift_audit.sh`

### Verified
- `omb status`: 3줄 요약 + 최근 기록. 내부 용어 없음 ✓
- `omb capsule status`: vault root `~/omb/brain/readonly`, 2 products built ✓
- `drift_audit.sh`: MISSING 0 / MISMATCH 0 ✓

---

## [v3.2] - 2026-04-18 — 볼트 2개로 쪼갬 (live / bench) — deprecated by v3.3

v3.1 의 "한 vault/ 안 2그룹" 해석이 사용자 의도와 달랐음. "볼트를 나누자" = **볼트 자체를 2개로**. 의미 축은 활성/비활성이 아니라 **사용 여부** — live 는 답하는 곳, bench 는 측정만.

### Changed (경로)
- `~/omb/vault/brain/` → `~/omb/live/` (wiki + capsule)
- `~/omb/vault/lab/` → `~/omb/bench/` (akasha + sandbox)
- `~/omb/vault/` 컨테이너 제거 — 볼트가 최상위 형제로 나란히
- `active-vault` pointer → `~/omb/bench/akasha`
- 코드 path 상수: `wiki_ops.py` · `vault_ops.py` · `cli.py` · `tools/drift_audit.sh`

### Why (네이밍 근거)
- `lab` 은 제가 지은 이름 — 의미 포괄적이고 사용자 의도 못 담음
- `bench` 는 사용자 제안 후보. `lab` 의 진짜 용도("wiki 에 도전하는 후보 측정") 가 이름에 드러남
- `live` 역시 사용자 제안. brain 보다 짧고 "운영 중" 의미 선명
- `brain` 폐기 이유: omb 프로젝트명(oh-my-**brain**) 과 중복, 페어 의미축(live/bench)으로 통일

### Verified
- `omb status`: `live (SERVING)` + `bench (BENCHMARK only, 측정·도전자 대기)` 2섹션 ✓
- `drift_audit.sh`: MISSING/MISMATCH 0 ✓
- wiki 10 pages, capsule 2 products 유지 ✓

---

## [v3.1] - 2026-04-18 — 2-그룹 볼트 구조 (deprecated by v3.2)

사용자 지시: *"볼트를 2가지로 나누자. 메인브레인+캡슐 용 볼트와 아카샤+실험용볼트."* 평평한 4개 → 2 그룹으로 정돈.

### Changed
- `~/omb/vault/wiki/` → `~/omb/vault/brain/wiki/`
- `~/omb/vault/capsule/` → `~/omb/vault/brain/capsule/`
- `~/omb/vault/akasha/` → `~/omb/vault/lab/akasha/`
- `~/omb/vault/lab/` (빈 슬롯) → `~/omb/vault/lab/sandbox/` (이름 명확화)
- `active-vault` pointer → `~/omb/vault/lab/akasha`
- 코드 path 상수 업데이트: `wiki_ops.py` · `vault_ops.py` · `cli.py` · `tools/drift_audit.sh`

### Why
평평한 구조(wiki + akasha + lab + capsule)가 "어느 것이 활성이고 어느 것이 비활성인지" 를 이름만으로 드러내지 못함. 2-그룹(brain vs lab) 으로 묶으면:
- `ls ~/omb/vault/` 만 봐도 역할 명확
- 하위 도구가 `brain/` 과 `lab/` 접근 권한을 그룹 단위로 구분 가능
- 교체 조건이 그룹 차원에서 표현됨 ("lab 의 무언가가 brain 을 뛰어넘으면")

### Verified
- `omb status`: `brain (MAIN group)` + `lab (INACTIVE group)` 2그룹으로 표시 ✓
- `drift_audit.sh`: 새 경로로 정상 작동 ✓

---

## [v3.0] - 2026-04-18 — **Re:Zero** (breaking)

Opus 4.7 이 2026-04-17 의 설계 stack 전체를 폐기하고 Karpathy 원안으로 회귀.

### Trigger (근본 원인)
- **드리프트 3건 관측** — Constella deprecated(2026-04-07) 가 `~/.claude/CLAUDE.md` 한글 매핑에 3주간 active 로 남음. ARIA/ClawVerse 경로 불일치.
- **observation drift** — `2026-04-14-infrastructure-infra-monitoring-stack` entry 가 Mac mini Netdata/Prom/Grafana up 주장, 실제 바이너리 미설치.
- **사용자 평가** — "아카샤가 뛰어날 것이라고 너가 만들어서 했는데 문제가 계속 생김 ... 너가 설계한 거 자체가 문제가 있다."

### Changed (볼트 재배치)
- `~/omb/vault/wiki/` → **MAIN** (Karpathy LLM Wiki). omb 의 유일한 기본 대상.
- `~/omb/vault/akasha/` → **INACTIVE** backup. `INACTIVE.md` 마커. `omb akasha <sub>` 명시 호출만.
- `~/omb/vault/lab/` → **INACTIVE** experimental slot (신규). 사용자 용도 지정 대기.
- `~/omb/vault/capsule/` → read-only delivery (변경 없음).

### Changed (omb CLI)
- `omb status / search / ingest` → wiki 대상
- `omb ingest <kind> <name>` → wiki 페이지 스켈레톤 생성. 내용은 LLM 이 직접 편집
- `omb akasha <sub>` → 이전 akasha 관련 명령 전부 이 하위로 이동 (status/search/ingest/health/audit/validate/supersede/rebuild/import)
- `omb search --no-capsule` → capsule 첨부 off (capsule 자동 매칭은 유지)
- `omb health/audit/supersede/validate/rebuild/import` 독립 커맨드 제거 → `omb akasha <...>` 필수

### Added
- `docs/REZERO-2026-04-18.md` — 전면 재설계 선언
- `tools/drift_audit.sh` — CLAUDE.md 매핑 × 실존 path × wiki deprecated 3방향 대조
- `~/omb/vault/wiki/entities/constella.md` (status=deprecated) — drift fix 페이지
- `~/omb/vault/wiki/concepts/drift-audit.md` — deprecation propagation 규약
- `vault/omb/src/omb/wiki_ops.py` — wiki 용 얇은 유틸 (status/search/new)

### Deprecated (삭제 아님, 헤더만 추가)
- `docs/priorities.md` · `docs/vault-versioning.md` · `docs/ingest-contract-v2.md`
- `docs/view-wiki.md` · `docs/plan-next.md` · `docs/experiment-3way-2026-04-17.md`
- `docs/bench-2026-04-17-rc1.md` · `docs/bench-2026-04-17-rc1-naming.md`
- 모두 `> DEPRECATED by docs/REZERO-2026-04-18.md` 헤더 추가

### CLAUDE.md (global) drift fix
- 한글 매핑: Constella → **DEPRECATED** 표시 / ARIA → `~/.aria/` 만 (repo 경로 삭제) / ClawVerse 라인 제거
- omb 섹션 전체 재작성: wiki=MAIN, tier 폐기, 단순 5개 규칙

### drift_audit 첫 실행 결과
- [1] CLAUDE.md 매핑 경로 실존: **0 mismatch** ✓
- [2] wiki deprecated ↔ CLAUDE.md active: **0 mismatch** ✓
- [3] akasha deprecated topics → wiki entity: GAP 5건 (hermes×2, omc×3) — 정보성, 다음 ingest 결정

### 설계 겸손 규약
- Karpathy 원안 이상 쌓지 않음
- 4단계 이상 의존 체인 금지
- 6개 이상 새 CLI 제안 시 사용자 승인 먼저
- 상세: memory `feedback_design_humility.md`

---

---

## [v2] - 2026-04-17

Tier 0/1 integrity principles 을 도구로 강제하기 시작한 첫 버전.

### Added
- Design priorities tier 체계 (`docs/priorities.md`) — Tier 0 integrity invariants / Tier 1 enforcement / Tier 2 quality / Tier 3 performance
- Ingest contract v2 spec (`docs/ingest-contract-v2.md`) — naming, frontmatter, evidence, pre-write search, source link, graph edge 강제
- `omb supersede <new-id> --replaces <old-ids>` — P0.1 Truth singularity. frontmatter 체인 merge + 옛 entry 를 `superseded/` 로 물리 이동
- `omb audit` — Tier 0/1 위반 가시화 (AUDIT.md 생성, no mutation)
- `omb health` strict mode — Tier 0/1 위반 시 CRITICAL + exit 1 (기존 "healthy 거짓말" 제거). `--legacy` 로 구 동작 호환
- `tools/benchmark_vault.py` — vault 간 정합성 지표 비교 도구
- `sources` 심볼릭 링크 → `~/omb/source` (traceability 경로 복구)
- Vault versioning 규약 (`docs/vault-versioning.md`) — 폴더명 `akasha` 고정, 버전 이력은 본 CHANGELOG

### Changed
- 네이밍 규칙: `<YYYY-MM-DD>-<topic>-<slug>.md` canonical form 으로 전체 통일 (606 entries rename). 원본 비율 4.7% → 100%
- 기존 frontmatter `source: sources/...` → 절대 경로 또는 vault-relative (266 entries 복구). source integrity 0% → 41.8%
- ATLAS.md 의 "Design Principles" → "Design Priorities" tier 구조
- plan-2026.md 에 §1.1 설계 우선순위 추가

### Removed
- 3-way 실험 vault `akasha-archive-2026-04-17`, `akasha-a-migrate`, `akasha-b-rebuild`, `akasha-c-hybrid` — 벤치마크 종료 후 전부 삭제 (결과는 `docs/experiment-3way-2026-04-17.md` 에 기록)
- vault 내부 `VERSION.md`, `EXPERIMENT.md` 메타 파일 — 중복 금지 원칙

### Known violations (다음 rc 목표)
- P0.2 Traceability: source integrity ~42% (약 370 broken links) — source 확보 또는 entry 삭제 필요
- P0.1 Truth singularity: 17 duplicate-decision topics 잔존 — 수동 supersede 필요
- P1.1 Discipline as code: `omb ingest` 에 contract v2 validator 미내장

### Supersede log (이번 버전에서 적용된 체인)
- `2026-04-17-deos-dgx-main-swap-decision` ← `2026-04-15-homelab-llm-final-decision`, `2026-04-16-deos-homelab-llm-decision-stack`, `2026-04-17-dgx-port-8000-qwen122b`

---

## [v2.1] - 2026-04-17

외부 응답 통합.

### Added
- `omb search` 가 query 에 capsule product 이름이 포함되면 해당 capsule 도 자동 검색해 결과에 병합. `--no-capsule` 로 비활성

### Changed
- 외부에서 `omb search` 호출 시 akasha + 매칭되는 capsule 결과를 같이 보여줌 — 단일 응답 창구

---

## [v2.2] - 2026-04-17

wiki 를 상시 view 로 정규 등록 (Karpathy LLM Wiki 패턴, akasha 와 병렬).

### Added
- `~/omb/vault/wiki/` 상주 vault — entities/ concepts/ sources/ syntheses/ + index.md + log.md + AGENTS.md
- seed 페이지 3개 (homelab 도메인): `entities/dgx-spark`, `concepts/llm-serving`, `sources/homelab-infra-reorg`
- `docs/view-wiki.md` — wiki view 운영 규약
- `docs/view-contract.md` 의 Current views 에 wiki 등록 (akasha + wiki + capsule 3 view)

### Rationale (뒤집음)
직전 판단 "wiki 는 상시 아님, /tmp 에 임시 빌드" 를 뒤집음. 근거: (a) Karpathy 패턴 자체가 incremental 유지 — 재빌드 부담 없음, (b) 상주해도 akasha 와 독립 view 이므로 진실 분열 아님 (둘 다 source 에서 유래), (c) 매번 빌드 = 토큰·시간 낭비 + compounding 이점 상실, (d) `~/omb/vault/` 에 자리 잡고 Obsidian 으로 바로 열리는 편익.

### Open-source
풀 설치 대신 규약·형식·워크플로만 차용. 주요 참고: [karpathy/llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), [ussumant/llm-wiki-compiler](https://github.com/ussumant/llm-wiki-compiler), [tobi/qmd](https://github.com/tobi/qmd).

---

## [v2.3] - 2026-04-17

wiki 확장 + 차기 계획 수립.

### Added
- wiki 페이지 5개 추가 (homelab 도메인 완성): `entities/homelab`, `entities/openclaw`, `concepts/model-selection`, `concepts/agent-topology`, `sources/llm-provider-audit`. 총 **8 페이지**
- wiki 첫 lint 실행 — issues 0 (broken link 0, orphan 0, contradiction 1 명시 기록)
- `docs/plan-next.md` 차기 작업 계획 — Tier 구조 매핑, rc 그룹핑, 일정, 스코프 명시

### Changed
- `omb audit` 재실행 — entries 638, broken source 373, orphan 329 (568 → 감소), superseded 2

### Known violations (rc1 타깃)
- P0.2 source integrity 41.5% → target ≥ 95%
- Naming canonical 73.5% → target ≥ 95%
- 17 duplicate-decision topics 수동 검토 대기

---

## [v2.4] - 2026-04-17

**첫 HEALTHY 도달.** Tier 1 enforcement 도구 대량 추가 + rc1 mechanical 정화 승격.

### Added (Tier 1 도구)
- `omb validate [--entry <id>] [--json]` (T1-A) — contract v2 C1..C6 검증, no mutation
- `omb audit --json` (T1-B) — 기계 처리용 출력
- `omb rebuild [--dry-run|--apply]` (T1-C) — akasha-rc1 skeleton 생성 (P0.4 대비)
- `omb import <path> [--normalize]` (I-A) — normalize 게이트
- `tools/wiki_lint.py` (W-B) — wiki L1..L5 자동 검증
- `tools/fix_sources.py` — broken source fuzzy-match 복구 (T0-A)
- `tools/fix_double_date.py` — `YYYY-MM-DD-YYYY-MM-DD-<hash8>-<slug>.md` → canonical 변환 (T0-B)
- `vault/omb/src/omb/validator.py` — contract v2 엔진

### Changed (rc1 승격 — mechanical 정화)
- **source integrity 41.5% → 98.4%** (T0-A 적용, 363 broken → 10 resolved + 2 unresolvable + 4 ambiguous)
- **naming canonical 73.5% → 100%** (T0-B 적용, 169 `2026-04-13-2026-04-13-<hash>-*.md` 패턴 정리)
- `omb health` 최종 상태: **HEALTHY** (Tier 0/1 위반 0)
- 기존 active akasha 제거, rc1 → akasha 승격 (vault-versioning 규약대로)

### Fixed
- lattice 마이그레이션 잔재 (이중 date prepend) 완전 해소
- validator `fix_double_date.py` 의 regex 를 `[0-9a-f]{8}` → `[0-9a-z]{8}` 로 확장 (hex 외 base36-류 ID 대응)

### Remaining (Re:Zero 이후 무의미 — 아래 v3.0 참조)
- P0.1 Truth singularity: 17 duplicate-decision topics 잔존 (semantic 판단, 수동 승인 반복 필요) — `docs/plan-next.md` T0-C
- P0.2 10건 broken source (source 파일 미존재 또는 fuzzy 충돌) — 개별 검토
- P0.4 Rebuildable quarterly 실증 — Q2 스케줄 유지
- W-A wiki 도메인 확장 (deos, openclaw 등)

### Benchmark 기록
- `docs/bench-2026-04-17-rc1.md` — source fix 직후
- `docs/bench-2026-04-17-rc1-naming.md` — naming fix 직후 (승격 최종)

### Lessons
- Tier 1 도구 (fix_sources + fix_double_date) 가 있으면 Tier 0 데이터 위반은 **한 세션 수 분에** 해소 가능. Q2 목표였던 HEALTHY 가 하루에 도달한 것은 "도구 먼저" 원칙 검증.
- 단 semantic 위반 (duplicate supersede) 는 여전히 수동 — 도구로 축소 불가.

---

## [v1] - pre 2026-04-17

owl/facet/lattice/cairn/wiki 수렴 직후 상태. Tier 0 integrity 가 convention-only 로 운영되다 붕괴한 버전.

### 시점 실측 (2026-04-17 측정)
- entries: 636 / compiled: 71 / graph edges: 562
- naming conformance: 4.7%
- source integrity: 0% (broken links 636)
- supersedes coverage: 1.3%
- superseded/: 0 files (물리 이동 디시플린 부재)
- duplicate decision topics: 18
- orphan ratio: 95.1%

이 수치들이 v2 의 tier 구조·enforcement 도입을 촉발. 상세 분석: `docs/experiment-3way-2026-04-17.md`.
