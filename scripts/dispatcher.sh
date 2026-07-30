#!/bin/bash
# ── Task Dispatcher — space-aware orchestration for mac-mini ──
# Polls Task API, finds best agent, launches Claude in space directory
# Usage: dispatcher.sh [--once] [--interval SECONDS]

set -euo pipefail

TASK_API="${TASK_API_URL:-http://vuzol:8000}"
INTERVAL=15
MAX_BACKOFF=300
MODEL_ROUTING="/root/.claude/model-routing.json"
SPACES_DIR="${SPACES_DIR:-$HOME/spaces}"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# ── Find best agent for a task ─────────────────────────────────
find_agent() {
    local space="$1" task="$2" best_agent="" best_score=0

    local agents_dir="$SPACES_DIR/$space/agents"
    [[ -d "$agents_dir" ]] || { echo ""; return; }

    for agent_file in "$agents_dir"/*.md; do
        [[ -f "$agent_file" ]] || continue
        local agent_name=$(basename "$agent_file" .md)
        local score=0

        # Keyword matching: role words in agent description → score
        for word in $(echo "$task" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' ' '); do
            grep -qi "$word" "$agent_file" && ((score+=1)) || true
        done

        # Bonus patterns for stronger matching
        grep -qiE "(primary|default|main|general)" "$agent_file" && ((score+=2)) || true

        if (( score > best_score )); then
            best_score=$score
            best_agent=$agent_name
        fi
    done

    # Fallback: first available agent
    [[ -z "$best_agent" ]] && best_agent=$(ls "$agents_dir"/*.md 2>/dev/null | head -1 | xargs basename | sed 's/\.md$//')

    echo "$best_agent"
}

# ── Get model for task complexity ──────────────────────────────
get_model() {
    local complexity="${1:-medium}"
    jq -r ".routing.${complexity} | join(\",\")" "$MODEL_ROUTING" 2>/dev/null || echo "ds-flash,ds-pro"
}

# ── Process one task ───────────────────────────────────────────
process_task() {
    # Claim next pending task
    local task_json
    task_json=$(curl -s --max-time 10 "${TASK_API}/task/next")
    [[ -n "$task_json" ]] || return 1

    local task_id=$(echo "$task_json" | jq -r '.id // empty')
    [[ -n "$task_id" ]] || return 1

    local space=$(echo "$task_json" | jq -r '.space // "default"')
    local payload=$(echo "$task_json" | jq -r '.payload.task // ""')
    local priority=$(echo "$task_json" | jq -r '.priority // 50')

    log "Claimed task #$task_id ($space, p=$priority): $payload"

    # Find agent
    local agent=$(find_agent "$space" "$payload")
    [[ -z "$agent" ]] && {
        log "No agent found for space=$space, skipping"
        curl -s -X POST "${TASK_API}/tasks/${task_id}/fail" \
            -H "Content-Type: application/json" \
            -d "{\"error\":\"no agent found for space $space\"}" > /dev/null
        return 1
    }
    log "  → agent: $agent"

    # Get model
    local complexity="medium"
    echo "$payload" | grep -qiE "(critical|urgent|складн)" && complexity="complex"
    echo "$payload" | grep -qiE "(review|перевір|критик)" && complexity="critique"
    local models=$(get_model "$complexity")
    local model=$(echo "$models" | cut -d, -f1)

    # Launch Claude in space
    local space_dir="$SPACES_DIR/$space"
    cd "$space_dir"

    local result_file="/tmp/task-${task_id}.result"
    local start_ts=$(date +%s)

    # Build context: AGENTS.md + SOUL.md + rules
    local context=""
    [[ -f "$space_dir/AGENTS.md" ]] && context+="$(cat "$space_dir/AGENTS.md")\n\n"
    [[ -f "$space_dir/SOUL.md" ]] && context+="$(cat "$space_dir/SOUL.md")\n\n"

    # Execute via Claude
    claude --model "$model" --prompt "$context\n\nTASK: $payload" > "$result_file" 2>/tmp/task-${task_id}.err || {
        local err=$(cat /tmp/task-${task_id}.err)
        log "  ✗ FAILED: $err"
        curl -s -X POST "${TASK_API}/tasks/${task_id}/fail" \
            -H "Content-Type: application/json" \
            -d "{\"error\":$(echo "$err" | jq -Rs .)}" > /dev/null
        return 1
    }

    local end_ts=$(date +%s)
    local duration=$((end_ts - start_ts))
    local result=$(cat "$result_file")

    log "  ✓ DONE (${duration}s)"

    # Report back
    curl -s -X POST "${TASK_API}/tasks/${task_id}/done" \
        -H "Content-Type: application/json" \
        -d "{\"result\":$(echo "$result" | jq -Rs .),\"agent\":\"$agent\",\"model\":\"$model\",\"duration_ms\":$((duration * 1000))}" > /dev/null

    # Cleanup
    rm -f "$result_file" /tmp/task-${task_id}.err
}

# ── Main loop ──────────────────────────────────────────────────
main() {
    local once=false
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --once) once=true; shift ;;
            --interval) INTERVAL="$2"; shift 2 ;;
            *) shift ;;
        esac
    done

    log "Dispatcher starting (interval=${INTERVAL}s)"
    local backoff=$INTERVAL

    while true; do
        local before=$(date +%s)

        if process_task; then
            backoff=$INTERVAL  # reset backoff on success
        else
            backoff=$(( backoff * 2 ))
            (( backoff > MAX_BACKOFF )) && backoff=$MAX_BACKOFF
            log "No task available, backoff=${backoff}s"
        fi

        $once && break

        local elapsed=$(($(date +%s) - before))
        local sleep_time=$(( backoff - elapsed ))
        (( sleep_time > 0 )) && sleep "$sleep_time"
    done
}

main "$@"
