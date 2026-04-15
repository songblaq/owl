---
id: benchmark-v6-results
status: completed
created: 2026-04-14
scope: facet compiled/ 검색 활성화 효과 측정
---

# benchmark-v6 — facet compiled layer 활성화 효과

## 변경 사항

- `views/facet/src/facet/searchcmd.py`: `compiled/` 디렉토리 검색 추가
  - `CompiledMatch` dataclass 추가 (path, shard, score, snippet)
  - `_score_compiled()`: raw text TF-IDF 스코어링 (shard name bonus +5)
  - `_build_compiled_snippet()`: frontmatter 제외 후 토큰 위치 기반 snippet 추출
  - `_search_compiled()`: `compiled/*.md` 전체 스캔
  - `run_search()`: entry match + compiled match 합산 → 점수 기준 정렬 → limit 적용
  - 출력: `[compiled] {shard}  (score: N)` prefix로 구분
- `views/omb/src/omb/cli.py`: help text `--view owl|cairn|all` → `--view owl|facet|lattice|all` 수정
- 검색 대상: shards/ (217 entries) + compiled/ (14 docs, avg 21.6KB)

## 검색 품질 비교 (지표 3)

| 쿼리 | v5 facet | v6 facet | v5 owl | 개선 여부 |
|------|---------|---------|--------|---------|
| Q1: orbit r4 scoring | 80 | 95 | 90 | +15 ✓ |
| Q2: nyx runtime migration | 45 | 70 | 95 | +25 ✓ |
| Q3: filing loop | 40 | 55 | 65 | +15 ✓ |
| Q4: r4 four axis definition | 85 | 85 | 65 | 0 |
| Q5: aria orchestration overview | 65 | 90 | 75 | +25 ✓ |
| Q6: khala nyx deos relationship | 65 | 80 | 95 | +15 ✓ |
| Q7: karpathy llm wiki | 95 | 95 | 100 | 0 |
| Q8: what not to do with RAG | 5 | 15 | 40 | +10 △ |
| Q9: omb cli commands list | 25 | 25 | 40 | 0 |
| Q10: why not use graph database | 5 | 10 | 35 | +5 △ |
| **평균** | **51.0** | **62.0** | **70.0** | **+11.0** |

## 쿼리별 분석

**Q1 orbit r4 scoring (+15)**: `[compiled] orbit` top hit (score 110). compiled/orbit.md가 R4 스코어링 관련 9개 entry를 집약해 매칭 표면을 크게 확장.

**Q2 nyx runtime migration (+25)**: `[compiled] aria` top hit (score 169). 41개 entry 집약으로 Nyx 관련 context가 풍부. 단 "migration" 내용 자체는 희박 — 부분 개선.

**Q3 filing loop (+15)**: alias resolved to karpathy shard. `[compiled] karpathy` 결과에 "filing" 워크플로우 snippet 노출. v5는 개별 entry 수준이라 coverage 낮았음.

**Q4 r4 four axis definition (0)**: v5에서 이미 85점. constella compiled가 top hit으로 등장하지만 개별 entry도 좋아서 차이 없음.

**Q5 aria orchestration overview (+25)**: `[compiled] aria` (score 160) — "orchestration" + "overview" 토큰이 41개 entry 집약 doc에서 풍부하게 매칭. 가장 큰 개선.

**Q6 khala nyx deos relationship (+15)**: `[compiled] deos` top hit (score 127) — deos/khala/nyx 세 토큰이 모두 포함된 deos compiled doc이 최상위.

**Q7 karpathy llm wiki (0)**: v5에서 이미 95점. compiled karpathy top hit (score 198)이지만 기존 entry 검색도 충분히 좋았음.

**Q8 RAG (+10, 한계 존재)**: karpathy compiled에 "RAG 대신 wiki" 내용이 있으나 #10위 — 대형 compiled doc("not" 반복 등 일반 토큰)이 상위를 점령하는 노이즈 문제. 실질적 개선 미미.

**Q9 omb cli (0)**: facet vault에 omb CLI 관련 content 없음. 구조적 한계.

**Q10 graph database (+5)**: graph database 관련 content 없음. 미미한 개선.

## 한계 및 관찰

1. **Large doc noise**: 대형 compiled doc(40KB+)은 일반적 토큰("not", "to", "with") 빈도가 높아 단순 쿼리에서 거짓 양성 발생 (Q8). TF-IDF의 알려진 한계.

2. **IDF 부재**: 문서 빈도 가중치 없이 raw count → 큰 doc이 구조적으로 유리. 향후 IDF 도입으로 개선 가능.

3. **Vault content gap**: Q9/Q10은 content가 없어 검색 품질 한계가 vault 수준에서 결정됨.

## 결론

- facet 검색 품질 변화: **51.0 → 62.0 (+11.0점)**
- owl(70.0)과의 격차: 19.0점 → 8.0점 (격차 절반 이상 해소)
- compiled layer 효과: **유효** — topic-dense 쿼리(aria, orbit, karpathy, khala)에서 15-25점 개선. 짧고 범용적인 쿼리(RAG, graph db)에서는 노이즈 증가.
- 권고: owl(70.0) 수준 달성을 위해 IDF 가중치 도입 고려. 현재 62.0으로 실용 범위 진입.
