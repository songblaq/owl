#!/usr/bin/env bash
# drift_audit — CLAUDE.md 매핑 × 실존 path × wiki deprecated 3방향 + (--endpoint-health) 대조.
#
# Why: omb 에 deprecation 기록이 있어도 CLAUDE.md 매핑이 자동 동기화 되지 않는
#      drift 가 3건(Constella/ARIA/ClawVerse) 관측됨. 감지자 부재가 원인.
# What: 3가지를 대조해 mismatch 리포트. 주 1회 실행 권장.
#       --endpoint-health 플래그로 homelab endpoint 5곳 응답 확인 + 실제 모델 목록 출력.
#
# Usage:
#   bash tools/drift_audit.sh                    # 기본 3 phase
#   bash tools/drift_audit.sh --endpoint-health  # + Phase 5 (endpoint health)

set -u
CLAUDE_MD="${HOME}/.claude/CLAUDE.md"
WIKI_ENTITIES="${HOME}/omb/brain/live/entities"
ENDPOINT_HEALTH=0
for arg in "$@"; do
  case "$arg" in
    --endpoint-health) ENDPOINT_HEALTH=1 ;;
  esac
done

echo "drift_audit — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "======================================"

# ── 1. CLAUDE.md 매핑 경로가 실존하는가 ───────────────────────────────────────
echo
echo "[1] CLAUDE.md 한글 매핑: 경로 실존 체크"
# 테이블 라인에서 백틱 경로 추출
grep -E '^\| [가-힣]+ \|' "$CLAUDE_MD" 2>/dev/null | while IFS='|' read -r _ kor eng rest; do
  kor=$(echo "$kor" | xargs)
  # 백틱 안의 경로 추출
  paths=$(echo "$rest" | grep -oE '`~/[^`]+`' | tr -d '`' | while read -r p; do echo "${p/#\~/$HOME}"; done)
  [ -z "$paths" ] && continue
  missing=""
  for p in $paths; do
    [ ! -e "$p" ] && missing="$missing $p"
  done
  if [ -n "$missing" ]; then
    echo "  MISSING [$kor]:$missing"
  fi
done

# ── 2. wiki 에 deprecated 페이지가 있으나 CLAUDE.md 에 active 로 남아있나 ────
echo
echo "[2] wiki deprecated ↔ CLAUDE.md active 매핑 mismatch"
if [ -d "$WIKI_ENTITIES" ]; then
  for f in "$WIKI_ENTITIES"/*.md; do
    [ -f "$f" ] || continue
    if grep -q "^status: deprecated" "$f" 2>/dev/null; then
      entity=$(basename "$f" .md)
      # CLAUDE.md 의 해당 라인에 DEPRECATED 표기가 있는지
      line=$(grep -i "$entity" "$CLAUDE_MD" | head -1)
      if [ -n "$line" ] && ! echo "$line" | grep -qi "deprecated"; then
        echo "  MISMATCH [$entity]: wiki=deprecated, CLAUDE.md 라인에 표시 없음"
        echo "    → $line"
      fi
    fi
  done
fi

# ── 3. akasha 에 deprecated 포함 entry 주제가 wiki 에 반영됐나 (샘플) ────────
echo
echo "[3] akasha (INACTIVE) 의 deprecated 토픽이 wiki 에 반영됐는지 (상위 10)"
akasha_entries="${HOME}/omb/bench/akasha/entries"
if [ -d "$akasha_entries" ]; then
  count=0
  grep -l -i "deprecated" "$akasha_entries"/*.md 2>/dev/null | head -10 | while read -r af; do
    topic_line=$(grep -m1 "^topics:" "$af" 2>/dev/null || echo "")
    primary=$(echo "$topic_line" | sed 's/topics:[[:space:]]*\[//' | sed 's/\].*//' | cut -d',' -f1 | xargs)
    if [ -n "$primary" ]; then
      wiki_page="$WIKI_ENTITIES/${primary}.md"
      if [ ! -f "$wiki_page" ]; then
        echo "  GAP [$(basename $af .md)]: topic=$primary → wiki/entities/$primary.md 없음"
      fi
    fi
    count=$((count+1))
  done
  [ "$count" -eq 0 ] && echo "  (none)"
fi

# ── 5. endpoint health (opt-in) ──────────────────────────────────────────────
if [ "$ENDPOINT_HEALTH" = "1" ]; then
  echo
  echo "[5] endpoint health — homelab 5 타겟 curl + /v1/models, /api/tags"
  # label|url|api (openai: /v1/models, ollama: /api/tags, raw: skip)
  # endpoints 값은 ~/.config/omb/endpoints.conf (또는 $OMB_ENDPOINTS_CONF) 에서 load.
  # 없으면 placeholder (*.local) 로 동작 → DOWN 으로 기록됨.
  OMB_ENDPOINTS_CONF="${OMB_ENDPOINTS_CONF:-$HOME/.config/omb/endpoints.conf}"
  if [ -f "$OMB_ENDPOINTS_CONF" ]; then
    # shellcheck disable=SC1090
    . "$OMB_ENDPOINTS_CONF"
  else
    # fallback to example defaults
    # shellcheck disable=SC1091
    . "$(dirname "$0")/endpoints.example.conf"
  fi
  ENDPOINTS=(
    "dgx-primary|${DGX_PRIMARY_URL}/v1/models|openai"
    "dgx-backup|${DGX_BACKUP_URL}/v1/models|openai"
    "mac-studio-ollama|${MAC_STUDIO_OLLAMA_URL}/api/tags|ollama"
    "nas|${NAS_URL}|raw"
    "5090-wsl|${WSL_5090_URL}/api/tags|ollama"
  )
  for ep in "${ENDPOINTS[@]}"; do
    IFS='|' read -r label url api <<< "$ep"
    # HEAD 는 ollama 가 거부 — GET 으로 통일, --max-time 5
    code=$(curl -s -o /tmp/drift-ep-$$.json -w '%{http_code}' --max-time 5 "$url" 2>/dev/null)
    [ -z "$code" ] && code="000"
    if [ "$code" = "200" ]; then
      case "$api" in
        openai) models=$(jq -r '.data[]?.id // empty' /tmp/drift-ep-$$.json 2>/dev/null | paste -sd',' -) ;;
        ollama) models=$(jq -r '.models[]?.name // empty' /tmp/drift-ep-$$.json 2>/dev/null | paste -sd',' -) ;;
        *) models="(raw 200)" ;;
      esac
      [ -z "$models" ] && models="(200, no model list)"
      printf "  OK    [%-20s] %s\n         models: %s\n" "$label" "$url" "$models"
    else
      printf "  DOWN  [%-20s] %s (HTTP %s)\n" "$label" "$url" "$code"
    fi
  done
  rm -f /tmp/drift-ep-$$.json
fi

echo
echo "done."
