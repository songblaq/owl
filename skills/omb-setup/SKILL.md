---
name: omb-setup
description: Install or reinstall the oh-my-brain plugin — pipx packages, skills symlinks, CLAUDE.md patch, vault initialization.
triggers:
  - "omb setup"
  - "omb 설치"
  - "setup omb"
  - "install omb"
  - "oh-my-brain 설치"
---

# OMB Setup

oh-my-brain 플러그인을 설치 또는 재설치한다.

## 사용법

```
/omb:setup
```

## 실행 순서

### Step 1: Repo 경로 확인
```bash
cat ~/.config/omb/plugin.json 2>/dev/null
```
저장된 repo 경로가 있으면 사용. 없으면 사용자에게 확인:
> "oh-my-brain repo 경로를 알려주세요 (기본: ~/_/projects/oh-my-brain)"

### Step 2: install.sh 실행
```bash
bash <REPO_ROOT>/plugin/scripts/install.sh
```

install.sh가 처리하는 것:
1. `pipx install -e vault/akasha --force`
2. `pipx install -e vault/omb --force`
3. vault 초기화 (`~/omb/vault/akasha` 없으면 `akasha init`)
4. skills symlink → `~/.agents/skills/omb-*/`
5. `~/.claude/CLAUDE.md` OMB 블록 upsert
6. repo 경로 → `~/.config/omb/plugin.json` 저장

### Step 3: 검증
```bash
omb status
```
정상 출력 확인. vault 경로·entries 수·graph 확인.

## 문제 해결

| 증상 | 해결 |
|------|------|
| `omb: command not found` | `pipx ensurepath` 후 shell 재시작 |
| `akasha not found` | `cd vault/akasha && pipx install -e . --force` |
| vault 없음 | `akasha init` |
| skills 없음 | install.sh 재실행 |
