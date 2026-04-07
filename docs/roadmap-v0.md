# Agent Brain 로드맵 v0

작성일: 2026-04-03
상태: 설계 초안

## 1단계 — 기본 골격
- 프로젝트 구조 생성
- 앱 데이터 경로 생성
- 핵심 명세 문서 작성
- source 보관 체계 구축

## 2단계 — KIB 운용 시작
- inbox/raw/compiled 흐름 고정
- 몇 개의 샘플 자료 수집
- 첫 compile 문서 생성
- report/note/index 예시 확보

## 3단계 — LKS 질의 루프
- compiled 문서를 바탕으로 Q&A
- 질의 결과를 다시 filing
- linting 시도

## 4단계 — MDV 최소 도입
- Research View
- Prompt View
- Community View
- General Meta View

## 5단계 — DKB 유산 마이그레이션
- 기존 DKB 개념 문서 정리
- 어떤 것은 KIB source로 이동
- 어떤 것은 MDV 관점 정의로 이동
- 어떤 것은 폐기/보류로 분류

## 6단계 — 자동화 강화 (진행 중, 2026-04-07; owl 리네임 동일자)
- ✓ `owl` CLI (search, health, ingest, compile, file, init, setup, status, use, hook)
- ✓ Claude Code 5개 hook (`owl hook <name>` 디스패처)
- ✓ 7개 슬래시 명령 (`/owl-search`, `/owl-health`, ...)
- ✓ 3개 owl-* 서브에이전트 (`owl-librarian`, `owl-compiler`, `owl-health`)
- ✓ `curl | sh` 설치 + interactive `owl setup`
- ✓ OpenClaw L0 canonical 심링크 보존
- ✓ Karpathy 의 LLM Wiki gist 를 origin source 로 박제 (`raw/2026-04-07-karpathy-llm-wiki-gist-raw.md`)
- 명세: `docs/operational-layer-spec-v0.md`

## 7단계 — 후속 (out of scope of v0)
- `brain pack` — vault portable tarball
- inbox watcher (자동 ingest)
- MDV view 자동 생성 도구
- Windows 지원
