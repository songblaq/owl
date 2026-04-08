# External Knowledge Integration v0

작성일: 2026-04-08
상태: v0

## 0. 목적

owl vault 를 **다른 프로젝트의 Claude Code 세션에서도 external knowledge source 로 사용** 할 수 있도록 글로벌 wiring. vault 외부 (e.g., `~/_/projects/foo`) 에서 작업 중에도 `/owl-search` 로 vault 쿼리 / `owl-*` 서브에이전트 호출 가능.

## 1. 배경 — 왜 필요한가

owl 은 개인 LLM-maintained wiki. 지금까지 축적된 200+ compiled docs 가 OpenClaw, ARIA, DE OS, Content Factory, Smart Gym, Runtimes 등 사용자의 여러 프로젝트 지식을 담고 있음.

기존 구조:
- vault 내부 (`~/owl-vault`) 에서 Claude Code 시작 → `CLAUDE.md` 자동 로드 → `/owl-*` 슬래시 명령 + 서브에이전트 모두 동작
- vault 외부 (다른 프로젝트) 에서 Claude Code 시작 → owl CLI 는 PATH 에 있지만 `/owl-*` 슬래시 명령 없음, 컨텍스트 힌트 없음

목표: **다른 프로젝트에서도 owl 의 지식을 쿼리** 가능하게.

## 2. 4 계층 통합

| 계층 | 접근 방식 | 설치 위치 | 글로벌 가용성 |
|---|---|---|---|
| **CLI** | `owl search`, `owl status`, `owl health` 등 | `~/.local/bin/owl` (pipx editable) | ✓ 항상 (PATH) |
| **서브에이전트** | Task tool: `owl-librarian`, `owl-compiler`, `owl-health` | `~/.claude/agents/owl-*.md` (symlink) | ✓ 항상 (Claude Code global) |
| **슬래시 명령** | `/owl-search`, `/owl-query`, `/owl-health` 등 7개 | `~/.claude/commands/owl-*.md` (symlink) | ✓ `owl setup` 이후 (v0.1.x+) |
| **컨텍스트 힌트** | `~/.claude/CLAUDE.md` 의 owl 섹션 | 사용자가 추가 (or OMC-adjacent section) | ✓ 수동 편집 |

## 3. 각 계층의 구현

### 3.1 CLI (이미 작동)

owl CLI 는 vault 자동 발견 chain 을 가짐:
1. `--vault` flag
2. `$OWL_VAULT` 환경변수
3. `~/.owl/active-vault` config
4. cwd 에서 위로 `.owl-vault` marker 탐색
5. `~/owl-vault` (기본)
6. `~/.agents/brain` (legacy fallback)

따라서 *어느 디렉토리에서 호출해도* owl CLI 는 active vault 를 찾음. `owl search "topic"` 은 `/tmp` 에서도 동작.

### 3.2 서브에이전트 (이미 작동)

`owl setup` 이 `~/.claude/agents/owl-{librarian,compiler,health}.md` 심링크를 `src/owl/claude_assets/agents/` 로 연결. Claude Code 글로벌 agent directory 라서 모든 세션에서 Task tool 호출 가능.

이 심링크는 owl 프로젝트 repo 가 source of truth — `git pull` 1회로 모든 세션의 서브에이전트 로직이 갱신됨.

### 3.3 슬래시 명령 (이 계획에서 추가)

**Before**: `owl init` 이 vault 의 `<vault>/.claude/commands/owl-*.md` 에만 설치. 다른 프로젝트에서 `/owl-search` 호출 불가.

**After**: `owl setup` 이 `~/.claude/commands/owl-*.md` 에도 추가로 심링크 설치. Claude Code 의 global command directory 라서 모든 세션에서 사용 가능.

**구현**: `src/owl/setupcmd.py` 의 `install_global_slash_commands()` 함수.

**소스**: 프로젝트 repo 의 `src/owl/claude_assets/commands/owl-*.md` (source of truth).

### 3.4 컨텍스트 힌트 (~/.claude/CLAUDE.md)

글로벌 instructions 파일에 "owl external knowledge" 섹션 추가. Claude 가 세션 시작 시 자동 로드하는 instructions 에 owl 의 존재 + 사용법 + 기본 reflex 를 명시.

**패턴**: ARIA 통합 섹션 + ATLAS 시스템 지식 섹션과 병렬. 사용자의 글로벌 owl 섹션도 같은 위치 (OMC:END 뒤) 에 박음 → OMC 갱신에 영향 안 받음.

**핵심 내용**:
- owl 의 정체 (vault 경로, 프로젝트 repo, 공개 URL)
- 언제 참조하는가 (축적된 지식 / 과거 결정 / 도메인 질문)
- 사용 방법 (CLI / slash / subagent)
- 현재 vault 규모
- 제약 (raw 불변, vault 공개 금지 등)
- **기본 reflex**: 축적 지식 질문 시 `owl search` 먼저 시도

## 4. 설계 원칙

### 4.1 CLI 는 primitive, wiki 는 LLM 이 유지

external 로 내보내도 이 원칙은 불변. `/owl-search` 는 `owl search` CLI 호출의 wrapper 이고, 결과 해석과 행동은 LLM 이 한다. vault 외부에서도 동일.

### 4.2 Write 작업은 vault 절대 경로

`/owl-query` 같은 write 성 슬래시 명령이 vault 외부에서 호출될 때 **cwd 에 파일 생성 금지**. 항상 `owl status` 로 active vault 경로 확인 → `<vault>/research/`, `<vault>/compiled/` 로 절대 경로 사용.

owl-query.md 의 body 에 명시됨 (2026-04-08 갱신).

### 4.3 Source of truth 는 프로젝트 repo

모든 슬래시 명령, 서브에이전트 프롬프트의 source of truth 는 `~/_/projects/owl/src/owl/claude_assets/`. global 심링크는 여기를 가리킴. `git pull` 한 번으로 모든 세션이 갱신됨.

예외: `<vault>/.claude/commands/` 에 `owl init` 이 복사해두는 것은 vault 가 자체 Claude Code 컨텍스트를 가지기 위함. global 심링크 (`~/.claude/commands/`) 와 중복 존재.

### 4.4 Private by default

owl vault 는 개인 데이터 저장소. *다른 사람의 세션* 에서는 접근되지 않음 — 이 통합은 *사용자 본인* 이 어느 프로젝트에서 작업하든 자기 지식에 접근 가능하게 하는 것.

Privacy 주의:
- vault 내용은 `~/owl-vault` (개인 홈) 에만 존재
- 프로젝트 repo 에 `/raw/`, `/compiled/` 등 커밋 금지 (`.gitignore` 방어층)
- 개인 대화방/채널 소스는 vault-local only (`source-ingest-policy-v0.md §6`)

## 5. 사용자 체감 흐름 (예시)

### 시나리오 1: 다른 프로젝트에서 과거 결정 참조

```
[~/_/projects/some-other-project] claude

User: "전에 smart gym WiFi CSI 실험 protocol 에 대해 뭐라고 정리했었지?"

Claude: [기본 reflex 발동]
!owl search "smart gym WiFi CSI" --json --limit 5

[결과 분석 후]
vault 에 2026-04-04 에 작성한 compiled/2026-04-04-smart-gym-
experiment-protocol-summary.md 가 있습니다. 핵심 내용:
- EXP-002 WiFi CSI 비접촉 감지 프로토콜
- M5StickC PLUS2 + 기존 라우터로 킬 테스트
- 3 정량 기준 (packet loss <5%, 2σ amplitude, FFT peak)
- Phase 2/3/4 로드맵 (dedicated AP → real-time → IMU fusion)
...
```

### 시나리오 2: 다른 프로젝트에서 질문을 wiki 에 환류

```
[~/_/projects/foo] claude

User: "/owl-query 우리 Content Factory 의 review 4원칙이 뭐였지?"

Claude:
1. owl search "Content Factory review 4원칙" 실행
2. owl status 로 vault 경로 확인 (e.g., /Users/.../owl-vault)
3. 검색 결과 읽고 답변
4. <vault>/research/2026-04-08-review-4원칙-query/ 생성
5. <vault>/compiled/2026-04-08-review-4원칙-report.md 작성 (filing loop)
```

## 6. 설치 흐름 (사용자 관점)

첫 설치:
```bash
curl -fsSL https://raw.githubusercontent.com/songblaq/owl/main/install.sh | sh
# → owl CLI + 서브에이전트 심링크 + 슬래시 명령 심링크 + vault init (옵션)
```

이후 `owl setup` 재실행 (업데이트 반영):
```bash
owl setup --non-interactive
# → 모든 심링크 refresh, 새 슬래시 명령 자동 install
```

`~/.claude/CLAUDE.md` 의 owl 섹션은 **수동 추가** (이 문서의 §3.4 참고). 자동 설치 안 하는 이유:
- CLAUDE.md 는 사용자의 개인 instructions 라 자동 편집 위험
- OMC 같은 다른 도구가 CLAUDE.md 관리 중일 수 있음
- 사용자가 원하는 톤/범위를 직접 정하는 게 나음

## 7. Verification

```bash
# 다른 디렉토리에서
cd /tmp
owl search "karpathy" --json --limit 3
# → vault 발견 + 검색 결과

ls ~/.claude/commands/owl-*
# → 7 slash commands (symlinks to project repo)

ls ~/.claude/agents/owl-*
# → 3 subagents (symlinks to project repo)

grep -c "owl — Personal LLM Wiki" ~/.claude/CLAUDE.md
# → 1 (section exists)
```

## 8. 향후 확장 가능성

### 8.1 MCP Server

Model Context Protocol 서버로 owl 을 노출하면 claude.ai, Claude Code 가 MCP 를 통해 vault 쿼리 가능. 현재 접근은 CLI subprocess 기반이라 충분하지만, MCP 로 구조화하면:
- 스키마 명시 (query, list, get_doc 등)
- Claude 가 tool call 형태로 직접 owl 쿼리
- 여러 vault 또는 원격 vault 지원 가능

### 8.2 Cross-vault federation

미래에 사용자가 여러 vault 를 가진다면 (예: `~/owl-vault-personal`, `~/owl-vault-work`), `owl setup --vault <path>` 로 vault 별 global wiring 지원.

### 8.3 Read-only export

vault 의 compiled 부분을 정적 사이트로 export 해서 `/owl-export` 같은 명령으로 외부 툴에서 읽기 전용 참조.

## 9. 관련 문서

- `docs/operational-layer-spec-v0.md` — 4계층 아키텍처 (spec/runtime/vault glue/data)
- `docs/cli-llm-handoff-v0.md` — CLI 출력 ↔ LLM 해석 계약
- `docs/source-ingest-policy-v0.md §6` — 개인 대화방/채널 privacy 규칙
- `src/owl/setupcmd.py` → `install_global_slash_commands()` — 글로벌 슬래시 명령 설치
- `src/owl/claude_assets/commands/owl-query.md` — vault-aware query 슬래시 명령 (2026-04-08 갱신)
