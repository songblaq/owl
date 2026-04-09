# Source Ingest Policy v0

작성일: 2026-04-03
상태: 설계 초안

## 1. 목적

어떤 자료를 어떻게 inbox/raw로 수집할지 기준을 정의한다.

---

## 2. 기본 원칙

- 우선 inbox로 받는다.
- 분류가 가능하면 raw로 이동한다.
- 원문 훼손을 최소화한다.
- 출처와 수집 시점을 남긴다.
- 나중에 compile 가능한 형태를 우선한다.
- 초기 ingest는 완전 자율화하지 않는다.
- 초기에 source를 하나씩 직접 추가하며 패턴을 고정한다.
- 패턴이 안정되면 `file this new doc to our wiki: (path)` 같은 짧은 filing 명령으로 처리할 수 있게 한다.

---

## 3. 자료 유형별 정책

### 웹 기사
- 가능하면 markdown 또는 html-to-md 형태로 저장
- Obsidian Web Clipper 확장을 우선 고려
- 원 URL 기록
- 관련 이미지가 중요하면 함께 저장

### 논문
- PDF 원본 보관
- 가능하면 제목/저자/링크 메모를 같이 남김

### GitHub 저장소
- README, 핵심 문서 링크, 참고 파일 목록 기록
- 전체 clone 이 필요한 경우와 문서 스냅샷만 필요한 경우를 구분

### 대화 로그
- 채널, 날짜, 맥락을 표시
- 요약 전에 원문을 가능한 한 유지

### 링크 모음
- 짧은 설명과 함께 저장
- 단순 북마크가 아니라 후속 조사 후보인지 표시

### 이미지
- 관련 출처와 설명을 남김
- 텍스트와 함께 있으면 어떤 문맥의 이미지인지 기록

---

## 4. 상태 구분

- `inbox`: 미분류 수집
- `raw`: 원본 보관
- `compiled`: 편찬 완료
- `research`: 조사 진행 중

---

## 5. 초기 권장 흐름

1. 자료 수집
2. inbox 적재
3. 분류 메모 추가
4. raw 이동
5. compile 후보 선정
6. summary/note 생성
7. index/concept 연결 여부 점검
8. 필요한 경우 한 줄 filing 명령 흐름으로 승격

---

## 6. 프라이버시 — 개인 대화방 / 채널 소스 (2026-04-08 추가)

**개인 대화방 (카카오톡, Discord 개인 채널, 개인 메신저 로그 등) 소스는 vault 안에서만 보관한다. 공개 repo (GitHub 등) 에 올리지 않는다.**

### 이유

- owl 은 개인 LLM-maintained wiki — 개인 지식이 raw/ 와 compiled/ 에 축적됨
- 대화 로그에는 제3자 발언, 개인 정보, 민감 맥락이 섞일 수 있음
- vault 자체를 GitHub 에 올리는 것은 금지 (owl 프로젝트 repo 와 vault 는 분리된 계층)

### How to enforce

- **vault 는 git repo 가 아니어야** — owl-vault 안에 `.git/` 없음을 확인
- **프로젝트 repo 의 `.gitignore`** 가 `/raw/`, `/compiled/`, `/views/`, `/outputs/`, `/inbox/`, `/research/` 를 root level 에서 차단 (방어층)
- **새 source 를 ingest 하기 전** 판단: 공개 가능한 자료인가? 판단 어려우면 vault-local 유지
- **compile 결과** 에서도 제3자 발언/이름/PII 를 최소화. 필요시 편집 후 compiled 로

### 예외

- 이미 공개된 자료 (Karpathy gist, 공개 문서, published 블로그 글 등) 는 vault 에 넣는 것 OK
- 프로젝트 docs/ 안의 ingest 계획 (예: `docs/sample-ingest-candidates-v0.md`) 은 *계획* 만 담고 *본문* 을 안 담으면 OK
