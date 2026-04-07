# Discord Channel Ingest Plan v0

작성일: 2026-04-04
상태: 계획 초안

## 목적

장기적으로 Discord의 열려 있는 채널들을 Agent Brain source로 흡수하기 위한 우선순위와 방식 기준을 정한다.

## 우선순위
1. 연구/리서치 성격이 강한 채널
2. 오케스트레이션/운영 구조 채널
3. 프로젝트 지식 채널
4. 일반 대화 채널

## ingest 방식
- 연구 채널: raw log + compiled digest/summary
- 운영 채널: raw log + policy/architecture summary
- 프로젝트 채널: raw log + concept/index 생성 후보
- 일반 대화 채널: 필요 시 digest 중심으로 제한

## 원칙
- 채널 전체를 한 번에 넣지 않는다.
- 먼저 요약 가치가 높은 채널부터 샘플 ingest 한다.
- 민감도 높은 채널은 원문 보존 범위를 별도 판단한다.
- channel -> digest -> concept/index -> view 순서로 정리한다.

## 첫 후보
- #뉴스-긱뉴스
- Discord research 하위 채널
- 리서치 요청 / 오케스트레이션 관련 채널
- `#cli › agent-cli-first · kb-first` 스레드 (meta-governance / project-knowledge channel 예시)
