# Incremental Maintenance Spec v0

작성일: 2026-04-03
상태: 보완 초안

## 1. 목적

Karpathy 원문에서 말하는 incremental compile / incremental maintenance 개념을 owl 운영 규칙으로 정리한다.

---

## 2. 정의

owl의 compiled wiki는 한 번 만들고 끝나는 정적 산출물이 아니라, raw source 추가와 질의응답, health check, filing loop에 따라 계속 갱신되는 지식 구조다.

---

## 3. 원칙

- 새 raw source가 들어오면 기존 compiled 문서도 다시 검토할 수 있다.
- 새 summary가 생기면 관련 concept/index 문서도 갱신 후보가 된다.
- 질의응답 결과는 기존 문서를 보강할 수 있다.
- health check는 누락/불일치/새 연결 후보를 찾아 incremental maintenance 를 유도한다.
- 사람이 매번 수동 편집하기보다 LLM 유지보수를 우선한다.

---

## 4. 갱신 트리거

### 4.1 source 추가
새 article, paper, repo, log 가 들어왔을 때

### 4.2 질문 발생
새로운 질문이 기존 구조의 공백을 드러낼 때

### 4.3 health check 결과
누락, 충돌, 연결 후보가 발견될 때

### 4.4 output filing
새 report, note, slides 가 다시 KIB로 들어올 때

---

## 5. 운영 효과

이 규칙을 통해 owl은 단발성 요약 저장소가 아니라, 점진적으로 정리 수준이 높아지는 운영형 지식 베이스가 된다.
