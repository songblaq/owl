# owl Vault — Claude Code Governance

> **owl** — 개인 LLM-maintained wiki.
> 사용자가 sources 를 큐레이트하고, LLM 이 나머지 (filing, cross-reference, 유지보수) 를 모두 한다.

이 vault 는 Karpathy 의 **LLM Wiki** 컨셉(2026)을 구현한 owl 의 데이터 저장소다.
이 파일은 Claude Code 가 이 디렉토리에서 세션을 시작할 때 자동으로 컨텍스트에 주입된다.

## Lineage

- **2026, Andrej Karpathy** — "LLM Wiki" gist (이 vault 의 `raw/2026-04-07-karpathy-llm-wiki-gist-raw.md`). LLM 이 raw 자료를 incremental 하게 wiki 로 컴파일/유지보수하는 패턴.
- **1945, Vannevar Bush** — "As We May Think" 의 Memex. 개인 큐레이트 지식 저장소 + associative trails. Karpathy 본인이 직접 인용하는 영적 조상. Bush 가 풀지 못한 부분이 "누가 유지보수하는가" 였고 LLM 이 그 답.

## 위키 컨셉 (가장 중요)

이것은 단순한 파일 관리 도구가 아니라 **점진적으로 LLM 이 유지보수하는 위키**다. 핵심 루프:

```
raw source → LLM compile → compiled wiki → QA/output → filing → compiled wiki
```

raw 는 절대 편집하지 않는다. LLM 은 raw 를 읽고 summary/note/concept/index/report 를 compiled/ 에 만들고, 시간이 지나면서 링크와 backlink 를 유지보수한다. RAG 가 아니라 **잘 유지된 wiki** 가 답이다 (`docs/small-scale-no-rag-policy-v0.md` 참조).

## 4계층 아키텍처

이 vault 는 owl 운영 체계의 **데이터층 (LAYER 4)** 일 뿐이다. 운영 로직은 별도 위치에 있다:

- **LAYER 1 — SPEC**: `~/_/projects/oh-my-brain/views/owl/` (정책 문서 + Python 소스)
- **LAYER 2 — RUNTIME**: `~/.local/bin/owl` CLI + `~/.claude/agents/owl-*` 서브에이전트
- **LAYER 3 — VAULT GLUE**: 이 vault 의 `.owl-vault`, `CLAUDE.md`, `.claude/`
- **LAYER 4 — DATA**: 이 vault 의 `raw/`, `compiled/`, `views/`, `outputs/` 등

**vault 는 데이터만 담는다**. `.claude/` 안에는 hook 호출 + 슬래시 명령 thin wrapper 만 있고 실제 코드는 없다. Python 파일을 vault 에 두지 마라.

## 디렉토리 계약

- `raw/` — 원본 자료. **절대 편집 금지**. 새 raw 는 `YYYY-MM-DD-<slug>-raw.md`
- `compiled/` — LLM 컴파일 결과. `*-summary.md`, `*-note.md`, `*-concept.md`, `*-index.md`, `*-report.md`
- `views/` — MDV 해석 뷰
- `outputs/` — slides, figures, visuals (filing loop 환류 대상)
- `inbox/` — 분류 전 자료
- `research/`, `logs/`, `tmp/`, `config/`

전체 파일 계약은 `~/_/projects/oh-my-brain/views/owl/AGENTS.md` 에 정의되어 있다.

## 핵심 원칙

1. **raw 불변**: 원본은 지우지 않는다 (Karpathy gist 의 `## Architecture` 참조)
2. **doc-first**: 정책 문서 → Python CLI → Claude 동작 (반대 방향 금지)
3. **파일명 계약**: `YYYY-MM-DD-<slug>-{raw|summary|note|concept|index|report}.md`
4. **링크 유지**: summary 는 raw 를 가리키고, compiled 끼리는 cross-link 를 유지한다
5. **wiki 자체 검증**: 의심스러우면 `owl health` 실행
6. **filing loop**: Q&A 결과나 산출물도 다시 compiled wiki 로 환류 (Karpathy 가 강조)

## 자주 쓰는 명령

| 명령 | 용도 |
|------|------|
| `owl status` | 현재 vault, version, 미해결 issue 개수 |
| `owl search "<query>"` | raw/compiled 토큰 스코어 검색 |
| `owl health` | 8가지 무결성 규칙 점검 |
| `owl health --json` | JSON 출력 (슬래시 명령용) |
| `/owl-search <query>` | 검색 + LLM 정리 (한 턴) |
| `/owl-health` | health check + LLM 해석 (한 턴) |
| `/owl-ingest <path>` | raw 후보 정리 → owl-librarian |
| `/owl-compile <raw-path>` | summary/note 생성 → owl-compiler |

## 서브에이전트

- **owl-librarian** — filing, naming, cross-link 유지 전문
- **owl-compiler** — raw → summary/note 컴파일
- **owl-health** — `owl health --json` 결과 해석 + 수정 제안

## Origin source

이 vault 의 컨셉을 정의하는 1차 원천 문서는:

```
raw/2026-04-07-karpathy-llm-wiki-gist-raw.md
```

Karpathy 가 직접 작성한 LLM Wiki gist 이며 raw 불변 원칙에 따라 절대 편집하지 않는다.

## 참조 문서 (project repo)

핵심 정책은 `~/_/projects/oh-my-brain/views/owl/docs/` 에 있다. 자주 참조:

- `agent-cli-doc-first-operating-principle-v0.md` — 상위 원칙
- `wiki-maintenance-spec-v0.md` — wiki 유지보수 규칙
- `wiki-linking-rules-v0.md` — 링크 컨트랙트
- `karpathy-ingest-rules-v0.md` — raw → compiled 규칙
- `compiled-format-spec-v0.md` — compiled 문서 형식
- `health-check-spec-v0.md` — 8개 health 규칙
- `workflow-v0.md` — 큰 질문 → 임시 위키 → report 흐름
- `operational-layer-spec-v0.md` — owl 운영 레이어 명세

---
이 파일은 `owl init` 가 생성했다. 수정하면 `owl init --refresh` 시 덮어써질 수 있다.
