---
name: omb-compile
version: "0.1.0"
description: Compile pending topics in the oh-my-brain vault — pick a topic, dump entries, and write a narrative summary.
author: songblaq
license: MIT
triggers:
  - "omb compile"
  - "컴파일"
  - "compile brain"
  - "vault compile"
prerequisites:
  - omb
  - akasha
metadata:
  hermes:
    tags:
      - knowledge
      - compile
      - narrative
      - omb
---

# OMB Compile

Pending topic을 골라 entries를 dump하고 LLM이 narrative를 작성한다.

## 사용법

```
/omb:compile [topic]
```

## 실행 순서

1. `akasha compile --dry-run` — pending topics 목록 확인
2. topic 선택 (사용자 지정 or 가장 entry 많은 것)
3. `akasha compile --dump <topic>` — entries + metadata dump
4. dump를 읽고 coherent narrative 작성
5. `~/omb/vault/akasha/compiled/<topic>.md`에 저장

## 작성 기준

- 원자적 entries를 하나의 흐름으로 연결
- 핵심 주장 + 근거(왜, 대안, 검증) 포함
- 약 500~2000 tokens
- 한국어/영어 혼용 OK (entries 언어 따름)

## 완료 확인

```bash
omb search "<topic>"
```

compiled 결과가 나오면 성공.
