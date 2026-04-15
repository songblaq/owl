---
id: benchmark-v4-results
status: completed
created: 2026-04-14
based_on: benchmark-v3-results.md (10-dimension methodology)
scope: 5-way (owl + facet + lattice + rehalf + rezero)
---

# benchmark-v4 결과 — owl vs facet vs lattice vs rehalf vs rezero

## 개요

| 항목 | 결과 |
|------|------|
| 측정 일시 | 2026-04-14 |
| 대상 view | owl / facet / lattice / rehalf / rezero |
| 총 지표 수 | 10개 (v3와 동일 가중치) |
| 쿼리셋 | 10개 (v3와 동일) |
| 최종 순위 | **facet 82.8 > rehalf 81.9 > rezero 79.3 > lattice 76.6 > owl 65.7** |

v3 대비 변경: owl/facet/lattice는 지표 1-3(저장소·속도·품질) 재측정, 지표 4-10은 v3 값 유지.  
rehalf/rezero는 전 지표 신규 측정. 단, coverage completeness는 facet도 100%로 상향 수정 (128/128 확인).

---

## 1. 기본 상태 (측정 기준점)

| view | entries | vault size | avg file size | 진입점 |
|------|---------|-----------|---------------|--------|
| owl | 233 compiled | 1.2MB | 3,029B | CLAUDE.md (4.9KB) |
| facet | 217 entries (14 shards) | 948KB | 1,351B | INDEX.md (40KB), MANIFEST.md (760B) |
| lattice | 169 entries | 676KB | 1,582B | MAP.md (17.5KB), GRAPH.tsv (12KB) |
| rehalf | 217 entries (14 shards) | 948KB | 1,362B | INDEX.md (41KB), MANIFEST.md (762B) |
| rezero | 217 entries + 14 compiled | 868KB entries + 324KB compiled | 1,365B (entries) | COMPILED_INDEX.md (822B) + compiled/{shard}.md |

Raw sources: **128개** (공통 — v3 이후 2개 추가)  
rehalf shards: 14개 (facet과 동일 구조, edges 필드 추가)  
rezero layers: entries(원자적 217개) + compiled(14개 내러티브 문서)

---

## 2. 지표별 점수

### 지표 1: 저장소 밀도 (Storage Density) — 가중치 9.52%

파일 수(coverage breadth) × 50 + 원자성(1/avg_size 정규화) × 50.

| view | 파일 수 | 파일수 점수 | 평균 크기 | 원자성 점수 | **밀도 점수** |
|------|---------|-----------|---------|-----------|------------|
| owl | 233 | 100.0 | 3,029B | 44.6 | **72.3** |
| facet | 217 | 93.1 | 1,351B | 100.0 | **96.6** |
| lattice | 169 | 72.5 | 1,582B | 85.4 | **79.0** |
| rehalf | 217 | 93.1 | 1,362B | 99.2 | **96.2** |
| rezero | 217 | 93.1 | 1,365B | 99.0 | **96.1** |

facet·rehalf·rezero가 원자성에서 99-100점으로 동점권. owl이 파일수 1위이나 원자성에서 44.6점으로 최하위.  
rezero의 compiled 14개 문서는 밀도 측정에서 제외 (read layer, write layer = entries 기준).

---

### 지표 2: 검색 속도 (Retrieval Speed) — 가중치 14.29%

5개 쿼리 × 2회 반복 평균. 최속 = 100 (v4 재측정).

| view | 평균 속도 | **속도 점수** |
|------|---------|------------|
| owl | 62ms | **66.1** |
| facet | 42ms | **97.6** |
| lattice | 44ms | **93.2** |
| rehalf | 41ms | **100.0** |
| rezero | 43ms | **95.3** |

rehalf가 41ms로 최속 — 14개 shard FTS 구조가 facet과 동일하고 graph 탐색 오버헤드가 없다.  
rezero는 양층(compiled + entries) 검색에도 43ms로 lattice보다 빠름.

---

### 지표 3: 검색 품질 (Search Quality) — 가중치 19.05%

10개 쿼리 top-5 결과 관련도 평가 (0-100점). owl/facet/lattice는 v3와 동일 쿼리셋 재실행 점수 유지.

| 쿼리 | owl | facet | lattice | rehalf | rezero | 비고 |
|------|-----|-------|---------|--------|--------|------|
| Q1: orbit r4 scoring | 90 | 80 | 90 | 85 | 90 | rehalf: 2개 관련 entry, rezero: orbit compiled 직접 히트 |
| Q2: nyx runtime migration | 95 | 45 | 45 | 40 | **85** | rezero: aria.md compiled narrative가 nyx runtime 커버. rehalf는 직접 히트 없음 |
| Q3: filing loop | 65 | 50 | **95** | 45 | 55 | lattice 압도적. rehalf alias 작동하나 top score 2점. rezero compiled mentions filing |
| Q4: r4 four axis definition | 65 | 85 | **90** | 80 | 85 | rehalf/rezero: constella 4-axis entry 보유 |
| Q5: aria orchestration overview | 75 | 65 | 70 | 60 | **90** | rezero: aria.md compiled narrative 강력 히트 |
| Q6: khala nyx deos relationship | **95** | 65 | 70 | 75 | **90** | rezero: deos+aria compiled 다중 히트. rehalf: deos-khala-sync 직접 히트 |
| Q7: karpathy llm wiki | **100** | 95 | 95 | 95 | **100** | rezero/owl: 최고점. 모두 우수 |
| Q8: what not to do with RAG | 40 | 10 | 10 | 10 | 15 | 전체 약세. rezero compiled에도 해당 문서 없음 |
| Q9: omb cli commands list | 40 | 25 | 30 | 15 | 20 | omb CLI 자체 문서 부재. rehalf/rezero도 동일 취약점 |
| Q10: why not use graph database | 35 | 5 | 20 | 5 | 10 | 전체 약세. 결정 근거 문서 없음 |
| **평균** | **70.0** | **52.5** | **61.5** | **51.0** | **64.0** | |

**핵심 관찰:**
- rezero가 64.0으로 v3의 owl(70.0) 다음으로 2위. Re:Zero 가설 부분 검증.
- Q2 (nyx runtime migration): rezero 85 vs owl 95 — 격차 10점으로 좁혀짐 (v3 lattice/facet은 45점).
- Q5 (aria orchestration overview): rezero 90 vs owl 75 — rezero가 owl을 역전.
- Q3 (filing loop): rezero 55로 lattice(95) 대비 여전히 40점 격차.
- rehalf(51.0)는 facet(52.5)보다 약간 낮음 — 검색 품질에서 얻는 이점 없음.

---

### 지표 4: Startup 비용 (Session Startup Cost) — 가중치 9.52%

| view | 진입점 | 크기 | LLM 유용성 | **Startup 점수** |
|------|--------|------|-----------|---------------|
| owl | CLAUDE.md | 4.9KB | 도구 가이드 있지만 entry 목록 없음 | **50** |
| facet | MANIFEST.md + INDEX.md | 760B + 40KB | MANIFEST로 전체 조망, INDEX로 217 entry 카탈로그 | **80** |
| lattice | MAP.md | 17.5KB | 커버리지 맵 — 구조는 보이나 entry 카탈로그 아님 | **65** |
| rehalf | MANIFEST.md + INDEX.md | 762B + 41KB | facet과 동일 구조 — 217 entry 카탈로그 | **80** |
| rezero | COMPILED_INDEX.md | 822B | 소형 인덱스 → 14개 compiled doc 직접 접근. narrative 요약 바로 활용 가능 | **85** |

rezero가 85로 최고점. COMPILED_INDEX(822B)는 facet MANIFEST보다 작고, 14개 compiled doc이 narrative 형태라 LLM 세션 시작 시 즉시 활용 가능. 반면 facet/rehalf INDEX.md(40KB)는 전체 entry 카탈로그로 더 상세하지만 더 무겁다.

---

### 지표 5: 쓰기 처리량 (Write Throughput) — 가중치 14.29%

| view | 방식 | 특성 | **처리량 점수** |
|------|------|------|-------------|
| owl | sequential compile | 파일당 5-10분, 병렬 불가 | **46.1** |
| facet | parallel-friendly atomic | 고정 schema, 1초 재인덱스 | **100.0** |
| lattice | parallel + edges | edge 생성 추가 비용 | **70.0** |
| rehalf | parallel-friendly atomic + optional edges | edges 필드 있으나 선택 사항 `edges: []` | **95.0** |
| rezero | parallel entries + `rezero compile` | entries 병렬 처리 → compile은 shard당 LLM 호출 | **70.0** |

rehalf는 edges 필드가 대부분 비어있어(`edges: []`) facet과 거의 동일한 쓰기 속도. 95점.  
rezero는 entries 추가는 facet과 동등하지만, `rezero compile` 실행 시 14개 shard에 LLM 호출이 필요해 배치 오버헤드 발생. lattice와 동점 70.

---

### 지표 6: 쓰기 인체공학 (Write Ergonomics) — 가중치 9.52%

| view | 스키마 복잡도 | 특수 구조 | **인체공학 점수** |
|------|------------|---------|--------------|
| owl | YAML frontmatter + 자유 본문 | 파일 유형 선택 필요 | **65** |
| facet | 고정 schema + 14 shard 분류 | ALIASES.tsv 별도 관리 | **60** |
| lattice | 고정 schema + edges YAML | content-addressed ID 생성, edge 명시 | **55** |
| rehalf | 고정 schema + shard + edges | edges는 선택적이나 인지 부하 존재 | **58** |
| rezero | 고정 schema + shard (entries) | compile 단계 별도 실행 인지 필요 | **60** |

---

### 지표 7: Source 역추적 가능성 (Source Traceability) — 가중치 4.76%

30개 random sample 기준 (v4 재측정).

| view | 소스 참조 | 비율 | **역추적 점수** |
|------|---------|------|------------|
| owl | 출처: 필드 | 100% | **100** |
| facet | source: 필드 | 100% | **100** |
| lattice | source: 필드 | 100% | **100** |
| rehalf | source: 필드 | 30/30 (100%) | **100** |
| rezero | source: 필드 | 30/30 (100%) | **100** |

전 5개 view 동점 100.

---

### 지표 8: Coverage 완전성 (Coverage Completeness) — 가중치 9.52%

v4에서 facet도 128/128로 100% 확인 (v3는 116/126으로 92% — 신규 source 추가 + 재측정으로 수정).

| view | 커버 소스 수 | 전체 소스 | 커버리지 | **Coverage 점수** |
|------|-----------|---------|---------|----------------|
| owl | 128 | 128 | 100% | **100** |
| facet | 128 | 128 | 100% | **100** |
| lattice | 128 | 128 | 100% | **100** |
| rehalf | 128 | 128 | 100% | **100** |
| rezero | 128 | 128 | 100% | **100** |

전 5개 view 동점 100.

---

### 지표 9: Cross-query 일관성 (Cross-query Consistency) — 가중치 4.76%

"orbit r4 scoring" 개념을 3개 표현으로 질의.

| view | Q: orbit r4 scoring (1위) | Q: R4 dispatch score (1위) | Q: r4 priority vector (1위) | **일관성 점수** |
|------|--------------------------|--------------------------|----------------------------|-------------|
| owl | 다른 파일 | 다른 파일 | 다른 파일 (1/3) | **33** |
| facet | entry A | entry B | entry B (2/3) | **67** |
| lattice | 동일 파일 3회 (3/3) | | | **100** |
| rehalf | orbit-r4-dispatch-engine | orbit-r4-scoring-dispatch | orbit-r4-scoring-dispatch (2/3) | **67** |
| rezero | orbit shard | orbit shard | constella+orbit 동점 (2/3) | **67** |

lattice의 content-addressed ID 우위 유지. facet/rehalf/rezero가 67점 동점.  
rezero는 compiled shard 단위로 라우팅되어 orbit shard가 2/3 일관성 달성.

---

### 지표 10: Update 전파 비용 (Update Propagation Cost) — 가중치 4.76%

| view | incremental 방식 | re-index 속도 | **Update 점수** |
|------|----------------|-------------|--------------|
| owl | 5-10분 sequential | 통합됨 | **55** |
| facet | 3-5분 parallel + `facet index` | **1초** | **95** |
| lattice | 3-5분 parallel + MANIFOLD/BLOOM 재빌드 | 수초 | **75** |
| rehalf | 3-5분 parallel + `rehalf index` | **1초** (facet과 동일) | **95** |
| rezero | 3-5분 parallel + `rezero index` + `rezero compile` | entries: 1초, compile: 수분 | **65** |

rehalf는 facet과 동일한 1초 재인덱스 구조로 95점. rezero는 `rezero compile`이 LLM 재호출을 수반하므로 compiled layer 갱신에 추가 비용 발생.

---

## 3. 종합 점수표

| 지표 | 가중치 | owl | facet | lattice | rehalf | rezero |
|------|--------|-----|-------|---------|--------|--------|
| 1. 저장소 밀도 | 9.52% | 72.3 | **96.6** | 79.0 | 96.2 | 96.1 |
| 2. 검색 속도 | 14.29% | 66.1 | 97.6 | 93.2 | **100.0** | 95.3 |
| 3. 검색 품질 | 19.05% | **70.0** | 52.5 | 61.5 | 51.0 | 64.0 |
| 4. Startup 비용 | 9.52% | 50 | 80 | 65 | 80 | **85** |
| 5. 쓰기 처리량 | 14.29% | 46.1 | **100.0** | 70.0 | 95.0 | 70.0 |
| 6. 쓰기 인체공학 | 9.52% | **65** | 60 | 55 | 58 | 60 |
| 7. Source 역추적 | 4.76% | 100 | 100 | 100 | 100 | 100 |
| 8. Coverage 완전성 | 9.52% | 100 | 100 | 100 | 100 | 100 |
| 9. Cross-query 일관성 | 4.76% | 33 | 67 | **100** | 67 | 67 |
| 10. Update 전파 비용 | 4.76% | 55 | **95** | 75 | **95** | 65 |
| **가중 종합 점수** | **100%** | **65.7** | **82.8** | **76.6** | **81.9** | **79.3** |

**1위: facet (82.8)** / 2위: rehalf (81.9) / 3위: rezero (79.3) / 4위: lattice (76.6) / 5위: owl (65.7)

---

## 4. 지표별 1위

| 지표 | 1위 | 점수 |
|------|-----|------|
| 저장소 밀도 | facet | 96.6 |
| 검색 속도 | **rehalf** | 100.0 |
| 검색 품질 | **owl** | 70.0 |
| Startup 비용 | **rezero** | 85 |
| 쓰기 처리량 | facet | 100.0 |
| 쓰기 인체공학 | owl | 65 |
| Source 역추적 | 동점 5개 | 100 |
| Coverage 완전성 | 동점 5개 | 100 |
| Cross-query 일관성 | **lattice** | 100 |
| Update 전파 비용 | facet·rehalf 동점 | 95 |

facet: 3개 지표 1위 / rehalf: 2개 지표 1위 / rezero·owl·lattice: 각 1개 지표 1위

---

## 5. 세부 기여도 분석

| 지표 | owl | facet | lattice | rehalf | rezero |
|------|-----|-------|---------|--------|--------|
| 저장소 밀도 | 6.88 | 9.20 | 7.52 | 9.16 | 9.15 |
| 검색 속도 | 9.45 | 13.95 | 13.32 | **14.29** | 13.62 |
| 검색 품질 | **13.34** | 10.00 | 11.72 | 9.72 | 12.19 |
| Startup 비용 | 4.76 | 7.62 | 6.19 | 7.62 | **8.09** |
| 쓰기 처리량 | 6.59 | **14.29** | 10.00 | 13.58 | 10.00 |
| 쓰기 인체공학 | **6.19** | 5.71 | 5.24 | 5.52 | 5.71 |
| Source 역추적 | 4.76 | 4.76 | 4.76 | 4.76 | 4.76 |
| Coverage 완전성 | 9.52 | 9.52 | 9.52 | 9.52 | 9.52 |
| Cross-query 일관성 | 1.57 | 3.19 | **4.76** | 3.19 | 3.19 |
| Update 전파 비용 | 2.62 | **4.52** | 3.57 | **4.52** | 3.09 |
| **합계** | **65.67** | **82.75** | **76.59** | **81.87** | **79.33** |

facet과 rehalf의 격차는 0.88 포인트 — 검색 품질(facet 52.5 vs rehalf 51.0, -0.28)과 쓰기 처리량(facet 100 vs rehalf 95, -0.71) 합산.  
rezero가 facet보다 앞서는 유일한 지표: Startup 비용 (8.09 vs 7.62, +0.47).

---

## 6. 서사 분석

### facet: 운영 최적화된 LLM-first brain — 여전히 1위

facet은 v4에서도 1위를 유지한다. 쓰기 처리량(100) + 저장소 밀도(96.6) + 검색 속도(97.6) + Update 전파(95)의 조합은 신규 뷰들이 복제하기 어려운 운영 최적화 세트다. rehalf가 0.88점 차이로 추격하지만 핵심 차별점인 쓰기 처리량(100 vs 95)에서 우위를 지킨다.

### rehalf: facet의 거의 완벽한 복제 + edges 추가 — 실질적 동점

rehalf(81.9)는 facet(82.8)과 0.88 차이로 측정 오차 범위에 근접한다. 14개 shard 구조와 MANIFEST+INDEX 진입점이 identical하여 속도·밀도·커버리지에서 facet과 동점권이다. 검색 품질(51.0)은 facet(52.5)보다 약간 낮아 역설적으로 edges 추가가 검색 품질 개선을 가져오지 못했다.

**rehalf의 edges는 측정된 어떤 지표에서도 유의미한 개선을 보이지 않는다.** cross-query 일관성이 67(facet과 동점)이고 검색 품질도 오히려 낮다. lattice(100)가 가진 content-addressed ID 기반의 그래프 탐색과는 다른 방식이다. rehalf edges의 현재 가치는 미측정 영역(1-hop expansion 쿼리)에 있을 수 있다.

### rezero: Re:Zero 가설 부분 검증 — 검색 품질 2위

rezero(79.3)는 compiled layer가 검색 품질을 유의미하게 높이는 것을 확인했다. 64.0점으로 facet(52.5)·lattice(61.5)보다 높고 owl(70.0)에 6점 차로 접근했다. 특히 Q2(nyx runtime migration: 85 vs owl 95), Q5(aria orchestration overview: 90 vs owl 75), Q6(khala nyx deos relationship: 90 vs owl 95)에서 owl 대비 거의 동등하거나 우위다.

약점: Q3(filing loop: 55)과 Q8-Q10(특정 부재 문서 쿼리들)에서는 여전히 낮다. compiled layer는 존재하는 내용의 내러티브를 강화하지, 없는 정보를 만들어내지 않는다.

startup 비용 1위(85): COMPILED_INDEX.md(822B)로 즉시 어느 shard 내러티브로 진입할지 파악 가능하고, compiled/{shard}.md가 LLM에게 바로 소화 가능한 narrative를 제공한다는 점이 차별점이다.

주요 비용: `rezero compile` 실행이 write throughput(70)과 update propagation(65)을 끌어내린다. compiled layer 갱신에 shard당 LLM 호출이 필요하다.

### lattice: cross-query 일관성 독보적 1위 — 운영 비용이 약점

lattice(76.6)는 v3와 동일한 위치. cross-query 일관성 100점은 여전히 독보적이며, 이는 5개 view 중 유일하다. 그래프 탐색(1-hop expansion)이 Q3(filing loop: 95)와 Q4(r4 four axis: 90)에서 실질적 품질 향상을 제공한다.

단, rehalf와 rezero의 등장으로 lattice의 고유 가치가 cross-query 일관성 하나로 좁아졌다. typed edges의 검색 품질 개선(61.5)은 rezero(64.0)보다 낮다.

### owl: 검색 품질 단독 1위 위치 일부 침식

owl(65.7)은 검색 품질에서 여전히 1위(70.0)이나, rezero(64.0)가 2.4점 차이로 추격했다. v3에서 facet과의 품질 격차가 -17.5점이었는데, v4에서 rezero와의 격차는 -6.0점으로 줄었다. Re:Zero가 목표한 "owl 수준의 검색 품질"은 아직 달성되지 않았으나 방향성은 확인됐다.

Q8-Q10 구조적 약점(부재 문서 문제)은 5개 view 모두에 공통적이며 owl만의 강점이 아니다.

---

## 7. Re:Zero 가설 검증

**가설**: "rezero의 compiled layer는 facet의 검색 품질 약점을 극복하고 owl 수준의 검색 품질을 달성할 수 있는가?"

| 항목 | 결과 | 판정 |
|------|------|------|
| rezero 검색 품질 vs facet | 64.0 vs 52.5 (+11.5점) | ✓ 가설 확인 |
| rezero 검색 품질 vs lattice | 64.0 vs 61.5 (+2.5점) | ✓ 가설 확인 |
| rezero 검색 품질 vs owl | 64.0 vs 70.0 (-6.0점) | △ 미달, 방향성 확인 |
| owl 수준 달성 | 아직 미달 | △ |

**결론**: Re:Zero 가설은 **부분 검증**. compiled layer가 facet 대비 검색 품질을 +11.5점 끌어올리는 것은 확인됐으나, owl의 70.0점은 아직 넘지 못했다. 격차는 6점으로 v3의 facet-owl 격차(-17.5점)에서 크게 줄었다.

핵심 미달 쿼리는 Q3(filing loop: 55 vs 65)로, lattice의 graph expansion이 95점을 내는 것과 달리 rezero compiled는 shard 단위 내러티브 병합으로는 이 특정 패턴을 포착하지 못한다.

**trade-off 정리**: rezero는 검색 품질을 facet 대비 크게 높이는 대신 write throughput(-30점)과 update propagation(-30점)을 지불한다. "검색 품질 개선이 compile 비용을 정당화하는가"가 채택 결정의 핵심이다.

---

## 8. v3 vs v4 비교

| 항목 | v3 결과 | v4 결과 |
|------|---------|---------|
| 1위 | facet (82.3) | facet (82.8) |
| 2위 | lattice (76.9) | rehalf (81.9) |
| 3위 | owl (65.6) | rezero (79.3) |
| — | — | lattice (76.6) |
| — | — | owl (65.7) |

facet이 0.5점 상승 (coverage 100% 수정으로 +0.76). lattice는 2위→4위로 밀림 — rehalf·rezero 진입으로.

---

## 9. Use-case별 권고

| 사용 시나리오 | 권고 | 이유 |
|------------|------|------|
| LLM 세션 시작 시 brain 전체 조망 | **rezero** | COMPILED_INDEX → compiled/{shard}.md 즉각 narrative 활용 |
| 특정 개념의 정확한 파일 검색 | **owl** | 검색 품질 1위 (70.0) |
| 새 raw source 대량 추가 | **facet** | 처리량 1위 (100), 1초 재인덱스 |
| 동의어/변형 표현 일관 검색 | **lattice** | cross-query 일관성 100 |
| graph 1-hop 연쇄 탐색 | **lattice** | typed graph edges |
| narrative query (migration, history) | **rezero** | compiled layer가 내러티브 커버 |
| 인간 Obsidian browsing | **owl** | compiled doc narrative |
| facet에 edges 추가만 필요 | **rehalf** | facet과 거의 동일 운영 효율, edge 정보 추가 |
| 운영 효율 최우선 | **facet** | 쓰기 처리량 + 속도 + 업데이트 비용 최적 |

---

## 10. 새 잠정 권고

benchmark-v4 결과 기반:

**옵션 A: facet + rezero (2-view)**
- 얻는 것: facet의 운영 효율(82.8) + rezero의 검색 품질 보완(64.0) + rezero의 startup 우위(85)
- 잃는 것: lattice의 cross-query 일관성 100, graph 1-hop expansion
- 비용: rezero compile 배치 실행 필요

**옵션 B: facet + lattice + rezero (3-view)**
- 얻는 것: 운영 효율 + cross-query 일관성 + compiled narrative 검색
- 비용: raw 추가 시 에이전트 3세트, 검색 결과 중복

**옵션 C: rehalf 단독 (facet 대체)**
- 얻는 것: facet의 운영 효율과 거의 동일 + edges 구조 포함
- 잃는 것: 검색 품질 (-1.5 vs facet), 실질적 이득 불분명

**필자 권고 → facet + rezero (2-view)**  
rezero는 facet이 가장 약한 검색 품질(52.5)을 64.0으로 보완하고, startup cost(85)에서도 1위다. facet의 운영 효율을 유지하면서 rezero를 "narrative search layer"로 병렬 활용하는 것이 현재 최선의 조합이다.

rehalf는 현재 결과에서 facet 대비 유의미한 개선을 보이지 않아 별도 view 유지의 근거가 약하다. edges 기능이 구체적 사용 사례(1-hop 연쇄 검색)로 검증되기 전까지 facet으로 충분하다.

lattice는 cross-query 일관성 100점이라는 고유 강점이 있으나, facet+rezero 조합에서 rezero의 compiled shard 라우팅이 일부 보완한다(67점). 완전한 그래프 탐색이 필요한 시나리오가 빈번하다면 유지 가치 있음.

