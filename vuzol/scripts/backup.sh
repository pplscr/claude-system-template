#!/bin/bash
# backup.sh — comprehensive daily backup
# Cron: 0 2 * * * /root/scripts/backup.sh >> /tmp/backup-cron.log 2>&1
set -euo pipefail

BACKUP_DIR=/root/backups
CLAUDE_BACKUP=/root/.claude/backups
CREDENTIALS=/root/.claude/credentials.env
DATE=$(date +%Y%m%d-%H%M)
RETENTION_DAYS=7

# Load credentials
source "$CREDENTIALS" 2>/dev/null || true

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
cleanup_old() {
    local prefix=$1 dir=$2
    local count=$(ls -1t "$dir/$prefix-"* 2>/dev/null | wc -l)
    if [ "$count" -gt "$RETENTION_DAYS" ]; then
        ls -1t "$dir/$prefix-"* 2>/dev/null | tail -n +$((RETENTION_DAYS + 1)) | xargs rm -f
        log "CLEANUP: removed old $prefix (kept last $RETENTION_DAYS)"
    fi
}

log "=== BACKUP START ==="

# 1. PostgreSQL dump
log "--- PostgreSQL ---"
mkdir -p "$BACKUP_DIR/postgres"
if sudo -u postgres pg_dumpall > "$BACKUP_DIR/postgres/full-$DATE.sql" 2>/dev/null; then
    gzip -f "$BACKUP_DIR/postgres/full-$DATE.sql"
    log "OK: PostgreSQL → full-$DATE.sql.gz"
    cleanup_old "full" "$BACKUP_DIR/postgres"
else
    log "FAIL: PostgreSQL dump"
fi

# 2. Qdrant snapshots (collections: agent_executions, checkpoints, factory_nsc_memory, rozum, system_memory, user_memory)
log "--- Qdrant ---"
mkdir -p "$BACKUP_DIR/qdrant"
for COL in user_memory system_memory checkpoints rozum factory_nsc_memory agent_executions; do
    STATUS=$(curl -s -o /dev/null -w '%{http_code}' -H "api-key: $QDRANT_API_KEY"         -X POST "http://localhost:6333/collections/$COL/snapshots" 2>/dev/null || echo '000')
    if [ "$STATUS" = "200" ] || [ "$STATUS" = "202" ]; then
        log "OK: Qdrant snapshot created for $COL"
    else
        log "WARN: Qdrant snapshot failed for $COL (HTTP $STATUS)"
    fi
done
# Remove snapshots older than 7 days from Qdrant (they're stored inside the volume)
log "OK: Qdrant snapshots done"
cleanup_old "" "$BACKUP_DIR/qdrant"

# 3. Docker volumes backup (Qdrant data)
log "--- Docker Volumes ---"
if [ -d /var/lib/docker/volumes/merezha_qdrant_data ]; then
    tar -czf "$BACKUP_DIR/qdrant/docker-volume-$DATE.tar.gz"         -C /var/lib/docker/volumes/ merezha_qdrant_data/_data 2>/dev/null &&         log "OK: Docker volume (qdrant_data)" || log "FAIL: Docker volume backup"
    cleanup_old "docker-volume" "$BACKUP_DIR/qdrant"
fi

# 4. Claude config
log "--- Config ---"
mkdir -p "$CLAUDE_BACKUP"
tar -czf "$CLAUDE_BACKUP/config-$DATE.tar.gz"     -C /root/ .claude/CLAUDE.md .claude/settings.json .claude/settings.local.json     .claude/mcp-registry.json 2>/dev/null && log "OK: claude config"
cleanup_old "config" "$CLAUDE_BACKUP"

# 5. мережа context
log "--- Merezha ---"
tar -czf "$CLAUDE_BACKUP/merezha-$DATE.tar.gz"     -C /root/ мережа/CLAUDE.md мережа/STRUCTURE.md мережа/TASKS.md     мережа/orchestrator/ мережа/src/ мережа/spaces/ 2>/dev/null && log "OK: мережа"
cleanup_old "merezha" "$CLAUDE_BACKUP"

# 6. Nginx + Systemd configs
log "--- System Configs ---"
tar -czf "$BACKUP_DIR/system-configs-$DATE.tar.gz"     -C /etc/ nginx/ systemd/system/task-api.service     systemd/system/task-broker.service systemd/system/upload-server.service     systemd/system/ttyd.service 2>/dev/null && log "OK: system configs"
cleanup_old "system-configs" "$BACKUP_DIR"

# 7. Disk check
USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$USAGE" -gt 80 ]; then
    log "⚠️  DISK WARNING: $USAGE% used!"
elif [ "$USAGE" -gt 70 ]; then
    log "⚠️  DISK NOTE: $USAGE% used — monitor closely"
fi

log "=== BACKUP DONE ==="
echo
