---
name: omb-search
description: Search the oh-my-brain knowledge vault. Use before answering knowledge questions. Runs 3-layer search (compiled narratives + atomic entries + graph expansion) and reads top results as evidence.
triggers:
  - "omb search"
  - "브레인 검색"
  - "지식 검색"
  - "search brain"
  - "search vault"
---

# OMB Search

지식 vault를 검색하고 결과를 근거로 답변한다.

## 사용법

```
/omb:search <query>
```

## 실행 순서

1. `omb search "<query>" --limit 10` 실행
2. 결과 파싱:
   - `[compiled]` 히트 → `~/omb/vault/akasha/compiled/<topic>.md` 읽기
   - `[entry]` 히트 → `~/omb/vault/akasha/entries/<slug>.md` 읽기 (상위 3개)
   - `[+graph]` 히트 → 그래프 확장 결과, 참고로 읽기
3. 읽은 문서를 근거로 답변
4. 매칭이 없거나 score < 3이면 결과 빈약함을 명시하고 `omb ingest`로 자료 추가 제안

## 출력 형식

- 검색 결과를 먼저 인용 (`> ` 블록)
- 그 다음 해석/답변
- 참고한 파일 경로 명시

## 규칙

- 답변 전 반드시 검색 먼저 실행
- 결과가 있어도 직접 읽기 전에 snippet만으로 답변하지 않을 것
- `--json` 플래그로 파싱이 필요하면 사용 가능
