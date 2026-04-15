---
id: benchmark-v2
status: designed
created: 2026-04-12
baseline: benchmark-v1 (owl vs cairn)
scope: 3-way (owl + cairn + wiki)
---

# 3-way 벤치마크 설계 — owl vs cairn vs wiki

## 목적

동일한 61개 raw source에서 독립적으로 생성된 3개 view를 공정하게 비교하여 다음을 결정한다:

1. **메인 뷰 선택** — LLM 검색 워크플로우의 기본값으로 어떤 view를 쓸 것인가?
2. **보조 뷰 역할** — 남은 view들이 구체적으로 어떤 용도에 쓰일 것인가?
3. **동기화 규칙** — raw source 추가 시 각 view를 어떤 우선순위로 업데이트할 것인가?

v1에서는 owl과 cairn을 비교했고 cairn이 6/6 승리. 이번 v2에서는 wiki를 3자 경쟁에 포함시킨다.

---

## 전제 조건

1. **동일 source** — 3개 view 모두 `brain-vault/sources/`의 동일한 61개 파일에서 독립 생성됨
2. **view-contract 준수** — 각 view는 자신의 형식 규약을 엄격히 따름:
   - **owl:** raw/ + compiled/ (YAML frontmatter + markdown, 232개 파일)
   - **cairn:** entries/ (YAML frontmatter + ~400 token 원자적 claim, 421개 파일)
   - **wiki:** raw/ + compiled/ (plain markdown, YAML 없음, 예상 ~180-200개 파일)
3. **측정 시점** — wiki view 생성 완료 직후 (본 벤치마크 기준점)
4. **불변성** — 벤치마크 측정 중 source 추가/변경 없음 (깨끗한 비교)

---

## 측정 지표 (10개)

### v1 유지 지표 (6개)

#### 1. **저장소 밀도 (Storage density)**
**목적:** 동일한 지식을 얼마나 효율적으로 저장하는가?

**측정 방식:**
- 각 view의 총 파일 수
- 각 view의 총 저장소 크기 (KB)
- 평균 파일 크기 (B)
- 중앙값 파일 크기 (B)
- 최대 파일 크기 (B)

**측정 명령:**
```bash
# owl
find ~/owl-vault/compiled -type f -name "*.md" | wc -l
du -sh ~/owl-vault/compiled
find ~/owl-vault/compiled -type f -exec wc -c {} + | awk '{sum+=$1} END {print sum/NR}'

# cairn
find ~/cairn-vault/entries -type f -name "*.md" | wc -l
du -sh ~/cairn-vault/entries
find ~/cairn-vault/entries -type f -exec wc -c {} + | awk '{sum+=$1} END {print sum/NR}'

# wiki
find ~/brain-vault/wiki/compiled -type f -name "*.md" | wc -l
du -sh ~/brain-vault/wiki/compiled
find ~/brain-vault/wiki/compiled -type f -exec wc -c {} + | awk '{sum+=$1} END {print sum/NR}'
```

---

#### 2. **검색 응답 속도 (Retrieval speed)**
**목적:** 같은 쿼리에 대해 각 view가 얼마나 빨리 결과를 반환하는가?

**측정 방식:**
- 각 쿼리마다 3회 반복 실행, 평균 측정
- 워밍업: 첫 번째 실행은 버림 (filesystem cache 워밍)
- 단위: 초 (s)

**측정 명령:**
```bash
# owl (3회 반복)
time owl search "QUERY"
time owl search "QUERY"
time owl search "QUERY"

# cairn (3회 반복)
time cairn search "QUERY"
time cairn search "QUERY"
time cairn search "QUERY"

# wiki (grep 기반, 3회 반복)
time grep -r "QUERY" ~/brain-vault/wiki/compiled
time grep -r "QUERY" ~/brain-vault/wiki/compiled
time grep -r "QUERY" ~/brain-vault/wiki/compiled
```

**기록:** `real` 시간 only (user + sys 무시)

---

#### 3. **검색 품질 (Search quality)**
**목적:** top-5 검색 결과가 얼마나 구체적이고 다양한가?

**측정 방식:**
- 정해진 10개 쿼리(아래 참조) 각각에 대해 top-5 결과 수집
- 각 결과를 "관련도" (1-5점) + "중복도" (none/minor/major) 평가
- 평가 기준:
  - **관련도 5** = 정확히 쿼리 의도를 푼다
  - **관련도 4** = 핵심은 있지만 tangential side content 포함
  - **관련도 3** = 관련 있지만 다른 주제와 혼재
  - **관련도 1-2** = 거의 무관
  - **중복도 major** = 같은 정보가 top-5 안에 2회 이상 반복
  - **중복도 minor** = 약간의 정보 중복 (예: 같은 fact의 다른 각도)

**평가 대상:** 각 view의 top-5 결과 set에서:
- 관련도 합계 (max 25)
- 중복도 점수 (-3점 major per instance, -1점 minor per instance)

---

#### 4. **세션 startup 비용 (Session startup cost)**
**목적:** LLM이 새 세션을 시작할 때 각 view의 진입점이 얼마나 효율적인가?

**측정 방식:**
- 각 view의 기본 진입점 파일 크기
- LLM이 session context에 로드하기에 적당한가?
- 파일이 vault 전체 내용을 대표하는가?

**측정 대상:**
- **owl:** CLAUDE.md (프로젝트 레벨) + owl/AGENTS.md (있다면)
- **cairn:** INDEX.md (auto-generated, 421개 entry 목록)
- **wiki:** 진입점 파일 (생성 후 결정, 아마 README.md 또는 index.md)

**측정 명령:**
```bash
wc -l ~/owl-vault/AGENTS.md  # if exists
wc -l ~/.claude/projects/oh-my-brain/CLAUDE.md

wc -l ~/cairn-vault/INDEX.md

wc -l ~/brain-vault/wiki/README.md  # or similar
```

**평가 기준:**
- session context (4K 토큰 = ~3200 단어)에 로드 가능한가?
- 진입점만으로 vault 내용이 충분히 visible한가?

---

#### 5. **쓰기 처리량 (Write throughput)**
**목적:** 새로운 raw source 추가 시 각 view를 업데이트하는 데 걸리는 시간?

**측정 방식:**
- **가상 시나리오:** 새로운 raw source 10개 추가
- 각 view마다 이를 처리하는 데 걸리는 예상 시간 기록
- 측정 기반:
  - owl: 기존 v1 migration 데이터 (244+193 entries, 70분 total)로부터 per-file 시간 계산
  - cairn: 기존 parallel migration 데이터로부터 per-wave 시간 계산
  - wiki: v0부터의 sequential compile 데이터 (있다면) 또는 예상

**기록 항목:**
- Sequential 처리 시간 (1 agent, 10 files)
- Parallel 처리 시간 (N agents)
- Full re-index 시간 (있다면)

---

#### 6. **쓰기 인체공학 (Write ergonomics)**
**목적:** LLM 또는 human이 새 지식을 각 format으로 추가하기 얼마나 쉬운가?

**측정 방식:**
- 정성적 평가 기반 (quantitative가 아님)
- 각 view의 작성 규약 체크:
  - 포맷 일관성: 부분적/일관성 있음/엄격
  - 필드 수: 최소/중간/많음
  - LLM 자유도: 제약 많음/중간/자유로움
  - 검증 난이도: 쉬움/중간/어려움

**평가 기준:**
- **owl:** 2-3개 mandatory frontmatter 필드 + 자유로운 본문
- **cairn:** 고정 frontmatter + 400 token 상한 + 타입 분류 (fact/claim/...)
- **wiki:** Karpathy spec (구체 사항은 wiki view 스펙 참고)

---

### v2 신규 지표 (4개)

#### 7. **Source 역추적 가능성 (Source traceability)**
**목적:** 특정 claim이나 파일이 어느 raw source에서 왔는지 추적할 수 있는가?

**측정 방식:**
- 각 view의 entry/file에서 raw source 참조 형식 확인
- backward link의 명확성 평가 (1-5점):
  1. 참조 없음 (불가능)
  2. 참조는 있지만 모호함 (예: "raw/aria")
  3. 구체적이지만 자동 링크 아님 (예: "raw/aria/orbit.md")
  4. 구체적이고 자동 verify 가능 (예: wikilink)
  5. 양방향 link (raw → compiled 도 추적 가능)

**측정 대상:**
- 각 view의 200개 random entry/file에서 raw source 참조 명확도 샘플

**평가 쿼리:**
```bash
# owl
grep -h "source\|raw\|reference" ~/owl-vault/compiled/**/*.md | head -20

# cairn
grep -h "source\|raw\|reference" ~/cairn-vault/entries/**/*.md | head -20

# wiki
grep -h "source\|raw\|reference" ~/brain-vault/wiki/compiled/**/*.md | head -20
```

---

#### 8. **Coverage 완전성 (Coverage completeness)**
**목적:** 각 view가 raw source의 몇 %를 실제로 cover하는가?

**측정 방식:**
- raw source 61개 파일 각각에 대해 "포함 여부" 체크
- 포함 기준:
  - **완전 포함** (100%): 원본 내용이 충분히 요약/변환되어 view에 있음
  - **부분 포함** (50%): 일부만 포함되거나 간단히 언급됨
  - **미포함** (0%): view에서 찾을 수 없음

**측정 대상:** 61개 raw source 파일 전수

**기록:**
- 각 view별 완전 포함 파일 수 / 부분 포함 수 / 미포함 수
- 커버리지 % = (완전 포함 + 부분 포함 × 0.5) / 61 × 100

**예시:**
```
v1 결과 (owl vs cairn):
owl: 232/232 compiled files, 61/61 raw covered = 100% (but distributed)
cairn: 421 entries, 61/61 raw covered = 100% (but atomized)
```

---

#### 9. **Cross-query 일관성 (Cross-query consistency)**
**목적:** 같은 개념을 다른 표현으로 물었을 때 일관된 결과를 주는가?

**측정 방식:**
- 같은 개념에 대한 3가지 query variant (예: "orbit r4", "R4 scoring", "r4-dispatch-score")
- 각 query마다 top-1 결과의 id/filename 기록
- 일관성 점수:
  - 3/3 동일한 결과 = 5점
  - 2/3 동일 = 3점
  - 모두 다름 = 1점

**측정 쿼리셋:** 아래 10개 쿼리셋 中 각 3-variant 생성

**기록:** 각 view별 평균 일관성 점수 (1-5)

---

#### 10. **Update 전파 비용 (Update propagation cost)**
**목적:** raw source 1개 추가 시 각 view를 갱신하는 데 걸리는 incremental cost?

**측정 방식:**
- **기준점:** 현재 상태 (owl + cairn + wiki, 각각 61개 raw에서 생성 완료)
- **가상 시나리오:** 새로운 raw source 1개 추가 (예: 새 orbit 문서)
- 각 view의 incremental update 비용 측정:

**owl:**
- 새 raw 파일 → compiled docs 생성 (컴파일러 실행)
- 영향 범위: 해당 topic의 summary/index 등 1-3개 doc 재작성
- 예상 시간: 5-10분 (sequential)

**cairn:**
- 새 raw 파일 → 2-4개 atomic entry 생성 (병렬 가능)
- 영향 범위: INDEX.md 1회 재생성
- 예상 시간: 3-5분 (N agents parallel) + INDEX regen 1분

**wiki:**
- 새 raw 파일 → compiled doc 생성 (Karpathy compile loop)
- 영향 범위: 해당 topic의 index 1-2개 수동 update
- 예상 시간: 5-15분 (sequential + manual)

**기록:**
```
| view | incremental time (1 raw) | re-index time | total |
|---|---|---|---|
| owl | 5-10m | integrated | 5-10m |
| cairn | 3-5m | 1m | 4-6m |
| wiki | 5-15m | 5-10m | 10-25m |
```

---

## 쿼리셋 (10개)

각 쿼리는 다음 정보를 포함:

- **ID** — 쿼리 번호
- **Query** — 검색 문구
- **Intent** — 무엇을 찾으려고 하는가? (평가자가 "정답"을 알기 위함)
- **Domain** — 어느 domain인가? (여러 domain 균형 확보)
- **Expected top-1** — 이상적인 결과 (view마다 다를 수 있음)

### Q1: 원자 개념 검색
- **Query:** "orbit r4 scoring"
- **Intent:** Orbit R4 scoring의 추상 모델과 concrete formula 찾기
- **Domain:** ORBIT scheduling
- **Expected:**
  - owl: `orbit-r4-scoring-concept.md` (또는 관련 compiled doc)
  - cairn: `r4-scoring-abstraction` entry
  - wiki: 가장 atomic한 R4 scoring 섹션

---

### Q2: 시스템 변경 추적
- **Query:** "nyx runtime migration"
- **Intent:** Nyx runtime이 제거되었는지, 재설계되었는지, 아니면 rename되었는지 파악
- **Domain:** Runtime infrastructure
- **Expected:**
  - owl: `nyx-migration-*.md` compiled doc
  - cairn: `nyx-not-removal-but-reframe` (anti-misreading claim) 또는 `nyx-routing-*`
  - wiki: Nyx 섹션의 마이그레이션 노트

---

### Q3: 절차적 지식 검색
- **Query:** "filing loop implementation"
- **Intent:** Karpathy's filing loop를 자신의 knowledge system에 적용하는 방법
- **Domain:** Knowledge ops
- **Expected:**
  - owl: `owl-filing-loop*.md` 또는 유사 compiled doc
  - cairn: 여러 atomic entries (`filing-loop-step-*`, etc.)
  - wiki: 구체 step-by-step instructions

---

### Q4: 구체적 데이터 구조
- **Query:** "r4 four axis definition"
- **Intent:** Orbit R4의 P = (p_luca, p_lord, p_internal, p_depth) vector의 정확한 정의
- **Domain:** ORBIT data model
- **Expected:**
  - owl: R4 definition 관련 doc
  - cairn: `orbit-aria-r4-four-axis-definition` entry
  - wiki: R4 정의 섹션

---

### Q5: 아키텍처 개요
- **Query:** "aria orchestration overview"
- **Intent:** ARIA 시스템의 전체 구조와 component 간 관계
- **Domain:** System architecture
- **Expected:**
  - owl: `aria-architecture/ARIA.md` 또는 유사 overview doc
  - cairn: 여러 ARIA-관련 atomic entries의 조합
  - wiki: ARIA overview 섹션

---

### Q6: 개념 간 관계
- **Query:** "khala nyx deos relationship"
- **Intent:** Khala, Nyx, Deos 간의 상호작용과 책임 분리
- **Domain:** System architecture
- **Expected:**
  - owl: `aria-architecture/khala-*.md`, `deos-*.md` 등 여러 doc
  - cairn: 개별 entries + cross-references
  - wiki: 각 component 섹션

---

### Q7: 작은 세부사항
- **Query:** "startup hooks initialization order"
- **Intent:** 시스템 startup 시 hooks가 어떤 순서로 실행되는가?
- **Domain:** Runtime initialization
- **Expected:**
  - owl: `hooks-*.md` 또는 `runtime-initialization.md`
  - cairn: `startup-hooks-*` atomic entries
  - wiki: startup 섹션의 hooks 부분

---

### Q8: 반대 주장 / Anti-pattern
- **Query:** "what not to do with RAG"
- **Intent:** RAG 사용할 때 피해야 할 안티패턴 (Karpathy 철학)
- **Domain:** Knowledge management principles
- **Expected:**
  - owl: karpathy-related compiled doc 또는 caveats section
  - cairn: 여러 `anti-rag-*` entries
  - wiki: pitfalls/anti-patterns 섹션

---

### Q9: 도구 사용법
- **Query:** "omb cli commands list"
- **Intent:** omb CLI의 모든 available commands 목록과 간단한 설명
- **Domain:** Tools & operations
- **Expected:**
  - owl: `omb-cli-reference.md` 또는 commands 목록
  - cairn: 여러 `omb-command-*` entries
  - wiki: omb 섹션 또는 commands index

---

### Q10: 의사결정 기록
- **Query:** "why not use graph database for brain"
- **Intent:** graph DB 대신 file-based vault를 선택한 이유와 trade-off
- **Domain:** Architecture decisions
- **Expected:**
  - owl: decision note 또는 rationale doc
  - cairn: `decision-graph-db-rejected` entry + 근거들
  - wiki: rationale 섹션

---

## 측정 프로토콜

### Phase 1: 준비 (측정 전)

1. **저장소 정리**
   ```bash
   rm -rf ~/.cache/owl ~/.cache/cairn ~/.cache/wiki  # if any
   sync  # filesystem sync
   ```

2. **Wiki view 생성 완료 확인**
   - wiki/compiled/ 디렉토리 존재 확인
   - 파일 개수 확인

3. **baseline 기록**
   - 각 view의 현재 상태 스냅샷 (파일 수, 크기, INDEX 상태)

### Phase 2: 지표 1-6 측정 (v1 지표)

1. **저장소 밀도 (지표 1)**
   - 위의 "측정 명령" 실행, 결과 표로 정리

2. **검색 응답 속도 (지표 2)**
   - filesystem cache 비우기: `sudo purge` (macOS)
   - 각 쿼리 Q1-Q10에 대해 3회 반복
   - 결과: 쿼리별 평균 시간 + 뷰별 전체 평균

3. **검색 품질 (지표 3)**
   - 각 쿼리 Q1-Q10의 top-5 결과 수집
   - 평가자(사용자)가 1-5점 + 중복도 평가
   - 결과: 쿼리별 점수 + 뷰별 평균

4. **Startup 비용 (지표 4)**
   - 진입점 파일 크기 측정
   - LLM session context 호환성 평가

5. **쓰기 처리량 (지표 5)**
   - 기존 데이터 (v1 migration) 재분석 + wiki estimate
   - 표 정리

6. **쓰기 인체공학 (지표 6)**
   - 각 view의 format spec 정리
   - 정성적 평가 기록

### Phase 3: 지표 7-10 측정 (v2 신규 지표)

7. **Source 역추적 가능성 (지표 7)**
   - 각 view에서 200개 random entry 샘플
   - raw source 참조 명확도 1-5점 평가
   - 평균 점수 계산

8. **Coverage 완전성 (지표 8)**
   - 61개 raw 파일 전수 체크
   - 각 view별 완전/부분/미포함 분류
   - 커버리지 % 계산

9. **Cross-query 일관성 (지표 9)**
   - 10개 쿼리 각각에 3-variant 생성
   - top-1 결과의 일관성 점수 (1-5)
   - 뷰별 평균

10. **Update 전파 비용 (지표 10)**
    - 기존 migration 데이터 기반 estimate
    - 각 view의 incremental + re-index 시간 표 정리

### Phase 4: 통합 분석

- 10개 지표 모두 표로 정리
- 뷰별 종합 점수 계산 (가중치 적용)
- narrative 작성: 각 뷰의 강점/약점 분석

---

## 평가 기준

### Scoring: 정규화 (0-100점)

각 지표를 100점 기준으로 정규화:

| 지표 | 가중치 | 계산 방식 |
|---|---|---|
| 1. 저장소 밀도 | 10% | best view = 100, 다른 뷰는 (best_size / this_size) × 100 |
| 2. 검색 속도 | 15% | fastest = 100, 다른 뷰는 (fastest_time / this_time) × 100 |
| 3. 검색 품질 | 20% | highest quality score = 100, 비례 배분 |
| 4. Startup 비용 | 10% | smallest entry point = 100, 비례 배분 |
| 5. 쓰기 처리량 | 15% | fastest update = 100, 비례 배분 |
| 6. 쓰기 인체공학 | 10% | qualitative, 정성 평가 후 점수 할당 |
| 7. Source 역추적 | 5% | 1-5점 평가 × 20 = 0-100 |
| 8. Coverage 완전성 | 10% | coverage % (0-100) |
| 9. Cross-query 일관성 | 5% | 1-5점 평가 × 20 = 0-100 |
| 10. Update 전파 비용 | 5% | fastest = 100, 역비례 |

### 승/패 판정

1. **최종 종합 점수** (가중평균) 기준 rank 1-3 결정
2. **지표별 승리** — 각 지표에서 1위 view 기록
3. **use-case별 winner** — 특정 workload (LLM 검색, human browsing, parallel writes 등)에 최적 view

### 동점 처리

가중치 재조정: 
- 20% 이상 차이 = 명확한 승자
- 10-20% 차이 = 약한 승자
- 10% 미만 = 동등, 다른 기준 (maintenance burden, ops cost 등)으로 결정

---

## 예상 결과 가설

### owl 예상 프로필

**강점:**
- Obsidian 통합 → human browsing 최고
- Compiled doc의 context 풍부성 → 검색 quality 높음
- 6주간의 ops infrastructure → startup 안정성

**약점:**
- 파일당 3KB 평균 → 저장소 밀도 낮음
- Sequential compile loop → 쓰기 처리량 낮음
- Raw + compiled 이중 관리 → update propagation 복잡

**예상 점수:** 65-75/100

---

### cairn 예상 프로필

**강점:**
- 421 entries의 높은 granularity → coverage 높고 일관성 좋음
- INDEX.md → LLM session startup 최고
- Parallel-friendly format → 쓰기 처리량 최고
- Atomic claims → cross-query 일관성 최고

**약점:**
- Grep-style search 밖에 없음 → 검색 UI 약함
- 중복 위험 (semantic duplicates) → 유지보수 비용
- No human GUI → human browsing 안 됨

**예상 점수:** 75-85/100

---

### wiki 예상 프로필

**강점:**
- Pure Karpathy spec → 철학적 일관성
- No tooling overhead → 유지보수 간단
- Plain markdown → 이식성 높음

**약점:**
- Grep only → 검색 속도/품질 낮음
- Manual index 관리 → update propagation 복잡
- Filing loop overhead → 쓰기 처리량 낮음
- No INDEX.md 같은 session entry point

**예상 점수:** 55-65/100

---

### 전체 예상 순위

1. **cairn** (75-85/100) — LLM-facing brain으로 최적
2. **owl** (65-75/100) — hybrid role (human + LLM)
3. **wiki** (55-65/100) — control group, 철학 검증용

---

## 결론 프레임워크

벤치마크 완료 후 다음을 판정한다:

1. **메인 뷰** — 점수 1위 view를 default로 설정
2. **보조 역할** — 각 view를 특정 용도에 배치:
   - LLM-first queries → cairn
   - Human visual browsing → owl
   - Philosophy control group → wiki
3. **동기화 규칙** — new raw 추가 시 어느 순서로 update 할 것인가?
4. **실험 계획** — v3 이후 개선 지점 (예: wiki에 rudimentary INDEX.md 추가? owl의 parallel compile?)

---

## Appendix: 측정 자동화

다음 스크립트를 사용하여 측정 자동화 가능:

```bash
#!/bin/bash
# benchmark-v2-runner.sh

RESULTS_DIR="./benchmark-v2-results"
mkdir -p "$RESULTS_DIR"

# 1. 저장소 밀도
echo "=== Storage Density ===" > "$RESULTS_DIR/density.txt"
for view in owl cairn wiki; do
    echo "View: $view" >> "$RESULTS_DIR/density.txt"
    find ~/$view-vault -type f -name "*.md" | wc -l >> "$RESULTS_DIR/density.txt"
    du -sh ~/$view-vault >> "$RESULTS_DIR/density.txt"
done

# 2. 검색 속도 (sample)
echo "=== Retrieval Speed ===" > "$RESULTS_DIR/speed.txt"
for query in "orbit r4 scoring" "nyx runtime migration"; do
    echo "Query: $query" >> "$RESULTS_DIR/speed.txt"
    for view in owl cairn; do
        echo "  $view:" >> "$RESULTS_DIR/speed.txt"
        for i in {1..3}; do
            time $view search "$query" 2>&1 | grep real >> "$RESULTS_DIR/speed.txt"
        done
    done
done

echo "Measurements complete. Results in $RESULTS_DIR/"
```

실제 벤치마크 수행 시 이 스크립트를 개선하여 사용.
