<!-- OMB:START -->
<!-- OMB:VERSION:0.1.0 -->

# oh-my-brain (omb) — Personal LLM Knowledge System

사용자의 개인 LLM-maintained 지식 시스템. 프로젝트: `<!-- OMB:REPO -->` (GitHub: `songblaq/oh-my-brain`).

단일 활성 vault: **akasha** (entries + compiled narratives + graph). owl/cairn/wiki는 deprecated.

## CLI

```bash
omb status                    # vault 전체 현황
omb search "<query>"          # 3-layer search (compiled + entries + graph)
omb ingest <file>             # 새 지식 추가
omb health                    # source coverage 확인
```

## Data layer

```
~/omb/
  source/          raw inputs (immutable)
  vault/akasha/    active vault
    entries/       atomic claims
    compiled/      LLM-written narratives
    INDEX.md       master index
    GRAPH.tsv      concept graph
    ALIASES.tsv    surface → canonical map
```

## 핵심 규칙

1. **source 불변** — `~/omb/source/` 파일은 절대 수정 금지
2. **vault = 데이터만** — 코드는 repo에, 데이터는 `~/omb/`에
3. **LLM이 writer** — entries/compiled는 LLM이 작성
4. **기록 시 evidence 동반** — 결과 + 근거(왜, 대안 비교, 검증) 함께

## 한글 프로젝트명 매핑

사용자가 한글로 프로젝트를 지칭할 때 정확한 프로젝트/시스템을 인식해야 한다:

| 한글 | 영문 | 프로젝트 경로 |
|------|------|--------------|
| 칼라 | Khala | `~/_/projects/khala` |
| 아리아 | ARIA | `~/_/projects/aria`, `~/.aria/` |
| 하이브 | AgentHive | `~/_/projects/agent-hive`, `~/.agenthive/` |
| 오빗 | ORBIT | `~/_/projects/orbit` |
| 콘스텔라 | Constella | `~/_/projects/constella-platform`, `~/.constellar/` |
| 데오스 | DEOS | `~/_/projects/deos-starter-kit` |
| 오픈클로 | OpenClaw | `~/_/projects/comfyui-openclaw`, `~/.openclaw/` |
| 키라클로 | KiraClaw | `~/_/projects/kiraclaw` |
| 에르메스, 허민희 | Hermes | `~/_/open-source/Hermes-Agent`, `~/.hermes/` |
| 클로버스 | ClawVerse | `~/_/projects/ClawVerse` |
| 테스트포지 | TestForge | `~/_/projects/testforge` |
| 브레인 | oh-my-brain | `~/_/projects/oh-my-brain` |

## 기본 reflex

사용자가 축적된 지식과 관련된 질문을 하면 **답변 전에** `omb search "<topic>"` 을 먼저 시도하는 게 기본 reflex. 결과가 있으면 해당 문서를 read 해서 근거로 답변. 결과가 없거나 빈약하면 그 사실을 명시하고 답변 후 사용자에게 `omb ingest` 로 자료 추가 제안.

<!-- OMB:END -->
