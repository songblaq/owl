---
name: omb-update
description: Update oh-my-brain plugin — git pull, reinstall pipx packages, re-sync skills symlinks, refresh CLAUDE.md OMB block. Run when the repo has changes or after version bumps.
triggers:
  - "omb update"
  - "브레인 업데이트"
  - "update omb"
  - "oh-my-brain 업데이트"
  - "omb 업그레이드"
---

# OMB Update

repo 최신화 + 패키지 재설치 + skills/CLAUDE.md 재동기화.

## 사용법

```
/omb:update
```

## 실행 순서

### Step 1: Repo 경로 확인
```bash
cat ~/.config/omb/plugin.json
```
`repoRoot` 값 읽기. 없으면 `/omb:setup` 먼저 실행 요청.

### Step 2: Git pull
```bash
git -C <REPO_ROOT> pull --ff-only
```
충돌 또는 diverged 상태면 사용자에게 알리고 중단.

변경된 파일 목록 확인:
```bash
git -C <REPO_ROOT> diff --name-only HEAD@{1} HEAD
```

### Step 3: 패키지 재설치 (소스 변경 시)
`vault/akasha/` 또는 `vault/omb/` 변경 감지 시:
```bash
cd <REPO_ROOT>/vault/akasha && pipx install -e . --force
cd <REPO_ROOT>/vault/omb && pipx install -e . --force
```

### Step 4: Skills 재동기화 (plugin/skills/ 변경 시)
`plugin/skills/` 변경 감지 시:
```bash
bash <REPO_ROOT>/plugin/scripts/install.sh --skills-only
```

### Step 5: CLAUDE.md 업데이트 (plugin/CLAUDE.md 변경 시)
`plugin/CLAUDE.md` 변경 감지 시:
```bash
bash <REPO_ROOT>/plugin/scripts/install.sh --claude-only
```

### Step 6: 검증
```bash
omb status
```

### Step 7: 변경사항 리포트

```
OMB Update Report
━━━━━━━━━━━━━━━━
Version: 0.x.x → 0.x.x
Changed files: N
  - vault/akasha/... (package reinstalled)
  - plugin/skills/... (skills re-synced)
  - plugin/CLAUDE.md (CLAUDE.md updated)

omb status: OK (396 entries, 57 compiled)
```

## 규칙

- `git pull --ff-only` 만 사용 — 강제 merge/rebase 금지
- 변경 없으면 ("Already up to date") 나머지 스텝 스킵
- Step별로 변경 감지 후 필요한 것만 실행
