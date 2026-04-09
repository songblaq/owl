# Post-Finishing Continuation 계획 — 2026-04-08

작성일: 2026-04-08
상태: v0 (실행 대기)
선행: `plans/2026-04-08-finishing-touches-v0.md` 완료 (7 commits @ origin/main)

## 0. Context

finishing-touches 후 남은 5 항목을 순차 진행 (1번 외부 install 테스트는 사용자 보류).

## 1. 항목 매핑

| # | 항목 | Phase | 위험 | 예상 시간 |
|---|---|---|---|---|
| 2 | 84 missing-summary batch compile | **I** (sample) | 중간 (시간 소모) | 1-3 hours (sample 5-10 개) |
| 3 | vault README.md 갱신 | **H** | 낮음 | 10분 |
| 4 | health.py code-block-aware | **G1** | 중간 (regex 변경) | 30분 |
| 5 | 새 health rule: missing-required-headers | **G2** | 낮음 | 20분 |
| 6 | v0.1.0 release tag + gh release | **J** | 낮음 | 5분 |

## 2. 순서

```
G (code 개선) → H (vault doc) → I (sample compile) → J (release tag)
```

- **G 먼저**: code 변경이 다른 작업에 기반. 안정화 후 다음 단계
- **H 다음**: vault doc, 독립적
- **I 그 다음**: 가장 긴 작업, 중간에 실행
- **J 마지막**: release tag 는 모든 개선 후 stable state 박제

---

## 3. Phase G — health.py 개선

### G1. Code-block-aware regex (playbook §6.1)

**문제** (2026-04-08 발견):
- `extract_output_links` 와 `extract_link_targets` 가 markdown code block 안의 literal 을 link 로 오인
- `brain-health-check-full-report.md` 의 코드 블록 안 `outputs/*` literal 이 false positive 유발

**Fix 방향**:
1. 신규 helper `strip_code_blocks(content) -> str`
   - Triple-backtick fenced 블록 (```...```) 제거
   - 4-space indented code block 제거 (안전 위해 optional)
   - Inline `...` 제거
2. 모든 link-추출 함수 (`extract_output_links`, `extract_link_targets`, `extract_related_items` 등) 가 `strip_code_blocks` 통과 후 실행
3. 단위 테스트 (직접 pytest 없으므로 inline assert 스크립트)

**Steps**:
1. `src/owl/health.py` 에 `strip_code_blocks` 함수 추가
2. 기존 `extract_*` 함수 내부에서 사용
3. `owl health` 재실행 → 기존 false positive 가 사라졌는지 확인
4. 역복귀 테스트: 만약 atomic fix 로 `brain-health-check-full-report.md` 를 rephrase 했으면 *원상 복구* 해서 새 code 가 정말 false positive 를 잡는지 검증 (후퇴)
   - 실제로 원상 복구는 안 함 (rephrase 가 더 명확) — 대신 별도 테스트 파일로 검증

**Risks**:
- 코드 블록 파싱 오류로 legit link 도 날릴 위험 → 보수적 regex 사용
- 기존 issue count 감소 → 기대됨, 문제 아님

### G2. 신규 rule: missing-required-headers

**목표**: compiled doc 가 compiled-format-spec-v0.md §3 의 필수 헤더 (`상태:`, `유형:`, `출처:`, `작성일:`, `관련 항목:`) 를 갖는지 체크

**Rule 설계**:
- Severity: medium
- Trigger: compiled/*.md 파일이 위 5 헤더 중 *하나라도* 빠진 경우
- Detail: `missing headers: [list]`
- Exception: `.md` 가 아닌 파일 제외, `raw/` 제외, views/ 제외

**Steps**:
1. `src/owl/health.py` 에 `check_required_headers(base)` 함수 추가
2. `ALL_RULES` 리스트에 등록
3. `owl health` 실행, 새 룰 결과 확인 (몇 건 뜰지 미리 알 수 없음)
4. playbook 의 룰 표 갱신

**Risks**:
- 새 룰이 수십 건 노출 → 전체 issue 카운트 증가 → 사용자가 놀랄 수 있음
- 대응: "이건 새 룰이 드러낸 것" 이라고 명확히 표시

### G Commit

`phase G: health.py code-block-aware + missing-required-headers rule`

---

## 4. Phase H — vault README.md 갱신 (vault 작업)

### 현재 상태
- `~/owl-vault/README.md` (5380 bytes, 4-04 작성)
- 스테일 내용:
  - "Agent Brain" 이름
  - `~/.aria/brain/` 경로 (훨씬 옛 경로 — agent-brain 시절보다 이전)
  - KIB/LKS/MDV 컨셉 설명 (여전히 유효)
- 역할: 사용자가 Obsidian 에서 vault 진입 시 홈 노트

### Target 상태
- Name: "owl" (Agent Brain 대체)
- Path: `~/owl-vault/` (또는 vault-relative references)
- 컨셉 (KIB/LKS/MDV) 그대로 유지
- CLAUDE.md 와의 역할 분리 명시:
  - README.md = Obsidian 사용자용 vault 홈 (human reader)
  - CLAUDE.md = Claude Code session context (LLM reader)

### Steps
1. vault README.md 를 read
2. 이름/경로 stale 수정
3. 새 섹션 추가: "owl 과의 관계"
4. CLAUDE.md 와의 분리 명시
5. `owl health` 로 regression 확인

### Commit?
- vault 는 git 외부 → project repo commit 대상 아님
- 프로젝트 repo 에는 이 Phase 결과물이 directly 남지 않음. 계획 문서 (이 파일) 에만 기록.

---

## 5. Phase I — Sample Compile (#2)

### 현실 인식

84 raws 를 한 세션에서 모두 컴파일하는 것은 **비현실적**. 각 compile 은 deep read + judgment 필요. 대신:

1. **Sample size**: 5-10 raws 처리 (대표성 우선)
2. **Group 선택**: 그룹별 1-2 개씩 (openclaw, deos, smart-gym, atlas, karpathy 등)
3. **도구**: Task tool 로 owl-compiler 서브에이전트에 위임
4. **검증**: 각 compile 후 `owl health` 로 missing-summary 카운트 감소 확인
5. **결과 문서화**: `plans/` 에 sample-compile report 작성

### Sample 선정 기준 (우선순위)

1. **karpathy 관련** (1 파일) — owl 자체의 origin source, 우선 compile
2. **atlas 관련** (2 파일) — 시스템 knowledge base
3. **openclaw 관련** (2 파일) — 관련 프로젝트
4. **deos 관련** (2 파일)
5. **smart-gym / content-factory** (2 파일)

총 9 compile 을 sample 로 진행. 각 compile 은 owl-compiler Task 1개.

### 세션 전략

- **Parallel vs Sequential**: 3개 parallel 까지 (Task tool 한도 + 품질 우선). 그 후 순차
- **각 Task 입력**: raw path + `owl compile <path>` metadata + 기존 관련 docs 힌트
- **각 Task 출력**: `compiled/*-summary.md` + (선택) `*-note.md`
- **검증**: health 재실행 + missing-summary 카운트 monitoring

### 실패 시 대응

- Task 결과가 품질 낮음 → 개별 재작업, 품질 기준 문서화
- Task 중단 → 진행분 commit + 재개 전략 명시
- health count 증가 → 새 issue 생김 → 원인 추적

### Commit

`phase I: sample compile of N raws via owl-compiler subagent + report`

Project repo 에 들어가는 건:
- `plans/` 에 sample compile 결과 보고서 (어느 raw 를 어떻게 처리했는지)
- vault 의 compiled/ 변경은 project repo 가 아님

### 비계획
- 나머지 75-79 raws 처리 → 별도 세션 또는 nightly batch

---

## 6. Phase J — v0.1.0 Release Tag

### Pre-checks
- [ ] 모든 changes pushed
- [ ] main branch clean
- [ ] owl --version 이 0.1.0
- [ ] pyproject.toml version 이 0.1.0
- [ ] CHANGELOG.md 작성 여부? (없으면 release note 에 대체)

### Steps

1. `git tag -a v0.1.0 -m "..."` 로 annotated tag
2. `git push origin v0.1.0` 으로 tag push
3. `gh release create v0.1.0 --title "..." --notes "..."` 로 GitHub release 생성
4. release note 에 이번 세션 전체 progress summary 포함

### Release note 구성

```
# owl v0.1.0 — First Public Release

A personal LLM-maintained wiki implementing Karpathy's LLM Wiki pattern (2026),
in the spirit of Bush's Memex (1945).

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/songblaq/owl/main/install.sh | sh
```

## What's in this release

- CLI: owl {status, init, setup, use, search, health, ingest, compile, file, hook}
- 4-layer architecture (spec / runtime / vault glue / data)
- Claude Code integration (subagents + slash commands + hooks)
- LLM-friendly CLI: next-step hints + JSON output + subagent handoff contract
- Health check with 8+ rules

## Philosophy

owl is not just a CLI. The CLI is a deterministic primitive — the real work
(interpretation, judgment, compilation) happens in the LLM layer. See
docs/cli-llm-handoff-v0.md for the full handoff contract.
```

### Risks

- Tag 이미 존재 (unlikely) → 에러
- gh release create 실패 → 권한 / network

---

## 7. 종료 기준 (전체)

| 항목 | 검증 |
|---|---|
| Phase G pushed | `owl health --json` 가 code-block false positive 줄어듦 + 새 룰 나타남 |
| Phase H done | vault README.md 가 "owl" 이름 + 새 경로 |
| Phase I done | compiled/ 에 새 summary 5-10 개 + plans/ 에 보고서 |
| Phase J done | gh release view v0.1.0 표시 + tag push 됨 |

## 8. 비계획

- 나머지 75-79 missing-summary 처리
- 외부 사용자 install 테스트 (사용자 보류)
- LICENSE 이외 legal docs (CONTRIBUTING, CODE_OF_CONDUCT 등)
