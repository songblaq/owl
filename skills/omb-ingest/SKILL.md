---
name: omb-ingest
description: Add new knowledge to the oh-my-brain vault. Handles file ingestion or raw text, then rebuilds the index.
triggers:
  - "omb ingest"
  - "브레인에 추가"
  - "지식 추가"
  - "vault에 추가"
  - "ingest brain"
---

# OMB Ingest

새 지식을 vault에 추가하고 인덱스를 재빌드한다.

## 사용법

```
/omb:ingest <file>
/omb:ingest --text "..."
```

## 실행 순서

### 파일 ingestion
1. `omb ingest <file> [--topic <name>] [--dry-run]`
   - `--dry-run` 먼저 실행해서 예상 결과 확인
   - 확인 후 실제 실행
2. `akasha index` 로 INDEX.md + GRAPH.tsv 재빌드

### 텍스트 직접 ingestion
1. `omb ingest --text "<content>" --title "<slug>" [--topic <name>]`
2. `akasha index`

## 옵션

| 옵션 | 설명 |
|------|------|
| `--topic <name>` | 주제 명시 (없으면 자동 감지) |
| `--dry-run` | 실제 쓰기 없이 미리보기 |
| `--title <slug>` | `--text` 사용 시 파일명 힌트 |

## 규칙

- raw source는 `~/omb/source/`에 복사됨 — 이후 절대 수정 금지
- ingestion 후 항상 `akasha index` 실행해서 INDEX.md 최신화
- 대용량 파일은 `--dry-run`으로 먼저 확인
