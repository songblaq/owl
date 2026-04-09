# Karpathy 체크리스트 감사 v1

작성일: 2026-04-03
상태: 감사 기록

## 감사 기준
Karpathy 원문을 항목 단위로 분해해 owl 문서 반영 상태를 점검한다.

---

## 체크리스트

### 1. Data ingest
- 상태: 반영됨
- 근거 문서:
  - `karpathy-ingest-rules-v0.md`
  - `source-ingest-policy-v0.md`
  - `workflow-v0.md`

### 2. raw 디렉토리 기반 원본 보관
- 상태: 반영됨
- 근거 문서:
  - `lks-kib-mdv-spec-v0.md`
  - `kib-spec-v0.md`

### 3. LLM이 incremental compile로 md wiki 생성
- 상태: 반영됨
- 근거 문서:
  - `incremental-maintenance-spec-v0.md`
  - `llm-maintained-wiki-principle-v0.md`

### 4. summary / backlinks / concept categorization / article writing / linking
- 상태: 반영됨
- 근거 문서:
  - `wiki-linking-rules-v0.md`
  - `index-and-backlink-spec-v0.md`

### 5. Obsidian Web Clipper 사용
- 상태: 반영됨
- 근거 문서:
  - `obsidian-ingest-spec-v0.md`

### 6. 관련 이미지 로컬 저장
- 상태: 반영됨
- 근거 문서:
  - `obsidian-ingest-spec-v0.md`

### 7. Obsidian을 IDE frontend로 사용
- 상태: 반영됨
- 근거 문서:
  - `obsidian-surface-spec-v0.md`
  - `owl-structure-v1.md`

### 8. LLM이 wiki를 쓰고 유지, 사람은 거의 직접 수정 안 함
- 상태: 반영됨
- 근거 문서:
  - `llm-maintained-wiki-principle-v0.md`

### 9. Obsidian plugin / Marp 같은 파생 렌더링
- 상태: 반영됨
- 근거 문서:
  - `output-format-spec-v0.md`

### 10. 충분한 규모에서 complex Q&A 수행
- 상태: 반영됨
- 근거 문서:
  - `workflow-v0.md`
  - `lks-kib-mdv-spec-v0.md`

### 11. fancy RAG 없이 small scale에서 auto-maintained index/summaries로 작동
- 상태: 반영됨
- 근거 문서:
  - `small-scale-no-rag-policy-v0.md`
  - `index-and-backlink-spec-v0.md`

### 12. output을 markdown/slides/images로 생성
- 상태: 반영됨
- 근거 문서:
  - `output-format-spec-v0.md`

### 13. filing loop
- 상태: 반영됨
- 근거 문서:
  - `workflow-v0.md`
  - `term-dictionary-v0.md`

### 14. linting / health checks
- 상태: 반영됨
- 근거 문서:
  - `workflow-v0.md`
  - `karpathy-gap-check-v0.md`

### 15. missing data imputation with web searchers
- 상태: 반영됨
- 근거 문서:
  - `health-check-spec-v0.md`

### 16. interesting connections / new article candidates
- 상태: 반영됨
- 근거 문서:
  - `health-check-spec-v0.md`
  - `index-and-backlink-spec-v0.md`

### 17. extra tools / naive search engine / CLI handoff
- 상태: 반영됨
- 근거 문서:
  - `tool-adapter-spec-v0.md`

### 18. synthetic data generation + finetuning
- 상태: 반영됨
- 근거 문서:
  - `long-term-exploration-v0.md`

---

## 감사 결론

초기 설계는 대략적인 저장 구조와 메타 구조는 잡았지만, Karpathy 원문이 강조하는 실제 운영 감각을 완전히 반영하지 못했다.

특히 다음은 핵심 누락 또는 약한 반영이다.
- Obsidian Web Clipper
- Obsidian frontend를 구조 중심에 두는 것
- backlinks / linking / concept article 규칙
- missing data imputation with web search
- CLI handoff 및 extra tools 규약

---

## 즉시 보완 대상
1. Obsidian surface 명세
2. wiki linking / backlinks / concept article 규칙
3. web clipper / image local save 규칙
4. output format 규칙
5. tool adapter / CLI handoff 규칙
6. health check 세부 규칙
