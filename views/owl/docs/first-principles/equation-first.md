# owl 연계 문맥에서의 equation-first

## 문서 목적
이 문서는 공통 규약 `~/.agents/first-principles/equation-first.md`를 owl 프로젝트 문맥에 연결하기 위한 브리지 문서다.

즉, equation-first를 단순 원칙으로 끝내지 않고 owl 내부 구조, 문서화 방식, runtime 적용 흐름과 연결한다.

## 위치
- 공통 canonical 규약: `~/.agents/first-principles/equation-first.md`
- 프로젝트 설계/적용 문맥: `~/_/projects/oh-my-brain/views/owl/docs/first-principles/equation-first.md`
- 운영 데이터/지식화 결과: `~/owl-vault/`

## owl에서 다뤄야 하는 핵심 질문
1. 어떤 판단이 수식화 가능한가?
2. 어떤 판단은 수식화하면 안 되는가?
3. 점수와 verdict를 어떤 schema로 보관할 것인가?
4. 런타임(OpenClaw, ARIA, AgentHive 등)별 적용 차이는 무엇인가?
5. 실제 적용 후 어떤 실패와 교정이 발생했는가?

## 추천 문서 축
- concept: equation-first 개념 정의
- report: 특정 런타임 적용 보고서
- note: 빠른 설계 메모
- index: 관련 수식/패턴/적용처 인덱스

## 추천 데이터 축
- priority scoring
- routing scoring
- evidence quality scoring
- ingest suitability scoring
- directive vector scoring
- verdict policy mapping

## DKB / Directive Graph와의 관계
DKB와 DG는 이미 다차원 벡터, 점수화, verdict 분리라는 구조를 갖고 있다.
owl에서 equation-first를 다룰 때는 이를 단순 참고가 아니라 다음처럼 일반화하는 것이 좋다.

- DKB/DG = directive artifact용 선행 수식화 사례
- equation-first = 그 원리를 agent 운영 전반으로 확장하는 상위 규약
- owl = 그 확장 결과를 저장·환류·재편하는 지식 운영 계층

## OpenClaw 적용 브리지
OpenClaw 쪽에는 다음 항목을 우선 붙이는 것이 적절하다.
- task priority formula
- subagent suitability formula
- risk gate
- evidence sufficiency check
- response mode recommendation

## 운영 원칙
- 공통 규약은 `.agents/first-principles`에 둔다.
- 구체 사례와 학습은 owl에 둔다.
- 프로젝트 차원의 설계 논의는 `~/_/projects/oh-my-brain/views/owl/docs`에서 관리한다.

## 다음 단계 제안
1. owl에 `equation-first-concept` compiled 문서 생성
2. OpenClaw 대상 초기 적용 함수 3개 선정
3. first-principles 인덱스 문서 생성
4. equation-first와 cli-first / dkb-first 관계도 작성

상태: bridge draft v0
최종 갱신: 2026-04-04
