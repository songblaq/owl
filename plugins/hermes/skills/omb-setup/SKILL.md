---
name: omb-setup
version: "0.1.0"
description: Install or reinstall the oh-my-brain plugin — pipx packages, skills, vault initialization.
author: songblaq
license: MIT
triggers:
  - "omb setup"
  - "omb 설치"
  - "setup omb"
  - "install omb"
prerequisites: []
metadata:
  hermes:
    tags:
      - setup
      - install
      - omb
---

# OMB Setup

oh-my-brain를 설치 또는 재설치한다.

## 사용법

```
/omb:setup
```

## 실행 순서

1. Repo 경로 확인: `cat ~/.config/omb/plugin.json 2>/dev/null`
2. install.sh 실행:
   ```bash
   bash <REPO_ROOT>/plugin/scripts/install.sh
   ```
3. 설치 완료 확인: `omb status`

## install.sh 처리 내용

1. `pipx install -e vault/akasha --force`
2. `pipx install -e vault/omb --force`
3. vault 초기화 (`~/omb/vault/akasha` 없으면 `akasha init`)
4. skills symlink → `~/.agents/skills/omb-*/`
5. `~/.claude/CLAUDE.md` OMB 블록 upsert
6. repo 경로 → `~/.config/omb/plugin.json` 저장
