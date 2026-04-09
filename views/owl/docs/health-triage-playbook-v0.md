# owl Health Triage Playbook v0

작성일: 2026-04-08
상태: v0

## 0. 목적

owl health 가 발견하는 issue 들을 *어떻게 분류하고 누구에게 위임하고 어떤 순서로 처리할지* 의 단일 진실. 이 문서는 owl-health 서브에이전트와 사람 둘 다 사용한다.

## 1. 룰별 fix 전략 매트릭스

| 룰 | Severity | 의미 | Fix 유형 | 위임 대상 | Batch 가능? |
|---|---|---|---|---|---|
| **missing-summary-for-raw** | high | raw 파일에 대응 summary 없음 | LLM compile (1당 한 번) | owl-compiler | ★ batch (분위 유사 raw 묶음) |
| **report-broken-output-link** | high | report 가 가리키는 outputs/ 파일 없음 | Read+Edit (link fix or 파일 생성) | owl-librarian | △ 개별 |
| **missing-required-headers** *(2026-04-08 추가)* | medium | compiled doc 가 5개 필수 헤더 (상태/유형/출처/작성일/관련 항목) 중 1개 이상 누락 | Read+Edit (헤더 추가) | owl-librarian | ★ batch (동일 패턴 다수) |
| **report-missing-output-links** | medium | report 가 outputs/ 참조 없음 | review (output 만들어야? 면제?) | 사용자 + owl-librarian | △ 개별 |
| **orphan-concept** | medium | concept 가 다른 문서에서 link 0 | review (link 추가 or 삭제) | 사용자 | △ 개별 |
| **concept-candidate-missing** | low | 2+ summary 가 같은 term 참조 but concept 없음 | promotion (LLM 판단) | owl-librarian | △ 개별 |
| **index-candidate-missing** | low | 3+ compiled doc 가 같은 subject but index 없음 | promotion | owl-librarian | △ 개별 |
| **stale-index-link-density** | low | index 가 <3 docs 만 link | review (확장 or 삭제) | owl-librarian | △ 개별 |
| **weak-backlinks** | low | summary/report 에 cross-link 0 | Read+Edit (관련 doc link 추가) | owl-librarian | ★ batch |

## 2. 우선순위 알고리즘 (severity × 비용)

**Phase A — Atomic high fixes** (1 issue 당 1-5 분):
- `report-broken-output-link` 의 atomic 사례 (link 1개 fix)
- 비용 낮음, 영향 큼 → 최우선

**Phase B — Batch low fixes** (5-10 분에 5-10 issue):
- `weak-backlinks`: 같은 패턴의 doc 묶어서 batch
- `concept-candidate-missing`: 비슷한 후보 묶어서 promotion 결정

**Phase C — Heavy compile work** (1 issue 당 5-15 분, 누적시 ~hours):
- `missing-summary-for-raw`: 84 raw 파일 하나씩 컴파일
- 별도 세션 권장. owl-compiler 서브에이전트에 위임. 우선순위는 raw 의 *주제 카테고리* 기준 (예: openclaw 관련 먼저).

**Phase D — Interpretive review** (사용자 결정 필요):
- `orphan-concept`: 정말 orphan 인지 / 삭제할지
- `stale-compiled-newer-raw`: raw 가 변경됐는데 compiled 는 옛 상태 → 재컴파일?
- `report-missing-output-links`: output 만들어야? 면제?

## 3. 알려진 함정 (False Positives)

### 3.1 Code-block literal 이 link 로 오인됨

**증상**: `report-broken-output-link` 가 raise 되지만 실제로 broken link 가 아님. 코드 블록 (```...```) 안에 `outputs/...` 같은 literal 이 있고, owl health regex 가 그것을 *진짜 link* 로 잘못 매칭.

**예 (2026-04-08 발견)**:
- File: `compiled/2026-04-04-brain-health-check-full-report.md`
- Line: ` :: report has no outputs/* links` (code block 안, 옛 brain_health_check.py 출력 인용)
- 결과: regex `outputs/[^\s\`)]+` 가 `outputs/*` literal 매칭 → false positive

**즉시 대응**: doc 의 literal 을 dodge 형태로 rephrase (예: `outputs/* links` → `output references`)

**근본 fix (TODO)**: `src/owl/health.py` 의 `extract_output_links` / `extract_link_targets` 가 markdown code block (``` 또는 indented) 를 스킵하도록 개선

### 3.2 "Fix" 가 다른 issue 로 변신

**증상**: high issue 1개 fix → medium 1개 새로 생김. Total 변동 0.

**의미**: false positive 가 제거되면서 *진짜* issue 가 드러나는 정상 동작. 이건 *fix 가 fail* 한 게 아니라 *분류 정확도가 향상* 된 것.

**대응**: 새로 드러난 medium 을 다음 batch 에 묶음.

**예 (2026-04-08)**:
- Before: 1 high (false broken-output-link) + 0 medium
- After: 0 high + 1 medium (true missing-output-links)
- Net total: 변동 없음, 하지만 *정확한 분류*

## 4. 84 missing-summary-for-raw 처리 전략 (별도 세션)

이번 세션에서는 *처리 안 함*. 84 raw 파일을 컴파일하려면:

### 4.1 Pre-flight
1. `owl health --json` 으로 raw 파일 path 84개 추출
2. raw 의 주제별 grouping (예: openclaw / deos / smart-gym / atlas / 기타)
3. 각 그룹의 priority 결정 (사용자 의도 기준)

### 4.2 Batch 처리
1. 그룹 1개씩 처리 (10-20 raw 가 1 batch)
2. 각 raw 마다:
   - `owl compile <raw-path>` 로 metadata 받음
   - `summary_exists: false` 확인
   - owl-compiler Task tool 호출 → summary 작성
   - `관련 항목:` cross-reference 추가
3. batch 끝나면 `owl health` 재실행, missing-summary count 줄어드는지 확인

### 4.3 안전장치
- 한 batch 가 끝날 때마다 `git status` (project repo 는 안 변하지만 vault 는 점검)
- compiled doc 의 `상태:`, `유형:`, `출처:`, `작성일:`, `관련 항목:` 헤더 누락 확인 → owl health 재실행
- batch 1-2개 후 사용자에게 sample review 요청

### 4.4 추정 시간
- 84 raw × 5분 = ~7 hours pure work (batch 처리)
- 실제로는 raw 길이/복잡도 차이로 2-12 hours 범위
- 별도 세션 (Claude Code 또는 owl-compiler 서브에이전트 batch run)

## 5. 이번 세션 (2026-04-08) 결과

### 5.1 오후 1차 (atomic fix)
- Atomic fix: 1 high `report-broken-output-link` 제거 (false positive)
- 부산물: 1 medium 새로 분류됨 (true positive 노출)
- 총 issue: 131 → 131 (변동 0, 분류 정확도 ↑)
- Playbook v0 작성

### 5.2 오후 2차 (health.py 코드 개선)
- `strip_code_blocks` helper 추가 → `extract_output_links` / `extract_brain_links` 가 code block 안의 literal 을 link 로 오인하던 버그 fix
- 신규 룰 `check_required_headers` → `missing-required-headers` (5개 필수 헤더 검증)
- Delegate 매핑에 새 룰 추가

### 5.3 코드 개선의 *반대* 효과

| 룰 | Before | After | 변동 이유 |
|---|---|---|---|
| missing-summary-for-raw | 84 | 84 | 영향 없음 (raw↔compiled 체크는 regex 비사용) |
| **missing-required-headers** | N/A | **63** | 신규 룰, 전부 true positive |
| report-missing-output-links | 10 | **30** | 이전 false negative 노출 (code-block 안의 `outputs/...` 가 "참조 있음" 으로 잘못 카운트됐음) |
| weak-backlinks | 17 | **82** | 이전 false negative 노출 (code-block 안의 `compiled/...` literal 이 cross-link 으로 잘못 카운트) |
| stale-index-link-density | 3 | **17** | 같은 이유 |
| orphan-concept | 2 | 2 | 영향 없음 |
| concept-candidate-missing | 13 | 13 | 영향 없음 |
| index-candidate-missing | 1 | 1 | 영향 없음 |
| **total** | **131** | **292** | **+161 (대부분 이전에 숨겨진 true positive)** |

**진실**: 숫자 증가 = regression 아님. 오히려 *분류 정확도 대폭 향상*. 이전 131 은 false-positive / false-negative 가 섞인 상태였고, 새 292 는 더 정확한 그림. §3.2 "fix 가 다른 issue 로 변신" 패턴의 극단적 버전 — 이번엔 1→1 이 아니라 0→65 같은 규모.

**영향**: `owl health --json` 으로 분류해 batch 처리할 때, `weak-backlinks` 가 이제 17 → 82 이지만 그만큼 **진짜 누락된 cross-link 이 드러난 것**. 한 번에 batch 처리하면 됨 (원래 fix 전략과 동일).

## 6. 장기 권장 (별도 PR/commit)

### 6.1 health.py 코드 개선

- markdown code block 인식 → 그 안의 link literal 무시
- `outputs/*` 같은 wildcard literal 는 무시
- `severity_distribution` 변동을 알리는 delta 출력

### 6.2 새 health rule 후보

- `missing-required-headers`: compiled doc 에 `상태:`, `유형:`, `출처:` 등 누락
- `dangling-link-in-raw`: raw 에 broken link (raw 는 immutable 이므로 warning only)
- `outdated-cross-reference`: 옛 path (`agents/brain` 등) 가 본문에 남아 있음

### 6.3 자동화 후보

- SessionStart hook 에서 `owl health --json` 자동 실행 → high ≥ N 시 사용자 알림
- nightly cron 으로 owl-compiler 가 missing-summary 자동 처리
