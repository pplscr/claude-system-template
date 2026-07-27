#!/bin/bash
# Авто-синхронізація MEMORY.md після кожної сесії
# Оновлює counters: агенти, скрипти, простори, launchd
# Викликається з session-файлу

set -euo pipefail

MEMORY_FILE="$HOME/spaces/system/memory/MEMORY.md"
TEMP_FILE=$(mktemp)

# --- Порахувати актуальні цифри ---
AGENTS_COUNT=$(ls "$HOME/.claude/agents/"*.md 2>/dev/null | wc -l | tr -d ' ')
SCRIPTS_COUNT=$(ls "$HOME/.claude/scripts/"*.{sh,py} 2>/dev/null | wc -l | tr -d ' ')
SPACES_COUNT=$(ls -d "$HOME/spaces/"*/ 2>/dev/null | wc -l | tr -d ' ')
LAUNCH_COUNT=$(ls "$HOME/Library/LaunchAgents/"*.plist 2>/dev/null | wc -l | tr -d ' ')

echo "[sync-memory] Агенти: $AGENTS_COUNT | Скрипти: $SCRIPTS_COUNT | Простори: $SPACES_COUNT | LaunchAgents: $LAUNCH_COUNT"

# --- Оновлення MEMORY.md ---
if [ ! -f "$MEMORY_FILE" ]; then
    echo "[sync-memory] ⚠️  MEMORY.md не знайдено: $MEMORY_FILE"
    exit 1
fi

# Оновлюємо updated date
TODAY=$(date +%Y-%m-%d)

while IFS= read -r line; do
    # Оновлюємо updated в metadata
    if [[ "$line" =~ ^[[:space:]]*updated: ]]; then
        echo "  updated: $TODAY"
    # Оновлюємо кількість агентів
    elif [[ "$line" =~ ^##[[:space:]]Agents[[:space:]]\( ]]; then
        echo "## Agents ($AGENTS_COUNT)"
    # Оновлюємо кількість скриптів
    elif [[ "$line" =~ ^##[[:space:]]Scripts[[:space:]]\( ]]; then
        echo "## Scripts ($SCRIPTS_COUNT)"
    # Оновлюємо кількість просторів
    elif [[ "$line" =~ ^##[[:space:]]Spaces[[:space:]]\( ]]; then
        echo "## Spaces ($SPACES_COUNT)"
    # Оновлюємо кількість LaunchAgents
    elif [[ "$line" =~ ^##[[:space:]]LaunchAgents[[:space:]]\( ]]; then
        echo "## LaunchAgents ($LAUNCH_COUNT)"
    else
        echo "$line"
    fi
done < "$MEMORY_FILE" > "$TEMP_FILE"

mv "$TEMP_FILE" "$MEMORY_FILE"
echo "[sync-memory] ✅ MEMORY.md синхронізовано ($TODAY)"
