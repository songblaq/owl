# Tool Adapter Spec v0

작성일: 2026-04-03
상태: 긴급 보완 초안

## 1. 정의

Tool Adapter는 LKS가 KIB를 더 잘 활용하기 위해 연결하는 보조 도구 계층이다.

예:
- 검색 도구
- CLI 질의 도구
- 시각화 도구
- export 도구

---

## 2. 목적

- LLM이 더 큰 질의를 처리하게 한다.
- 지식 베이스 위에 검색/변환/시각화 능력을 더한다.
- 단순 문서 저장을 넘어 작업 가능한 시스템으로 확장한다.

---

## 3. 초기 원칙

- 도구는 KIB를 대체하지 않는다.
- 도구는 KIB와 compiled wiki를 보조한다.
- 가능한 경우 CLI handoff 형태를 우선 고려한다.
- 반복 사용되는 것은 추후 Agent CLI 승격 후보로 본다.

## 4. 우선 도입할 도구 유형

### 4.1 Wiki CLI Search
- compiled/wiki 위에 얹는 간단한 검색 도구를 우선 고려한다.
- 목적은 fancy한 RAG 대체가 아니라, LLM이 빠르게 관련 문서를 찾도록 보조하는 것이다.
- 초기 구현은 grep류, index 파일 탐색, 간단한 메타 검색 정도로 충분하다.
- 현재 최소 구현: `src/wiki_search.py`
- 예시:
  - `python3 src/wiki_search.py "priority query" --scope compiled`
  - `python3 src/wiki_search.py "filing loop" --scope all --limit 8`
  - `python3 src/wiki_search.py "Karpathy" --scope raw --type article`

### 4.2 Filing Helper
- 새 raw source를 받아 정해진 naming/template으로 filing 하는 보조 도구를 둘 수 있다.
- 패턴이 안정되면 `file this new doc to our wiki: (path)` 같은 얇은 인터페이스로 노출한다.

### 4.3 Render Helper
- markdown report, Marp slide, matplotlib figure를 생성하는 보조 함수/스크립트를 연결할 수 있다.
