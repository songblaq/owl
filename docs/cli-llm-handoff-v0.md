# CLI ↔ LLM Handoff v0

작성일: 2026-04-08
상태: v0

## 0. Premise — owl 의 진짜 layer 는 LLM 이다

owl 의 본질은 *LLM 이 컴파일·관리·분석·환류* 하는 wiki 다. CLI 는 그 LLM 이 사용하는 *결정적 도구* 의 한 형태일 뿐.

따라서 owl CLI 의 모든 명령은 두 종류의 소비자를 동시에 가진다:

1. **사람** — 직접 CLI 호출, 텍스트 출력 읽음
2. **LLM (서브에이전트)** — Claude Code 안에서 Bash 도구로 호출, 출력을 *해석* 하고 *다음 행동* 을 결정함

이 문서는 두 소비자에 대한 CLI 출력의 *handoff 계약* 을 정의한다.

## 1. 핵심 원칙

| # | 원칙 | 의미 |
|---|---|---|
| 1 | **두 소비자 모두 1급** | 모든 명령이 사람 + LLM 모두에게 유용해야 |
| 2 | **`--json` 으로 분리** | 기계 파싱은 `--json`. 사람 출력은 default. LLM 은 둘 중 선택 |
| 3 | **데이터 + hint** | 출력은 *원시 데이터* 만이 아니라 *다음 행동* hint 도 포함 |
| 4 | **Hint 는 사람에게도 유용** | LLM 친화 hint 는 사람도 도움받음 — 분리 안 함 |
| 5 | **명확한 종료 코드** | 0 = clean, 1 = issues found, 2 = error. LLM 이 분기 가능 |
| 6 | **위치 무관 flag** | `owl health --json` 도 `owl --json health` 도 `owl health <args> --json` 도 동작 |
| 7 | **CLI ≠ end product** | CLI 는 *deterministic primitive*. 진짜 작업 (해석/판단/행동) 은 LLM 이 한다 |

## 2. 명령별 Handoff 계약

### 2.1 `owl status`

**현재 출력 (사람용)**:
```
owl status
==========
  version:        0.1.0
  vault:          /Users/lucablaq/owl-vault
    discovered via: active-vault config
  ...
Vault state:
  marker (.owl-vault):   ✓
  CLAUDE.md:              ✓
  hooks installed:        ✓
Counts:
  raw                  124
  compiled             203
  ...
Health: 131 issue(s)
  high       85
  medium     12
  low        34
```

**`--json` 출력**: 동일 정보, JSON 구조

**LLM 해석 패턴**:
1. `marker / CLAUDE.md / hooks` 중 하나라도 ✗ → "사용자에게 `owl init [--hooks]` 권유"
2. `raw_count > compiled_count * 0.5` → "compile backlog 큼. owl-compiler 에 raw 처리 위임"
3. `health.high ≥ 10` → "owl health 호출, 우선순위 분류 시작"
4. `vault discovered via: env` 와 `active config` 가 다름 → "사용자가 임시 override 했다는 신호. 명시적으로 알려주기"

**Next-step hint 권장**:
```
Next steps:
  Vault has 85 high-severity issues. Run `owl health` for details.
  84 raw files lack a compiled summary. The owl-compiler subagent can fill these in.
```

### 2.2 `owl search <query>`

**현재 출력 (사람용)**:
```
[1] compiled/2026-04-04-brain-maintenance-loop-index.md
    title: Brain Maintenance Loop Index
    type: index
    score: 12
    snippet: # Brain Maintenance Loop Index
[2] ...
```

**`--json` 출력**:
```json
{
  "vault": "...",
  "count": 10,
  "matches": [
    {"path": "...", "score": 12, "title": "...", "kind": "index", "snippet": "..."},
    ...
  ]
}
```

**LLM 해석 패턴**:
1. `count == 0` → "검색어 broaden, 또는 raw/ 도 함께 검색 (`--scope all`)"
2. `count ≥ 10` → "결과 너무 많음. 1-3등을 사용자에게 보여주고 더 보고 싶은지 물음"
3. `top match score >= 10` → "강한 매치. 그 파일을 Read 도구로 읽고 사용자 질문에 답"
4. `top match score < 5` → "약한 매치. 검색어 refine 권유, 또는 결과 신뢰도 명시"
5. `kind == 'index'` 우선 → "index 문서는 다른 문서로의 지도. 거기서 link 따라가기"

**Next-step hint 권장**:
```
Next steps (count=10):
  Top hit score 12 is strong — read it directly.
  4 results have score < 5 — consider narrowing the query.
```

### 2.3 `owl health`

**현재 출력 (사람용)**:
```
owl Wiki Health Check
vault: /Users/lucablaq/owl-vault
issues: 131

[missing-summary-for-raw] count=84
- (high) raw/2026-04-04-... :: expected compiled/...
...
[broken-cross-reference] count=12
...
```

**`--json` 출력** (health.py 가 이미 지원, **단 cli.py wiring 버그로 노출 안 됨**):
```json
{
  "total_issues": 131,
  "by_severity": {"high": 85, "medium": 12, "low": 34},
  "rules": {
    "missing-summary-for-raw": [
      {"severity": "high", "path": "...", "message": "..."},
      ...
    ],
    ...
  },
  "status": "issues_found"
}
```

**LLM 해석 패턴**:
1. `status == 'clean'` → "vault 건강. 다른 일 진행"
2. `by_severity.high ≥ 50` → "긴급. 사용자에게 경고 + owl-health 서브에이전트 호출 권유"
3. 룰별 분기:
   - `missing-summary-for-raw` → owl-compiler 에 위임
   - `broken-cross-reference` → 자체 Read+Edit 으로 fix
   - `stale-compiled-newer-raw` → 사용자에게 검토 요청
   - `dangling-link` → 자체 fix
4. **하나씩 fix 하지 말고 batch 처리** — 같은 룰 위반 여러 개를 한 commit 으로

**Next-step hint 권장**:
```
Next steps (131 issues):
  Worst rule: missing-summary-for-raw (84 entries). Owl-compiler can compile these in batch.
  broken-cross-reference (12) needs Read+Edit on each affected compiled doc.
  Use `owl health --json` for structured input to subagents.
```

### 2.4 `owl init [path] [--hooks]`

**역할**: vault 디렉토리에 owl 표식과 Claude Code 통합을 박는 setup 명령. 사람이 주로 호출하지만 LLM 도 사용자에게 권유 + (사용자 동의시) 실행 가능.

**출력 (text)**:
```
owl — vault initialization
==========================
Vault subdirs already in place ✓
Wrote owl-vault/.owl-vault ✓
Wrote owl-vault/CLAUDE.md ✓
Wrote owl-vault/.claude/settings.json ✓ (5 hooks)
Wrote owl-vault/.claude/commands/ ✓ (7 slash commands)
Set /Users/lucablaq/owl-vault as active vault ✓

Done. Next steps (for humans and LLM agents):
  cd <vault>
  claude
  owl status

  LLM agents: this vault now has /owl-* slash commands and SessionStart
  hooks installed. New Claude Code sessions in this directory will auto-
  load the wiki context. Use owl-{librarian,compiler,health} subagents
  for filing / compilation / health-check work.
```

**LLM 해석 패턴**:
| Signal | Action |
|---|---|
| `owl status` 가 marker / CLAUDE.md / hooks 중 ✗ | 사용자에게 `owl init [--hooks]` 권유 |
| 사용자 명시 동의 후 | Bash 도구로 실행 가능 |
| init 실패 (vault 가 file 임 등) | 에러 보고, 직접 fix 안 함 |

**Next-step hint** (위 출력 끝에 자동 표시): cd / claude / owl status + LLM 가족 안내

### 2.5 `owl setup [--non-interactive]`

**역할**: 환경 진단 + ~/.claude/agents/owl-* 심링크 설치 + ~/.owl/installed-at stamp. install.sh 가 자동 호출.

**출력 (text)**:
```
owl — setup
===========

1) Environment diagnostic
  Python:       3.14.3
    ✓
  owl CLI:      /Users/lucablaq/.local/bin/owl
    ✓
  version:      0.1.0

2) Vault discovery
  Found existing vault(s):
    - /Users/lucablaq/owl-vault

3) User-global subagent symlinks
Symlinking subagents to ~/.claude/agents/ ...
  - owl-librarian: → ...
  - owl-compiler: → ...
  - owl-health: → ...

4) Marking setup complete
  ✓ stamped /Users/lucablaq/.owl/installed-at

Setup complete. Next steps (for humans and LLM agents):
  owl status
  owl search 'filing loop'
  owl health
```

**LLM 해석 패턴**:
| Signal | Action |
|---|---|
| `Environment diagnostic` 에서 `owl CLI: NOT FOUND` | 사용자에게 PATH 추가 가이드 |
| `Vault discovery` 에서 결과 0 | `owl init <path>` 권유 |
| `4) Marking setup complete` 가 안 보임 | 실패. 사용자 보고 |
| 정상 종료 | Task tool 로 owl-* 서브에이전트 즉시 사용 가능 |

### 2.6 `owl use <vault-path>`

**역할**: active vault 를 즉시 전환. `~/.owl/active-vault` 갱신.

**출력 (text)**:
```
Active vault set to: /path/to/new/vault

Next steps (for humans and LLM agents):
  owl status   # confirm the new vault is recognized
  cd <vault>   # start a Claude Code session in the new vault
```

**LLM 해석 패턴**:
| Signal | Action |
|---|---|
| Active vault 전환 후 | 즉시 `owl status` 로 새 vault 검증 권유 |
| 같은 세션 안에서 vault 전환 | 이전 vault 의 컨텍스트 잊을 것 — 새 컨텍스트 로드 |

### 2.7 `owl ingest <file>` (JSON 출력)

**역할**: deterministic primitive. raw 파일을 vault/raw/ 로 옮기고 파일명 계약 적용. *압축/요약/cross-reference 는 안 함* — 그건 LLM 이 follow up.

**출력 (JSON, 항상)**:
```json
{
  "vault": "/Users/lucablaq/owl-vault",
  "source": "/path/to/source.md",
  "target": "raw/2026-04-08-<slug>-raw.md",
  "target_absolute": "/Users/lucablaq/owl-vault/raw/2026-04-08-<slug>-raw.md",
  "action": "moved",
  "expected_summary": "compiled/2026-04-08-<slug>-summary.md",
  "next_step": "Hand off to owl-librarian via /owl-ingest, or directly compile via /owl-compile <name>"
}
```

**LLM follow-up 패턴** (필수 7-단계 절차):
1. `owl ingest <file>` 호출 → JSON 받음
2. `target_absolute` 로 raw 위치 확인
3. `expected_summary` 확인 (이미 존재하면 duplicate 위험)
4. `/owl-ingest <target>` 슬래시 명령 OR Task tool 로 owl-compiler 호출
5. owl-compiler 가 raw 를 read → summary draft
6. summary 에 `관련 항목:` cross-reference 추가
7. existing index 갱신 (필요시)

이 분리가 *CLI = primitive, LLM = composer* 패턴의 정확한 예. JSON 의 `next_step` field 는 *suggestion only* — 더 적절한 행동이 있으면 LLM 이 선택.

### 2.8 `owl compile <raw-path>` (JSON 출력)

**역할**: raw 파일에 대한 *compile metadata* 만 print. 실제 compile 결과 markdown 은 LLM (owl-compiler) 가 생성.

**출력 (JSON, 항상)**:
```json
{
  "vault": "/Users/lucablaq/owl-vault",
  "raw": "raw/2026-04-08-<slug>-raw.md",
  "raw_absolute": "...",
  "date": "2026-04-08",
  "slug": "<slug>",
  "expected_summary": "compiled/2026-04-08-<slug>-summary.md",
  "expected_note": "compiled/2026-04-08-<slug>-note.md",
  "summary_exists": false,
  "note_exists": false,
  "next_step": "Hand off to owl-compiler subagent via /owl-compile..."
}
```

**LLM 해석 패턴**:
| Signal | Action |
|---|---|
| `summary_exists: true` | duplicate. 사용자에게 확인 (덮어쓸지 / skip 할지) |
| `summary_exists: false`, `note_exists: false` | 정상 진행. owl-compiler 호출 |
| `note_exists: true` only | summary 만 만들고 note 는 skip (또는 갱신) |

**핵심 원칙**: compile 자체는 LLM 의 책임. CLI 는 metadata 만 제공. *raw 를 read 하지 않은 채로* compile 하면 안 됨.

### 2.9 `owl file <path> <kind>` (JSON 출력)

**역할**: output (slide/figure/visual) 를 vault/outputs/<kind>/ 로 이동. 단순 파일 이동.

**출력 (JSON, 항상)**:
```json
{
  "vault": "/Users/lucablaq/owl-vault",
  "source": "/path/to/output.png",
  "target": "outputs/figures/output.png",
  "target_absolute": "...",
  "kind": "figures",
  "next_step": "Hand off to owl-librarian via /owl-file to add a link from the relevant compiled/*-report.md (closing the filing loop)."
}
```

**LLM follow-up 패턴**:
1. `owl file <path> <kind>` 호출 → JSON
2. `target` 의 vault-relative path 확보
3. 어떤 report (compiled/*-report.md) 가 이 output 을 referencing 해야 하는지 결정 (sometimes 사용자에게 물음)
4. 그 report 를 Read+Edit 해서 link 추가
5. `owl health` 재실행 → `report-broken-output-link` 가 줄어들었는지 확인

이게 Karpathy 가 강조한 *"outputs return to wiki"* (filing loop) 의 구체 구현.

### 2.8 `owl hook <name>`

**역할**: Claude Code hook 이벤트 dispatcher. *사용자/LLM 이 직접 호출하지 않음*. session_start, user_prompt 등 lifecycle 이벤트에서 자동 호출.

**LLM 해석 패턴**: 없음. 이건 시스템 hook.

## 3. 공통 패턴 — 서브에이전트가 따라야 할 절차

이 패턴은 owl-librarian / owl-compiler / owl-health 모든 서브에이전트가 공유한다.

```
1. CLI 호출 (deterministic primitive)
   ↓
2. 출력 read
   - 텍스트 모드: 사람 친화 출력
   - --json 모드: 기계 파싱
   ↓
3. 분류 (severity / category / count 기준)
   ↓
4. 행동 결정
   - fix now (Read + Edit)
   - 다른 owl-* 서브에이전트에 위임 (Task tool)
   - 사용자에게 escalate
   - 무시 (low severity, 누적 후 batch)
   ↓
5. 행동 실행
   ↓
6. 결과 검증 (필요시 owl status / health 재호출)
   ↓
7. filing loop — 결과를 compiled wiki 에 반영
```

이 7단계가 owl 이 *LLM-driven* 임을 보여주는 핵심. CLI 는 1번과 2번에만 등장한다.

## 4. 알려진 wiring 이슈 (TODO)

### 4.1 REMAINDER 버그

`src/owl/cli.py` 의 `sp_search` 와 `sp_health` 가 `nargs=argparse.REMAINDER` 를 사용해서 sub-command 의 자체 argparse 로 위임. 그런데 argparse REMAINDER 는 *leading `--option`* 을 잘 못 잡음:

- `owl health --json` → 실패 (top parser 가 `--json` 해석 시도)
- `owl search --json query` → 실패
- `owl health <positional>` → 동작 (positional 부터 capture 됨)

**Fix 방향** (Phase B4):
- cli.py 의 sp_health, sp_search 를 명시적 flag (`--json`, `--vault`) 등록 + 자체 dispatch
- 또는 `parse_known_args` 사용으로 unknown 을 sub-command 에 pass-through

### 4.2 출력에 next-step hint 없음

현재 `owl status / health / search` 출력은 *원시 데이터만*. LLM 이 다음에 무엇을 해야 할지 hint 가 없다.

**Fix 방향** (Phase B4):
- 텍스트 출력 끝에 1-3줄 "Next steps:" 추가
- `--json` 모드에서는 `next_steps: [...]` field 추가 (선택)

## 5. 향후 추가 (Out of Scope)

- `--llm` 또는 `--for-llm` 플래그 — LLM 친화 출력 모드 (현재는 hint 가 항상 표시되도록 설계)
- 모든 명령에 `--json` 일관 추가 (init/setup 등 setup 류는 제외)
- `owl explain <topic>` — LLM 이 vault 를 읽고 자연어로 답하는 wrapper 명령
- `owl compose <kind>` — 새 문서 생성 wrapper

## 6. 한 줄 요약

> **owl CLI 의 출력은 LLM 이 다음에 무엇을 할지 결정할 수 있도록 설계되어야 한다.**
> 데이터만 주는 게 아니라 hint 도 줘야 하고, hint 는 사람도 도움받는 부수효과여야 하며, 진짜 결정과 행동은 LLM 이 한다.
