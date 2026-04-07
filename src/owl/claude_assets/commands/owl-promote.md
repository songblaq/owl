---
description: Promote raw/summary clusters into concept or index documents
argument-hint: <subject-or-term>
---

!`owl health --json`

위 health 결과에서 다음 두 규칙에 주목하세요:
- `concept-candidate-missing` — 동일 term 이 ≥2 summary 에서 등장하지만 concept 없음
- `index-candidate-missing` — 동일 subject 가 ≥3 compiled 문서에 등장하지만 index 없음

만약 사용자가 인자로 특정 term/subject 를 줬다면 (`$ARGUMENTS`), 그 항목과 관련된 후보만 다루세요. 인자가 비어 있다면 모든 promotion 후보를 살펴보세요.

이제 **owl-librarian 서브에이전트**에 promotion 작업을 위임하세요 (`Task` tool, subagent_type="owl-librarian"):

owl-librarian 이 수행할 일:
1. 대상 term/subject 와 관련된 모든 summary/note 파일 수집 (`owl search`)
2. 각 파일이 정말 같은 개념인지 확인 (false positive 거르기)
3. concept 승격 시:
   - `compiled/YYYY-MM-DD-<slug>-concept.md` 생성
   - 정의, 요약 inbound link, 관련 개념 cross-link 포함
4. index 승격 시:
   - `compiled/YYYY-MM-DD-<slug>-index.md` 생성
   - 모든 관련 compiled 문서를 항목별로 나열
5. 기존 summary 들에서 새 concept/index 로의 cross-link 추가
6. `owl health` 재실행해 delta 보고

**주의**: 너무 빨리 promote 하지 마세요. 진짜 wiki 노드로 가치 있을 때만 만듭니다. 의심스러우면 사용자에게 묻기.
