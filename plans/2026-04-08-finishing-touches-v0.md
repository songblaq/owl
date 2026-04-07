# Finishing Touches 계획 — 2026-04-08

작성일: 2026-04-08
상태: v0 (실행 대기)
선행:
- `plans/2026-04-08-post-backronym-cleanup-v0.md` ✓
- `plans/2026-04-08-github-release-and-llm-tool-reorientation-v0.md` ✓ (4 commits @ origin/main)

## 0. Context

오늘 두 차례 큰 작업 마치고 4 commits push 완료. 사용자가 다음 6 항목 중 5개를 진행 요청 (1번 외부 install 테스트는 사용자 본인 보류):

1. ~~첫 외부 사용자 install 테스트~~ (사용자 보류)
2. **LICENSE 파일 추가**
3. **README 에 GitHub badges**
4. **vault 데이터 정리** (root .md 2개 → 적절 폴더)
5. **owl health 131 issue 우선순위대로 정리**
6. **handoff 계약 다른 명령에도 확대** (init/setup/use/ingest 등)
7. **master → main migration 메모리 박제**

## 1. 작업을 4 phase 로 묶음

| Phase | 항목 | 의도 |
|---|---|---|
| **C — quick wins** | LICENSE, badges, memory note | 작고 독립, 한 commit |
| **D — handoff 확대** | 6개 명령에 next-step hint + handoff doc 업데이트 | 코드 + 문서, 한 commit |
| **E — vault data move** | root .md 2개 → 적절 폴더 | vault 작업, commit 대상 아님 (vault 가 git 외부) |
| **F — health triage** | 1 atomic fix + 전략 playbook doc + 84 deferred | 작은 commit + 큰 작업은 다음 세션 위임 |

## 2. 실행 순서

```
C → D → E → F
```

빠른 wins 먼저, vault 작업은 안전한 마지막 시점, health 마지막.

---

## 3. Phase C — Quick Wins

### C1. LICENSE 파일

**Goal**: public repo 의 표준. 라이선스 명시.

**선택**: **MIT** — 가장 자유롭고 일반적, oh-my-zsh 등도 MIT.

**Steps**:
1. `LICENSE` 파일 생성 (MIT, Luca, 2026)
2. pyproject.toml 의 `[project]` 에 license 필드 추가
3. README 에 license 한 줄 추가 (badges 옆)

### C2. README badges

**Goal**: 한눈에 프로젝트 상태 확인. 신뢰감.

**Badges**:
- License: MIT (img.shields.io)
- Python version: ≥3.9 (img.shields.io)
- "Built on Karpathy's LLM Wiki pattern" (custom badge)

**Steps**:
1. README 첫 줄 (제목 아래) 에 4-5 badges 한 줄 추가
2. 사용 기술 / lineage 시각적 표현

### C3. Memory: master → main migration 박제

**Goal**: 다른 프로젝트에서도 동일 이슈 만났을 때 즉시 적용 가능

**Steps**:
1. 새 메모리 파일: `feedback_git_master_to_main.md` 또는 기존 feedback 에 추가
2. 내용:
   - `gh repo create --source . --push` 가 로컬 master 를 그대로 push 함
   - GitHub 의 default branch convention 은 main 이므로 마이그레이션 권장
   - 마이그레이션 4 단계: rename / push / set default / delete remote master
   - 새 프로젝트 시작 시 commit 전에 main 으로 미리 rename 권장

---

## 4. Phase D — Handoff 확대

### D1. 코드: 6 명령에 next-step hint 추가

**대상 명령** (현재 hint 없음):
- `owl init` — vault 초기화 결과
- `owl setup` — 환경 진단 결과
- `owl use` — vault 전환 결과
- `owl ingest` — raw 파일 이동 결과
- `owl compile` — metadata 출력 결과
- `owl file` — output 이동 결과

**각 명령의 hint 패턴**:
- `init` 성공 시: "다음 단계: cd <vault>, owl status, claude (Claude Code 시작)"
- `setup` 성공 시: "다음 단계: owl init <vault path> 또는 owl status"
- `use` 성공 시: "다음 단계: owl status 로 활성 vault 확인"
- `ingest` 성공 시: "다음 단계: /owl-ingest 슬래시 명령으로 LLM 컴파일 시작 또는 owl-compiler 위임"
- `compile` 성공 시: "다음 단계: 위 metadata 를 owl-compiler 에 전달, related_existing 검토"
- `file` 성공 시: "다음 단계: compiled wiki 에 reference 추가 (filing loop)"

**Steps**:
1. `src/owl/initcmd.py` — 성공 출력에 hint
2. `src/owl/setupcmd.py` — 성공 출력에 hint
3. `src/owl/cli.py` `_run_use` — hint
4. `src/owl/ingestcmd.py` — `ingest_file`, `compile_metadata`, `file_output` 모두 hint

### D2. handoff doc 업데이트 (v0 → v1?)

**Goal**: 위 6개 명령의 handoff 계약을 v0 doc 의 §2 에 추가

**Steps**:
1. `docs/cli-llm-handoff-v0.md` 의 §2.4-§2.7 (현재 짧음) 을 expand
2. v0 그대로 유지 (v1 으로 bump 안 함 — 같은 doc 안에서 진화)
3. 각 명령에 "출력", "LLM 해석 패턴", "Next-step hint" 표 추가

---

## 5. Phase E — Vault Data Move

### E1. root .md 2개 정리

**현재 상태**:
- `~/owl-vault/README.md` (vault 자체 README, 보존)
- `~/owl-vault/CLAUDE.md` (어제 owl init 으로 설치, 보존)
- `~/owl-vault/2026-04-04-agent-cli-operating-principle-summary.md` (1712 bytes)
- `~/owl-vault/2026-04-04-openclaw-skill-structure-principles.md` (902 bytes)

**Steps**:
1. 두 .md 파일 read (kind 결정)
2. `2026-04-04-agent-cli-operating-principle-summary.md` → 이미 `-summary` suffix → `compiled/` 로 mv
3. `2026-04-04-openclaw-skill-structure-principles.md` → suffix 없음 → 내용 read 후 결정:
   - raw text 같으면 → `-raw.md` rename + `raw/` 로
   - 정리된 글이면 → `-note.md` rename + `compiled/` 로
4. mv 후 `owl health` 재실행 → 새 stale 추가됐는지 확인

**Risk**:
- 사용자가 의도적으로 root 에 둔 파일일 수 있음 → 내용 보고 신중 결정
- 옮긴 후 다른 곳에서 link 끊어짐 → owl health 로 검증

---

## 6. Phase F — Health Triage

### F1. 우선순위 — 솔직한 평가

전체 131 issue 의 분포:

| 룰 | count | severity | 작업 유형 | 이번 세션 처리? |
|---|---|---|---|---|
| **missing-summary-for-raw** | **84** | high | LLM compile (84 회) | ✗ **defer to next session** (owl-compiler 위임 필요) |
| weak-backlinks | 17 | low | Read+Edit, 1당 ~3분 | △ 일부만 (5-6개) |
| concept-candidate-missing | 13 | low | promotion (LLM 판단) | ✗ defer |
| report-missing-output-links | 10 | medium | review + edit | ✗ defer |
| stale-index-link-density | 3 | low | promotion | ✗ defer |
| orphan-concept | 2 | medium | review (사용자) | ✗ defer |
| **report-broken-output-link** | **1** | **high** | atomic fix | ✓ **이번에 fix** |
| index-candidate-missing | 1 | low | promotion | ✗ defer |

**핵심 결정**:
- **84 missing-summary 는 이번 세션에서 처리 안 함**. 84 LLM 컴파일 호출이 필요하고, 각각 별도 판단이 들어가야 함. 이건 owl-compiler 서브에이전트가 별도 세션에서 batch 처리할 작업.
- **1 broken-output-link 는 atomic** 이라서 즉시 fix
- **17 weak-backlinks 는 low** 이지만 5-6개 sample fix 로 패턴 입증 가능

### F2. Health Triage Playbook (신규 doc)

**Goal**: 다음 세션 (또는 owl-compiler 호출) 이 131 issue 를 어떻게 처리할지 결정 가능한 single source

**File**: `docs/health-triage-playbook-v0.md`

**Contents**:
- 8 룰 별 fix 전략 (CLI → 분류 → 행동 매핑)
- 위 분포표
- 우선순위 알고리즘 (severity × 작업 비용)
- 84 missing-summary 처리 전략 (batch / batch size / 검증)

### F3. atomic fix: report-broken-output-link (1 개)

**Steps**:
1. `owl health --json` 으로 정확한 path + detail
2. 해당 report 파일 read
3. broken link 식별 + fix
4. `owl health` 재실행 → 1 fewer issue

### F4. sample weak-backlinks fix (5-6 개)

**선택적**. 시간 남으면. 5-6개 weak-backlinks 를 read+edit 으로 fix 해서 패턴 입증.

---

## 7. Commit 전략

| Commit | 포함 |
|---|---|
| **C** | LICENSE, README badges, pyproject license 필드 |
| **D** | 6 명령 next-step hints + handoff doc 업데이트 |
| **F** | health-triage-playbook-v0.md, atomic fix, (옵션) sample backlink fixes |

E (vault move) 는 commit 대상 아님 (vault 가 git 외부)

## 8. 종료 기준

| 항목 | 검증 |
|---|---|
| LICENSE 존재 | `cat LICENSE | head -3` 정상 |
| Badges 표시 | README 첫 단락에 ![] 마크 5개 |
| Memory 박제 | `~/.claude/projects/.../memory/` 새 파일 또는 갱신 |
| 6 명령 hint | 각 명령 출력 끝에 "Next steps:" 표시 |
| handoff doc 갱신 | §2.4-§2.7 expanded |
| Vault root | 의도적 파일 (README, CLAUDE.md) 만 남음 |
| atomic high fix | `owl health --json` 의 high count 가 85 → 84 |
| triage playbook | `docs/health-triage-playbook-v0.md` 존재 |
| Commit 3개 push | `git log --oneline @{u}` 가 7 commits (4 + 3) |

## 9. 비계획

- 84 missing-summary-for-raw 의 일괄 처리 → 별도 세션
- 외부 install 테스트 → 사용자 본인 (보류)
- 새 owl-* 서브에이전트 추가
- vault 의 13 candidate-missing promotion 처리
