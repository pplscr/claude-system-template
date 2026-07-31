#!/bin/bash
# Trading 212 Quick Sync Hook — запускається перед аналізом портфеля
# Використовується PreToolUse для Bash команд що містять "trading" або "t212"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SCRIPT="$HOME/spaces/finance/trading212/sync.py"
CACHE_FILE="$HOME/spaces/finance/trading212/cash.json"
CACHE_MAX_AGE=300  # 5 хвилин

# Перевіряємо вік кешу
if [ -f "$CACHE_FILE" ]; then
    NOW=$(date +%s)
    FILE_TIME=$(stat -f %m "$CACHE_FILE" 2>/dev/null || stat -c %Y "$CACHE_FILE" 2>/dev/null)
    AGE=$((NOW - FILE_TIME))
    if [ $AGE -lt $CACHE_MAX_AGE ]; then
        echo "[trading-hook] Cache is $AGE seconds old — skipping sync"
        exit 0
    fi
fi

echo "[trading-hook] Cache expired ($AGE sec) — running quick sync..."
python3 "$SYNC_SCRIPT" --quick 2>&1 | head -5
echo "[trading-hook] Sync done"
