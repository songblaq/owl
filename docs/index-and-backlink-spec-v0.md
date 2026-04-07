# Index and Backlink Spec v0

작성일: 2026-04-03
상태: 보완 초안

## 1. 목적

Karpathy 원문에서 강조한 index, summary, backlink, linking 구조를 Agent Brain 규칙으로 구체화한다.

---

## 2. 기본 문서 구조

### Summary
- 하나의 raw source를 요약
- 원 source를 가리킴

### Concept
- 여러 summary를 묶어 하나의 주제/개념을 설명
- 관련 summary를 링크

### Index
- 특정 주제군의 진입점
- 하위 summary / concept / report 목록 제공

### Report
- 질문이나 조사 결과를 정리
- 관련 summary / concept / index 를 링크

---

## 3. Backlink 의식 규칙

- 각 compiled 문서는 관련 문서 섹션을 가진다.
- source -> summary -> concept -> report 간 연결을 명시한다.
- 자동 백링크 시스템이 없더라도, LLM이 관련 항목 목록을 유지하게 한다.

---

## 4. Index 유지 원칙

- 같은 주제의 문서가 3개 이상 쌓이면 index 생성 후보로 본다.
- summary가 여러 개 쌓이면 concept 문서 생성 후보로 본다.
- report가 반복되면 상위 index 또는 FAQ형 문서 후보로 본다.

---

## 5. 목적 효과

이 규칙은 compiled wiki를 단순 파일 더미가 아니라, 탐색 가능한 연결 지식 구조로 만든다.
