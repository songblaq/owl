> **DEPRECATED by docs/REZERO-2026-04-18.md.** 이 문서는 Opus 4.6 이 2026-04-17 에 쌓은 설계 stack 의 일부다. 2026-04-18 Re:Zero 로 전면 격하. 참조 목적으로만 보존.

---
id: experiment-3way-2026-04-17
status: complete
created: 2026-04-17
---

# 3-way vault 실험 보고서 (2026-04-17)

오염된 akasha vault를 3가지 전략(A/B/C)으로 분기 처리하고 원본(archive)과 함께 4-way 비교한 결과. 반면교사 관점에서 최초 기획/설계의 어느 부분이 유효했고 어느 부분이 실제 운영에서 깨졌는지 확인한다.

## 설계 의도 복기

2026-04-09 cairn + 2026-04-15 akasha 수렴 시점의 5대 원칙:
1. Raw = immutable
2. LLM is the writer
3. Atomic ~500 tok claim
4. Supersede, never mutate (옛 entry를 `superseded/`로 물리 이동)
5. Rebuildable from source

## 4-way 결과 (2026-04-17 측정)

| metric | archive (baseline) | A (aggressive migrate) | B (rebuild from source) | C (hybrid) |
|---|---|---|---|---|
| entries | 636 | 636 | 0 (spec only) | 636 |
| compiled | 71 | 71 | 0 | 71 |
| superseded_dir | **0** | 0 | 0 | 0 |
| naming_conformance | **4.7%** | **100%** | n/a | **100%** |
| source_integrity | **0.0%** | 41.8% | n/a | 41.8% |
| orphan_ratio | 95.1% | 89.3% | n/a | 89.3% |
| supersedes_coverage | 1.3% | 1.3% | n/a | 1.3% |
| duplicate_decision_topics | 18 | 18 | n/a | 18 |

추가 산출물:
- A: `migrate_a.py` 1회 실행 (자동)
- B: `ingest-contract-v2.md` spec + 수동 샘플 3개 (개념 증명)
- C: A와 동일 migrate + `AUDIT.md` (370 broken source + 568 orphan + 18 duplicate topic 전수 기록)

## 5대 원칙 실증 결과

| 원칙 | 원본 상태 | 어느 실험이 살렸나 |
|---|---|---|
| Raw = immutable | O — source/ 237개 불변 | 전부 |
| LLM is the writer | O (하지만 enforcer 아님) | B contract v2만 enforcement 보강 |
| Atomic ~500 tok | O | 전부 |
| Supersede + 물리 이동 | **X** (superseded/ 0개) | B가 C3/C4 contract로 설계상 보장. A/C는 도구 미완. |
| Rebuildable from source | **X** (source link 전부 broken) | A가 mechanical 41.8% 복구. B가 설계상 100% 약속. |

## 원칙별 근본 원인

1. **Supersede 붕괴**: 설계 문서에 원칙으로 명시됐지만 **구현(`omb supersede` CLI)이 없음**. convention-only → frontmatter에만 적기 → 검색 시 진실 중첩.
2. **Rebuildable 약속 허위**: `~/omb/source/`(spec) ↔ `vault/akasha/sources/`(실제 entry 참조) 경로 분열. 한 번도 실증 테스트 안 함.
3. **Naming 지층**: owl→cairn→lattice→akasha 수렴이 "합병"이 아니라 "그대로 덮기"였음. normalize 단계 없었기에 3가지 스타일이 카탈로그에 그대로 남음.
4. **Health check 거짓 안심**: `omb health`가 source coverage 0%를 알리면서도 "Vault looks healthy" 반환. 위반을 에러로 승격 안 함.

## 실험별 판정

### 실험 A — Aggressive migrate
- **장점**: mechanical 오염(naming, source path)은 자동 스크립트로 2초 만에 해결. 비용 0.
- **단점**: supersede 체인/중복/orphan은 그대로. LLM 자동 제안으로 이어지면 오판 리스크 큼 (같은 topic이어도 다른 주장일 수 있음).
- **발견된 취약점**: lattice 엔트리에 날짜 이중 prepend 버그(`2026-04-13-2026-04-13-...`). "단순 rename이 얼마나 취약한가"의 반증.
- **교훈**: mechanical 수정은 쉽지만, semantic 판단은 여전히 LLM 또는 사람 개입 필요.

### 실험 B — Rebuild from source
- **실행 안 함**: 237 source × 3회 LLM call ≈ $30, 1시간 (추정). 샘플 3개로만 contract 증명.
- **장점**: contract v2 5개 규약(naming/frontmatter/evidence/pre-write search/source link/graph edge)이 설계 의도를 도구 수준으로 구현. 중복 구조적 차단 가능.
- **단점**: source에 없는 대화 중 즉석 지식 소실. 토큰 비용. 재해석 비결정성.
- **교훈**: "Rebuildable" 약속은 수용 가능한 비용으로 실증 가능. 단, 전면 rebuild는 실용적이지 않고 **contract를 신규 ingest에만 적용**하는 게 현실적.

### 실험 C — Hybrid
- **장점**: A의 mechanical 이득 + AUDIT.md로 수동 리뷰 포인트 전수 기록 + contract v2를 신규에만 적용. 과거 오염은 자연 소진.
- **단점**: audit 사이클을 실제로 돌려야 효과 있음. 방치 시 A만도 못함.
- **교훈**: 도구(contract validator) + 프로세스(월간 audit)의 조합이 "LLM is the writer" 원칙을 살리는 현실적 경로.

## 승자: C + B 결합

단독 승자는 없음. **C의 운영 방식 + B의 contract v2 spec**이 최적 조합.

- **지금**: A/C가 이미 적용한 naming/source 복구 유지
- **신규 ingest**: B의 contract v2 (`ingest-contract-v2.md`)를 `omb ingest`에 통합
- **과거 감사**: C의 `AUDIT.md` + 월간 수동 리뷰

A 단독은 위험 (semantic 자동화 오판), B 단독은 비용, C 단독은 오염 잔존. 셋의 장점만 취하는 것이 결론.

## 최초 기획/설계에 반영해야 할 업데이트

1. **Design Principle 추가**: "Discipline은 convention이 아니라 도구다 (enforcement as code, not docs)."
2. **Design Principle 추가**: "Rebuildable은 분기별로 실증 테스트해야 한다."
3. **Source-layer spec 명시**: entry의 `source:` 필드는 `~/omb/source/`에 실존해야 하며, 절대경로 또는 vault 내 symlink 경로만 허용.
4. **Ingest contract**: `docs/ingest-contract-v2.md` 채택.
5. **CLI 추가 계획**: `omb supersede`, `omb audit`, `omb migrate --apply`.
6. **Health 로직 강화**: source coverage < 95%면 "unhealthy" 분류.
7. **Vault 수렴 프로토콜**: 향후 view 통합 시 "normalize 단계" 필수화 — naming/frontmatter/source 일괄 검증 후 병합.

## 교훈 (반면교사)

1. **Convention은 도구 없이 지켜지지 않는다.** 문서 5개 써도 안 지켜진다. 위반 시 에러가 나야 지켜진다.
2. **"Rebuildable"은 주기적으로 실증해야 한다.** 실증 테스트 0회면 사실상 죽은 약속.
3. **통합/수렴은 normalize 단계를 건너뛰면 안 된다.** 옛 데이터를 그대로 가져오는 순간 오염이 영속화.
4. **Health check가 "healthy"로 끝나면 건강하지 않다.** 경보는 구체적 위반 지점을 내야 한다.
5. **Mechanical vs Semantic을 구분하라.** mechanical(rename, path fix)은 자동화해도 되지만, semantic(supersede 여부 판단)은 LLM/사람 승인 없이 자동화하면 진실을 왜곡한다.
