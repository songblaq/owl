---
name: omb-search
version: "0.1.0"
description: Search the oh-my-brain knowledge vault. Runs 3-layer search (compiled + entries + graph). Use before answering knowledge questions.
author: songblaq
license: MIT
triggers:
  - "omb search"
  - "브레인 검색"
  - "지식 검색"
  - "search brain"
  - "search vault"
prerequisites:
  - omb
metadata:
  hermes:
    tags:
      - knowledge
      - search
      - vault
      - omb
---

# OMB Search

지식 vault를 검색하고 결과를 근거로 답변한다.

## 사용법

```
/omb:search <query>
```

## 실행 순서

1. `omb search "<query>" --limit 10` 실행
2. 결과 파싱:
   - `[compiled]` 히트 → `~/omb/vault/akasha/compiled/<topic>.md` 읽기
   - `[entry]` 히트 → `~/omb/vault/akasha/entries/<slug>.md` 읽기 (상위 3개)
   - `[+graph]` 히트 → 그래프 확장 결과, 참고로 읽기
3. 읽은 문서를 근거로 답변
4. 매칭이 없거나 빈약하면 명시 후 `omb ingest` 제안

## 출력 형식

- 검색 결과 인용 (`> ` 블록)
- 해석/답변
- 참고 파일 경로 명시

## 규칙

- 답변 전 반드시 검색 먼저
- snippet만으로 답변하지 않을 것 — 직접 읽기
