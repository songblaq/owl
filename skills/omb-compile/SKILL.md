---
name: omb-compile
version: "0.1.0"
author: songblaq
license: MIT
description: Compile oh-my-brain vault topics — check pending topics, dump entries for a topic, and write LLM narrative to compiled/<topic>.md
triggers:
  - "omb compile"
  - "컴파일"
  - "narrative 작성"
  - "compiled 업데이트"
  - "topic compile"
---

# OMB Compile

akasha vault의 topic별 narrative 문서를 LLM이 직접 작성한다.

## 사용법

```
/omb:compile              # pending topics 확인 후 대화형 선택
/omb:compile <topic>      # 특정 topic 바로 컴파일
```

## 실행 순서

### Step 1: Pending topics 확인
```bash
akasha compile --dry-run
```
출력에서 `[pending]` 표시된 topic 목록 제시.

### Step 2: Topic 선택
- topic을 명시하지 않은 경우 사용자에게 선택 요청
- 명시한 경우 바로 Step 3으로

### Step 3: Entries 덤프
```bash
akasha compile --dump <topic>
```
출력된 entries 전체를 읽는다.

### Step 4: Narrative 작성
읽은 entries를 기반으로 `~/omb/vault/akasha/compiled/<topic>.md` 작성:

```markdown
---
topic: <topic>
compiled: YYYY-MM-DD
entry_count: N
---

# <Topic> — Compiled Narrative

<LLM-written synthesis of all entries for this topic>
```

작성 원칙:
- 모든 entries의 핵심 claim 포함
- 중복 없이 흐름 있게 서술
- 각 claim의 근거/맥락 보존
- 마지막에 "Key takeaways" 섹션

### Step 5: Index 재빌드
```bash
akasha index
```

## 규칙

- entries를 요약해서 버리지 말 것 — 정보 손실 금지
- compiled 파일은 LLM이 작성, 사람이 편집하지 않는 것이 원칙
- 기존 compiled 파일이 있으면 덮어쓰기 전 확인
