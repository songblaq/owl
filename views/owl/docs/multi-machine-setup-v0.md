# Multi-Machine Setup v0

작성일: 2026-04-08
상태: v0

## 0. 목적

owl 을 여러 머신에서 사용할 때의 **machine identity 체계 + vault 동기화 전략 + 연결 패턴** 을 정의한다. 현재 Mac mini (`LucaBlaiMacmini`) 가 canonical primary. 다른 머신 (노트북, WSL, 서버 등) 이 여기에 연결된다.

## 1. Machine Roles

| Role | 의미 | 로컬 vault 보유? | `~/.owl/machine.json` `role` |
|---|---|---|---|
| **primary** | Canonical vault host. 진실의 원천 | ✓ (`~/owl-vault` 원본) | `"primary"` |
| **mirror** | Primary vault 의 동기화 copy 보유 | ✓ (`~/owl-vault` 동기화) | `"mirror"` |
| **client** | 로컬 vault 없음. primary 를 원격 쿼리 | ✗ | `"client"` |

현재 owl 프로젝트에서는 **primary + mirror** 조합이 가장 실용적. *client* 는 향후 MCP 서버 배포 시 의미가 생김.

## 2. 머신 식별 (`~/.owl/machine.json`)

각 머신의 `~/.owl/` 에 `machine.json` 파일이 있으면 해당 머신의 정체성을 owl CLI 가 인지한다.

### 생성

```bash
# Primary 로 마킹 (Mac mini 같은 canonical host)
owl setup --non-interactive --mark-primary

# Mirror 로 마킹 (동기화 copy 를 가진 머신)
owl setup --non-interactive --mark-mirror

# Client 로 마킹 (로컬 vault 없음)
owl setup --non-interactive --mark-client
```

### 예시 파일

```json
{
  "hostname": "LucaBlaiMacmini",
  "os": "Darwin",
  "os_release": "25.3.0",
  "arch": "arm64",
  "python": "3.14.3",
  "role": "primary",
  "primary": true,
  "vault_path": "/Users/lucablaq/owl-vault",
  "recorded_at": "2026-04-08T11:29:23+00:00"
}
```

### 확인

```bash
owl status
# machine: LucaBlaiMacmini (primary) 표시
```

### 드리프트 감지

`owl status` 는 `current hostname` 과 `machine.json` 의 `hostname` 을 비교한다. 다르면 경고:

```
machine: LucaBlaiMacmini (primary)
  ⚠ current hostname is foo-laptop but recorded is LucaBlaiMacmini
  ⚠ this machine may be a mirror/clone or ~/.owl/machine.json is stale
```

이 경고는 `~/.owl/` 디렉토리가 실수로 다른 머신에 그대로 복사된 경우 잡는다.

## 3. Vault 동기화 전략 (Primary → Mirror)

**vault 자체를 어떻게 머신 간 sync 하느냐** 는 owl 이 간섭하지 않는 별도 문제. owl 은 로컬 `active-vault` 포인터만 본다. 사용자가 도구를 선택.

### 선택지 비교

| 도구 | 장점 | 단점 | 추천? |
|---|---|---|---|
| **Syncthing** | 자체 호스팅, 심링크 지원, 숨김 파일 OK, 충돌 해결 강함 | 초기 셋업 약간 복잡 | ★ 가장 추천 |
| **rsync** (수동/cron) | 신뢰성 최고, 복잡 조건 처리 가능 | 수동 트리거 또는 cron 필요 | ★ 추천 (간단한 경우) |
| **iCloud Drive** | macOS 네이티브 | 숨김 파일 (`.owl-vault`, `.obsidian`) 불안정, 충돌 시 데이터 손실 위험 | × 비추천 |
| **Dropbox** | 안정적 동기화 | 심링크 미지원, 숨김 파일 일부 문제 | △ 주의 |
| **Git** | 버전 관리 | 바이너리/outputs 취약, 대용량 vault 부적합 | △ 작은 vault 만 |
| **SMB/NFS 마운트** | 실시간, 단일 진실 | 네트워크 의존, 오프라인 불가 | △ LAN 환경 |
| **Resilio Sync** | Syncthing 과 유사 | 유료 | △ |

### 현재 사용자 환경 (2026-04-08)

Mac mini 에 `/Users/lucablaq/_/Sync/` 디렉토리 존재 — sync 도구 사용 중 (Syncthing 가능성 높음). `~/owl-vault` 는 **홈 직속**, `_/Sync/Obsidian/owl` 이 `~/owl-vault` 로의 심링크. 즉 vault 본체는 `~/owl-vault` 에 있고 sync 도구는 아직 vault 본체에는 적용 안 된 상태.

옵션:
1. **Move vault into _/Sync/**: `~/owl-vault` 를 `~/_/Sync/owl-vault` 로 이동, `~/owl-vault` 를 심링크로 유지. Sync 도구가 vault 를 자동 관리.
2. **Sync ~/owl-vault directly**: sync 도구의 sync 경로에 `~/owl-vault` 추가. 홈 위치는 유지.

옵션 1이 더 깨끗 (sync 디렉토리 한 곳에 집중). 옵션 2가 덜 이동적.

## 4. 각 머신의 설치 순서

### Primary (Mac mini — 현재 상태)

```bash
git clone https://github.com/songblaq/agent-brain.git ~/_/projects/agent-brain
cd ~/_/projects/agent-brain/views/owl
pipx install --editable .
owl setup --mark-primary --non-interactive
owl init ~/owl-vault --hooks --non-interactive  # 이미 되어 있으면 skip
owl status  # machine: <hostname> (primary) 확인
```

### Mirror (두 번째 Mac 또는 노트북)

```bash
# 1. 프로젝트 repo clone
git clone https://github.com/songblaq/agent-brain.git ~/_/projects/agent-brain
cd ~/_/projects/agent-brain/views/owl
pipx install --editable .

# 2. vault 동기화 설정 (별도 도구 — Syncthing 등)
#    Primary 의 ~/owl-vault 를 이 머신의 ~/owl-vault 로 sync

# 3. Mirror 마킹
owl setup --mark-mirror --non-interactive

# 4. 검증
owl status  # machine: <hostname> (mirror)
```

**중요**: Mirror 는 `owl init` 을 **재실행하지 말 것**. Primary 가 이미 초기화한 `.owl-vault` 마커, `CLAUDE.md`, `.claude/settings.json` 이 sync 로 이미 들어와 있음.

### Client (향후 MCP 서버 기반)

현재는 미구현. §7.1 참조.

## 5. 머신별 독립 영역 vs 공유 영역

| 항목 | 동기화? | 비고 |
|---|---|---|
| `~/_/projects/agent-brain/` | ✗ (git 로 관리) | 각자 clone |
| `~/.local/bin/owl` (pipx) | ✗ | 각자 install |
| `~/.owl/active-vault` | **✗ 절대 sync 금지** | 머신별 로컬 경로 |
| `~/.owl/machine.json` | **✗ 절대 sync 금지** | 머신별 identity |
| `~/.owl/installed-at` | ✗ | 머신별 |
| `~/owl-vault/` 데이터 (raw/compiled/...) | **✓ sync 대상** | vault 콘텐츠 |
| `~/owl-vault/.claude/settings.json` (hooks) | ✓ (vault 의 일부) | primary 가 init, sync 됨 |
| `~/owl-vault/CLAUDE.md` | ✓ (vault 의 일부) | 같음 |
| `~/.claude/agents/owl-*` (심링크) | ✗ | 각자 `owl setup` |
| `~/.claude/commands/owl-*` (심링크) | ✗ | 각자 `owl setup` |
| `~/.claude/CLAUDE.md` 의 owl 섹션 | ✗ | 수동 복제 권장 |

**핵심 규칙**: **`~/.owl/` 는 절대 sync 대상에 포함하지 말 것**. vault 콘텐츠 (`~/owl-vault/`) 만 sync.

## 6. 충돌 시나리오 + 대처

### 6.1 Primary 와 Mirror 가 동시에 compile

- Primary 에서 `compiled/X.md` 작성
- Mirror 에서 동시에 같은 파일 작성
- Sync 도구가 conflict 처리 → 불확실성

**대처 (컨벤션)**: **쓰기 작업은 primary 에서만**. Mirror 는 읽기/검색 전용. `owl-compiler`, `owl-librarian` 호출은 primary 에서. (향후 코드 강제 가능.)

### 6.2 `~/.owl/` 실수로 sync 에 포함

- Sync 도구가 `~/.owl/` 통째로 동기화
- Mirror 머신의 `~/.owl/active-vault` 가 primary 의 `/Users/lucablaq/owl-vault` 경로를 받음
- Mirror 머신에서는 해당 경로가 존재 X → `owl status` 실패

**대처**:
- `~/.owl/` 는 sync 대상 아님 (§5 규칙)
- `owl status` 의 hostname mismatch 경고가 감지
- 각 머신의 `~/.owl/active-vault` 는 **수동** 설정

### 6.3 Stale mirror 에서 검색

- Primary 가 새 summary 추가
- Mirror 의 sync 지연 → mirror 에서 최신 결과 못 찾음

**대처**: 사용자가 sync 상태 인지. 향후 `owl status` 에 "last sync" 표시 고려.

## 7. 향후 확장

### 7.1 MCP 서버 (Client 지원)

Primary 에 `owl mcp-serve` 데몬 → 다른 머신이 MCP 로 쿼리. 장점: single source of truth, sync 불필요. 단점: 네트워크 의존, primary offline 시 불가.

### 7.2 `owl remote` 명령

SSH wrapper:

```bash
owl remote search "topic" --host macmini.local
# → SSH 로 primary 에 owl search 원격 실행
```

간단 구현, MCP 없이도.

### 7.3 내장 `owl sync`

owl 이 vault sync 를 자체 관리. 구현 복잡도 높아 현재는 외부 도구 권장.

### 7.4 머신 레지스트리

Primary 의 `.owl/registry.json` 이 central registry 역할. 각 머신이 heartbeat.

## 8. 현재 상태 (2026-04-08)

- **Primary**: `LucaBlaiMacmini` (Mac mini, macOS 26.3, arm64, Python 3.14.3)
  - vault: `/Users/lucablaq/owl-vault`
  - project repo: `/Users/lucablaq/_/projects/agent-brain`
  - marked primary via `owl setup --mark-primary` (2026-04-08)
  - `~/.owl/machine.json` 존재
- **Mirror / Client**: 아직 없음. 사용자가 다음 단계에서 설정 예정.

## 9. 사용자 다음 단계 (Mirror 추가 시)

1. **Sync 도구 선택** — Syncthing 권장
2. **Sync 경로 결정** — `~/owl-vault` 또는 `~/_/Sync/owl-vault` 로 이동 후 sync
3. **Mirror 머신에서** (위 §4 절차 실행)
4. **`~/.owl/` 는 sync 대상 제외** — 이게 제일 중요
5. **쓰기 작업은 primary 에서만** (컨벤션)

## 10. 관련 코드 / 문서

- `src/owl/config.py` — `detect_machine()`, `get_machine_info()`, `set_machine_info()`, `MACHINE_FILE`
- `src/owl/setupcmd.py` — `setup(mark_primary=, mark_mirror=, mark_client=)`
- `src/owl/statuscmd.py` — machine info display + drift 경고
- `docs/external-knowledge-integration-v0.md` — 단일 머신에서의 external knowledge 통합
- `docs/folder-policy-v0.md` — vault 구조
- `~/.owl/machine.json` — 머신별 identity (각 머신에 설치)
