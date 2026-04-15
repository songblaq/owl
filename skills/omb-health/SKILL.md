---
name: omb-health
version: "0.1.0"
author: songblaq
license: MIT
description: Check oh-my-brain vault coverage — which sources have been ingested and which are missing. Reports gaps and suggests next ingestion targets.
triggers:
  - "omb health"
  - "브레인 헬스"
  - "vault 커버리지"
  - "coverage check"
  - "브레인 상태"
---

# OMB Health

source coverage를 점검하고 미처리 source를 파악한다.

## 사용법

```
/omb:health
```

## 실행 순서

1. `omb health --json` 실행
2. 결과 파싱:
   - `covered`: ingestion 완료된 sources
   - `missing`: 아직 entries가 없는 sources
   - coverage % 계산
3. 요약 리포트 작성:
   - 전체 coverage 비율
   - missing sources 목록 (있다면 상위 5개)
   - 권장 다음 action

## 출력 형식

```
OMB Health Report
━━━━━━━━━━━━━━━━
Coverage: X/Y sources (Z%)

Missing sources (top 5):
  - <source-slug>
  ...

Next steps:
  - omb ingest ~/omb/source/<slug>.md
```

## 규칙

- missing sources가 있으면 `omb ingest` 명령 예시 제시
- coverage 100%면 `akasha compile --dry-run`으로 미컴파일 topic 확인 제안
