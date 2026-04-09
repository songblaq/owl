# Phase L2 + N Report — 2026-04-08

작성일: 2026-04-08
상태: v0 (완료)
선행: `plans/phase-l1-compile-report-2026-04-08-v0.md`

## 0. 결과

### Phase N (완료)
- **30 reports 에 `outputs-exempt: true` 추가** (옛 brain-era 텍스트-only 분석 reports)
- `src/owl/health.py` 에 `is_outputs_exempt()` 함수 + `check_report_outputs()` 에 exempt 체크
- `docs/health-check-spec-v0.md` §2.5.1 추가
- **Phase N 후 report-missing-output-links: 30 → 0**

### Phase L2 (완료)
- **63 compiled docs 의 missing headers 수정** via 5 parallel owl-librarian tasks
- 5 batches × 12-13 files each
- 각 batch 가 각 파일 read → 미싱 헤더 식별 → 추론 값으로 헤더 삽입
- **Phase L2 후 missing-required-headers: 63 → 0**

## 1. Phase N 실행 내역

Python 스크립트로 30 reports 에 `outputs-exempt: true` 를 `관련 항목:` 다음 줄에 삽입. 30/30 성공.

## 2. Phase L2 실행 내역

### Batch 분포

| Batch | Files | 특징 |
|---|---|---|
| 1 | 13 | agent-brain note + openclaw concepts + aria-architecture/* 다수 |
| 2 | 13 | karpathy + doc-first + aria-architecture gui/orbit/routing |
| 3 | 13 | deos narrow-path + openclaw-kb + plaza/runtime/equation-first |
| 4 | 12 | songdori + deos phase-a + aria-architecture m2/cron/progress |
| 5 | 12 | agent-cli doc-first summary + deos real-api + aria-architecture migration |

### 추론 규칙 (각 owl-librarian task 에 embed)

- **상태**: always `compiled`
- **유형**: filename suffix (-summary/-note/-report/-concept/-index), no suffix → content-based judgment
- **출처**: matching raw path or `내부 작성`
- **작성일**: filename date or body date or `2026-04-08`
- **관련 항목**: 3-5 concept terms from content

### 주요 ambiguity 해결

- `aria-architecture/*` 파일들은 raw 매치 거의 없어 대부분 `출처: 내부 작성`
- 날짜 미상 파일들은 `2026-04-08` default
- 일부 note vs concept vs report 구분 owl-librarian 판단 (명확한 경우는 filename, 애매하면 content 읽고 결정)

## 3. Health Delta 전체

| 지표 | L1 후 | Phase N 후 | Phase L2 후 (final) |
|---|---|---|---|
| **total** | 244 | 214 | 195 |
| **high** | 0 | 0 | 0 |
| medium | 95 | 65 | **21** |
| low | 149 | 149 | 174 |
| **missing-required-headers** | 63 | 63 | **0** ✓ |
| **report-missing-output-links** | 30 | **0** | 19 (secondary) |
| weak-backlinks | 109 | 109 | 132 |
| concept-candidate-missing | 21 | 21 | 23 |

## 4. Secondary effect 설명

Phase L2 에서 일부 파일의 `유형:` 을 `report` 로 새로 분류했고, 이들이 `outputs-exempt: true` 가 없는 상태. 결과:
- **report-missing-output-links: 0 → 19**
- **weak-backlinks: 109 → 132** (+23: 새로 summary/report 로 분류된 파일들)

이건 regression 이 아니라 **정확한 분류**. 새 classification 이 drive 한 결과. 다음 세션에서 이 19 개도 exempt 마킹 or 개별 review.

## 5. 오늘 (2026-04-08) 전체 세션 progression

| Checkpoint | total | high | notable |
|---|---|---|---|
| 세션 시작 (v0.1.0) | 292 | 84 | 84 missing-summary |
| Phase K 후 | 235 | 21 | atlas 58 제외 |
| Phase L1 후 | 244 | **0** | 22 compile 완료 |
| Phase N 후 | 214 | 0 | 30 reports exempt |
| **Phase L2 후 (final)** | **195** | **0** | 63 headers fixed |

**Net: -97 issues, high 84 → 0** 오늘 하루 진행.

## 6. 남은 작업

- **132 weak-backlinks**: 가장 큰 batch, 2-3 세션 (owl-librarian 의 가장 무거운 일)
- **19 new report-missing-output-links**: exempt 추가 or 개별 review (secondary from L2)
- **23 concept-candidate-missing**: promotion 판단 (owl-librarian)
- **18 stale-index-link-density**: index 보강 (owl-librarian)
- **2 orphan-concept**: 사용자 review
- **1 index-candidate-missing**: promotion
- 가능하면 **v0.1.1 또는 v0.2.0 patch release**

## 7. 커밋 포함물

이 세션의 commits (post-v0.1.0):
- `9116590` phase K: atlas exclusion + reference index
- `d23a08a` phase L1: 22 raws compile
- `2a4fceb` phase N: outputs-exempt policy + 30 reports
- (pending) phase L2: 63 headers + this report
