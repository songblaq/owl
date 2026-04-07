# owl

A personal LLM-maintained wiki.

You bring the sources. The LLM does everything else — files them,
cross-references them, keeps the wiki alive.
Implements Andrej Karpathy's LLM Wiki pattern (2026), spiritually
descended from Vannevar Bush's Memex (1945).

## Lineage

- **2026 — Karpathy's LLM Wiki**: the originating gist that defines this project's pattern. RAG rediscovers knowledge on every query; an LLM-maintained wiki *accumulates* it. Captured at `<vault>/raw/2026-04-07-karpathy-llm-wiki-gist-raw.md`.
- **1945 — Bush's Memex**: a personal, curated knowledge store with associative trails between documents. Bush's vision was closer to this than to what the web became. The part he couldn't solve was "who maintains it?" — LLMs handle that.

owl is the Karpathy pattern made executable: a CLI, a set of Claude Code hooks, slash commands, and `owl-*` subagents that turn raw markdown sources into a self-maintaining wiki.

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/yourname/owl/main/install.sh | sh
```

설치 후 `owl setup` 이 자동 실행되며 vault 발견, 서브에이전트 심링크, hook 활성화를 단계별로 안내한다. 그 다음:

```bash
owl status              # 활성 vault, version, health 요약
owl search "wiki"       # 토큰 스코어 검색 (RAG 없음)
owl health              # 8가지 무결성 규칙
```

Claude Code 안에서는:

```
/owl-search filing loop
/owl-health
/owl-ingest <path>
/owl-compile <raw-path>
```

## 4계층 아키텍처

```
LAYER 1 — SPEC      ~/_/projects/owl          (정책 + Python 패키지 owl)
LAYER 2 — RUNTIME   ~/.local/bin/owl + ~/.claude/agents/owl-*
LAYER 3 — VAULT GLUE  vault/.owl-vault + vault/CLAUDE.md + vault/.claude/
LAYER 4 — DATA      vault/raw/, compiled/, views/, outputs/  (코드 없음)
```

vault 는 데이터만, 운영 로직은 프로젝트 리포에 있어 `git pull` 1회로 모든 vault 업데이트.

## 현재 운영 모델
- **원천 데이터 → raw/**
  - 논문, 기사, 저장소, 이미지, 대화 로그 등을 파일 단위로 보존한다.
- **LLM compile → compiled/**
  - summary, note, concept, index, report 같은 `.md` 문서를 점진적으로 만든다.
- **Obsidian surface**
  - raw 데이터, compiled wiki, 시각화 결과를 같은 작업 표면에서 본다.
- **Q&A / filing loop**
  - 답변 문서, Marp 슬라이드, matplotlib 이미지도 다시 wiki에 파일링한다 (Karpathy 가 강조).
- **health check / tools**
  - 불일치, 누락, 연결 후보를 점검하고, 필요하면 작은 CLI 검색 도구를 붙인다.
  - 검색: `owl search "filing loop"` (또는 레거시 `python3 src/wiki_search.py "filing loop" --scope all`)
  - 헬스체크: `owl health` (또는 레거시 `python3 src/brain_health_check.py`)
  - 검사 범위: raw-summary 누락, 관련 항목 누락, report outputs 링크, concept/index 후보, orphan concept, stale index, weak backlink

## 핵심 구조
- **LKS**: 전체 운영 체계
- **KIB**: raw/compiled를 보관하고 다시 읽는 지식 기반
- **MDV**: 필요할 때만 쓰는 선택적 메타 뷰 계층

MDV는 초기 필수 축이 아니다. 기본은 `raw/ -> compiled/ -> QA/output -> filing` 루프다.

## 기본 경로
- 프로젝트 리포: `~/_/projects/owl` (Python 패키지 + 정책 + claude_assets)
- vault (앱 데이터): `~/owl-vault` (visible top-level. 레거시 `~/.agents/brain` 도 폴백 인식)
- user config: `~/.owl/` (active-vault 포인터, 설치 timestamp)

## 스키마/계약 문서
- 루트 `AGENTS.md`: 단일 운영 스키마와 파일 계약
- `docs/`: 세부 정책과 명세
- 운영 원칙 인덱스: `docs/operating-principles-index-v0.md`
- 상위 원칙: `docs/agent-cli-doc-first-operating-principle-v0.md`
- 개별 원칙: `docs/doc-first-operating-principle-v0.md`, `docs/agent-cli-operating-principle-summary-v0.md`
- 운영 레이어 명세: `docs/operational-layer-spec-v0.md` (owl CLI + hook + 슬래시 명령 + owl-* 서브에이전트)

## 앱 데이터 구조
- `raw/`: 원본 자료 (절대 편집 금지)
- `compiled/`: LLM이 편찬한 마크다운/위키/리포트
- `views/`: 메타 뷰 산출물
- `research/`: 조사 작업 및 중간 산출물
- `outputs/`: 슬라이드, 이미지, 시각화 같은 파생 산출물
- `inbox/`: 수집 대기 자료
- `logs/`: 작업 로그
- `tmp/`: 임시 파일
- `config/`: 설정

## 개념 요약

owl 은 원본 자료를 파일 단위로 저장하고, LLM 이 이를 지식으로 컴파일하며, 그 결과를 다시 질의응답과 산출물 생성, 헬스체크, 도구 연결을 통해 성장시키는 **파일 기반 self-maintaining wiki**다. RAG 가 아니라 잘 유지된 wiki 가 답이다 (Karpathy 2026 의 핵심 주장).

Karpathy 의 원문은 vault 의 origin source 로 박제되어 있다:
```
~/owl-vault/raw/2026-04-07-karpathy-llm-wiki-gist-raw.md
```
