# Wiki Linking Rules v0

작성일: 2026-04-03
상태: 긴급 보완 초안

## 1. 목적

Karpathy식 compiled wiki가 단순한 요약 파일 모음이 아니라 연결된 지식 구조가 되도록 linking 규칙을 정의한다.

---

## 2. 필수 요소

### 2.1 Summary
각 raw source는 최소 하나의 summary 문서를 가져야 한다.

### 2.2 Related Links
각 compiled 문서는 관련 문서 섹션을 가져야 한다.

### 2.3 Concept Article
여러 source가 같은 주제를 가리키면 concept 문서를 만든다.

### 2.4 Index
주제군에는 index 문서를 둔다.

### 2.5 Backlinks 의식
직접적인 자동 백링크 시스템이 없더라도, 관련 항목을 수동/LLM 생성 방식으로 유지한다.

---

## 3. 최소 규칙

- summary는 raw source를 가리킨다.
- concept는 여러 summary를 가리킨다.
- report는 관련 concept나 summary를 가리킨다.
- 각 문서는 다음 작업 또는 관련 항목을 포함한다.
