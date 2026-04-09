# owl AGENTS.md

작성일: 2026-04-03 (owl 리네임: 2026-04-07)
상태: active

## 0. 정체성과 lineage

**owl — 개인 LLM-maintained wiki.**

사용자가 sources 를 가져온다. LLM 이 나머지 (filing, cross-reference, 유지보수) 를 모두 한다.

owl 은 Andrej Karpathy 의 "**LLM Wiki**" 패턴(2026) 의 구현체다. Vannevar Bush 의 Memex(1945) 영적 후손. RAG 가 아니라 잘 유지된 wiki 가 답이라는 철학을 따른다.

- **Origin source**: `~/owl-vault/raw/2026-04-07-karpathy-llm-wiki-gist-raw.md` (Karpathy 의 원문 gist, 절대 편집 금지)
- **CLI 이름**: `owl` (이전 `brain` 에서 리네임. 2026-04-07. 이유: Karpathy LLM Wiki 정체성 + Apache Bench 충돌 회피)
- **프로젝트 디렉토리**: `~/_/projects/owl`

## 1. 목적

이 문서는 owl 의 단일 운영 스키마다.
복잡한 데이터베이스나 서비스 계약 대신, 파일 트리와 문서 규칙만으로 raw → compiled → Q&A → filing 루프를 유지하게 한다.

## 2. 기본 경로

- 프로젝트: `~/_/projects/owl`
- 앱 데이터 (vault): `~/owl-vault` (레거시 `~/.agents/brain` 도 폴백 인식)
- user config: `~/.owl/`
- 기본 surface: Obsidian

## 3. 핵심 루프

```text
raw source -> LLM compile -> compiled wiki -> QA/output -> filing -> compiled wiki
```

필요 시 다음이 덧붙는다.
- health check / lint
- wiki CLI search
- MDV views

## 4. 디렉토리 계약

### 프로젝트
- `README.md`: 빠른 개요
- `AGENTS.md`: 단일 스키마/운영 계약
- `docs/`: 세부 정책과 명세
- `src/owl/`: Python 패키지 (CLI + hooks + claude_assets)
- `src/wiki_search.py`, `src/brain_health_check.py`: 레거시 호환 wrapper
- `pyproject.toml`: 패키지 정의 + `owl` console_script
- `install.sh`: curl | sh 진입점
- `examples/`: 예시 데이터
- `plans/`: 계획 문서

### 앱 데이터 (vault)
- `inbox/`: 아직 정리 전인 수집 대기 자료
- `raw/`: 원본 source 보관 (절대 편집 금지)
- `compiled/`: summary, note, concept, index, report 등 wiki 문서
- `views/`: 선택적 메타 뷰
- `research/`: 조사 중간 산출물
- `outputs/`: slides, figures, visuals 같은 파생 산출물
- `logs/`: 작업 로그
- `tmp/`: 임시 파일
- `config/`: 설정
- `.owl-vault`: vault 식별 marker (`owl init` 가 생성, 1줄 metadata)
- `CLAUDE.md`: vault governance (`owl init` 가 생성, ~80줄)
- `.claude/settings.json`: 5개 hook (`owl init --hooks` 가 생성, 모두 `owl hook <name>` 호출)
- `.claude/commands/owl-*.md`: 7개 슬래시 명령 (`owl init --hooks` 가 복사)
- 위 4개 항목은 코드 없음 — `~/_/projects/owl/src/owl/` 의 로직을 호출만 함

## 5. 파일 유형 계약

### Raw
- 목적: 원본 source 보관
- 권장 파일명: `YYYY-MM-DD-<slug>-raw.md`
- 최소 메타:
  - 상태: raw
  - 유형: article | thread | repo | paper | image-set | note | transcript
  - 출처: source 설명 또는 URL
  - 날짜: 보관 날짜

### Compiled Summary
- 목적: source의 정규 요약
- 권장 파일명: `YYYY-MM-DD-<slug>-summary.md`
- 최소 메타:
  - 상태: compiled
  - 유형: summary
  - 출처: 대응 raw 경로
  - 작성일: 날짜
  - 관련 항목: 개념 목록

### Compiled Note
- 목적: 해석, 관찰, 갭, 후속 질문 정리
- 권장 파일명: `YYYY-MM-DD-<slug>-note.md`
- 최소 메타:
  - 상태: compiled
  - 유형: note
  - 출처: 대응 raw 경로
  - 작성일: 날짜

### Concept / Index / Report
- 목적:
  - concept: 여러 source를 묶는 개념 문서
  - index: 탐색용 문서 목록
  - report: Q&A 또는 조사 결과
- 모두 `compiled/`에 둔다.

### Outputs
- `outputs/slides/`: Marp 슬라이드
- `outputs/figures/`: matplotlib 이미지
- `outputs/visuals/`: 기타 시각화

## 6. 링크 계약

- 각 summary는 raw source를 가리킨다.
- 각 compiled 문서는 관련 항목 또는 관련 자료를 가진다.
- 여러 source가 같은 주제를 가리키면 concept 문서를 만든다.
- 주제군이 커지면 index 문서를 만든다.
- 역방향 링크는 자동 시스템이 없어도 문서 수준에서 유지한다.

## 7. ingest 계약

- 초기 ingest는 완전 자율화하지 않는다.
- source를 하나씩 직접 추가하며 naming/template 패턴을 고정한다.
- 웹 기사 수집은 가능하면 Obsidian Web Clipper 기반 markdown을 우선한다.
- 관련 이미지는 로컬에 저장해 LLM이 참조할 수 있게 한다.
- 패턴이 안정되면 `file this new doc to our wiki: (path)` 같은 한 줄 filing 동작으로 승격한다.
- CLI: `owl ingest <path>` (deterministic 이동) → `/owl-ingest` (LLM 정리)

## 8. 운영 원칙

- 원본은 지우지 않는다.
- wiki는 LLM이 관리하고, 사람 수동 편집은 예외적이다.
- fancy한 RAG보다 잘 유지된 summary/index/concept/wiki를 우선한다 (Karpathy 2026 의 핵심 주장).
- 큰 질문은 필요한 source를 모아 임시 위키를 만들고, lint와 반복 보강을 거쳐 최종 report를 만든다.
- 구조나 계약이 바뀌면 README, AGENTS.md, 관련 docs를 즉시 갱신한다.
- 완료 주장은 실제 파일 생성 또는 문서 갱신으로 검증한다.

## 9. 최소 성장 기준

위키가 어느 정도 커지면(대략 100개 문서, 40만 단어 규모를 가이드라인으로 삼음) summary/index/concept 축만으로도 실용적 Q&A가 가능하다고 본다.

## 10. 금지/주의

- raw와 compiled를 섞지 않는다.
- 설명만 하고 파일을 남기지 않는 응답에 의존하지 않는다.
- source 없는 주장 문서를 만들지 않는다.
- 복잡한 구조를 먼저 도입하지 않는다. 반복 패턴이 생기면 그때 승격한다.
- vault 안에 Python/실행 코드를 두지 않는다 (4계층 invariant). 모든 로직은 `~/_/projects/owl/src/owl/` 에.

## 11. 운영 레이어 (owl)

운영 레이어는 정책을 Claude Code 가 자동으로 따르게 만드는 코드층이다. 핵심:

- **CLI**: `owl` (pipx 로 `~/.local/bin/owl` 설치). 명령: `status`, `init`, `setup`, `use`, `search`, `health`, `ingest`, `compile`, `file`, `hook`
- **5 hook**: `session_start`, `user_prompt`, `post_tool_use`, `pre_compact`, `stop` — 모두 `owl hook <name>` 디스패처
- **7 슬래시 명령**: `/owl-search`, `/owl-health`, `/owl-ingest`, `/owl-compile`, `/owl-file`, `/owl-promote`, `/owl-query` — CLI 결정성 + LLM 해석을 한 턴에
- **3 서브에이전트**: `owl-librarian` (filing/linking), `owl-compiler` (raw→summary/note), `owl-health` (health 해석)

자세한 명세: `docs/operational-layer-spec-v0.md`. 설치: `curl -fsSL .../install.sh | sh`.
