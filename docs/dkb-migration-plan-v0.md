# DKB 마이그레이션 계획 v0

작성일: 2026-04-03
상태: 설계 초안

## 1. 목적

기존 4종 DKB 프로젝트 또는 그 개념 자산을 Agent Brain 안으로 재배치하기 위한 기준을 정한다.

현재는 실제 데이터가 많지 않을 수 있으므로, 우선은 **개념 마이그레이션**과 **뷰 마이그레이션** 중심으로 본다.

---

## 2. 기본 원칙

- 기존 DKB를 그대로 복제하지 않는다.
- Agent Brain의 LKS/KIB/MDV 구조에 맞게 재해석한다.
- 데이터가 없으면 억지로 파일을 만들기보다, profile/view 또는 placeholder 문서로 남긴다.

---

## 3. 예상 마이그레이션 대상

기존 논의 기준 예시:
- ai-store-dkb
- community-store-dkb
- research-dkb
- agent-prompt-dkb

---

## 4. 재배치 방향

### ai-store-dkb
- KIB source 후보 또는 compiled 기술 자산 후보
- Prompt View / General Meta View 와 연결 가능

### community-store-dkb
- KIB source 후보
- Community View에서 우선 해석

### research-dkb
- KIB compiled 또는 research 폴더와 연결
- Research View에서 우선 해석

### agent-prompt-dkb
- compiled prompt 자산 또는 Prompt View 와 연결

---

## 5. 초기 마이그레이션 전략

1. 기존 DKB별로 문서/개념/파일 존재 여부 확인
2. 실제 데이터가 있으면 KIB raw/compiled로 이동 후보 분류
3. 데이터가 없으면 MDV 문서로만 개념 이관
4. 중복되거나 모호한 것은 폐기 후보로 분리

---

## 6. 우선 생성할 MDV 문서 예시

- `views/research-view.md`
- `views/prompt-view.md`
- `views/community-view.md`
- `views/general-meta-view.md`

이 문서들은 처음에는 실제 데이터보다 개념적 뷰 정의로 시작할 수 있다.
