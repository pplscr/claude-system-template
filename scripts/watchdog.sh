#!/bin/bash
# watchdog.sh — health monitoring for vuzol (Linux)
# Run: every 5 min via cron
set -euo pipefail
LOG="/tmp/watchdog.log"
MAX_LINES=500
log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG"; }
tail -n "$MAX_LINES" "$LOG" > "${LOG}.tmp" 2>/dev/null && mv "${LOG}.tmp" "$LOG" || true
FAILS=0; ISSUES=""
log "=== Watchdog pulse ==="

# Tailscale
if tailscale status &>/dev/null; then
    TS_OFF=$(tailscale status 2>/dev/null | grep -c "offline" || true)
    [ "$TS_OFF" -gt 0 ] && { log "WARN: Tailscale $TS_OFF offline"; ISSUES+="  - Tailscale: $TS_OFF offline\n"; FAILS=$((FAILS+1)); } || log "OK: Tailscale"
else
    log "ERROR: Tailscale stopped"; ISSUES+="  - Tailscale: stopped\n"; FAILS=$((FAILS+1))
fi

# mac-mini SSH
if ssh -o ConnectTimeout=5 -o BatchMode=yes mac-mini "echo ok" &>/dev/null; then log "OK: mac-mini SSH"
else log "ERROR: mac-mini unreachable"; ISSUES+="  - mac-mini: SSH failed\n"; FAILS=$((FAILS+1)); fi

# Docker
if docker ps &>/dev/null; then
    DOCKER_DOWN=$(docker ps -a --format "{{.Names}} {{.Status}}" | grep -c -v "Up" || true)
    [ "$DOCKER_DOWN" -gt 0 ] && { log "WARN: $DOCKER_DOWN containers down"; ISSUES+="  - Docker: $DOCKER_DOWN down\n"; FAILS=$((FAILS+1)); } || log "OK: Docker"
else log "ERROR: Docker not running"; ISSUES+="  - Docker: stopped\n"; FAILS=$((FAILS+1)); fi

# Qdrant
curl -s --connect-timeout 3 -H "api-key: $QDRANT_API_KEY" http://localhost:6333/healthz &>/dev/null && log "OK: Qdrant" || { log "WARN: Qdrant not responding"; ISSUES+="  - Qdrant: down\n"; FAILS=$((FAILS+1)); }

# Disk
DISK_PCT=$(df -h / | awk "NR==2 {print \$5}" | sed "s/%//")
[ "$DISK_PCT" -gt 90 ] && { log "CRIT: disk ${DISK_PCT}%"; ISSUES+="  - Disk: ${DISK_PCT}% CRIT\n"; FAILS=$((FAILS+1)); }
[ "$DISK_PCT" -gt 80 ] && [ "$DISK_PCT" -le 90 ] && { log "WARN: disk ${DISK_PCT}%"; ISSUES+="  - Disk: ${DISK_PCT}%\n"; } || log "OK: disk ${DISK_PCT}%"

# Memory
MEM_AVAIL=$(free | awk "/^Mem:/ {printf \"%.0f\", \$7/\$2*100}")
[ "$MEM_AVAIL" -lt 15 ] && { log "WARN: mem free ${MEM_AVAIL}%"; ISSUES+="  - Memory: free ${MEM_AVAIL}%\n"; FAILS=$((FAILS+1)); } || log "OK: mem free ${MEM_AVAIL}%"

# Claude daemon
pgrep -f "claude.*daemon" &>/dev/null && log "OK: Claude daemon" || log "OK: daemon idle (normal)"

[ "$FAILS" -gt 0 ] && { log "RESULT: $FAILS issue(s)"; printf "⚠️ vuzol watchdog: %d issue(s)\n%b\n" "$FAILS" "$ISSUES" > /tmp/watchdog-alert; } || { log "RESULT: all clear"; rm -f /tmp/watchdog-alert; }
exit 0
