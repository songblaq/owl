---
name: omb-update
version: "0.1.0"
description: Update oh-my-brain to the latest version — git pull then selective reinstall.
author: songblaq
license: MIT
triggers:
  - "omb update"
  - "브레인 업데이트"
  - "update omb"
  - "update brain"
prerequisites:
  - git
metadata:
  hermes:
    tags:
      - update
      - upgrade
      - omb
---

# OMB Update

최신 버전으로 업데이트한다.

## 사용법

```
/omb:update
```

## 실행 순서

1. Repo 경로 확인: `cat ~/.config/omb/plugin.json`
2. `git -C <REPO_ROOT> pull --ff-only`
3. 변경된 컴포넌트 확인:
   - `vault/akasha/` 변경 → `pipx install -e vault/akasha --force`
   - `vault/omb/` 변경 → `pipx install -e vault/omb --force`
   - `skills/` 변경 → symlink 재동기 (자동, symlink이므로)
   - `plugin/CLAUDE.md` 변경 → `install.sh --claude-only`
4. `omb status` 로 버전 및 상태 확인

## 변경 없을 때

"Already up to date." 출력 후 종료.
