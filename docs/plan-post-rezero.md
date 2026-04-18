---
id: plan-post-rezero
status: active
created: 2026-04-18
updated: 2026-04-18
supersedes: docs/plan-next.md (DEPRECATED by REZERO-2026-04-18)
---

# Post-Re:Zero 작업 체크리스트

`docs/REZERO-2026-04-18.md` 의 Definition of Done 5항목은 모두 완료 (2026-04-18). 이후 사용자가 정의한 작업을 여기 모은다. **이 문서가 `omb` + `plan-check` 가 인식하는 active plan** — `plan-next.md` 는 deprecated 상태 유지.

## 원칙

- Karpathy 원안 이상으로 쌓지 않는다 (→ memory feedback_design_humility)
- 체크리스트는 실행 가능한 단위로만. 장기 비전은 별도 문서
- 완료 시 `- [x]`, 부분 진행 시 `- [~]`, 미착수 `- [ ]`

## Tier 0 — 즉시 실행 / 복구

- [x] input/ top-level 231 파일 wiki 현행화 (100% citation coverage) — 2026-04-18 Phase 2
- [x] 서브디렉토리 atlas/ codex/ runtimes/ 현행화 — 2026-04-18 Phase 3
- [x] agents/*/models.json stale 항목 (gemma4 / bge-m3 / custom-provider / 5090 models) 정리 — 2026-04-18 5 에이전트 완료
- [x] iMac Ollama 중단 + 5090 Ollama 없음 wiki 현행화 — 2026-04-18
- [x] 중복 raw 파일 3 삭제 (md5 동일 확인 후) — 2026-04-18
- [x] drift_audit.sh 정기 실행 기록 — 2026-04-18
- [x] feedback_omb_search_reflex memory 추가 — 2026-04-18

## Tier 1 — 근시일 (이번 주)

- [x] **git commit** — 2026-04-18 완료 (5 커밋: Re:Zero / init+plan / Obsidian+probe+bench / Tier1 tick / plan rename)
- [x] **Obsidian 호환 README 문서화** — 2026-04-18 완료
- [~] **git push** — local 5 ahead. **사용자 승인 대기 중 (next action)**
- [ ] **NAS NIC1 (.178) DOWN 복구** — 물리/DSM 조치 (사용자 직접)
- [ ] **구독 fallback 연동** — Claude Code CLI (Claude), OAuth/codex/opencode (GPT) 를 OpenClaw providers 로 실연결
- [ ] **원격 WSL 접근 어댑터** — `ssh → wsl -- bash -lc '...'` 패턴 표준화. ssh config `Host blaqtower-wsl` / `pd-5090-wsl` 추가

## Tier 2 — 중기 (이번 달)

### T2-A. Refusal probe 실행 (스캐폴드 → 데이터)
- [x] 스캐폴드 (`tools/refusal_rate_probe.sh` + `docs/refusal-probe-prompts.md`) — 2026-04-18
- [ ] prompts 확장: 현재 seed → **최소 30문항** (카테고리별 6-8개 × {일반/우회/롤플/코딩/멀티턴})
- [ ] 타겟 모델 확정: supergemma4 (iMac 중단됨 → 대체 필요) / DGX `gpt-oss-120b` / 5090 후보 / mac-studio `qwen3-coder-480b`
- [ ] 1차 실행 → `~/omb/bench/refusal-2026-04-XX.json` 결과 저장
- [ ] 결과 분석 → `brain/live/syntheses/refusal-rate-comparison-<date>.md` 작성

### T2-B. omb 자체 벤치 v0 실행
- [x] 설계 draft (`docs/bench-design-2026-04-18.md`) — 2026-04-18
- [ ] **gold Q&A 50문항 작성** — 3 축 × 17 (사용자 도메인 지식 필수)
  - retrieval: wiki search 정확도 15
  - synthesis: cross-entity 종합 20
  - freshness: drift 감지 후 최신 정보 반영 15
- [ ] scoring rubric 확정 (LLM-judge? human? hybrid?)
- [ ] 5 타겟 실행 baseline — 결과 `bench/akasha/` 미사용 → `~/omb/bench/omb-v0-<date>/` 신설

### T2-C. drift_audit 확장
- [ ] Phase 5: endpoint health check (`curl` 기반 5 endpoint — iMac / NAS / DGX / 5090 / mac-studio)
- [ ] config provider ↔ actual model 정합성 비교 (models.json 대조)
- [ ] `tools/drift_audit.sh` 에 `--endpoint-health` flag 추가

### T2-D. 인프라 확장 조사
- [ ] DGX factory 확장 검토 — SDXL/Flux/video 워크로드 GB10 Blackwell 성능·전력·소음. ComfyUI 호환성
- [ ] kiraclaw 120K excerpt 깊게 ingest — full entity 승격

## Tier 3 — 장기 / 연구

- [ ] **쿼리 답변 자동 filing** — Karpathy 원안의 "좋은 답변은 syntheses/ 로 filing" 을 CLI 1 명령으로
- [ ] **active learning 확장** — rohitg00 LLM Wiki v2 gist 검토
- [ ] **tobi/qmd 통합 판단** — 페이지 100+ 도달 시 재검토 (현재 44 페이지)
- [ ] **vision ingest** — Ar9av/obsidian-wiki 참조. 이미지 raw 수집

## 이번 주 실행 순서 (next actions)

1. **git push 승인** → remote 동기화 (사용자 1 decision)
2. **refusal probe prompts 확장 30문항** → 1차 실행 (반나절, 데이터 수집)
3. **bench gold Q&A 50문항 작성** → 사용자 도메인 세션 1회 (2-3h)
4. **drift_audit --endpoint-health** 구현 → T2-C (1-2h 코딩)
5. NAS NIC1 + WSL ssh config 는 사용자 물리 작업 블록에서 병행

## 미결 drift / 이상 징후 (monitor)

- [x] collect.sh primary_plan 휴리스틱 — `plan-next.md` → `legacy-plan-next.md` rename 으로 해결 (2026-04-18 C5)
- [ ] Hermes 5090 WSL config 의 `mac-studio` custom provider 사용 여부 — [[syntheses/homelab-endpoint-audit-2026-04-18]] 참조

## 검증 / KPI

```
tier_0_status = HEALTHY (7/7 DONE)
tier_1_completion = 2/6 done + 1 partial ≈ 42%  (push 승인 시 50%, NAS/구독/WSL 남음)
tier_2_completion = 2/10 scaffolded ≈ 20%
drift_count = drift_audit.sh + endpoint health (Phase 5 후 측정)
```
