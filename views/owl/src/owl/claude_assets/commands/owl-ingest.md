---
description: Ingest a candidate file into the owl vault as raw
argument-hint: <path-to-file>
---

!`owl ingest "$ARGUMENTS"`

위 출력은 ingest CLI 의 결정성 결과입니다 (파일이 raw/ 로 이동/복사된 결과).

이제 **owl-librarian 서브에이전트**에 작업을 위임해서 wiki 컨트랙트에 맞게 정리하세요 (`Task` tool, subagent_type="owl-librarian"):

owl-librarian 이 수행할 일:
1. 새로 들어온 raw 파일의 naming convention 검증 (`YYYY-MM-DD-<slug>-raw.md`)
2. 필요시 owl-compiler 호출해서 summary/note 생성
3. 기존 compiled 문서와의 cross-link 추가
4. `owl health` 재실행해 새 issue 가 생기지 않았는지 확인

위임 후 결과를 사용자에게 보고:
- 이동된 raw 파일 경로
- 생성된 compiled 문서 (있다면)
- 추가된 cross-link
- health delta

**주의**: raw 파일은 ingest 후 절대 편집하지 않습니다. 모든 LLM 작업은 compiled/ 에서만.
