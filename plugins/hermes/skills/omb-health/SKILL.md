---
name: omb-health
version: "0.1.0"
description: Check oh-my-brain vault health — source coverage, missing compilations, stale entries. Returns actionable fix plan.
author: songblaq
license: MIT
triggers:
  - "omb health"
  - "커버리지 확인"
  - "vault health"
  - "brain health"
prerequisites:
  - omb
metadata:
  hermes:
    tags:
      - knowledge
      - health
      - coverage
      - omb
---

# OMB Health

Vault source coverage를 확인하고 다음 ingestion을 제안한다.

## 사용법

```
/omb:health
```

## 실행 순서

1. `omb health --json` 실행
2. 결과 파싱:
   - `coverage`: 전체 coverage %
   - `missing_compiled`: compiled 없는 topic 목록
   - `stale_entries`: 오래된 entry 목록
   - `uncovered_sources`: ingest 안 된 source 파일
3. 우선순위에 따라 fix 계획 제시:
   - coverage < 50% → 주요 source 파일 ingest 제안
   - missing_compiled 있음 → `omb compile` 실행 제안
   - stale entries 있음 → 재검토 제안

## 출력 형식

```
Coverage: XX%
Missing compiled: N topics
Action plan:
1. ...
2. ...
```
