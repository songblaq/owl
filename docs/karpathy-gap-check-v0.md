# Karpathy 원문 대비 누락 요소 점검 v0

작성일: 2026-04-03
상태: 점검 초안

## 1. 목적

초기 Agent Brain 설계 문서가 Karpathy 원문에서 어떤 요소를 충분히 반영했는지, 무엇이 빠졌는지 점검한다.

---

## 2. 반영된 요소

- raw source 보관
- LLM compile 개념
- compiled markdown 지식 문서
- KIB와 MDV의 역할 분리
- Q&A 및 산출물 환류의 기본 개념

---

## 3. 덜 반영된 요소

### 3.1 Surface / IDE 관점
Karpathy는 Obsidian을 단순 뷰어가 아니라 raw, compiled, visualization을 함께 보는 프론트엔드로 설명한다.

### 3.2 Filing loop
답변과 산출물을 다시 위키에 넣는 누적 성장 루프가 매우 중요하지만, 현재 문서에는 상대적으로 약하다.

### 3.3 Linting / health checks
지식 베이스 건강 점검, 누락 보완, 흥미로운 연결 제안 기능을 별도 운영 루프로 강조해야 한다.

### 3.4 Extra tools
작은 검색 엔진이나 CLI 도구를 LLM이 활용하는 구조가 Karpathy 글의 핵심 중 하나인데, 현재 설계에는 약하게만 반영됐다.

### 3.5 Further explorations
synthetic data generation 및 finetuning 가능성은 당장 구현 요소는 아니지만, 장기 방향으로 남길 가치가 있다.

---

## 4. 보완 제안

- workflow 문서에 surface / filing / linting / tools 섹션 강화
- roadmap에 health check와 tool adapter 항목 추가
- term dictionary에 surface, filing loop, health check, tool adapter 용어 추가
- 장기 연구 항목으로 synthetic data / finetuning 메모 추가
