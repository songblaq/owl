# owl 용어 사전 v0

작성일: 2026-04-03
상태: 초안

## 상위 개념

### owl
에이전트가 사용하는 전체 지식 체계 프로젝트 이름.

### LKS — LLM Knowledge System
원본 수집, 지식 컴파일, 지식 보관, 열람, 질의응답, 환류, 린팅, 메타 뷰를 포함하는 전체 시스템.

## 하위 계층

### KIB — Karpathy Info Base
raw 자료와 compiled 지식을 함께 보관하는 정보 기반.

### MDV — Multi Dimension View
같은 KIB를 여러 차원과 관점으로 해석하는 메타 뷰 계층.

## 데이터 구분

### Raw
원본 자료. 아직 편찬되기 전의 입력 자산.

### Compiled
LLM이 raw를 읽고 구조화한 결과물.

### View
원본 또는 compiled를 다시 해석한 관점 산출물.

### Research
조사 중간 산출물 또는 후속 조사 문맥.

### Surface
raw, compiled, visualization, output을 함께 열람하는 작업 표면.

### Filing Loop
질의응답과 산출물을 다시 지식 베이스에 넣어 누적 성장시키는 루프.

### Health Check / Linting
불일치, 누락, 연결 후보를 점검하는 운영 행위.

### Tool Adapter
검색, CLI, 시각화 도구처럼 LKS에 연결되는 보조 도구 층.

### Verification
변경 전후 영향과 실제 반영 여부를 확인하는 검증 행위.

### Prevention Rule
반복 실수나 누락을 다시 발생시키지 않기 위해 문서화된 재발 방지 규칙.

### Operating Principle
특정 개별 작업 지침이 아니라 에이전트의 기본 사고 흐름과 행동 우선순위를 규정하는 원칙. 예: CLI First, 문서 우선 기록, KB 우선 활용.

### CLI-only / LLM-only / Hybrid
작업을 실행 관점에서 분류하는 세 구분.
- CLI-only: 절차화 가능한 실행 작업
- LLM-only: 해석, 판단, 추론, 생성이 본질인 작업
- Hybrid: LLM과 CLI가 함께 필요한 작업

## 핵심 행위

### Ingest
자료를 받아 저장소에 넣는 것.

### Compile
LLM이 raw 자료를 읽고 지식 문서로 편찬하는 것.

### File / Re-file
산출물을 다시 지식 베이스에 환류하는 것.

### Linting
불일치, 누락, 추가 연결 후보를 점검하는 것.

### View Generation
같은 지식을 특정 관점으로 다시 읽을 수 있게 만드는 것.
