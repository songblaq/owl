> **DEPRECATED by docs/REZERO-2026-04-18.md.** 이 문서는 Opus 4.6 이 2026-04-17 에 쌓은 설계 stack 의 일부다. 2026-04-18 Re:Zero 로 전면 격하. 참조 목적으로만 보존.

---
id: vault-versioning-v3
status: active
created: 2026-04-17
updated: 2026-04-17
---

# Vault Versioning — akasha 버전 관리 규약

## 원칙

**vault 폴더명은 항상 `akasha` 로 고정.** 버전 번호를 폴더명에 넣지 않는다. 버전 전환은 폴더 rename 이 아니라 **내용 교체**로 한다. 이력은 `docs/CHANGELOG.md` 가 담는다.

폴더명을 버전에 묶으면 active pointer, 도구 설정, 스크립트, 심볼릭 링크가 버전마다 재배선돼야 한다. 실용 불가.

## 디스크 규칙

```
~/omb/vault/
  akasha              현재 active (고정 이름, 내용은 계속 업데이트)
  # 실험 기간에만 잠시:
  akasha-rc1          next-version candidate
  akasha-rc2          ...
```

- 안정 상태: `akasha/` 하나만.
- 실험 기간: `akasha/` (active) + `akasha-rc*` (candidate) 병존. 승격 직후 rc 전부 제거.

## 버전 기록 (폴더가 아니라 문서)

`docs/CHANGELOG.md` 가 vault 의 버전 이력을 담는다. keep-a-changelog 형식.

```markdown
## [v2] - 2026-04-17

### Added
- `omb supersede`, `omb audit`, `omb health` (strict) CLI
- `sources` 심볼릭 링크 → ~/omb/source

### Changed
- 네이밍 100% canonical
- health 로직: Tier 0/1 위반 시 CRITICAL + exit 1

### Removed
- `akasha-archive-*`, `akasha-*-migrate/rebuild/hybrid` 실험 vault (벤치마크 완료, 결과는 experiment-*.md)
```

새 버전 확정 시 CHANGELOG 에 한 섹션 추가. 버전 번호(v1, v2, ...)는 CHANGELOG 내부에서만 의미 갖는다 — 파일시스템에는 드러나지 않는다.

## 새 버전이 필요한 조건

다음 중 하나라도 해당하면 rc 생성:

1. 모든 entries 에 적용되는 mechanical migration (네이밍, frontmatter 스키마, source path)
2. contract 변경 (`docs/ingest-contract-v2.md` → v3 등)
3. 대량 supersede (> 10 entries) 또는 대량 삭제
4. view 구조 변경 (entries/ compiled/ superseded/ 외 레이아웃 추가)
5. 외부 view 통합

조건 해당 안 하면 — 일반 ingest, 일상 supersede, compile 리프레시 — `akasha/` 에서 직접 수행, rc 안 만들고 CHANGELOG 도 업데이트 안 함.

## 절차

### RC 생성

```bash
cp -R ~/omb/vault/akasha ~/omb/vault/akasha-rc1
# 실험·마이그레이션 작업은 rc 안에서만
python3 tools/benchmark_vault.py ~/omb/vault/akasha ~/omb/vault/akasha-rc1
```

### RC 승격 — 구 active 즉시 제거

```bash
# 1) 벤치마크 결과 기록
python3 tools/benchmark_vault.py ~/omb/vault/akasha ~/omb/vault/akasha-rc1 > docs/bench-$(date +%Y-%m-%d).md

# 2) 구 active 제거 + rc 를 active 로 교체
rm -rf ~/omb/vault/akasha
mv ~/omb/vault/akasha-rc1 ~/omb/vault/akasha
rm -rf ~/omb/vault/akasha-rc*   # 나머지 rc 전부 정리

# 3) CHANGELOG.md 에 새 버전 섹션 추가
# 4) active pointer 는 그대로 — 경로가 안 바뀌었으므로
```

### 롤백

구버전 폴더를 유지하지 않으므로 **rebuild** 로 롤백. 이게 어렵다는 것 = P0.4 Rebuildable 약속이 아직 허위라는 신호 (우선순위 작업).

```bash
rm -rf ~/omb/vault/akasha
omb rebuild --contract v<N>    # 미구현 시 수동 재생성
```

## 중복 금지 — 진실은 한 곳에만

| 어디 | 무엇 |
|---|---|
| `~/omb/vault/akasha` | 현재 데이터 (entries/ compiled/ superseded/ INDEX/GRAPH/ALIASES/AUDIT) |
| `~/.config/akasha/active-vault` | active pointer |
| `docs/CHANGELOG.md` | 버전 이력 |
| `docs/ingest-contract-v<N>.md` | 해당 버전의 contract |
| `docs/experiment-*.md`, `docs/bench-*.md` | 전환 근거·벤치마크 |
| vault 내부 | **데이터만** |

vault 루트에 `VERSION.md`, `EXPERIMENT.md`, `README.md` 등 메타 문서 금지.

## 반면교사 (왜 이 규약이 생겼나)

2026-04-17 하루 안에 피드백 5단계로 규약이 확정됨:

1. "이상한 이름 부여하지 말고 버전을 올리는 식으로 관리해" → 의미 라벨 금지
2. "벤치마크했으면 하나만 남겨놔야지 왜 2개야" → 승자 외 즉시 제거
3. "구버전 지식을 남겨놓는게 무슨 의미가 있는지 모르겠네" → baseline 보관 금지
4. "그거 자체가 중복이야" → vault 내부 메타 파일 금지
5. "폴더를 -v2 빼세요. 앞으로도 변경사항이 있으면 그걸로 계속 바꿀 수 없으니까요. 따로 체인지로그나 릴리즈나 정리해두시고요" → 폴더명 고정, CHANGELOG 도입

핵심: 폴더명은 identity, CHANGELOG 는 history. identity 에 버전을 박는 순간 모든 도구/참조가 버전에 묶여 변경 비용 폭발.
