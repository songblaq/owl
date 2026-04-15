# oh-my-brain (omb) — Gemini CLI

Personal LLM-maintained knowledge system. Single active vault: **akasha**.

## Tool Mapping

| Claude Code | Gemini CLI equivalent |
|-------------|----------------------|
| `Bash` | `run_shell_command` |
| `Read` | `read_file` |
| `Write` | `write_file` |
| `Glob` | `list_directory` |
| `Grep` | `run_shell_command` (rg) |

## Skills

Skills activate via `activate_skill` in Gemini CLI:

| Skill | Trigger |
|-------|---------|
| `omb-search` | "omb search", "브레인 검색" |
| `omb-ingest` | "omb ingest", "브레인에 추가" |
| `omb-health` | "omb health", "커버리지 확인" |
| `omb-compile` | "omb compile", "컴파일" |
| `omb-setup` | "omb 설치", "setup omb" |
| `omb-update` | "omb update", "브레인 업데이트" |

## Usage

```bash
omb status               # vault overview
omb search "<query>"     # 3-layer search
omb ingest <file>        # add knowledge
omb health               # coverage check
```

## 기본 reflex

사용자가 축적된 지식과 관련된 질문을 하면 **답변 전에** `run_shell_command: omb search "<topic>"` 을 먼저 시도한다. 결과가 있으면 해당 파일을 `read_file`로 읽어 근거로 답변. 없으면 명시하고 `omb ingest` 제안.

## Data

```
~/omb/source/           raw inputs (immutable)
~/omb/vault/akasha/     active vault
  entries/              atomic claims
  compiled/             LLM narratives
  INDEX.md              master index
```
