---
description: Compile a raw file into summary/note via the owl-compiler subagent
argument-hint: <raw-file-path>
---

!`owl compile "$ARGUMENTS"`

위 출력은 compile 메타데이터 (대상 raw 의 naming, slug, 기대 compiled 경로) 입니다.

이제 **owl-compiler 서브에이전트**에 작업을 위임하세요 (`Task` tool, subagent_type="owl-compiler"):

owl-compiler 가 수행할 일:
1. 대상 raw 파일을 끝까지 읽기 (raw 는 절대 편집 금지)
2. `compiled-format-spec-v0.md` 형식에 맞춰 summary 작성
   - 필수 헤더: `상태:`, `유형:`, `출처:`, `작성일:`, `관련 항목:`
   - 본문: `핵심 주장`, `맥락`, `인용/근거`, `후속 작업`
3. 가치가 있다면 note 도 작성 (해석/갭/후속 질문)
4. `owl search` 로 기존 관련 compiled 문서를 찾고 cross-link 추가
5. `owl health` 로 새 issue 없는지 확인

위임 후 결과 보고:
- 생성된 파일 (path + 1줄 요약)
- 추가된 cross-link 대상
- health delta
- 참조한 정책 문서

**주의**: 이것은 단순 요약이 아닙니다. **위키의 한 노드**를 생성하는 것입니다 (Karpathy LLM Wiki 철학). 후속 작업, 관련 항목, 출처를 빠뜨리지 않아야 위키가 유지됩니다.
