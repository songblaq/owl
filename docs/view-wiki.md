> **DEPRECATED by docs/REZERO-2026-04-18.md.** 이 문서는 Opus 4.6 이 2026-04-17 에 쌓은 설계 stack 의 일부다. 2026-04-18 Re:Zero 로 전면 격하. 참조 목적으로만 보존.

---
id: view-wiki
status: active
created: 2026-04-17
updated: 2026-04-17
---

# wiki view — Karpathy LLM Wiki (상시 companion view)

akasha 와 병렬로 운영되는 **상시** view. 같은 `~/omb/source/` 를 읽지만 해석 방식이 다르다 — akasha 는 atomic claims + compiled narratives (머신 감사 최적), wiki 는 entity/concept 단위 narrative (사람 읽기 최적).

상주 결정 근거: Karpathy 패턴은 incremental 유지 설계이므로 재빌드 부담 없음. 비상주로 `/tmp` 에 매번 만들면 토큰·시간 낭비 + compounding 이점 상실.

## 디렉토리

```
~/omb/vault/wiki/
  AGENTS.md      schema (이 view 의 운영 규약)
  index.md       content-oriented catalog
  log.md         chronological append-only
  entities/      인물·장비·제품
  concepts/      아이디어·패턴
  sources/       raw 요약
  syntheses/     쿼리 답변 filing
  raw/           → ~/omb/source/ (symlink)
  .wiki-vault    마커
```

## view-contract 준수

1. **raw 에서만 읽기** — akasha 의 derived (entries/, compiled/, GRAPH.tsv) 를 읽지 않음. 양쪽 모두 source 가 ground truth
2. **자기 vault 에만 쓰기** — cross-view write 금지
3. **search 지원** — 현재는 `grep` + `index.md` 읽기. 규모 커지면 [tobi/qmd](https://github.com/tobi/qmd) 도입
4. **format 문서화** — `vault/wiki/AGENTS.md` 가 페이지 표준 명시
5. **rebuildable from source** — source 만 있으면 재생성 가능 (Karpathy 패턴의 핵심)

## 기술 스택 — 오픈소스 차용 (설치 아님)

규약·형식·워크플로만 가져오고 구현은 우리식 간결하게.

| 자료 | 차용한 것 |
|---|---|
| [karpathy/llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) | 전체 패턴 (3 layer, ingest/query/lint, index+log) |
| [ussumant/llm-wiki-compiler](https://github.com/ussumant/llm-wiki-compiler) | topic-based compile 워크플로, health-check 항목 |
| [Ar9av/obsidian-wiki](https://github.com/Ar9av/obsidian-wiki) | `[[wiki link]]` 문법 |
| [tobi/qmd](https://github.com/tobi/qmd) | (미통합) 검색 도구 후보 |
| [rohitg00/LLM Wiki v2 gist](https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2) | active learning 확장 개념 (향후) |

풀 설치를 고려한 이유와 포기한 이유:
- Claude Code plugin / Obsidian 결합이 많아 **무거움**
- 우리는 view-contract 준수가 핵심 — 외부 툴의 자기 구조를 그대로 못 씀
- 규약·페이지 형식만 빌려쓰면 80% 가치 확보, 통합 복잡도 0

## akasha 와의 관계

독립 view. 하나가 진실이고 다른 하나가 거울이 아니다. 같은 source 에서 **다르게 해석한 결과물**.

| 축 | akasha | wiki |
|---|---|---|
| 단위 | 1 파일 = 1 atomic claim | 1 파일 = 1 entity / concept |
| 카탈로그 | INDEX.md (auto-generated) | index.md (LLM-curated) |
| 이력 | superseded/ 물리 이동 | log.md chronological, 페이지는 in-place rewrite |
| 검색 | 3-layer (compiled + entries + graph) | index-first + drill-down (+ grep) |
| enforcement | contract v2 + `omb audit` | lint workflow (수동) |
| 사람 읽기 | compiled 만 친화적 | 모든 페이지 narrative |
| 머신 감사 | 강함 — superseded 물리 이동, evidence 블록 | 약함 — 페이지 내 다중 claim |

## 운영 흐름

### Ingest

```
1. 새 source drop → ~/omb/source/
2. wiki 쪽: "이 raw 읽고 영향받는 페이지 업데이트"
   a. LLM read
   b. 기존 entity/concept 페이지 업데이트 (contradiction 명시)
   c. 새 페이지 생성
   d. sources/<slug>.md 요약
   e. index.md 갱신
   f. log.md append
3. akasha 쪽: omb ingest (독립 수행)
```

### Query

wiki 는 사람 읽기 중심 → index.md → 관련 페이지 read → 답변. 답변이 반복 가치 있으면 `syntheses/<slug>.md` 로 filing.

머신 감사 / 원자 단위 추적이 필요하면 akasha.

### Lint (정기)

`log.md` 에 주기적으로 `## [date] lint | issues: N` 추가. 검사 항목:
- contradictions (페이지 간 충돌)
- stale claims (새 source 미반영)
- orphan pages (inbound link 0)
- broken `[[wiki links]]`
- missing concepts (여러 페이지 언급되는데 본인 페이지 없음)

## 벤치마크 (필요 시)

wiki 는 상시 운영이지만 "wiki vs akasha 비교" 는 여전히 가끔 할 가치가 있다. 동일 query 를 양쪽에 던져 결과 품질 대조.

```bash
omb search "<q>" > /tmp/akasha.txt   # akasha + capsule 자동 연결
grep -l "<keyword>" ~/omb/vault/wiki/**/*.md | xargs cat > /tmp/wiki.txt
# 비교 후 개선점은 양쪽 view 에 흡수
```

## 현재 상태 (seed)

- AGENTS.md 존재
- seed 페이지 3개 (homelab 도메인): entities/dgx-spark, concepts/llm-serving, sources/homelab-infra-reorg
- index.md, log.md 초기화
- 다음 ingest 후보: 나머지 homelab raw 5 개

**Obsidian 관점** 에서 바로 열어도 graph / backlinks 가 작동한다.
