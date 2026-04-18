> **DEPRECATED by docs/REZERO-2026-04-18.md.** 이 문서는 Opus 4.6 이 2026-04-17 에 쌓은 설계 stack 의 일부다. 2026-04-18 Re:Zero 로 전면 격하. 참조 목적으로만 보존.

---
id: ingest-contract-v2
status: draft (experiment B)
created: 2026-04-17
---

# Ingest Contract v2 — akasha 재생성 파이프라인 스펙

실험 B의 핵심. 기존 `omb ingest`가 "파일 → entry 1개 작성"에 그쳐 중복과 스타일 표류를 허용했다면, v2는 모든 write 전에 **contract validation**을 강제한다.

## Entry write preconditions

새 entry 작성 시 다음이 모두 참이어야 write 허용:

### C1. Naming contract
- 파일명: `YYYY-MM-DD-<topic>-<slug>.md` (정규식: `^\d{4}-\d{2}-\d{2}-[a-z][a-z0-9-]*\.md$`)
- `<topic>`: `ALIASES.tsv`에 존재하는 canonical topic
- `<slug>`: kebab-case, 영문+숫자+하이픈만

### C2. Frontmatter required fields
```yaml
id: <same as filename stem>
type: claim | fact | procedure | decision | observation | definition | preference | open-question
topics: [<primary>, ...]
confidence: high | medium | low
source: <absolute path under ~/omb/source/, must exist>
authored: <ISO date — source 원본 작성일>
ingested: <ISO date — ingest 시점>
supersedes: [<old-id>, ...]  # empty if none
edges: [<related-id>, ...]   # empty if none
```
`created` 단일 필드는 deprecated (authored/ingested 이원화).

### C3. Body required blocks
```markdown
## <claim statement>

<core content>

## Why it matters
<rationale>

## Evidence
- <source citation with line or section ref>
- <alternatives considered>
- <verification: how was this checked>
```
Evidence 블록 누락 시 write 거부.

### C4. Pre-write search (duplicate/supersede detection)
Writer는 반드시 다음을 수행:
1. `(topic, type)` 튜플로 기존 entries 검색
2. 유사 claim (token overlap > 0.6 또는 LLM semantic match) 발견 시:
   - **동일 주장**: write 스킵, 기존 entry의 `sources:` 리스트에 현재 source 추가
   - **갱신 주장**: `supersedes: [old-ids]` 포함 + old entry를 `superseded/`로 물리 이동
3. Pre-write search 결과를 entry body 하단 `<!-- pre-write-search: ... -->` 주석에 기록 (audit trail)

### C5. Source link integrity
- `source:` 경로의 파일이 `~/omb/source/` 하위에 실제 존재해야 함
- 심볼릭 링크 `<vault>/sources → ~/omb/source` 유지 (하위 호환)

### C6. Graph edge suggestion
- Writer는 related entries 1~3개를 `edges:`에 제시
- 최소 1개 edge 필수 (orphan 금지) — 단, 첫 entry거나 완전 새 topic이면 예외

## Validator CLI

```bash
omb ingest --text "..." --validate-only   # dry-run: contract 위반만 보고
omb ingest --text "..."                    # 위반 없으면 write, 있으면 거부 + 수정안 제시
omb ingest --force <file>                  # contract 우회 (migration 전용)
```

## Supersede CLI

```bash
omb supersede <new-entry-id> --replaces <old-id-1> <old-id-2> ...
# effect:
#   1. new entry의 frontmatter supersedes에 old ids 추가
#   2. each old-id → superseded/ 로 물리 이동
#   3. GRAPH.tsv에서 old → new edge 추가
#   4. INDEX.md에서 old 제거
```

## Audit CLI

```bash
omb audit                    # AUDIT.md 생성 (duplicate / broken / orphan)
omb audit --since <date>     # 해당 이후 ingest된 entries만 검사
omb audit --fail-on broken-source    # CI용 exit code 1
```

## Migration from legacy vault

기존 636 entries → v2 contract 적용:
1. `omb migrate --dry-run` 으로 위반 entries 목록
2. Manual review: 각 위반에 대해 (a) rewrite (b) supersede (c) delete 중 선택
3. `omb migrate --apply` 로 일괄 적용
4. superseded/로 이동된 것은 3개월 후 `omb prune` 으로 삭제 가능

## Cost estimate (237 source 전면 rebuild)

- Source 1개당 LLM call: ~3회 (pre-search, write, verify) × 평균 2k tokens
- 237 × 3 × 2k = ~1.4M tokens input + ~0.5M output
- Opus 4.6 기준: ~$30 예상
- 실행 시간: 병렬 5개 워커로 ~1시간

## Rebuildability test protocol

Spec을 실증하려면:
1. v2 contract 기반 ingest를 237 source 전체에 적용
2. 결과 vault의 benchmark 지표가 v2 contract와 일치하는지 확인
3. 2주 후 동일 source로 다시 rebuild → 두 결과의 diff가 "LLM 재해석 범위" 내에 있는지
4. 차이가 크면 contract에 결정론성 부족 — prompt 강화
