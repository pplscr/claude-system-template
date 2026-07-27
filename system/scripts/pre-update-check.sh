#!/bin/bash
# pre-update-check.sh — перевірка перед macOS оновленням
# Usage: ~/spaces/system/scripts/pre-update-check.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

issues=0

echo "═══════════════════════════════════════════"
echo "🔍 Pre-Update Check — $(date '+%Y-%m-%d %H:%M')"
echo "═══════════════════════════════════════════"

# ── 1. Free Space ──
echo ""
echo "💾 1. Disk Space"
available=$(df -g / | tail -1 | awk '{print $4}')
echo "   Available: ${available}GB"
if [[ $available -lt 20 ]]; then
    echo -e "   ${RED}❌ Less than 20GB free — update may fail${NC}"
    ((issues++))
else
    echo -e "   ${GREEN}✅ Sufficient space${NC}"
fi

# ── 2. Time Machine / Backup ──
echo ""
echo "📦 2. Time Machine Status"
if tmutil status 2>/dev/null | grep -q 'BackupPhase = "NotBackingUp"' 2>/dev/null; then
    last_backup=$(tmutil latestbackup 2>/dev/null || echo "unknown")
    echo -e "   ${YELLOW}⚠️  No active backup. Last: ${last_backup}${NC}"
    echo -e "   ${BLUE}   → Run: tmutil startbackup --auto${NC}"
    ((issues++))
elif ! tmutil status &>/dev/null; then
    echo -e "   ${YELLOW}⚠️  Time Machine not configured${NC}"
    echo -e "   ${BLUE}   → Consider manual backup before update${NC}"
    ((issues++))
else
    echo -e "   ${GREEN}✅ Time Machine active${NC}"
fi

# ── 3. Running services ──
echo ""
echo "🔧 3. Critical Services"
services=(
    "tailscaled:VPN mesh"
    "com.vuzol.tunnel:SSH tunnel to vuzol"
)
for svc in "${services[@]}"; do
    name="${svc%%:*}"
    label="${svc##*:}"
    if pgrep -x "$name" &>/dev/null || launchctl list 2>/dev/null | grep -q "$name"; then
        echo -e "   ${GREEN}✅${NC} $label (will restart after reboot)"
    else
        echo -e "   ${YELLOW}⚠️${NC} $label — not running"
    fi
done

# ── 4. Pending reboots ──
echo ""
echo "🔄 4. Pending Reboots"
if [[ -f /private/var/db/.AppleSetupDone ]]; then
    echo -e "   ${GREEN}✅ No pending setup${NC}"
fi
if softwareupdate --history 2>/dev/null | head -5 | grep -q "restart"; then
    echo -e "   ${YELLOW}⚠️  Previous update required restart${NC}"
fi

# ── 5. Claude Code state ──
echo ""
echo "🤖 5. Claude Code State"
if [[ -f ~/.claude/settings.json ]]; then
    echo -e "   ${GREEN}✅ Settings preserved${NC}"
fi
if [[ -d ~/.claude/session-env ]]; then
    sessions=$(ls ~/.claude/session-env/ 2>/dev/null | wc -l | tr -d ' ')
    echo -e "   ${BLUE}ℹ️  ${sessions} session(s) — will be restored${NC}"
fi

# ── 6. Available updates ──
echo ""
echo "📥 6. Available macOS Updates"
updates=$(softwareupdate -l 2>/dev/null | grep -c "Title:" || echo "0")
if [[ $updates -gt 0 ]]; then
    echo -e "   ${BLUE}ℹ️  ${updates} update(s) available${NC}"
    softwareupdate -l 2>/dev/null | grep "Title:" | head -10 | while read line; do
        echo -e "   → ${line#*: }"
    done
else
    echo -e "   ${GREEN}✅ System up to date${NC}"
fi

# ── Summary ──
echo ""
echo "═══════════════════════════════════════════"
if [[ $issues -eq 0 ]]; then
    echo -e "${GREEN}✅ All checks passed — ready for update${NC}"
else
    echo -e "${YELLOW}⚠️  ${issues} issue(s) found — review before updating${NC}"
fi
echo "═══════════════════════════════════════════"

exit $issues
