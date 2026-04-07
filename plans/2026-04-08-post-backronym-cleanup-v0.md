# 백로닉 폐기 후 정리 작업 계획 — 2026-04-08

작성일: 2026-04-08
상태: v0 (실행 대기)

## 0. Context

2026-04-07 (어제):
- 오전: brain → owl 풀 리네임 (CLI/패키지/vault/env/슬래시/서브에이전트)
- 오후: "OWL = Own your Wiki, LLM" 백로닉 폐기. 8개 파일 (README, AGENTS, docs, src, vault-template, 메모리) 의 백로닉 단락만 도려냄. CLI/파일시스템 0줄 변경.

오늘 (2026-04-08): 리네임 + 백로닉 폐기 직후 남은 청소 작업 4개를 한 번에 처리.

## 1. 작업 범위 — 4개

| # | 작업 | 위험도 | 예상 시간 |
|---|---|---|---|
| 1 | **첫 git commit** (현재 55개 untracked/staged 파일) | 낮음 (.gitignore 만들어야) | 10분 |
| 2 | **install.sh stale 값 정리** (placeholder URL, agent-brain 경로 기본값) | 낮음 (텍스트만) | 5분 |
| 3 | **owl init** (vault 마커 + CLAUDE.md + hooks 설치) | 낮음 (vault 비파괴 추가) | 5분 |
| 4 | **docs/ 8개 파일 stale 참조 정리** (옛 경로, 옛 백로닉) | 중간 (점진 정리) | 20분 |

## 2. 실행 순서 (의존성 + 안전성 기준)

```
1 (commit) → 2 (install.sh) → 3 (owl init) → 4 (docs cleanup) → 5 (final commit)
```

**왜 이 순서**:
- **1번 먼저**: 현재 commit 0개. 후속 작업 중 사고 시 복구 불가 → 안전 백업 먼저.
- **2번 그 다음**: 텍스트만, 매우 안전. 외부 entry point 라 빨리 정리.
- **3번 그 다음**: vault 가 변경되지만 비파괴 추가 (마커/CLAUDE.md/hooks 만 새로 생성).
- **4번 마지막**: 가장 큰 작업 (8개 파일). 1-3 완료 후 건드림.
- **5번**: 1-4 결과 모두 묶어서 두 번째 commit 으로 마감.

## 3. Git Author 식별

현재 상태:
- 로컬 git config: 없음
- 글로벌 git config: 없음
- gh CLI: `songblaq` 로그인 중
- pyproject.toml: `authors = [{ name = "Luca" }]`

**결정**: 인라인 `-c user.name=... -c user.email=...` 사용 (글로벌 config 안 만짐).
- name: `Luca` (pyproject.toml 의 authors 와 일치)
- email: `songblaq@users.noreply.github.com` (GitHub 표준 noreply)

다른 값 원하시면 step 1 시작 전 알려주시면 변경.

## 4. 단계별 상세 계획

### Step 1 — First Git Commit

**Goal**: 현재 모든 작업물을 첫 commit 으로 박제.

**Pre-checks** (이미 완료):
- ✓ 민감 파일 없음 (.env, .key, credentials 검색 결과 0)
- ✓ .DS_Store 노이즈 없음
- ✓ 55개 파일 staged/untracked
- ✓ git author 결정됨

**Steps**:
1. `.gitignore` 생성:
   ```
   .omc/state/
   .omc/sessions/
   .omc/logs/
   .omc/research/
   __pycache__/
   *.pyc
   *.pyo
   .DS_Store
   .venv/
   *.egg-info/
   build/
   dist/
   ```
   - `.omc/project-memory.json` 은 keep (의도된 메모리)
2. `.gitignore` 자체를 stage
3. `git add` 로 모든 파일 stage (already-staged + untracked)
4. `git -c user.name="Luca" -c user.email="songblaq@users.noreply.github.com" commit -m "..."`
5. commit 메시지:
   ```
   initial owl project import after brain → owl rename
   
   - 어제 (2026-04-07) brain → owl 풀 리네임 + "OWL = Own your Wiki, LLM"
     백로닉 폐기 결과를 첫 commit 으로 박제.
   - 50+ 정책 docs, AGENTS.md, src/owl/ Python 패키지, vault-template,
     install.sh, README 모두 포함.
   - CLI: owl. 패키지: owl. vault: ~/owl-vault.
   ```
6. `git status` 로 clean state 확인
7. `git log --oneline` 로 1개 commit 확인

**Risks**:
- `.gitignore` 가 너무 좁으면 노이즈 commit
- `.gitignore` 가 너무 넓으면 의도된 파일 누락
- → 위 패턴이 균형: state/sessions/logs 만 제외, project-memory 는 포함

**Verification**:
- `git log --oneline | wc -l` → `1`
- `git status` → `nothing to commit, working tree clean`
- `git ls-files | wc -l` → 50+

---

### Step 2 — install.sh Stale 값 정리

**Goal**: install.sh 의 placeholder URL 과 agent-brain 경로 기본값 갱신.

**현재 상태** (확인됨):
- Line 11: `# 1. Clones (or updates) the project repo to ~/_/projects/agent-brain`
- Line 24: `REPO_DIR="${OWL_REPO:-${AGENT_BRAIN_REPO:-$HOME/_/projects/agent-brain}}"`
- Line 25: `REPO_URL="${OWL_REPO_URL:-${AGENT_BRAIN_REPO_URL:-https://github.com/yourname/owl.git}}"`

**Steps**:
1. Line 11 주석: `agent-brain` → `owl` 로 교체
2. Line 24 기본값: `$HOME/_/projects/agent-brain` → `$HOME/_/projects/owl` 로 교체. AGENT_BRAIN_REPO 는 폴백으로 보존 (호환성).
3. Line 25 placeholder: `https://github.com/yourname/owl.git` → `https://github.com/<owner>/owl.git` 로 교체 (더 명확한 placeholder). 진짜 GitHub 만들면 그때 sed.
4. `bash -n install.sh` 로 syntax check
5. grep 으로 `agent-brain` 사라짐 확인 (env var 폴백 이름 제외)

**Decision**: 진짜 GitHub repo 는 만들지 않음 (사용자 미지시). placeholder 만 더 명확하게.

**Risks**: 매우 낮음

**Verification**:
- `bash -n install.sh` → exit 0
- `grep 'yourname' install.sh` → empty
- Line 24 의 기본값이 owl

---

### Step 3 — owl init (Vault 공식화)

**Goal**: `~/owl-vault` 에 마커, CLAUDE.md, hooks 설치하여 공식 owl vault 로 만듦.

**현재 vault 상태** (확인됨):
- 위치: `~/owl-vault`
- marker `.owl-vault`: ✗ 없음
- `CLAUDE.md`: ✗ 없음
- hooks (`.claude/hooks.json`): ✗ 없음
- 기존 데이터: `.obsidian/`, `compiled/` (167), `raw/` (61), `views/`, `outputs/`, `research/`, `logs/`, `inbox/`, `tmp/`, `config/`, README.md, 2 raw md 파일

**Steps**:
1. `owl init` 명령 실행 (마커 + CLAUDE.md)
2. `owl init --hooks` 또는 위 명령에 포함됐는지 확인
3. `owl status` 로 모든 항목 ✓ 확인
4. `ls -la ~/owl-vault/.owl-vault ~/owl-vault/CLAUDE.md ~/owl-vault/.claude/` 존재 확인

**Risks**:
- vault 안에 새 파일 생성 (비파괴)
- 기존 README.md 와 충돌 없음 (CLAUDE.md 는 별도 파일)
- 기존 .obsidian/ 와 충돌 없음 (.claude/ 는 별도 디렉토리)

**Verification**:
- `owl status` 가 `marker`, `CLAUDE.md`, `hooks installed` 모두 ✓
- vault 데이터 카운트 (raw 124, compiled 203, views 10) 변동 없음

---

### Step 4 — docs/ 8개 파일 Stale 참조 정리

**Goal**: docs/ 안의 옛 경로 (`agents/brain`, `agent-brain`) 와 옛 백로닉 (`Own your Wiki`) 잔여 참조 정리.

**대상 파일** (grep 결과):
1. `docs/operational-layer-spec-v0.md` — 핵심 spec, 어제 1줄만 갱신, 본문에 더 있을 수 있음
2. `docs/folder-policy-v0.md` — 핵심 정책
3. `docs/lks-kib-mdv-spec-v0.md` — 핵심 spec
4. `docs/karpathy-checklist-audit-v1.md` — 감사 문서
5. `docs/karpathy-ingest-rules-v0.md` — 정책
6. `docs/openclaw-reflection-log-v0.md` — 회고 로그
7. `docs/doc-first-application-example-v0.md` — 예시
8. `docs/first-principles/equation-first.md` — 원칙

**Steps** (각 파일별):
1. 파일 read
2. stale 패턴 식별:
   - `~/.agents/brain` → `~/owl-vault`
   - `agent-brain` (프로젝트 dir) → `owl`
   - `Own your Wiki, LLM` → 삭제 또는 *"개인 LLM-maintained wiki"* 로 교체
3. 컨텍스트 보존하며 Edit
4. 다음 파일

**Order** (위험도 낮은 순):
- 회고 로그 → 감사 문서 → 정책/spec → 핵심 spec
- 다만 8개 모두 1 batch 로 처리 가능 (각 파일이 작음)

**Risks**:
- 본문에 `agent-brain` 이 *역사적 맥락* (예: "이전 이름은 agent-brain") 으로 등장할 수 있음 → 그건 보존
- 백로닉이 description 외 다른 의미로 등장할 수 있음 → 컨텍스트 봐서 결정

**Verification**:
- 정리 후 grep:
  ```
  grep -rn "agents/brain\|Own your Wiki" docs/
  ```
- 결과가 *역사 맥락* 만 남고 *현재 정의/명령* 은 0

---

### Step 5 — Final Commit

**Goal**: Step 2-4 의 결과를 두 번째 commit 으로 박제.

**Steps**:
1. `git status` 로 변경된 파일 확인
2. `git diff --stat` 로 변경 규모 확인
3. `git add` 로 stage
4. `git -c user.name="Luca" -c user.email="songblaq@users.noreply.github.com" commit -m "..."`
5. commit 메시지:
   ```
   post-rename cleanup: install.sh, vault init, docs stale refs
   
   - install.sh: placeholder URL and agent-brain default path → owl
   - owl init: vault marker, CLAUDE.md, hooks installed
   - docs/: 8 files with stale agent-brain paths and owl backronym
     references cleaned up
   ```
6. `git log --oneline` → 2 commits

## 5. 종료 기준 (Exit Criteria)

다음 모두 만족 시 작업 종료:

| 항목 | 검증 |
|---|---|
| Git history | `git log --oneline` 가 2 commits |
| Working tree | `git status` 가 clean |
| install.sh | `grep 'yourname\|agent-brain' install.sh` 가 env var 폴백만 |
| owl status | marker / CLAUDE.md / hooks 모두 ✓ |
| docs stale | `grep -rn "Own your Wiki\|agents/brain" docs/` 가 역사 맥락만 |
| owl 동작 | `owl status / search 'wiki' / health` 모두 정상 |

## 6. 비계획 (Out of Scope)

다음은 이번 작업에 포함하지 않음:

- 진짜 GitHub repo 생성 (`gh repo create`) — 사용자 미지시
- 두 번째 풀 rename (owl → wikibrain 등) — 어제 결정 보존
- vault 데이터 마이그레이션 (raw 폴더 정리, 2 .md 파일 raw/ 로 이동 등) — owl-librarian 작업
- docs/ 의 *내용* 갱신 (stale 참조 외) — 별도 작업
- Tier 2 secondary docs (sample, audit 외) 의 점진 정리 — 후속

---

## 7. 진행 후 다음 작업 후보

이 계획 완료 후 다음 자연스러운 작업:

1. **GitHub repo 생성** + remote 연결 + push (사용자 명시 시)
2. **owl-librarian 으로 vault 정리** (raw 폴더 형태, stale 노트 등)
3. **Karpathy gist 의 새 항목** (있다면) 다시 ingest
4. **secondary docs 의 점진 정리** (50+ 파일)
5. **스킬/agent prompt 의 voice 통일** (백로닉 폐기 톤 반영)
