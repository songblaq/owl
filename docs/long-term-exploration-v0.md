# Long-Term Exploration v0

작성일: 2026-04-03
상태: 장기 메모 초안

## 1. 목적

Karpathy 원문에서 언급된 장기 확장 방향을 기록한다.

---

## 2. 장기 탐색 주제

### 2.1 Synthetic Data Generation
- 축적된 KIB와 compiled wiki를 바탕으로 합성 데이터 생성 가능성 검토
- 학습/검증용 파생 데이터셋 설계 가능성 검토

### 2.2 Finetuning
- 단순 컨텍스트 주입이 아니라 모델 가중치 수준에서 지식 반영 가능성 검토
- 어떤 범위의 지식이 finetuning 대상이 될지 검토

### 2.3 Knowledge-to-Weights 전략
- 언제 컨텍스트 기반이 충분한지
- 언제 장기 학습이 더 나은지
- Agent Brain이 장기적으로 어떤 수준까지 확장될지 탐색

---

## 3. 현재 원칙

- 이 문서는 당장 구현 계획이 아니라 연구 메모다.
- 현재 우선순위는 KIB/LKS 운영 안정화다.
- synthetic data / finetuning 은 장기 연구 항목으로만 유지한다.
