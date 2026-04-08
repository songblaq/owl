# owl 폴더 규약 v0

작성일: 2026-04-03 (owl 리네임 반영: 2026-04-08)
상태: 초안

## 1. 프로젝트 폴더
- `~/_/projects/owl`

### 하위 폴더
- `docs/`: 구조, 명세, 소스 문서
- `plans/`: 계획 문서
- `examples/`: 예시 데이터
- `src/`: 구현 코드
- `AGENTS.md`: 단일 스키마/운영 계약 문서

## 2. 앱 데이터 폴더
- `~/owl-vault`

### External reference subtrees (예외)

`raw/` 하위에는 owl 의 `YYYY-MM-DD-<slug>-raw.md` 파일명 계약을 따르지 않는 **external reference subtree** 가 존재할 수 있다. 이들은 다른 시스템에서 import 된 self-contained knowledge pack 으로, 자체 내부 구조 (manifest, indexes, pages 등) 를 유지한다.

현재 등록된 external reference subtrees:

- **`raw/atlas/`** — ARIA 의 "Constella System Knowledge Pack". `compiled/atlas-external-reference-index.md` 참조.

이 subtree 들은:
- `owl health` 의 `missing-summary-for-raw` 등 raw-based 룰에서 자동 제외됨 (`src/owl/health.py` 의 `EXTERNAL_REFERENCE_SUBTREES` 상수)
- 개별 `compiled/*-summary.md` 대신 **하나의 reference index doc** (`compiled/<name>-external-reference-index.md`) 로 wiki 에 진입점 제공
- 원본 구조 무변경 (raw 불변 원칙 유지)

새 external reference subtree 를 import 하면:
1. `EXTERNAL_REFERENCE_SUBTREES` 에 추가
2. `compiled/<name>-external-reference-index.md` 작성
3. 이 섹션 (folder-policy) 에 등록

### 하위 폴더 의미
- `inbox/`: 아직 분류되지 않은 수집 대기 자료
- `raw/`: 원본 자료 보관
- `compiled/`: LLM이 편찬한 정리 문서
- `views/`: MDV 산출물
- `research/`: 리서치 중간 산출물
- `outputs/`: 슬라이드, 이미지, 시각화 같은 파생 산출물
- `logs/`: 작업 로그
- `tmp/`: 임시 파일
- `config/`: 설정 파일

## 3. 기본 원칙
- raw와 compiled는 섞지 않는다.
- source는 가능한 원본 상태로 보존한다.
- compiled는 사람이 읽기 쉬운 마크다운 중심으로 유지한다.
- views는 원본 데이터를 덮어쓰지 않고 해석 결과만 저장한다.
- research는 최종본이 아니라 진행 중 자료를 담는다.
- 이미지, 슬라이드, 시각화는 `outputs/`에 두고, 가치 있는 것은 compiled 문서에서 다시 참조·파일링한다.
- 구조 설명과 파일 계약은 여러 schema 파일로 쪼개기보다 루트 `AGENTS.md`를 기준으로 유지한다.
