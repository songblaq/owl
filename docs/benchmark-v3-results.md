---
id: benchmark-v3-results
status: completed
created: 2026-04-14
based_on: benchmark-v2.md (10-dimension methodology)
scope: 3-way (owl + facet + lattice)
---

# benchmark-v3 결과 — owl vs facet vs lattice

## 개요

| 항목 | 결과 |
|------|------|
| 측정 일시 | 2026-04-14 |
| 대상 view | owl / facet / lattice |
| 총 지표 수 | 10개 (v2와 동일 가중치) |
| 쿼리셋 | 10개 (v2 4개 포함) |
| 최종 순위 | **facet 82.3 > lattice 76.9 > owl 65.6** |

---

## 1. 기본 상태 (측정 기준점)

| view | entries | vault size | avg file size | 진입점 |
|------|---------|-----------|---------------|--------|
| owl | 233 compiled | 1.2MB | 3,029B | CLAUDE.md (4.9KB) |
| facet | 217 entries (14 shards) | 948KB | 1,351B | INDEX.md (40KB), MANIFEST.md (760B) |
| lattice | 169 entries | 676KB | 1,582B | MAP.md (17.5KB), GRAPH.tsv (12KB) |

Raw sources: **126개** (공통)  
ALIASES.tsv: **137줄** (facet)  
Typed edges: **243개** (lattice)

---

## 2. 지표별 점수

### 지표 1: 저장소 밀도 (Storage Density) — 가중치 9.52%

파일 수(coverage breadth) × 50 + 원자성(1/avg_size 정규화) × 50.

| view | 파일 수 | 파일수 점수 | 평균 크기 | 원자성 점수 | **밀도 점수** |
|------|---------|-----------|---------|-----------|------------|
| owl | 233 | 100.0 | 3,029B | 44.6 | **72.3** |
| facet | 217 | 93.1 | 1,351B | 100.0 | **96.6** |
| lattice | 169 | 72.5 | 1,582B | 85.4 | **79.0** |

facet이 파일 수와 원자성에서 균형 있는 최고점.

---

### 지표 2: 검색 속도 (Retrieval Speed) — 가중치 14.29%

5개 쿼리 × 2회 반복 평균. 최속 = 100.

| view | 평균 속도 | **속도 점수** |
|------|---------|------------|
| owl | 0.066s | **65.2** |
| facet | 0.043s | **100.0** |
| lattice | 0.045s | **95.6** |

---

### 지표 3: 검색 품질 (Search Quality) — 가중치 19.05%

10개 쿼리 top-5 결과 관련도 평가 (0-100점).

| 쿼리 | owl | facet | lattice | 비고 |
|------|-----|-------|---------|------|
| Q1: orbit r4 scoring | 90 | 80 | 90 | owl/lattice: 정확 단일 히트. facet: 동점 2개 |
| Q2: nyx runtime migration | 95 | 45 | 45 | owl 압도적 — nyx-native-runtime-migration.md 정확 히트 |
| Q3: filing loop | 65 | 50 | **95** | lattice 압도적 — 전용 entry 존재. facet ALIASES 작동했으나 스코어 약함 |
| Q4: r4 four axis definition | 65 | 85 | **90** | facet/lattice 우세 — 4축 정의 원자 entry 보유 |
| Q5: aria orchestration overview | 75 | 65 | 70 | owl 약간 우세, 내러티브 문서 강점 |
| Q6: khala nyx deos relationship | **95** | 65 | 70 | owl 압도적 — discord-khala-mapping 직접 히트 |
| Q7: karpathy llm wiki | **100** | 95 | 95 | 셋 모두 우수. owl이 해당 주제 전용 summary 문서 보유 |
| Q8: what not to do with RAG | 40 | 10 | 10 | 셋 모두 약함. owl만 karpathy raw 문서 간접 히트 |
| Q9: omb cli commands list | 40 | 25 | 30 | omb CLI 자체 문서가 brain에 없음 |
| Q10: why not use graph database | 35 | 5 | 20 | 해당 결정 근거 문서 없음 |
| **평균** | **70.0** | **52.5** | **61.5** | |

**v2 동일 4쿼리 (Q1, Q3, Q7, Q8) 비교:**
- owl: (90+65+100+40)/4 = **73.8**
- lattice: (90+95+95+10)/4 = **72.5**
- facet: (80+50+95+10)/4 = **58.8**

검색 품질은 owl이 1위. v2에서 cairn이 검색 품질 2위였던 것과 달리, facet은 3위.

---

### 지표 4: Startup 비용 (Session Startup Cost) — 가중치 9.52%

LLM 세션 시작 시 진입점 파일의 유용성.

| view | 진입점 | 크기 | LLM 유용성 | **Startup 점수** |
|------|--------|------|-----------|---------------|
| owl | CLAUDE.md | 4.9KB (≈1.2K tokens) | 도구 가이드 있지만 entry 목록 없음 | **50** |
| facet | INDEX.md | 40KB (≈10K tokens) | 전체 217 entry 카탈로그 | **80** |
| lattice | MAP.md | 17.5KB (≈4.4K tokens) | 커버리지 맵 — 구조는 보이나 entry 카탈로그 아님 | **65** |

---

### 지표 5: 쓰기 처리량 (Write Throughput) — 가중치 14.29%

v2 methodology 기반 추정 (cairn과 facet은 동일 포맷).

| view | 방식 | 특성 | **처리량 점수** |
|------|------|------|-------------|
| owl | sequential compile | 파일당 5-10분, 병렬 불가 | **46.1** |
| facet | parallel-friendly atomic | cairn과 동일 포맷 → 100 유지 | **100.0** |
| lattice | parallel + edges | edge 생성 추가 비용 | **70.0** |

---

### 지표 6: 쓰기 인체공학 (Write Ergonomics) — 가중치 9.52%

| view | 스키마 복잡도 | 특수 구조 | **인체공학 점수** |
|------|------------|---------|--------------|
| owl | YAML frontmatter + 자유 본문 | 파일 유형 선택 필요 | **65** |
| facet | 고정 schema + 14 shard 분류 | ALIASES.tsv 별도 관리 | **60** |
| lattice | 고정 schema + edges YAML | content-addressed ID 생성, edge 명시 | **55** |

---

### 지표 7: Source 역추적 가능성 (Source Traceability) — 가중치 4.76%

50개 random sample 기준.

| view | 소스 참조 | **역추적 점수** |
|------|---------|------------|
| owl | 출처: 필드 | 50/50 (100%) | **100** |
| facet | source: 필드 | 50/50 (100%) | **100** |
| lattice | source: 필드 | 50/50 (100%) | **100** |

---

### 지표 8: Coverage 완전성 (Coverage Completeness) — 가중치 9.52%

| view | 커버 | 커버리지 | **Coverage 점수** |
|------|------|---------|----------------|
| owl | 233 compiled (126 raw) | 100% | **100** |
| facet | 116 unique source refs / 126 raw | ~92% | **92** |
| lattice | coverage.tsv 128/128 covered | 100% | **100** |

---

### 지표 9: Cross-query 일관성 (Cross-query Consistency) — 가중치 4.76%

"orbit r4 scoring" 개념을 3개 표현("orbit r4 scoring" / "R4 dispatch score" / "r4 priority vector")으로 질의.

| view | 1위 결과 일관성 | **일관성 점수** |
|------|-------------|-------------|
| owl | 3개 질의 → 3개 다른 파일 (1/3 일치) | **33** |
| facet | 3개 질의 → 2개 파일 (2/3 일치) | **67** |
| lattice | 3개 질의 → 동일 파일 3회 (3/3) | **100** |

lattice의 content-addressed ID가 cross-query 일관성을 완벽하게 보장.

---

### 지표 10: Update 전파 비용 (Update Propagation Cost) — 가중치 4.76%

| view | incremental | re-index | **Update 점수** |
|------|------------|---------|--------------|
| owl | 5-10분 sequential | 통합됨 | **55** |
| facet | 3-5분 parallel + `facet index` 1초 재생성 | **1초** | **95** |
| lattice | 3-5분 parallel + MANIFOLD/BLOOM 재빌드 | 수초 | **75** |

---

## 3. 종합 점수표

| 지표 | 가중치 | owl | facet | lattice |
|------|--------|-----|-------|---------|
| 1. 저장소 밀도 | 9.52% | 72.3 | **96.6** | 79.0 |
| 2. 검색 속도 | 14.29% | 65.2 | **100.0** | 95.6 |
| 3. 검색 품질 | 19.05% | **70.0** | 52.5 | 61.5 |
| 4. Startup 비용 | 9.52% | 50 | **80** | 65 |
| 5. 쓰기 처리량 | 14.29% | 46.1 | **100.0** | 70.0 |
| 6. 쓰기 인체공학 | 9.52% | **65** | 60 | 55 |
| 7. Source 역추적 | 4.76% | 100 | 100 | 100 |
| 8. Coverage 완전성 | 9.52% | **100** | 92 | **100** |
| 9. Cross-query 일관성 | 4.76% | 33 | 67 | **100** |
| 10. Update 전파 비용 | 4.76% | 55 | **95** | 75 |
| **가중 종합 점수** | **100%** | **65.6** | **82.3** | **76.9** |

**1위: facet (82.3)** / 2위: lattice (76.9) / 3위: owl (65.6)

---

## 4. 지표별 1위

| 지표 | 1위 | 점수 |
|------|-----|------|
| 저장소 밀도 | facet | 96.6 |
| 검색 속도 | facet | 100.0 |
| 검색 품질 | **owl** | 70.0 |
| Startup 비용 | facet | 80 |
| 쓰기 처리량 | facet | 100.0 |
| 쓰기 인체공학 | owl | 65 |
| Source 역추적 | 동점 | 100 |
| Coverage 완전성 | owl/lattice 동점 | 100 |
| Cross-query 일관성 | **lattice** | 100 |
| Update 전파 비용 | facet | 95 |

facet: 5개 지표 1위 / owl: 3개 지표 1위 / lattice: 1개 지표 1위

---

## 5. 세부 기여도 분석

| 지표 | owl 기여 | facet 기여 | lattice 기여 | facet−owl | lattice−owl |
|------|---------|----------|------------|---------|-----------|
| 저장소 밀도 | 6.88 | 9.20 | 7.52 | +2.32 | +0.64 |
| 검색 속도 | 9.32 | 14.29 | 13.66 | +4.97 | +4.34 |
| 검색 품질 | **13.34** | 10.00 | 11.72 | −3.34 | −1.62 |
| Startup 비용 | 4.76 | 7.62 | 6.19 | +2.86 | +1.43 |
| 쓰기 처리량 | 6.59 | **14.29** | 10.00 | +7.70 | +3.41 |
| 쓰기 인체공학 | 6.19 | 5.71 | 5.24 | −0.48 | −0.95 |
| Source 역추적 | 4.76 | 4.76 | 4.76 | 0.00 | 0.00 |
| Coverage 완전성 | 9.52 | 8.76 | 9.52 | −0.76 | 0.00 |
| Cross-query 일관성 | 1.57 | 3.19 | **4.76** | +1.62 | +3.19 |
| Update 전파 비용 | 2.62 | **4.52** | 3.57 | +1.90 | +0.95 |
| **합계** | **65.55** | **82.34** | **76.94** | **+16.79** | **+11.39** |

facet이 owl을 이기는 핵심: **쓰기 처리량 (+7.70)**, **검색 속도 (+4.97)**, **Startup 비용 (+2.86)**.  
owl이 facet을 앞서는 부분: **검색 품질 (−3.34)** — 19.05% 가중치에서 유일한 역전.

---

## 6. 서사 분석

### facet: 운영 최적화된 LLM-first brain

facet은 cairn의 진화형으로, 운영 지표 전반에서 압도적이다.  
쓰기 처리량 (100) + 검색 속도 (100) + Update 비용 (95) + Startup 비용 (80)이 결합하여 "빠르고, 가볍고, 유지보수하기 쉬운" brain으로 기능한다. 14개 shard + ALIASES.tsv가 disambiguation을 자동 처리한다.

결정적 약점은 **검색 품질 (52.5)**이다. owl 대비 -17.5점 차이는 가중치(19.05%)를 감안하면 -3.34 weighted points 손실이다. Q2(nyx migration, 45점), Q3(filing loop, 50점), Q10(graph db, 5점) 등에서 관련 없는 결과 반환이 잦다.

### lattice: 일관성의 챔피언

lattice의 content-addressed ID는 cross-query 일관성 100점을 만들어낸다. 같은 개념을 3가지 다른 표현으로 질의해도 항상 동일한 entry가 1위에 오른다. 이는 disambiguation + graph expansion의 결합이다.

검색 품질(61.5)도 facet보다 높다. graph 1-hop expansion이 결과 품질을 실제로 높이는 증거: Q3 filing loop (95점), Q4 r4 four axis (90점)에서 facet보다 40~5점 높다.

단점: 쓰기 처리량(70)과 인체공학(55)이 facet보다 낮다. typed edge 생성이 추가 비용이다.

### owl: 검색 품질 단독 1위, 운영 지표 최하위

owl은 검색 품질(70.0)에서만 1위다. 특히 narrative query (Q2 nyx migration 95점, Q5 aria overview 75점, Q6 khala deos 95점)에서 강하다. 구체적 관계와 migration 히스토리가 요약 문서에 잘 보존되어 있기 때문이다.

그러나 쓰기 처리량(46.1), 검색 속도(65.2), Startup 비용(50)이 3위다. cross-query 일관성(33)은 최하위 — 같은 개념을 다른 표현으로 물으면 전혀 다른 문서가 반환된다.

---

## 7. v2 vs v3 비교

| 항목 | v2 결과 | v3 결과 |
|------|---------|---------|
| 1위 | cairn (77.33) | facet (82.34) |
| 2위 | owl (66.81) | lattice (76.94) |
| 3위 | wiki (66.13) | owl (65.55) |

cairn → facet 진화: 77.33 → 82.34 (+5.01)  
owl은 v2와 유사 (66.81 → 65.55)  
lattice는 신규 진입 (76.94 — cairn과 owl 사이)

---

## 8. Use-case별 권고

| 사용 시나리오 | 권고 | 이유 |
|------------|------|------|
| LLM 세션 진입 시 brain 전체 조망 | **facet** | INDEX.md 217 entry 카탈로그 |
| 특정 개념의 정확한 파일 검색 | **owl** | 검색 품질 1위 (70.0) |
| 새 raw source 대량 추가 | **facet** | 처리량 1위 (100), 1초 재인덱스 |
| 동의어/변형 표현 일관 검색 | **lattice** | cross-query 일관성 100 |
| 관련 개념 연쇄 탐색 (1-hop) | **lattice** | typed graph edges |
| 인간 Obsidian browsing | **owl** | compiled doc narrative |
| migration/history 추적 | **owl** | 내러티브 요약 문서 강점 |

---

## 9. 통합 검토 문서 (`view-consolidation-review.md`) 수정 사항

benchmark-v3 실측 결과가 기존 검토 문서의 일부 주장을 수정한다:

| 항목 | 기존 주장 | 실측 결과 |
|------|---------|---------|
| owl entry 수 | 192개 | **233개** |
| ALIASES.tsv 수 | 121개 | **137줄 (헤더 2개 포함)** |
| raw source 수 | 128개 | **126개** |
| lattice 삭제 근거 | "facet이 흡수 가능" | **근거 부족 — lattice cross-query 일관성 100 > facet 67** |
| "20줄 코드로 graph 흡수" | 가능 | **틀림 — MANIFOLD+GRAPH+BLOOM+탐색 알고리즘 필요** |
| 잠정 결론: owl+facet 최선 | 직관 기반 | **benchmark 기반: facet+lattice가 운영 최적, owl은 검색 품질 보완역** |

---

## 10. 새 잠정 권고

benchmark-v3 결과 기반:

**옵션 A: facet + lattice (2-view)**
- 얻는 것: 최고 운영 효율 + cross-query 일관성 + graph expansion
- 잃는 것: owl의 검색 품질 차이 (-9점), 내러티브 문서, human browsing
- 통합 가중 점수 잠정 추정: ~82-85 (facet 베이스 + lattice graph 보완)

**옵션 B: owl + facet + lattice (3-view 유지)**
- 얻는 것: 검색 품질 owl 1위 + 운영 효율 facet + 일관성 lattice
- 비용: raw 추가 시 에이전트 3세트, 검색 결과 중복 15개

**필자 권고 → facet + lattice (2-view)**  
owl의 검색 품질 우위(+7.5점)는 가중치 19.05%에서 +1.43 weighted points.  
owl을 제거해도 facet 검색 품질(52.5)이 약점이지만, lattice가 61.5로 보완한다.  
쓰기 비용 2/3, 검색 결과 노이즈 2/3, 유지보수 2/3의 운영 절감이 owl 유지 비용을 상회한다.

단, owl의 **human browsing + Obsidian 통합**은 facet/lattice가 대체 불가. 이 기능이 필요한 동안은 3-view 유지.
