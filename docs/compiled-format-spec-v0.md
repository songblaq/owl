# Compiled Format Spec v0

작성일: 2026-04-03
상태: 설계 초안

## 1. 목적

Compiled 문서는 raw source를 LLM이 읽고 구조화한 결과물이다. 이 문서 규격은 Agent Brain 안에서 사람이 읽기 쉽고, LLM이 다시 읽기 쉬운 지식 문서 형식을 정의한다.

---

## 2. 기본 원칙

- markdown 우선
- 짧은 front matter 또는 최소 메타 헤더 허용
- 문서 목적이 한눈에 보여야 함
- source link / related / next actions 를 남길 것
- 지나치게 장황한 자동 생성 문체보다 재사용 가능한 구조를 우선할 것

---

## 3. 공통 템플릿

```md
# 제목

상태: draft | compiled | reviewed
유형: summary | concept | index | report | comparison | note
출처: ...
작성일: YYYY-MM-DD
관련 항목: ...

## 개요
짧은 요약

## 핵심 내용
- 핵심 1
- 핵심 2
- 핵심 3

## 상세
필요한 본문

## 관련 자료
- raw source
- 연결 문서

## 다음 작업
- 후속 조사
- 비교 대상
- 보완 포인트
```

---

## 4. 문서 유형

### Summary
한 source 또는 주제를 요약하는 문서.

### Concept
여러 source를 묶어 하나의 개념을 설명하는 문서.

### Index
주제별 문서 목록, 탐색 경로, 하위 문서를 연결하는 문서.

### Comparison
두 개 이상의 개념/기술/자료를 비교하는 문서.

### Report
질의응답이나 조사 결과를 보고서 형태로 정리한 문서.

### Note
짧은 관찰, 메모, 후속 실험 아이디어.

---

## 5. 파일명 권장

- 날짜 + 슬러그
- 예: `2026-04-03-karpathy-llm-knowledge-bases-summary.md`
- index는 `index-주제명.md` 가능

---

## 6. 최소 품질 기준

- 제목만 있는 문서는 피한다.
- source 없이 주장만 있는 문서는 피한다.
- 관련 문서와 후속 작업이 없으면 확장성이 떨어진다.
- 한 문서에 서로 다른 목적을 과도하게 섞지 않는다.
