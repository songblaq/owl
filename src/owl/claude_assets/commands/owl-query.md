---
description: Big-question workflow — search, build temporary wiki, draft report
argument-hint: <big question>
---

!`owl search "$ARGUMENTS" --json --limit 20`

위 검색 결과는 사용자의 큰 질문에 관련된 vault 자료입니다. 이제 `workflow-v0.md` §4 의 "큰 질문" 패턴을 실행하세요:

## 단계 1: 자료 모으기
검색 결과 중 관련도 높은 문서들을 식별. 부족하면 `owl search` 를 다른 키워드로 추가 실행해서 확장하세요.

## 단계 2: 임시 wiki 만들기
`research/` 에 다음 파일을 작성:
- `research/YYYY-MM-DD-<question-slug>/` 디렉토리 생성
- `research/.../sources.md` — 모은 자료 목록
- `research/.../draft.md` — 초안 답변

## 단계 3: 린트 + 보강
- 빠진 자료가 있으면 inbox 또는 raw 에 추가 필요한지 사용자에게 묻기
- 답변에 인용 없는 주장이 있으면 raw 에서 근거 추출

## 단계 4: 최종 report
완성되면:
- `compiled/YYYY-MM-DD-<question-slug>-report.md` 생성
- 모든 인용 raw/compiled 문서 cross-link
- `outputs/` 에 시각화/슬라이드가 있으면 함께 링크
- 필수 헤더 포함 (`상태:`, `유형: report`, `출처:`, `작성일:`, `관련 항목:`)

## 단계 5: filing loop
- report 가 vault 의 일부가 됐으니 `owl health` 재실행해 새 issue 없는지 확인
- 향후 같은 질문이 재발하면 이 report 가 답변의 1차 source 가 됨

**중요**: 답변만 출력하고 끝내지 마세요. 항상 `compiled/` 에 report 를 박제해야 wiki 가 성장합니다. 이것이 RAG 가 아니라 **잘 유지된 wiki** 가 답이라는 Karpathy 철학의 핵심입니다 (origin source: `raw/2026-04-07-karpathy-llm-wiki-gist-raw.md`).
