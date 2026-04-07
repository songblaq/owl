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

### 2.4 `owl init / setup / use`

이 셋은 *사람의 환경 setup* 명령이라 LLM 이 직접 호출하는 경우는 드물다. 다만:
- LLM 이 `owl status` 결과 보고 vault state 가 ✗ 면 → 사용자에게 `owl init` 권유 (LLM 이 직접 실행하지 않음)
- 새 vault 로 전환은 사용자 명시적 의도가 있을 때만

### 2.5 `owl ingest <file>`

**역할**: deterministic primitive. raw 파일을 vault/raw/ 로 옮기고 파일명 계약 적용. *압축/요약/cross-reference 는 안 함* — 그건 LLM 이 follow up.

**LLM follow-up 패턴**:
1. `owl ingest <file>` 호출
2. 결과 path 받음 (vault/raw/2026-04-08-<slug>-raw.md)
3. `/owl-ingest <path>` 슬래시 명령 호출 OR owl-compiler 서브에이전트에 위임
4. compiled summary 생성 → cross-reference 추가 → existing index 갱신

이 분리가 *CLI = primitive, LLM = composer* 패턴의 정확한 예.

### 2.6 `owl compile <raw-path>`

**역할**: raw 파일에 대한 *compile metadata* 만 print. 실제 compile 결과 markdown 은 LLM (owl-compiler) 가 생성.

**출력 예**:
```
raw_file: <path>
expected_compiled: <expected path>
title: <inferred>
date: <YYYY-MM-DD>
slug: <derived>
suggested_kinds: [summary, note]
related_existing: [list of existing compiled files about same topic]
```

**LLM 해석 패턴**:
- `related_existing` 가 비어있지 않으면 → "기존 문서 갱신 vs 새 문서 생성 결정"
- `suggested_kinds` 의 순서 = priority. 보통 summary 먼저
- compile 자체는 LLM 의 책임. CLI 는 metadata 만 제공

### 2.7 `owl file <path> <kind>`

**역할**: output (slide/figure/visual) 를 vault/outputs/<kind>/ 로 이동. 단순 파일 이동.

**LLM follow-up**:
- 이동 후 → compiled wiki 에 reference 추가 (filing loop)
- 이게 Karpathy 가 강조한 "outputs return to wiki" 의 구체 구현

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
