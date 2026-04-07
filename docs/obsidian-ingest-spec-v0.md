# Obsidian Ingest Spec v0

작성일: 2026-04-03
상태: 보완 초안

## 1. 목적

Karpathy 원문에서 언급된 Obsidian 기반 수집 방식을 Agent Brain 규칙으로 정리한다.

---

## 2. 핵심 원칙

- 웹 자료는 가능하면 markdown 형태로 보존한다.
- Obsidian Web Clipper 같은 도구를 사용해 기사/문서를 `.md`로 수집하는 방식을 우선 고려한다.
- 관련 이미지가 중요하면 로컬에 함께 저장해 LLM이 참조 가능하게 한다.
- 수집 결과는 raw source 로 취급한다.

---

## 3. 웹 기사 수집 규칙

### 3.1 기본 방식
- 웹 기사나 글은 가능하면 markdown으로 클립한다.
- 원 URL과 수집 날짜를 함께 기록한다.
- 제목과 짧은 메모를 남긴다.

### 3.2 저장 위치
- 본문 markdown: `raw/`
- 관련 이미지: `raw/` 하위 또는 추후 media 규칙에 따른 경로

### 3.3 메타 정보
최소한 다음은 남긴다.
- 원 URL
- 수집 날짜
- 제목
- source type = article / blog / note

---

## 4. 이미지 로컬 저장 원칙

- 본문 맥락 이해에 중요한 이미지는 로컬에 같이 저장한다.
- 나중에 LLM이 같은 디렉토리 또는 연결 경로에서 참조할 수 있게 한다.
- 이미지 출처와 설명이 가능하면 함께 남긴다.

---

## 5. Obsidian Surface 연결

- 수집된 raw markdown은 Obsidian surface에서 바로 열람 가능해야 한다.
- compiled 결과와 source를 한 surface에서 오갈 수 있어야 한다.
- 장기적으로는 raw, compiled, outputs, views를 같은 vault 또는 연결된 작업 표면으로 다루는 것을 목표로 한다.
