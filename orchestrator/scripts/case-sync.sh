#!/bin/bash
# case-sync.sh — Cross-space sync utility
# Usage: case-sync.sh {push|pull|status|log}

set -euo pipefail

ORCH_DIR="$HOME/spaces/orchestrator"
SCRIPT_DIR="$ORCH_DIR/scripts"

show_help() {
    echo "case-sync — Cross-space synchronization"
    echo ""
    echo "Usage: case-sync.sh <command>"
    echo ""
    echo "Commands:"
    echo "  push     Process inbound messages (inbox → route → outbox)"
    echo "  pull     Pull updates from remote spaces"
    echo "  status   Show current sync status"
    echo "  log      Show recent routing log entries"
    echo "  help     Show this help"
}

cmd_push() {
    echo "🔄 Pushing sync..."
    "$SCRIPT_DIR/check-inbox.sh" --once
}

cmd_pull() {
    echo "📥 Pulling from remote spaces..."
    # Check for results from remote nodes
    for node in vuzol hp-pavilion; do
        if tailscale status 2>/dev/null | grep -q "$node"; then
            echo "  🟢 $node — checking outbox..."
            scp -o ConnectTimeout=5 -q "${node}:~/spaces/orchestrator/outbox/"*.md "$ORCH_DIR/outbox/" 2>/dev/null && \
                echo "  ✅ $node outbox pulled" || \
                echo "  ⚠️  $node — no outbox files or error"
        else
            echo "  🔴 $node — offline"
        fi
    done
}

cmd_status() {
    echo "═══════════════════════════════════════════"
    echo "📊 Sync Status — $(date '+%Y-%m-%d %H:%M:%S')"
    echo "═══════════════════════════════════════════"

    local inbox_count
    inbox_count=$(find "$ORCH_DIR/inbox" -maxdepth 1 -name "*.json" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "📨 Inbox pending: $inbox_count"

    local outbox_count
    outbox_count=$(find "$ORCH_DIR/outbox" -maxdepth 1 -name "*.md" -not -name "README.md" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "📤 Outbox results: $outbox_count"

    local archive_count
    archive_count=$(find "$ORCH_DIR/archive" -maxdepth 1 -name "*.json" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "🗄️  Archive: $archive_count"

    echo ""
    echo "🌐 Remote spaces:"
    for node in vuzol hp-pavilion; do
        if tailscale status 2>/dev/null | grep -q "$node"; then
            echo "  🟢 $node — online"
        else
            echo "  🔴 $node — offline"
        fi
    done
}

cmd_log() {
    local lines="${1:-10}"
    echo "═══════════════════════════════════════════"
    echo "📋 Routing Log — останні $lines записів"
    echo "═══════════════════════════════════════════"
    if [[ -f "$ORCH_DIR/memory/routing-log.md" ]]; then
        head -5 "$ORCH_DIR/memory/routing-log.md"
        echo "..."
        tail -n "$lines" "$ORCH_DIR/memory/routing-log.md"
    else
        echo "❌ Лог не знайдено"
    fi
}

# ── Main ──
case "${1:-help}" in
    push)   cmd_push ;;
    pull)   cmd_pull ;;
    status) cmd_status ;;
    log)    cmd_log "${2:-10}" ;;
    help|*) show_help ;;
esac
