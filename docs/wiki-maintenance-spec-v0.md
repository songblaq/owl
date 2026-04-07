# Wiki Maintenance Spec v0

작성일: 2026-04-03
상태: 신규 초안

## 1. 목적

Agent Brain wiki를 단순한 요약 파일 모음이 아니라, LLM이 유지하는 점진적 지식 구조로 관리하기 위한 규칙을 정의한다.

## 2. 핵심 가정

- raw source는 계속 쌓인다.
- compiled wiki는 한 번 완성되는 산출물이 아니라 점진적으로 유지보수된다.
- fancy한 RAG보다 summary, index, concept, backlink 유지가 먼저다.
- wiki가 커질수록 Q&A 품질은 문서 간 연결 품질에 좌우된다.

## 3. 최소 유지 단위

각 source는 가능하면 다음을 가진다.
- raw source
- summary 문서
- note 문서

주제군이 커지면 추가한다.
- concept 문서
- index 문서
- report 문서

## 4. 유지 규칙

### 4.1 Summary 유지
- 각 raw source는 최소 하나의 summary를 가진다.
- summary는 source가 실제로 말하는 내용을 정규화한다.
- summary에는 관련 항목과 다음 작업을 남긴다.

### 4.2 Note 유지
- note는 해석, 관찰, 누락, 후속 질문을 담는다.
- summary와 note의 역할을 섞지 않는다.

### 4.3 Concept 문서 승격
- 서로 다른 source 2개 이상이 같은 주제를 가리키면 concept 후보로 본다.
- concept는 source 하나를 다시 말하는 문서가 아니라, 주제 자체를 설명해야 한다.

### 4.4 Index 문서 유지
- 동일 주제군 문서가 늘어나면 index를 만든다.
- index는 entry point 역할을 하며 관련 summary, concept, report를 묶는다.

### 4.5 Backlink 유지
- 자동 시스템이 없어도 문서 안에서 관련 항목과 관련 자료를 유지한다.
- concept는 summary를, report는 관련 concept/summary를, summary는 raw source를 가리킨다.

## 5. 품질 기준

- 제목만 있고 source가 없는 문서는 피한다.
- source path 없이 주장만 있는 문서는 피한다.
- 다음 작업 또는 관련 항목이 없는 문서는 확장성이 낮다.
- 중복 summary가 생기면 분화 이유를 명확히 하거나 통합한다.

## 6. 성장 기준

위키가 어느 정도 커지면(대략 100개 문서, 40만 단어 규모 가이드라인) summary/index/concept 유지 만으로도 실용적인 Q&A가 가능하다고 본다.

## 7. 유지보수 루프

```text
new raw -> summary/note 생성 -> concept/index 연결 -> health check -> missing link 보완 -> QA/output -> filing
```

## 8. 후속 과제

- index 템플릿 정의
- concept 문서 템플릿 정의
- backlink 점검용 간단한 CLI search/lint 도구 연결
