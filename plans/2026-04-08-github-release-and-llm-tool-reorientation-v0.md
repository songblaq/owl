# GitHub Release + LLM-Tool 재정향 계획 — 2026-04-08

작성일: 2026-04-08
상태: v0 (실행 대기)
선행: `plans/2026-04-08-post-backronym-cleanup-v0.md` 완료 (2 commits 박제됨)

## 0. Context

오늘 오전에 백로닉 폐기 후 cleanup 1차를 끝내고 (commit `b83606a`), 사용자가 다음 두 축의 작업을 한 번에 요청:

1. **install flow 실제 동작화**: `owl → GitHub → curl 설치 → $owl, .owl 순으로 떨어져서 동작` — install.sh 에 박힌 placeholder URL 을 진짜로 만들고, end-to-end 검증
2. **LLM-tool 재정향**: owl 은 본질적으로 *LLM 이 컴파일·관리·분석* 하는 시스템. CLI 는 LLM 이 사용하는 도구의 한 형태일 뿐. CLI 결과를 LLM 이 *어떻게 해석하고 다음에 무엇을 할지* 가 더 본질. CLI 출력 + 서브에이전트 prompt 가 이를 반영해야

## 1. 디자인 원칙 (이 계획 전체에 적용)

| 원칙 | 의미 |
|---|---|
| **CLI ≠ end product** | CLI 는 LLM 의 *도구*. 사람이 읽기 좋은 출력보다 LLM 이 *해석하고 행동* 할 수 있는 출력이 우선 |
| **Two consumers** | 모든 CLI 명령은 (a) 사람이 직접 (b) LLM 이 subagent 안에서 — 두 소비자 모두 고려 |
| **Hint, not just data** | 명령 출력은 *원시 데이터* 만이 아니라 *LLM 이 다음에 할 수 있는 행동* 의 hint 도 포함 |
| **Subagent prompt = handoff contract** | 서브에이전트 prompt 는 "이 CLI 출력을 받으면 → 이렇게 해석 → 이런 행동" 의 명시적 계약 |
| **Doc-first 보존** | 위 원칙들이 코드보다 먼저 docs/ 에 박힘 |

## 2. 두 단계

```
Phase A — GitHub Release        (5 작업, 코드/인프라)
Phase B — LLM-Tool 재정향       (5 작업, 문서/디자인)
```

Phase A 가 먼저 (인프라 안정화), Phase B 가 그 위에서 진행.

---

## 3. Phase A — GitHub Release + Curl 설치 검증

### A1. Pre-flight (안전 점검)

**Goal**: 공개 push 전 민감 정보 / stale 데이터 점검

**Checks**:
- ✓ `.omc/project-memory.json` — OMC 메타데이터만, 민감 정보 0 (확인 완료)
- ✓ git author = `Luca <<owner>@users.noreply.github.com>` — noreply, 안전
- ✓ gh CLI auth = `songblaq` — 진짜 GitHub 계정
- 결정: **public** 가시성 (curl 설치 흐름의 본질이 공개 가능)

**Decisions** (자동 결정, 사용자 push-back 없으면 진행):
- repo name: `owl` (로컬과 일치)
- repo owner: `songblaq`
- visibility: **public**
- description (gh repo create --description): *"A personal LLM-maintained wiki. Karpathy's LLM Wiki pattern (2026), in the spirit of Bush's Memex (1945)."*

### A2. Create GitHub Repo + Push

**Steps**:
1. `gh repo create songblaq/owl --public --source . --push --description "..."`
2. 검증: `gh repo view songblaq/owl --json url,visibility,defaultBranchRef`
3. 검증: `git remote -v` 가 `origin` 가리킴
4. 검증: `git log --oneline @{u}` 가 2 commits 표시 (push 됨)

**Risks**:
- 이미 같은 이름 repo 존재 → 수동 처리 필요
- master 브랜치를 GitHub 가 main 으로 자동 변환할 수 있음 → 변환 후 우리도 master → main rename 검토

**Verification**:
- `gh repo view songblaq/owl` 정상
- `git ls-remote origin` 에 master/main commit 보임

### A3. Update install.sh URL

**Goal**: install.sh 의 `<owner>` placeholder → `songblaq` 실제 값

**Steps**:
1. Edit install.sh:
   - line 8 (Usage 주석): `<owner>` → `songblaq`
   - line 26 (REPO_URL): `<owner>/owl.git` → `songblaq/owl.git`
2. Update README.md:
   - Quick Install 의 curl 명령어를 `songblaq/owl` 로 갱신
3. `bash -n install.sh` syntax check
4. grep 으로 `<owner>` 잔여 0 확인

### A4. Test Install Flow (End-to-End)

**Goal**: `curl | sh` 가 정말 동작하는지 검증

**Test 전략** (가장 안전):
1. 임시 디렉토리에서 install.sh 실행
2. `OWL_REPO=/tmp/owl-install-test` 환경변수로 옛 ~/_/projects/owl 침범 방지
3. 실행 후 verify:
   - `/tmp/owl-install-test/.git/` 존재 (clone 됨)
   - `~/.local/bin/owl` 동작 — 다만 *지금 이게 이전 editable install 이라 path 가 ~/_/projects/owl 인지 /tmp/owl-install-test 인지 확인 필요*
   - `~/.owl/installed-at` timestamp 갱신
4. 검증 후 **복구**: `cd ~/_/projects/owl && pipx install --editable . --force` 로 owl entry point 를 본 프로젝트로 복원
5. 정리: `rm -rf /tmp/owl-install-test`

**Risks**:
- pipx --force 가 owl entry point 를 /tmp/... 로 일시 옮김 → 4번 단계로 복구 필수
- 도중 실패 시 owl CLI 가 깨질 수 있음 → 복구 절차 명확히

**Decision**: 위 4-단계 전략 그대로 실행. 문제 있으면 즉시 5 단계로 정리.

**Verification 후**:
- `owl --version` 정상
- `owl status` 가 `~/owl-vault` 정상 인식 (vault 는 환경변수/config 로 발견되므로 install path 와 무관)
- `~/.owl/installed-at` timestamp 새로 찍힘

### A5. Commit Phase A + Push

**Steps**:
1. `git status` 확인 (install.sh + README 변경)
2. `git add` + commit
3. commit message: `phase A: github release + install.sh real URL`
4. `git push`
5. 검증: GitHub 에서 새 commit 보임

---

## 4. Phase B — LLM-Tool 재정향

### B1. CLI 명령 audit (LLM 소비 관점)

**Goal**: 현재 owl CLI 의 모든 명령에 대해 *"LLM 이 이 출력을 받으면 다음에 무엇을 할 수 있는가?"* 를 정리

**대상 명령**:
- `owl status` — vault 정보, 카운트, health 요약
- `owl init [path] [--hooks]` — vault 초기화
- `owl setup` — 환경 진단 + 심링크 + (옵션) init
- `owl use <vault>` — 활성 vault 전환
- `owl search <query> [--json]` — 토큰 스코어 검색
- `owl health` — vault 무결성 점검
- `owl ingest <file>` — raw 파일 ingest (현재 stub?)
- `owl compile` (현재 stub?)
- `owl file` (현재 stub?)
- `owl hook <name>` — Claude Code hook dispatcher

**각 명령 audit 항목**:
1. 현재 출력 형식 (text / json / 양쪽)
2. 일반 사람이 보고 할 수 있는 일
3. **LLM (서브에이전트) 가 보고 할 수 있는 일** ← 핵심
4. LLM 가 즉시 사용 가능한 *next-action* 이 출력에 포함되어 있는가?
5. 부족하다면 어떻게 보강할지

**산출물**: audit 결과를 다음 단계 (B2) 의 input 으로 사용. 별도 commit 안 함.

### B2. 신규 문서: `docs/cli-llm-handoff-v0.md`

**Goal**: CLI 출력 ↔ LLM 해석 사이의 *handoff 계약* 을 단일 문서로 정의

**구조**:
```
# CLI ↔ LLM Handoff v0

## 0. 원칙
- owl CLI 는 LLM 의 도구다
- 모든 CLI 출력은 두 소비자 (사람 + LLM) 용
- 출력은 데이터 + next-action hint

## 1. 명령별 handoff

### owl status
- 출력 (사람용): vault 경로, version, health 요약
- 출력 (LLM용): 같은 텍스트 + 다음 권장 행동
- LLM 해석:
  - marker ✗ → "사용자에게 owl init 권유"
  - hooks ✗ → "owl init --hooks 권유"
  - health 이슈 high≥10 → "owl health 실행 권유 + 우선순위 분류"

### owl search
- 출력 (사람용): 색인 hits with scores
- 출력 (LLM용, --json): 같은 데이터 구조화
- LLM 해석:
  - 결과 0개 → 검색어 broaden
  - 결과 ≥10 → 너무 많음, refine 권유
  - title/score 기준 top-3 으로 사용자 답변

### owl health
- ...

(각 명령마다 똑같이)

## 2. 서브에이전트가 따라야 할 패턴

(공통 패턴들 — 출력 read → 분류 → 행동 결정 → Read/Edit 적용)

## 3. 향후 추가
- --llm 출력 형식 (가능한 모든 명령에)
- next-action JSON field
```

**Steps**:
1. 위 구조로 신규 doc 작성
2. 각 명령에 대해 audit 결과 (B1) 를 채워 넣음

### B3. 서브에이전트 prompt 갱신

**대상**:
- `src/owl/claude_assets/agents/owl-librarian.md`
- `src/owl/claude_assets/agents/owl-compiler.md`
- `src/owl/claude_assets/agents/owl-health.md`

**갱신 내용** (각 prompt 에 추가):
- "## CLI 출력 해석 패턴" 섹션
- "owl status / search / health 의 출력을 받으면 다음 절차로 행동" 단계 명시
- 예시 출력 + 해석 예 1-2개

**Risks**:
- prompt 길이 증가 → 토큰 비용. 다만 정확성 우선
- 기존 prompt 의 다른 섹션과 충돌 → manual review 필요

### B4. (선택) CLI 출력 형식 보강

**Goal**: 가장 자주 쓰이는 명령 (status, search, health) 의 출력에 LLM 친화 hint 추가

**Options**:
- (a) 아무 변경 안 함 (B2 + B3 으로 충분)
- (b) 출력 끝에 "Next steps:" 섹션 추가 (사람도 도움됨, LLM 도 활용)
- (c) `--llm` 또는 `--for-llm` 플래그 추가 (분리된 출력 모드)

**결정**: (b) 채택. status/search/health 의 출력 끝에 "Next steps:" 1-2 줄 추가. 코드 변경 최소.

**Steps**:
1. `owl status` 끝에 vault state 기반 next-step suggestion 1줄
2. `owl health` 끝에 issue 카운트 기반 next-step suggestion 1줄
3. `owl search` 끝에 결과 카운트 기반 next-step suggestion 1줄

**Risks**:
- 출력 형식 변경 → 기존 test 깨질 수 있음 (현재 test 0개라 안전)
- json 모드는 next-step 안 박음 (기계 파싱 보호)

### B5. Commit Phase B + Push

**Steps**:
1. `git add` (cli-llm-handoff doc + 3 agent prompts + 옵션 .py 변경)
2. commit message: `phase B: cli-llm handoff doc + subagent prompt updates + cli next-step hints`
3. push
4. GitHub 검증

---

## 5. 종료 기준 (전체)

| 항목 | 검증 |
|---|---|
| GitHub repo | `gh repo view songblaq/owl` 가 public 표시 |
| Commits pushed | `git log --oneline @{u}` 가 4+ commits |
| Install flow | `curl | sh` 가 깨끗한 디렉토리에서 동작 (test 결과로 증명) |
| owl CLI 동작 | `owl --version / status / search / health` 모두 정상 |
| handoff doc | `docs/cli-llm-handoff-v0.md` 존재 |
| 3 서브에이전트 prompt | "CLI 출력 해석 패턴" 섹션 존재 |
| CLI 출력 hint | `owl status / health / search` 끝에 next-step 1-2줄 |

## 6. 비계획 (Out of Scope)

- 다른 외부 통합 (Slack, Discord 등)
- 새로운 명령 추가 (`owl chat`, `owl ask` 등) — 별도 계획
- 새로운 서브에이전트 추가 (`owl-curator`, `owl-graph` 등) — 별도 계획
- vault 데이터 정리 (raw 폴더 형태 등) — owl-librarian 에 위임
- README 외 docs/ 의 추가 cleanup — 어제 완료된 분량 외 안 건드림
- master → main rename — GitHub 의 default 가 main 일 가능성 있어 migrate 검토는 필요하나 이번 계획에선 보류

## 7. 위험 요약

| 위험 | 완화 |
|---|---|
| pipx --force 가 owl entry point 를 /tmp 로 옮김 | A4 마지막 단계에서 본 프로젝트 dir 에서 pipx --force 다시 실행해 복원 |
| GitHub repo 이름 충돌 | 사전 `gh repo view songblaq/owl` 로 확인 |
| 공개 push 후 민감 정보 발견 | A1 에서 사전 점검 완료. 그래도 발견 시 force-push 또는 history 재작성 (마지막 수단) |
| Phase B 의 prompt 변경이 기존 동작 깨짐 | 점진 확장 (기존 섹션 보존) + manual review |

## 8. 다음 작업 (이 계획 완료 후)

- master → main rename 검토
- README 에 GitHub badges (build / license / version)
- LICENSE 파일 추가 (현재 없음)
- 첫 외부 사용자 대상 install 테스트 (사용자 본인 친구 등)
