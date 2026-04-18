---
id: bench-design-2026-04-18
status: draft
created: 2026-04-18
supersedes: docs/bench-2026-04-17-rc1.md (pre-Re:Zero)
---

# omb 자체 벤치 설계 (v0 draft)

## 목적

ussumant/llm-wiki-compiler 가 "LLM-wiki 구현체 중 유일한 real benchmark" 라 주장. omb 도 자체 벤치로 **(a) 다른 구현체 비교, (b) owl/cairn/wiki 3-view 내부 실험** 이 가능해야 함 (→ [[syntheses/llm-wiki-comparison]] Phase 4 결정).

## 축 (3 항목만)

Karpathy 원안 너머 tier 쌓지 않는다 (→ memory `feedback_design_humility`). 최소 측정:

| # | 지표 | 측정 방법 | 목표 |
|---|---|---|---|
| 1 | **Retrieval cost** | query N회 실행 시 `omb search` 이 읽는 총 파일 수 + 토큰 수 | 낮을수록 좋음 |
| 2 | **Write efficiency** | raw 1개 ingest 시 LLM 이 생성·수정한 페이지 수 + 토큰 수 | 적절히 incremental (너무 적으면 cross-ref 부족, 너무 많으면 낭비) |
| 3 | **Query quality** | 고정 Q&A 셋에 대한 답변 정확도 (수동 scoring, 맹검 5점) | 높을수록 좋음 |

## 데이터셋

- **Gold Q&A 50 문항** — Luca 의 실제 지식베이스 질의 로그 / 수동 선별
  - 카테고리: HomeLab infra (10) / 프로젝트 (15) / 설계 패턴 (10) / 드리프트 이력 (10) / 메타 (5)
- **Ingest corpus** — `~/omb/input/` 에서 샘플 20 raw (사용된 적 없는 것 순으로 고정)
- **Evaluation set** — 샘플 20 raw 가 wiki 에 이미 ingested 된 이후 상태로 평가

## 절차

```
1. snapshot  → vault 백업 (~/omb/brain/live.snapshot-<tag>/)
2. baseline  → 50 문항 × N 구현체 = 답변 세트
3. compute   → axis 1,2,3 별 수치
4. report    → docs/bench-result-<tag>.md
```

## 비교 대상 (2026-04-18 기준)

| 타겟 | 설치 위치 | 비고 |
|---|---|---|
| **omb (wiki MAIN)** | `~/omb/brain/live/` | 현재 시스템 |
| akasha (INACTIVE) | `~/omb/bench/akasha/` | 이미 보존 — 백업 대조 가능 |
| ussumant/llm-wiki-compiler | `/tmp/bench/ussumant/` (설치 필요) | Claude Code plugin |
| nashsu/llm_wiki | `/tmp/bench/nashsu/` (설치 필요) | 680★ 데스크톱 앱 |
| Ar9av/obsidian-wiki | `/tmp/bench/ar9av/` (설치 필요) | 3-layer 명시적 구현 |

선택적: coleam00/claude-memory-compiler (session hook 기반, 다른 축).

## Axis 1 측정 세부 (retrieval cost)

```bash
# 개조 omb search 가 파일 read 수 + 바이트를 JSON 으로 반환
omb search "<q>" --bench-json
# 출력: {"files_read": N, "bytes": M, "duration_ms": T}
```

→ tool 변경 필요: `vault/omb/src/omb/wiki_ops.py` 에 `--bench-json` 플래그 추가 (50 라인 내외).

## Axis 2 측정 세부 (write efficiency)

```bash
# raw 파일 1개 drop → LLM ingest 완료까지 touch 된 파일 카운트
git -C ~/omb/brain/live diff --stat HEAD~1..HEAD   # 단, vault 가 git repo 여야 함
```

→ 현재 `~/omb/brain/live/` 는 git repo 아님. **bench 전 git init** 필요 (별도 단계).

## Axis 3 측정 세부 (query quality)

수동 scoring. 5 점 척도:

- 5 = 정확 + citations + 근거
- 4 = 정확
- 3 = 부분 정확
- 2 = 방향 맞지만 오답
- 1 = 오답
- 0 = refuse / empty

scorer: Luca 본인 + Claude (double-blind). Kappa 확인.

## 비실행 전 체크리스트

- [ ] `tools/bench-compare.sh` 스캐폴드 (이 설계 다음 작업)
- [ ] `~/omb/brain/live/` git init (write efficiency 측정 전제)
- [ ] `omb search --bench-json` 플래그 구현
- [ ] Gold Q&A 50 문항 작성 (사용자 필요)
- [ ] 비교 구현체 설치 디렉토리 정의
- [ ] `docs/bench-result-v0.md` 템플릿

## "설계 겸손" 규약 체크

- 축 3개 이하 ✓
- 새 CLI 커맨드 추가 없음 (omb search 플래그만) ✓
- tier / contract / validator stack 없음 ✓
- Karpathy 원안 밖이지만 **명시적 벤치 목적** 만 추가 — 일상 운영 강제 규칙 아님 ✓

## 관련 페이지

- [[syntheses/llm-wiki-comparison]]
- [[sources/llm-wiki-derivatives-research]]
- [[concepts/llm-wiki-pattern]]
