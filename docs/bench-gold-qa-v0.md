---
id: bench-gold-qa-v0
status: draft-skeleton
created: 2026-04-18
owner: luca (domain knowledge required)
consumer: docs/bench-design-2026-04-18.md axis 3 (query quality)
---

# omb bench — Gold Q&A v0 (50 문항)

`docs/bench-design-2026-04-18.md` axis 3 (query quality) 의 gold set. 5 카테고리 × 10 문항.

## 사용법

- 각 문항에 **Q / Expected / Citation / Scoring note** 4 필드.
- `Expected` 는 사용자(Luca) 가 직접 채움 — LLM이 짐작 금지. 현재 버전은 **질문 슬롯만** skeleton.
- `Citation` 은 `[[entities/…]]` 또는 `[[syntheses/…]]` 페이지 경로. wiki 에 해당 근거가 실재해야 retrieval 축 비교 가능.
- scoring: 5/4/3/2/1/0 (→ `docs/bench-design-2026-04-18.md` axis 3).

## 채움 순서 (사용자 세션 가이드)

1. 카테고리 A (HomeLab) → 가장 최근 knowledge 라 쉬움
2. 카테고리 D (드리프트) → `~/omb/brain/live/log.md` 참조
3. 카테고리 B (프로젝트) → 한글 매핑 테이블 기반
4. 카테고리 C (설계 패턴) → REZERO / feedback memory
5. 카테고리 E (메타) → 2-3h 세션 마지막

---

## [A] HomeLab infra (10)

1. **Q**: DGX Spark 기본 LLM 허브의 primary/backup 엔드포인트와 각 모델은?
   **Expected**: _( Luca 작성 — 예: `:8000 Qwen3.6-35B-A3B-Q8_0, :8001 Qwen3.5-122B-A10B-UD-IQ3_S`)_
   **Citation**: `[[entities/dgx-spark]]`
   **Scoring**: 둘 다 맞고 포트/모델명 정확 = 5

2. **Q**: iMac 의 Ollama 역할은 현재 어떻게 바뀌었고, 이유는?
   **Citation**: `[[syntheses/2026-04-18-homelab-5axis-report]]`

3. **Q**: NAS (DS923+) 의 NIC1 (.178) 상태는? 최근 조치는?
   **Citation**: `[[entities/homelab]]` 또는 drift log

4. **Q**: mac-studio 에서 현재 실행 중인 모델 목록은?
   **Citation**: `[[entities/mac-studio]]`

5. **Q**: 5090-WSL 의 엔드포인트가 아직 not-ready 인 근거는?
   **Citation**: `[[syntheses/2026-04-18-homelab-5axis-report]]`

6. **Q**: OpenClaw 의 primary provider 체인은?
   **Citation**: `[[entities/openclaw]]`

7. **Q**: homelab 전체 네트워크 서브넷과 주요 호스트 IP 매핑은?
   **Citation**: `[[entities/homelab]]`

8. **Q**: DGX 의 메모리·GPU 사양 (GB10 Blackwell) 과 현재 활용률은?
   **Citation**: `[[entities/dgx-spark]]`

9. **Q**: homelab 에서 현재 idle 상태로 강등된 장비와 역할은?
   **Citation**: `[[syntheses/2026-04-18-homelab-5axis-report]]`

10. **Q**: 임베딩 모델이 어떤 호스트로 단일화됐는가?
    **Citation**: `[[syntheses/2026-04-18-homelab-5axis-report]]`

## [B] 프로젝트 (10)

11. **Q**: "칼라" 프로젝트의 실제 경로와 한줄 설명?
    **Citation**: `CLAUDE.md` 한글 매핑 + `[[entities/khala]]`

12. **Q**: Constella 상태와 deprecation 날짜, 대체 시스템은?
    **Citation**: `[[entities/constella]]`

13. **Q**: OpenClaw ↔ KiraClaw ↔ Hermes 관계는?
    **Citation**: `[[concepts/…]]` 또는 각 entity

14. **Q**: oh-my-brain 의 active vault 는? INACTIVE 레이어는?
    **Citation**: `[[entities/oh-my-brain]]` + REZERO doc

15. **Q**: TestForge 가 해결하려는 문제와 현재 단계는?
    **Citation**: `[[entities/testforge]]`

16. **Q**: DEOS 의 정체성 한 줄?
    **Citation**: `[[entities/deos]]`

17. **Q**: AgentHive 와 ARIA 의 차이는?
    **Citation**: 해당 entities

18. **Q**: ORBIT 이 주소로 존재하는 repo 와 최근 활동 요약?
    **Citation**: `[[entities/orbit]]`

19. **Q**: 각 프로젝트의 commit identity 는? (git author)
    **Citation**: `user_git_identity` memory + global config

20. **Q**: Hermes-Agent 가 5090-WSL 에서 failing 상태인 이유?
    **Citation**: syntheses 최신본

## [C] 설계 패턴 (10)

21. **Q**: Re:Zero 2026-04-18 의 5 규칙을 순서대로?
    **Citation**: `[[REZERO-2026-04-18]]` (docs) + `feedback_design_humility`

22. **Q**: 왜 tier / contract / validator stack 을 폐기했나?
    **Citation**: REZERO doc + `feedback_design_humility`

23. **Q**: Karpathy LLM-wiki 원안의 핵심 3 가지 특징?
    **Citation**: `[[concepts/llm-wiki-pattern]]`

24. **Q**: omb 의 INACTIVE 레이어 (akasha, sandbox) 의 존재 이유는?
    **Citation**: REZERO + `project_vault_experiments`

25. **Q**: capsule 이 akasha 와 다른 핵심 차이는?
    **Citation**: CLAUDE.md project section + capsule AGENTS.md

26. **Q**: drift_audit 가 감지하는 3 축은? Phase 5 는 무엇?
    **Citation**: `tools/drift_audit.sh` 주석

27. **Q**: "evidence 동반" 원칙이란?
    **Citation**: `feedback_evidence_with_records`

28. **Q**: wiki incremental 유지 vs 일괄 rebuild — 어떤 선택이고 왜?
    **Citation**: REZERO doc

29. **Q**: "source 불변" 규칙의 구체적 경로와 예외는?
    **Citation**: REZERO 규칙 1

30. **Q**: omb 외부 인터페이스 규약 — 사용자에게 노출하면 안 되는 단어는?
    **Citation**: REZERO doc + 프로젝트 CLAUDE.md

## [D] 드리프트 이력 (10)

31. **Q**: 2026-04 초에 발견된 drift 3건 (Constella / ARIA / ClawVerse) 의 각 원인은?
    **Citation**: `tools/drift_audit.sh` 주석 + 각 entity

32. **Q**: gemma4 / bge-m3 / custom-provider 가 models.json 에서 제거된 날짜와 이유?
    **Citation**: drift log

33. **Q**: `collect.sh` 가 `plan-next.md` 를 잘못 잡던 버그의 해결 방법은?
    **Citation**: 2026-04-18 rename commit

34. **Q**: 중복 raw 파일 3건 삭제 근거는?
    **Citation**: REZERO Phase 1

35. **Q**: supergemma4-uncensored 는 현재 어느 호스트에만 남아있나?
    **Citation**: endpoint-health 결과 (2026-04-18)

36. **Q**: ClawVerse 의 현재 상태와 후속 시스템은?
    **Citation**: `[[entities/clawverse]]`

37. **Q**: 5axis-report 의 5 축은?
    **Citation**: `[[syntheses/2026-04-18-homelab-5axis-report]]`

38. **Q**: CLAUDE.md 한글 매핑에서 2026-04-18 이후 업데이트된 항목?
    **Citation**: git log + CLAUDE.md

39. **Q**: 2026-04 개선 이전의 tier 구조는 몇 계층이었나?
    **Citation**: deprecated docs

40. **Q**: feedback_omb_search_reflex 가 만들어진 계기는?
    **Citation**: 해당 memory

## [E] 메타 (10)

41. **Q**: omb 의 CLI 는 왜 `omb / owl / cairn` 3 이름을 거쳐 `omb` 로 수렴했나?
    **Citation**: `feedback_owl_cli_naming`

42. **Q**: Re:Zero 라는 명명의 의미는?
    **Citation**: REZERO doc preamble

43. **Q**: 모든 응답 한국어 규칙의 근거는?
    **Citation**: `feedback_language`

44. **Q**: omb 의 drift 감지가 자동화 되지 못하고 수동 주간 실행인 이유는?
    **Citation**: REZERO 규칙 4 (설계 겸손)

45. **Q**: bench v0 의 3 축은? tier 축 아닌 이유는?
    **Citation**: `[[bench-design-2026-04-18]]`

46. **Q**: wiki 페이지가 몇 개 넘으면 qmd 통합을 재검토하나? 현재 페이지 수?
    **Citation**: plan-post-rezero Tier 3

47. **Q**: refusal-probe 의 6 카테고리는?
    **Citation**: `docs/refusal-probe-prompts.md`

48. **Q**: 왜 omb search 가 답변의 기본 창구이고, akasha 는 아닌가?
    **Citation**: REZERO + project CLAUDE.md

49. **Q**: plan-check 가 어떤 파일을 primary_plan 으로 인식하는가?
    **Citation**: collect.sh 휴리스틱 + rename commit

50. **Q**: `git identity` 는? (user / email)
    **Citation**: `user_git_identity` memory

---

## 스코어링 시트 템플릿

| # | target | score | citation match? | note |
|---|---|---|---|---|
| 1 | omb-wiki | | | |
| 1 | akasha-legacy | | | |
| 1 | raw-llm | | | |
| 1 | capsule | | | |
| 1 | wiki+llm | | | |
| … | | | | |

결과는 `~/omb/bench/omb-v0-<date>/scores.csv` 로 저장.
