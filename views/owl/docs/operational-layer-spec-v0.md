# owl Operational Layer Spec v0

작성일: 2026-04-07
상태: v0 (구현 1차 완료, owl 리네임 반영)

> **owl** — Karpathy LLM Wiki (2026) + Bush Memex (1945) lineage 의 실행 구현체. 개인 LLM-maintained wiki.

## 0. Lineage

- **2026, Andrej Karpathy** — "LLM Wiki" gist 가 owl 의 모든 동작 컨셉의 1차 원천. `<vault>/raw/2026-04-07-karpathy-llm-wiki-gist-raw.md` 에 origin source 로 박제됨
- **1945, Vannevar Bush** — Memex. Karpathy 가 직접 인용한 영적 조상

## 1. 목적

owl 의 정책(48+ docs)을 Claude Code 가 자동으로 따르게 하는 **운영 레이어**의 단일 명세. policy-as-docs 에서 **policy-as-code** 로의 전환을 정의한다.

이 문서는 `agent-cli-doc-first-operating-principle-v0.md` 의 구현 매뉴얼이다 — 정책 → 명세 → CLI → Claude 동작의 전체 루프.

## 2. 4계층 분리

```
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 1 — SPEC (project repo, source of truth)                   │
│ ~/_/projects/oh-my-brain/views/owl/                                        │
│   ├── docs/             ← 48+개 정책 문서                         │
│   ├── src/owl/          ← Python 패키지 (CLI + hooks + assets)   │
│   ├── pyproject.toml    ← `owl` console_script                   │
│   └── install.sh        ← curl | sh 진입점                        │
└──────────────────────────────────────────────────────────────────┘
                              ↓ pipx install --editable
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 2 — RUNTIME (user-global, installed by curl)               │
│ ~/.local/bin/owl                         ← CLI (pipx 진입점)      │
│ ~/.claude/agents/owl-librarian.md        ← 서브에이전트 (symlink) │
│ ~/.claude/agents/owl-compiler.md         ← (symlink)              │
│ ~/.claude/agents/owl-health.md           ← (symlink)              │
│ ~/.agents/skills/owl-*  ← OpenClaw L0 canonical (symlink, 보존)   │
│ ~/.owl/                                  ← user config dir        │
│   ├── active-vault                       ← 현재 활성 vault 경로   │
│   └── installed-at                       ← setup 완료 timestamp   │
└──────────────────────────────────────────────────────────────────┘
                              ↓ owl init <vault>
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 3 — VAULT GLUE (per vault, 코드 없음)                       │
│ ~/owl-vault/                                                 │
│   ├── .owl-vault               ← marker (vault 식별)             │
│   ├── CLAUDE.md                ← vault governance                 │
│   └── .claude/                                                    │
│       ├── settings.json        ← 5개 hook → owl hook <name>       │
│       └── commands/            ← 7개 슬래시 명령 (thin wrapper)    │
└──────────────────────────────────────────────────────────────────┘
                              ↓ user 작업
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 4 — DATA (vault, 절대 코드 없음)                            │
│ ~/owl-vault/raw/, compiled/, views/, outputs/, ...           │
└──────────────────────────────────────────────────────────────────┘
```

## 3. 핵심 invariant

1. **vault = 데이터만**. `.claude/` 안에는 hook 호출 + 슬래시 명령 thin wrapper 만 있고 Python 등 실행 코드 일체 없음.
2. **모든 실제 로직은 LAYER 1 의 `owl/` 패키지**. `git pull` 1회로 모든 vault 가 새 동작을 받음.
3. **정책 문서 (48+개)는 vendoring 하지 않음**. 프로젝트 리포가 곧 spec; 서브에이전트 system prompt 가 절대 경로로 직접 참조.
4. **CLI 이름은 `owl`** (Karpathy LLM Wiki → wl → owl + 지혜 메타포. 이전 `brain` 에서 리네임).
5. **vault 기본은 `~/owl-vault`**. 레거시 `~/.agents/brain` 은 폴백으로 자동 인식 (rename 비파괴 보장).

## 4. CLI 표면

```
owl status                       # 활성 vault, version, health 요약
owl init <path> [--hooks]        # vault 초기화 (interactive TUI)
owl setup                        # 환경 진단 + 심링크 + init 권유
owl use <vault>                  # 활성 vault 전환
owl search "<query>" [--json]    # 토큰 스코어 검색 (RAG 없음)
owl health [--json]              # 8가지 무결성 규칙
owl ingest <path>                # 후보 파일 → raw/ (deterministic)
owl compile <raw-path>           # compile 메타 (서브에이전트 위임용)
owl file <path> <kind>           # outputs/{slides|figures|visuals}/
owl hook <name>                  # Claude Code hook 디스패처
```

## 5. 5개 라이프사이클 hook

| Hook | 역할 |
|------|------|
| `session_start` | vault 상태 + 최근 log + inbox 카운트 + health 요약 자동 주입 |
| `user_prompt` | 발화 분류 → 적절한 슬래시 명령 또는 서브에이전트 권유 |
| `post_tool_use` | raw/compiled 쓰기 후 무결성 경고 (cooldown throttling) |
| `pre_compact` | 컨텍스트 압축 전 세션 상태 → logs/ 스냅샷 |
| `stop` | 세션 중 생성된 raw 중 summary 미생성 알림 |

모두 `owl hook <name>` 이 디스패처. vault `.claude/settings.json` 은 `command: "owl hook <name>"` 만 담는다.

## 6. 7개 슬래시 명령

각 명령은 **CLI 결정성 + LLM 해석 한 턴** 패턴:
```markdown
!`owl <subcommand> --json`
이 결과를 해석해서 ...
```

| 명령 | CLI | 위임 대상 |
|------|-----|-----------|
| `/owl-search <query>` | `owl search --json` | (직접 정리) |
| `/owl-health` | `owl health --json` | owl-health |
| `/owl-ingest <path>` | `owl ingest` | owl-librarian |
| `/owl-compile <raw>` | `owl compile` | owl-compiler |
| `/owl-file <path> <kind>` | `owl file` | owl-librarian |
| `/owl-promote [<term>]` | `owl health --json` | owl-librarian |
| `/owl-query <question>` | `owl search --json` | (workflow-v0 §4 패턴) |

## 7. 3개 owl-* 서브에이전트

| 이름 | 역할 | 모델 | 참조 정책 |
|------|------|------|-----------|
| `owl-librarian` | filing, naming, cross-link 유지, concept/index 승격 | sonnet | AGENTS.md §5–7, wiki-linking-rules-v0, wiki-maintenance-spec-v0 |
| `owl-compiler` | raw → summary/note 컴파일 | sonnet | karpathy-ingest-rules-v0, compiled-format-spec-v0 |
| `owl-health` | health check 결과 해석 + fix 우선순위 계획 | sonnet | health-check-spec-v0 |

OMC 의 `executor`/`planner`/`writer`/`document-specialist` 와 이름 충돌 없음 (`owl-` prefix). OpenClaw L0 에도 동일 심링크 보존.

## 8. vault 경로 발견 우선순위

```
1. --vault (또는 deprecated --brain) CLI 인자
2. $OWL_VAULT 환경변수
3. ~/.owl/active-vault (owl use 로 설정)
4. cwd 에서 위로 .owl-vault marker 탐색
5. ~/owl-vault (기본값) — 없으면 ~/.agents/brain 폴백 (legacy)
```

`owl.vault.discover_vault()` 가 단일 진실의 원천. 모든 CLI 명령과 hook 이 동일 함수 사용.

## 9. 설치 흐름

```bash
curl -fsSL https://raw.githubusercontent.com/<owner>/owl/main/install.sh | sh
```

`install.sh` 는:
1. git clone (또는 pull) → `~/_/projects/oh-my-brain`
2. `cd views/owl && pipx install --editable .` → `~/.local/bin/owl`
3. `owl setup` 실행 (interactive TUI)
   - 환경 진단
   - vault 발견 → `owl init` 실행 권유
   - `~/.claude/agents/owl-*` 심링크 생성
   - `~/.agents/skills/owl-*` 심링크 생성 (OpenClaw L0)
   - `~/.owl/installed-at` 스탬프

## 10. doc-first 원칙 일치

`agent-cli-doc-first-operating-principle-v0.md` 의 루프:

```
docs → spec → CLI → execution → docs (환류)
```

이 운영 레이어는:
- **docs**: 48+개 정책 + 이 문서 자체
- **spec**: 이 문서가 LAYER 분리, hook, CLI, 서브에이전트의 단일 spec
- **CLI**: `owl` 명령 (deterministic primitive)
- **execution**: hook + 슬래시 명령 + owl-* 서브에이전트
- **환류**: hook 이 vault 변화를 감지해 다음 세션에 컨텍스트로 주입

## 11. 호환성 보장

- 기존 `python3 src/wiki_search.py "<query>"` 명령은 변경 전과 동일 동작 (8줄 wrapper 가 `owl.search.cli` 호출)
- 기존 `python3 src/brain_health_check.py` 명령도 동일
- README.md, tool-adapter-spec-v0.md, health-check-spec-v0.md 의 문서화된 호출 방식 모두 회귀 0
- CLI flag `--brain` 도 alias 로 유지 (deprecated, `--vault` 권장)

## 12. OpenClaw 보존

`plans/openclaw-skill-structure-principles-2026-04-04.md` 의 L0/L1/L2 모델 유지:
- L0 canonical: `~/.agents/skills/owl-*` (이 운영 레이어가 심링크 생성)
- L1 runtime: `~/.openclaw/workspace/skills/owl-*` (OpenClaw 가 자체적으로 L0 → L1 동기화)
- L2 명세: 이 문서 + claude_assets 의 .md 들

OpenClaw 는 그대로 owl 정책 consumer 로 동작.

## 13. 향후 확장 (out of scope)

- `owl pack` — vault 를 self-contained tarball 로 vendoring (Obsidian Mind 식 portable 모드)
- 자동 ingest watcher (inbox 폴더 감시)
- MDV view 자동 생성 도구
- Windows 지원 (현재 macOS/Linux)
- Brain 군 multi-module 통합 (owl + brain-memory + ...)

## 관련 항목

- `agent-cli-doc-first-operating-principle-v0.md` (상위 원칙)
- `doc-first-operating-principle-v0.md`
- `agent-cli-operating-principle-summary-v0.md`
- `health-check-spec-v0.md`
- `wiki-maintenance-spec-v0.md`
- `karpathy-ingest-rules-v0.md`
- `compiled-format-spec-v0.md`
- `plans/openclaw-skill-structure-principles-2026-04-04.md`
