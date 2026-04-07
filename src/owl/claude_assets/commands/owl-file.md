---
description: File an output (Q&A result, slide, figure) back into the wiki (filing loop)
argument-hint: <output-path> <kind>
---

!`owl file "$ARGUMENTS"`

위는 filing CLI 의 결정성 결과입니다 (파일이 outputs/ 의 적절한 하위 (slides|figures|visuals) 로 이동된 결과).

이제 **owl-librarian 서브에이전트**에 환류 작업을 위임하세요 (`Task` tool, subagent_type="owl-librarian"):

owl-librarian 이 수행할 일:
1. 이동된 output 파일이 어떤 compiled 문서와 연관되는지 식별
2. 해당 compiled 문서 (주로 report) 에 `outputs/...` 링크 추가
3. 필요시 새 report 문서 생성 (`*-report.md`) 해서 output 을 wiki 에 박제
4. `owl health` 로 `report-missing-output-links`, `report-broken-output-link` 가 해결됐는지 확인

이것이 **filing loop** 입니다 — Q&A 결과나 산출물이 outputs 폴더에 머물지 않고 다시 compiled wiki 로 환류되어 다음 질문의 답변 자료가 됩니다 (Karpathy 가 강조한 "good answers can be filed back into the wiki" 원칙).

위임 후 결과 보고:
- 이동된 output 경로
- 갱신된 compiled 문서 (path)
- 추가된 링크
- health delta
