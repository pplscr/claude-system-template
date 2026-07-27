#!/bin/bash
# health-check.sh — комплексна перевірка стану mac-mini
# Usage: ~/spaces/system/scripts/health-check.sh [--quick]

set -euo pipefail

QUICK_MODE=false
[[ "${1:-}" == "--quick" ]] && QUICK_MODE=true

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

pass=0; fail=0; warn=0

check() {
    local name="$1"; shift
    if "$@" &>/dev/null; then
        echo -e "  ${GREEN}✅${NC} $name"
        ((pass++))
        return 0
    else
        echo -e "  ${RED}❌${NC} $name"
        ((fail++))
        return 1
    fi
}

check_warn() {
    local name="$1"; shift
    if "$@" &>/dev/null; then
        echo -e "  ${GREEN}✅${NC} $name"
        ((pass++))
        return 0
    else
        echo -e "  ${YELLOW}⚠️${NC} $name"
        ((warn++))
        return 1
    fi
}

echo "═══════════════════════════════════════════"
echo "🩺 mac-mini Health Check — $(date '+%Y-%m-%d %H:%M')"
echo "═══════════════════════════════════════════"

# ── System ──
echo ""
echo "🖥️  System"
check "macOS booted"       pgrep -x launchd
check "Uptime < 30 days"   bash -c '[[ $(uptime | grep -o "up [0-9]*" | grep -o "[0-9]*") -lt 30 ]]'
check_warn "SSD > 10% free" bash -c '[[ $(df / | tail -1 | awk "{print \$5}" | tr -d "%") -lt 90 ]]'
check_warn "RAM < 80% used" bash -c '[[ $(vm_stat | awk "/Pages active/ {a=\$NF} /Pages wired/ {w=\$NF} END {printf \"%.0f\", (a+w)*4096/1024/1024/1024*100/16}") -lt 80 ]]'

# ── Network ──
echo ""
echo "🌐 Network"
check "Internet access"    ping -c 1 -t 2 1.1.1.1
check "DNS resolution"     nslookup google.com
check_warn "Tailscale running" pgrep -x tailscaled
check_warn "Tailscale connected" bash -c 'tailscale status --json 2>/dev/null | grep -q "100\."'

# ── Services ──
echo ""
echo "🔧 Services"
check_warn "SSH tunnel (launchd)" bash -c 'launchctl list 2>/dev/null | grep -q "com.vuzol.tunnel"'

# ── Claude Code ──
echo ""
echo "🤖 Claude Code"
check "Claude binary"      which claude
check "Agents dir"         test -d ~/.claude/agents
check_warn "Settings.json" test -f ~/.claude/settings.json

if ! $QUICK_MODE; then
    # ── Spaces ──
    echo ""
    echo "📂 Spaces"
    check "system space"        test -f ~/spaces/system/CLAUDE.md
    check "orchestrator space"  test -f ~/spaces/orchestrator/CLAUDE.md

    # ── Memory ──
    echo ""
    echo "🧠 Memory"
    check_warn "Memory bridge"  test -x ~/.claude/scripts/memory-bridge.sh
    check_warn "Vuzol reachable" bash -c 'ssh -o ConnectTimeout=3 vuzol "echo ok" 2>/dev/null | grep -q ok'
fi

# ── Summary ──
echo ""
echo "═══════════════════════════════════════════"
echo -e "📊 Results: ${GREEN}${pass} passed${NC}  ${RED}${fail} failed${NC}  ${YELLOW}${warn} warnings${NC}"
echo "═══════════════════════════════════════════"

if [[ $fail -gt 0 ]]; then
    exit 1
fi
exit 0
