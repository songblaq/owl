> **DEPRECATED by docs/REZERO-2026-04-18.md.** 이 문서는 Opus 4.6 이 2026-04-17 에 쌓은 설계 stack 의 일부다. 2026-04-18 Re:Zero 로 전면 격하. 참조 목적으로만 보존.

---
id: plan-next
status: active
created: 2026-04-17
supersedes-snapshot: 2026-04-17 이전 plan-2026.md 의 "향후 과제" 단락
---

# Next Plan — 2026-04-17 이후 omb 작업 계획

2026-04-17 하루에 확정된 것 (tier 구조, enforcement, vault 버저닝, wiki view 상시, capsule 자동 연결) 이후 남은 일을 우선순위로 정리. `docs/priorities.md` tier 와 매핑.

---

## 0. 현재 스냅샷 (계획 입력값)

| 축 | 2026-04-17 초 | 2026-04-17 말 | 타깃 |
|---|---|---|---|
| akasha entries | 638 | 638 | — |
| superseded/ | 2 | 2 | 18+ |
| source integrity | 41.5% | **98.4%** ✓ | ≥ 95% |
| naming canonical | 73.5% | **100%** ✓ | ≥ 95% |
| duplicate-decision topics | 18 | 18 | 0 (또는 supersede 체인) |
| wiki 페이지 | 8 | 8 | 도메인별 확장 |
| wiki lint issues | 0 | 0 | 0 유지 |
| contract validator | 없음 | **`omb validate` 존재** ✓ | ingest 통합 |
| rebuild 실증 | 0 회 | 0 회 | 분기 1 회 |
| `omb health` | CRITICAL | **HEALTHY** ✓ | HEALTHY 유지 |

**Definition of Done 달성** (2026-04-17). 이후 남은 것 = semantic 작업 (T0-C), Q2 실증 (T0-D), 운영 확장 (W-A).

---

## 1. 실행 순서 (도구 먼저, 데이터 나중)

Tier 번호가 작을수록 중요하지만, **실무 순서는 Tier 1 enforcement 도구를 먼저 짓고 그걸로 Tier 0 데이터 위반을 잡는다.** 도구 없이 데이터 수작업을 반복하면 같은 오염이 재발.

```
P1.1 validator 구현
      ↓ (도구 확보)
P0.2 broken source 복구    ← rc 필요 (대량)
P0.1 duplicate supersede   ← active 직접 (수동 승인 반복)
Naming 이중-prepend 정리   ← rc 필요 또는 active
      ↓ (Tier 0 HEALTHY)
P0.4 rebuild 실증          ← Q2 1 회
wiki 도메인 확장            ← 상시 병행
contract v3 검토            ← 다음 큰 변경 시
```

---

## 2. 작업 카드 (✓ = 완료, ◐ = 부분, ○ = 미진행)

### ✓ [T1-A] contract validator (MVP 완성, ingest 통합은 다음 rc)

`omb validate` 커맨드 + `validator.py` C1..C6 엔진 완성. `omb ingest` 에 내장하는 것은 pipeline 변경 필요 — 차기 작업. 현재는 ingest 후 수동 `omb validate` 권장.

### ✓ [T0-A] broken source 복구 (98.4% 달성, 잔여 10)

`tools/fix_sources.py` fuzzy-match 로 363 건 복구. 남은 10건 = 원본 존재 안 함 or 모호. 개별 검토 대상 (T0-A-residual).

### ✓ [T0-B] naming 이중-prepend 정리 (100% 달성)

`tools/fix_double_date.py` 로 169 파일 canonical 화. regex 확장 (hex → base36) 으로 2 패스에 완료.

### ○ [T0-C] Duplicate-decision 17 topics — **다음 세션 우선순위**

- **Tier**: P1.1 Discipline as code
- **범위**: `vault/akasha/src/akasha/ingestcmd.py` + 신규 `validator.py`
- **내용**: 아래 C1–C6 를 write 전 검사 (`docs/ingest-contract-v2.md` 참조)
  - C1 Naming regex
  - C2 Required frontmatter fields
  - C3 Required body blocks (claim / Why / Evidence)
  - C4 Pre-write duplicate search (simple topic+tokens 기반, LLM 호출 없이 시작)
  - C5 Source link resolvable
  - C6 At least 1 graph edge suggestion (첫 entry/새 topic 예외)
- **플래그**: `--validate-only` (dry-run), `--force` (우회, migration 전용)
- **리스크**: C4 false positive → 수작업 override 필요
- **완료 신호**: CRITICAL 위반 있는 source 를 ingest 시도 시 non-zero exit + 이유 명시

### [T0-A] P0.2 broken source links 373개 복구

- **Tier**: P0.2 Traceability
- **범위**: 638 entries 중 373개
- **방법**: rc vault (`akasha-rc1`) 에서 처리
  1. `tools/fix_sources.py` (신규): frontmatter `source:` 값을 ~/omb/source/ 에서 fuzzy match (filename 포함/유사 slug)
  2. 매칭 성공 → 경로 재작성 / 실패 → `source_orphan: true` 마킹 또는 entry 삭제 후보 목록
  3. `tools/benchmark_vault.py` 로 before/after 확인
- **리스크**: 잘못된 source 연결 → 오히려 P0.2 위반 심화. fuzzy match 신뢰도 임계값 엄격.
- **완료 신호**: source integrity ≥ 95%, 나머지는 명시적 삭제 결정
- **rc 필요**: 예

### [T0-B] Naming 이중-prepend 169개 정리

- **Tier**: P1.3 Merge requires normalize (지난 마이그레이션의 여파)
- **범위**: `2026-04-13-2026-04-13-19387885-*.md` 패턴 등 169 파일
- **방법**: rc vault 에서 `tools/migrate_a.py` 의 lattice 분기 개선 → 날짜 중복 제거 + hash prefix 제거 후 canonical
- **리스크**: 재-rename 이 이전 rename 과 충돌 → entry id/INDEX 불일치. 스크립트 dry-run 검증 필수.
- **완료 신호**: naming canonical ≥ 95%
- **rc 필요**: 예 (T0-A 와 같은 rc 에서 병행)

### [T0-C] Duplicate-decision 17 topics 수동 supersede

- **Tier**: P0.1 Truth singularity
- **범위**: AUDIT.md 의 18 topic → 동일 swap 1건 처리 후 17 남음
- **방법**: active 직접
  1. `omb audit` 로 AUDIT.md 생성
  2. 각 topic 의 entries 를 LLM 이 읽고 "같은 주장 연속 / 다른 주장 병렬" 판정
  3. "같은 주장 연속" 이면 사용자 승인 후 `omb supersede` 실행
  4. "다른 주장 병렬" 이면 기각 (AUDIT.md 에 "reviewed-split" 마킹 — 추가 필드 도입 필요)
- **리스크**: 가장 큼 — 내용 확인 없는 supersede 는 정보 손실. 각 케이스 사용자 승인 게이트 필수.
- **완료 신호**: superseded/ 에 적정 개수 이동 + 남은 duplicate topic 은 "의도된 다중 entry" 로 AUDIT 에서 제외
- **rc 필요**: 아니오 (적은 건수씩 점진)

### ✓ [T1-B] `omb audit --json`

- **Tier**: P1.2 Health fails loudly (기계 처리 용이화)
- **범위**: `vault/omb/src/omb/vault_ops.py::audit`
- **내용**: `omb audit --json` 추가 — CI / 스크립트 통합 용
- **완료 신호**: `omb audit --json | jq` 작동

### ◐ [T1-C] `omb rebuild` 골격 — skeleton 완료, 실제 rebuild 는 LLM 통합 필요

- **Tier**: P0.4 Rebuildable + proven
- **범위**: `vault/omb/src/omb/cli.py` 신규 커맨드
- **내용**:
  - 기존 vault 백업 옵션 없음 (설계상 금지 — 구버전 보관 안 함)
  - 빈 vault 에 `~/omb/source/` 전체를 T1-A validator 통과하도록 순회 ingest
  - 끝나면 benchmark 자동 출력 (old vs new)
- **리스크**: 대량 LLM 호출 필요 (C4 pre-write search 가 LLM 필요 시). 최초 구현은 mechanical 만 (filename 기반 dedupe).
- **완료 신호**: `omb rebuild --dry-run` 이 전체 플랜 출력, `--apply` 로 rc 생성

### [T0-D] P0.4 rebuild 첫 실증 (Q2 target)

- **Tier**: P0.4
- **범위**: 위 T1-C 도구로 실제 rc 재생성 → active 와 benchmark
- **완료 신호**: `docs/bench-rebuild-Q2.md` 생성, Tier 0 위반 수 비교

### [W-A] wiki 도메인 확장 — homelab 외

- **Tier**: 없음 (상시 companion view 운영 작업)
- **범위**: `~/omb/vault/wiki/`
- **내용**: 현재 homelab 만 커버됨. 주요 도메인별 페이지 추가
  - deos (→ `entities/deos`, `concepts/content-factory-pipeline` 등)
  - openclaw 세부 arch (현재 stub 에서 확장)
  - constella (4-layer)
  - hermes
  - aria
- **방법**: 사용자 요청 시 ingest, 또는 분기별 일괄. 현재 TODO: `entities/mac-mini-orchestrator`, `concepts/comfyui-pipeline`, `sources/llm-model-comparison`
- **완료 신호**: 도메인별 entity + 최소 1 concept 페이지 존재

### ✓ [W-B] `tools/wiki_lint.py` 완성

- **Tier**: 없음 (운영 개선)
- **범위**: `tools/wiki_lint.py` 신규
- **내용**: AGENTS.md lint checklist 를 스크립트화
  - broken `[[wiki link]]`
  - orphan page (inbound link 0)
  - frontmatter 필수 필드 검증
- **완료 신호**: `python3 tools/wiki_lint.py ~/omb/vault/wiki` 가 위반 건수 리포트

### ◐ [I-A] `omb import --normalize` — skeleton 완료, auto-fix 는 미구현

- **Tier**: P1.3 Merge requires normalize
- **범위**: 신규 CLI
- **내용**: 외부 knowledge 파일을 import 할 때 C1–C6 normalize 후에만 entries/ 로 이동. 2026-04-15 lattice/cairn/owl merger 같은 재앙 방지.
- **완료 신호**: `omb import <path> --view akasha --normalize` 가 위반 시 거부

### [C-A] Capsule 신규 product 필요시 추가

- **Tier**: 없음 (운영)
- **범위**: 사용자 요청 기반. 현재 openclaw, hermes-agent 외 필요 판정
- **참고**: `omb search` 자동 매칭이므로 새 product 이름이 쿼리에 등장할 경우만 의미 있음

---

## 3. 그룹핑 — rc 계획

하나의 rc 에 2~3 개 mechanical 작업을 묶어 비용 분산.

### rc1 (mechanical 정화): T0-A + T0-B 병행

- broken source 복구 + naming 이중-prepend 정리
- 둘 다 script 기반, semantic 판단 거의 없음
- 예상 기간: 하루
- 승격 조건: source integrity ≥ 95% AND naming canonical ≥ 95%

### rc2 (도구 통합 후): T1-C 로 rebuild 실증

- Q2 (2026-07 경) 예정
- 전제: T1-A validator 가 완성되어 contract 강제가 돌아가는 상태
- 승격 조건 아님 — **rebuild 결과가 현 active 와 동등하거나 더 적은 위반** 이면 활동 유지 (rebuild 는 P0.4 실증이지 active 교체 목적 아님)

---

## 4. 일정 (느슨한 target)

| 시점 | 달성할 것 |
|---|---|
| 이번 주 내 | T1-A validator, T1-B audit JSON, T0-C duplicate 샘플 3건 |
| 2026-05 중 | rc1 승격 (T0-A + T0-B), wiki 2 도메인 추가 |
| 2026-06 | T1-C rebuild 도구, T0-C 대부분 소진 |
| 2026-07 (Q2 end) | T0-D rebuild 실증 1 회, `omb health` HEALTHY 첫 도달 |

개인 프로젝트라 엄격한 일정 아님. 순서와 전제 관계가 핵심.

---

## 5. 하지 않을 것 (스코프 명시)

- 구버전 vault 보관 (vault-versioning 규약)
- 의미 라벨 폴더명 (`akasha-migrate` 등)
- vault 내부 메타 파일 (`VERSION.md`, `EXPERIMENT.md` 등)
- 수동 확인 없는 semantic 자동 supersede
- wiki 풀 오픈소스 설치 (규약 차용만)
- akasha ↔ wiki 간 derived artifact 교차 read (view-contract)
- capsule 을 writable 로 승격

이 목록은 지난 24시간 시행착오의 결과. 어기는 선택이 보이면 이 문서 다시 확인.

---

## 6. 검증

각 작업 완료 시:

```bash
# Tier 0/1 가시화
omb health
omb audit
python3 tools/benchmark_vault.py ~/omb/vault/akasha

# wiki
python3 tools/wiki_lint.py ~/omb/vault/wiki   # T1-B 이후
```

`omb health` 가 HEALTHY 로 전환되는 시점이 이 계획의 **Definition of Done**.
