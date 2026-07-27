#!/bin/bash
# check-inbox.sh — обробляє нові .json в inbox/, маршрутизує до цільових просторів
# Usage: ~/spaces/orchestrator/scripts/check-inbox.sh [--once]

set -euo pipefail

SPACES_DIR="$HOME/spaces"
ORCH_DIR="$SPACES_DIR/orchestrator"
INBOX="$ORCH_DIR/inbox"
OUTBOX="$ORCH_DIR/outbox"
ARCHIVE="$ORCH_DIR/archive"
LOG="$ORCH_DIR/memory/routing-log.md"
ONCE_MODE=false

[[ "${1:-}" == "--once" ]] && ONCE_MODE=true

# ── Кольори ──
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

# ── Перевірка директорій ──
for dir in "$INBOX" "$OUTBOX" "$ARCHIVE"; do
    [[ -d "$dir" ]] || { echo "❌ $dir не існує"; exit 1; }
done

# ── Допоміжні функції ──
log_route() {
    local task_id="$1" from="$2" to="$3" status="$4" notes="${5:-}"
    local ts
    ts=$(date '+%Y-%m-%d %H:%M:%S')
    echo "| $ts | $task_id | $from | $to | $status | $notes |" >> "$LOG"
}

extract_field() {
    local file="$1" field="$2"
    python3 -c "import json; d=json.load(open('$file')); print(d.get('$field',''))" 2>/dev/null || echo ""
}

is_local_space() {
    local name="$1"
    [[ -d "$SPACES_DIR/$name" ]] && [[ -f "$SPACES_DIR/$name/CLAUDE.md" ]]
}

is_remote_online() {
    local node="$1"
    tailscale status 2>/dev/null | grep -q "$node"
}

process_inbox_file() {
    local file="$1"
    local fname
    fname=$(basename "$file")

    # ── Читаємо поля ──
    local task_id from to task priority context created
    task_id=$(extract_field "$file" "id")
    from=$(extract_field "$file" "from")
    to=$(extract_field "$file" "to")
    task=$(extract_field "$file" "task")
    priority=$(extract_field "$file" "priority")
    created=$(extract_field "$file" "created")

    [[ -n "$task_id" ]] || { echo "  ⚠️  $fname: немає id, пропускаю"; return 1; }
    [[ -n "$to" ]] || { echo "  ⚠️  $fname: немає to, пропускаю"; return 1; }

    # ── Перевіряємо чи вже оброблено ──
    local result_file="$OUTBOX/${task_id}.md"
    if [[ -f "$result_file" ]]; then
        echo "  ⏭️  $task_id: вже є результат у outbox, архівую"
        mv "$file" "$ARCHIVE/"
        return 0
    fi

    echo ""
    echo "📥 Обробляю: $task_id (→ $to, priority: ${priority:-normal})"
    echo "   From: ${from:-<unknown>}"
    echo "   Task: ${task:0:80}..."

    # ── Визначаємо тип простору ──
    local status="failed"
    local notes=""

    if is_local_space "$to"; then
        echo "   🏠 Локальний простір: $to"

        # Створюємо sync-директорію якщо не існує
        local sync_dir="$SPACES_DIR/$to/tasks/sync"
        mkdir -p "$sync_dir"

        # Записуємо задачу в цільовий простір
        local task_file="$sync_dir/task-${task_id}.md"
        cat > "$task_file" << MARKDOWN
# Task: $task_id

- **From**: ${from:-<unknown>}
- **Priority**: ${priority:-normal}
- **Deadline**: $(extract_field "$file" "deadline")
- **Created**: ${created:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}

## Context
\`\`\`json
$(python3 -c "import json; print(json.dumps(json.load(open('$file')).get('context',{}), indent=2))" 2>/dev/null || echo "{}")
\`\`\`

## Task
$task
MARKDOWN

        echo "   ✅ Задачу записано: $task_file"
        notes="local → $to/tasks/sync/"

        # Перевіряємо — чи є вже результат?
        local result_md="$sync_dir/task-${task_id}.result.md"
        local done_file="$SPACES_DIR/$to/tasks/done/task-${task_id}.md"

        if [[ -f "$result_md" ]]; then
            status="done"
            notes+=", result received"
            # Копіюємо результат в outbox
            cp "$result_md" "$result_file"
            echo "   📤 Результат: $result_file"
        elif [[ -f "$done_file" ]]; then
            status="done"
            notes+=", found in done/"
            cp "$done_file" "$result_file"
            echo "   📤 Результат: $result_file"
        else
            status="pending"
            notes+=", awaiting execution"
        fi

    else
        # ── Віддалений простір ──
        echo "   🌐 Віддалений простір: $to"

        # Мапінг імені простору на Tailscale-вузол
        local node=""
        case "$to" in
            vuzol)       node="vuzol" ;;
            hp-pavilion) node="hp-pavilion" ;;
            *)           node="$to" ;;
        esac

        if is_remote_online "$node"; then
            echo "   🟢 $node онлайн, передаю задачу..."

            # Формуємо inbox-файл для віддаленого вузла
            local tmp_json
            tmp_json=$(mktemp /tmp/check-inbox-XXXXXX.json)
            cp "$file" "$tmp_json"

            # Передаємо через scp
            if scp -o ConnectTimeout=5 "$tmp_json" "${node}:~/spaces/orchestrator/inbox/$(basename "$file")" 2>/dev/null; then
                echo "   ✅ Задачу передано на $node"
                notes="remote → $node, delivered"
                status="pending"
            else
                echo "   ❌ Помилка передачі на $node"
                notes="remote → $node, scp failed"
                status="failed"
            fi
            rm -f "$tmp_json"

        else
            echo "   🔴 $node офлайн"
            notes="remote → $node, offline"
            status="failed"
        fi
    fi

    # ── Записуємо результат в outbox (якщо done/failed) ──
    if [[ "$status" == "failed" ]]; then
        cat > "$result_file" << RESULT
# Result: $task_id

- **From**: ${from:-<unknown>}
- **To**: $to
- **Status**: failed
- **Completed**: $(date -u '+%Y-%m-%dT%H:%M:%SZ')

## Error
$notes
RESULT
        echo "   📤 Outbox (failed): $result_file"
    fi

    # ── Архівуємо inbox-файл ──
    if [[ "$status" == "done" || "$status" == "failed" ]]; then
        mv "$file" "$ARCHIVE/"
        echo "   🗄️  Архівовано: $fname → archive/"
    fi

    # ── Логуємо ──
    log_route "$task_id" "${from:-?}" "$to" "$status" "$notes"
    return 0
}

# ═══════════════════════════════════════════
# Основна логіка
# ═══════════════════════════════════════════

echo "═══════════════════════════════════════════"
echo "📬 check-inbox.sh — $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════"

# Збираємо JSON-файли (пропускаємо README.md)
json_files=()
while IFS= read -r line; do
    json_files+=("$line")
done < <(find "$INBOX" -maxdepth 1 -name "*.json" -type f 2>/dev/null | sort)

if [[ ${#json_files[@]} -eq 0 ]]; then
    echo "📭 Inbox порожній — нічого обробляти."
    exit 0
fi

echo "📨 Знайдено ${#json_files[@]} файлів у inbox"

processed=0
for file in "${json_files[@]}"; do
    process_inbox_file "$file" && ((processed++)) || true
done

echo ""
echo "═══════════════════════════════════════════"
echo -e "✅ Оброблено: ${GREEN}${processed}${NC} / ${#json_files[@]}"
echo "═══════════════════════════════════════════"

exit 0
