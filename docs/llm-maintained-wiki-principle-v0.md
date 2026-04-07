# LLM-Maintained Wiki Principle v0

작성일: 2026-04-03
상태: 보완 초안

## 1. 목적

Karpathy 원문에서 중요한 "위키는 사람이 직접 많이 손대기보다 LLM이 쓰고 유지한다"는 원칙을 명문화한다.

---

## 2. 원칙

- compiled wiki의 기본 작성 주체는 LLM이다.
- 사람은 방향 제시, 검토, 승인, 예외 수정에 집중한다.
- 사람이 세부 문서 구조를 매번 수동 정리하는 방식은 기본 모델이 아니다.
- LLM은 summary, concept, index, report, link maintenance 를 담당할 수 있다.

---

## 3. 이유

- 사람이 직접 모든 문서를 관리하면 확장성이 낮다.
- LLM이 유지보수 주체가 되면 filing loop 와 incremental maintenance 가 자연스럽게 이어진다.
- Agent Brain은 수동 위키보다 운영형 지식 시스템을 지향한다.

---

## 4. 예외

- 민감한 문서
- 최종 대외 배포 문서
- 표현 정밀도가 매우 중요한 문서
는 사람이 더 강하게 개입할 수 있다.
