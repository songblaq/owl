---
description: Search owl vault and have Claude organize the results
argument-hint: <query>
---

!`owl search "$ARGUMENTS" --json --limit 10`

위 검색 결과(JSON)를 정리해주세요. owl 은 Karpathy 식 LLM-maintained wiki 이며, 검색 결과는 단순 grep 이 아니라 위키 문서들의 토큰 스코어 매칭입니다.

다음 형식으로 정리:

1. **상위 5개 결과**를 표로 정리 (path, type, title, snippet)
2. **주제 클러스터**: 결과들이 어떤 주제로 묶이는지 1-2 문장
3. **추천 액션**:
   - 더 깊이 읽을 가치가 있는 문서가 있으면 제시
   - 같은 주제에 여러 compiled 문서가 있으면 concept/index 승격 후보로 표시 (`/owl-promote`)
   - 결과가 없거나 빈약하면 `raw/` 에 자료 추가가 필요한지 제안

검색이 0건이거나 모두 점수가 낮으면 사용자에게 vault 에 관련 자료가 부족할 수 있다고 알려주고 `inbox/` 에 자료 추가를 제안하세요.
