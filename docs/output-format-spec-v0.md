# Output Format Spec v0

작성일: 2026-04-03
상태: 보완 초안

## 1. 목적

Karpathy 원문에서 말한 markdown, slides, images 같은 출력 형식을 Agent Brain 산출물 규칙으로 정리한다.

---

## 2. 지원할 기본 출력 형식

### 2.1 Markdown Documents
- summary
- note
- report
- comparison
- concept article

### 2.2 Slides
- Marp 기반 슬라이드 초안
- 발표용 요약 자료

### 2.3 Visual Outputs
- 차트
- 개념도
- matplotlib 이미지
- 기타 시각 자료

---

## 3. 출력 원칙

- 출력은 text/terminal 응답으로만 끝나지 않는다.
- 유의미한 출력은 파일로 남긴다.
- 출력은 다시 Obsidian surface에서 열람 가능해야 한다.
- 가치 있는 출력은 filing loop 를 통해 KIB로 환류한다.

---

## 4. 산출물 경로 원칙

초기에는 다음처럼 단순하게 둔다.
- markdown 출력: `compiled/`
- 조사 중간 출력: `research/`
- 슬라이드/시각 자료: `outputs/`

권장 세부 예시는 다음과 같다.
- Marp 슬라이드: `outputs/slides/`
- matplotlib 이미지: `outputs/figures/`
- 기타 시각화: `outputs/visuals/`

이들 출력은 Obsidian에서 바로 열람 가능해야 하며, 대응하는 summary/report 문서에서 다시 참조되어야 한다.

---

## 5. 후속 과제

- Marp 슬라이드 템플릿 정의
- 시각 자료 naming 규칙 정의
- output별 메타 정보 템플릿 정의
- 질의 응답 결과를 compiled/report와 outputs에 함께 filing 하는 규칙 고정
