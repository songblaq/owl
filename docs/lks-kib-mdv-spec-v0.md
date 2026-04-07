# LKS / KIB / MDV 기능 명세 v0

작성일: 2026-04-03
상태: 초안

## 1. 상위 개념

### Agent Brain
Agent Brain은 프로젝트명이며, 전체 LLM Knowledge System(LKS)을 가리키는 상위 이름이다.

### LKS
LLM Knowledge System.
원본 자료 수집, 지식 컴파일, Obsidian surface 기반 열람, 질의응답, 산출물 환류, 린팅, 도구 연결, 메타 뷰 해석을 포함하는 전체 체계다.

다만 내부 구조는 의도적으로 단순하게 유지한다. 기본 단위는 `.md`, `.png`, `.csv`, `.py` 파일의 중첩 디렉토리이며, 복잡한 데이터베이스나 서비스 설계보다 파일 계약과 운영 루프를 우선한다.

---

## 2. 하위 구성

### KIB — Karpathy Info Base
역할:
- raw 데이터 저장
- compiled 데이터 저장
- 사람이 읽는 위키/노트/리포트 저장
- LLM이 다시 읽는 지식 기반 제공

핵심 기능:
- source ingest
- raw file storage
- compiled markdown/wiki storage
- report/note/image/link storage
- browse and retrieval

비유:
- 데이터베이스의 원 테이블 + 컴파일된 결과 테이블

### MDV — Multi Dimension View
역할:
- KIB를 여러 차원과 관점으로 바라보는 메타 해석 계층
- 차원값, 관계, 프로파일, 스키마를 통해 KIB를 재해석

핵심 기능:
- metadata enrichment
- dimension assignment
- relation mapping
- profile/schema views
- interpretation and exploration

운영 원칙:
- MDV는 선택적 확장이다.
- raw/compiled/wiki 루프가 먼저이며, MDV는 그 위에 얹는다.

비유:
- 데이터베이스의 분석 뷰, 의미 뷰, 프로파일 뷰

---

## 3. 데이터 흐름

1. 자료를 `raw/`에 수집한다.
2. LLM이 raw 자료를 읽고 `compiled/`에 정리된 지식 문서를 만든다.
3. KIB는 raw와 compiled를 함께 보관하고 열람하게 한다.
4. MDV는 KIB를 읽고 다차원 관점, 관계도, 해석 뷰를 만든다.
5. 질의응답, 리서치, 보고서, 산출물은 다시 KIB로 환류될 수 있다.

---

## 4. 기본 디렉토리 정책

### 프로젝트 경로
- `~/_/projects/agent-brain`

### 앱 데이터 경로
- `~/.agents/brain`

### 앱 데이터 하위 폴더
- `raw/`
- `compiled/`
- `views/`
- `research/`
- `outputs/`
- `inbox/`
- `logs/`
- `tmp/`
- `config/`

---

## 5. 초기 운영 원칙

- 원본은 가능한 파일 단위로 보존한다.
- LLM이 정리한 결과도 파일로 남긴다.
- raw와 compiled를 섞지 않는다.
- MDV는 우선 가벼운 뷰 계층으로 시작하고, 필요할 때만 강화한다.
- 필요 없으면 MDV는 축소하거나 제거할 수 있어야 한다.

---

## 6. 한 줄 정의

- **LKS**: 지식을 수집, 컴파일, 열람, 성장시키는 전체 체계
- **KIB**: raw와 compiled 지식을 보관하는 정보 기반
- **MDV**: 같은 지식을 여러 차원으로 바라보는 메타 뷰 계층
