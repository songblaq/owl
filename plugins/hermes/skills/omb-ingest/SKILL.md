---
name: omb-ingest
version: "0.1.0"
description: Ingest a file or raw text into the oh-my-brain knowledge vault, then rebuild the index.
author: songblaq
license: MIT
triggers:
  - "omb ingest"
  - "브레인에 추가"
  - "add to brain"
  - "ingest knowledge"
prerequisites:
  - omb
metadata:
  hermes:
    tags:
      - knowledge
      - ingest
      - vault
      - omb
---

# OMB Ingest

새 지식을 vault에 추가하고 인덱스를 재빌드한다.

## 사용법

```
/omb:ingest <file-or-text>
```

## 실행 순서

### 파일 ingest
```bash
omb ingest <file-path>
```

### 텍스트 ingest
```bash
omb ingest --text "<raw text>"
```

### 인덱스 재빌드 (자동)
ingest 후 akasha가 자동으로 INDEX.md + GRAPH.tsv를 재생성한다.

## 완료 확인

```bash
omb status
```

entries 수가 증가했는지 확인.
