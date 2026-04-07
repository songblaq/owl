# Obsidian Surface Spec v0

작성일: 2026-04-03
상태: 긴급 보완 초안

## 1. 정의

Obsidian은 owl의 기본 surface이자 IDE frontend다.

이는 단순 노트 앱이 아니라 다음을 함께 다루는 작업 표면이다.
- raw source
- compiled wiki
- derived visualizations
- output artifacts

---

## 2. 역할

### 2.1 열람 표면
사람은 Obsidian에서 raw, compiled, views, reports를 함께 탐색한다.

### 2.2 LLM 유지보수 결과의 확인 표면
위키는 사람이 직접 많이 수정하는 것이 아니라, LLM이 작성·유지한 결과를 사람이 검토하고 활용하는 방향을 기본 원칙으로 한다.

### 2.3 파생 표현 표면
슬라이드, 시각 자료, 요약 문서 같은 산출물을 다시 Obsidian에서 열람한다.

---

## 3. 원칙

- Obsidian은 선택 사항이 아니라 현재 기본 surface다.
- raw와 compiled를 한 vault/작업 표면에서 함께 본다.
- LLM 유지보수가 우선이고 수동 편집은 보조적이다.
- output도 다시 surface에서 검토 가능해야 한다.

---

## 4. 추후 보완 항목

- Web Clipper 수집 규칙
- 이미지 로컬 저장 규칙
- Marp / slides 연계 규칙
- vault 구조와 앱 데이터 경로의 연결 방식
