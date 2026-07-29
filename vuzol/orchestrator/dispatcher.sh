#!/usr/bin/env bash
# dispatcher.sh — Mac Executor v2: poll vuzol → claim task → space-aware dispatch
# v2 (2026-07-29): просторовий контекст + правильний агент + model-routing.json
#
# Сервер (vuzol) класифікує задачу → простір.
# Mac забирає готову задачу, знаходить правильного агента в просторі,
# запускає Claude з просторовим контекстом (CLAUDE.md + SPACE.md).
# Claude делегує агенту через launch_agent (або inline якщо orchestration OFF).
#
# Запускається через LaunchAgent як KeepAlive-демон.

# ── Запобігання подвійному запуску ──
PIDFILE="/tmp/worker.pid"
if [[ -f "$PIDFILE" ]]; then
  old_pid=$(cat "$PIDFILE" 2>/dev/null)
  if kill -0 "$old_pid" 2>/dev/null; then
    exit 0
  fi
fi
echo $$ > "$PIDFILE"
trap "rm -f $PIDFILE" EXIT

set -euo pipefail

API_PRIMARY="http://100.84.177.33:8000"   # Tailscale direct
API_FALLBACK="http://localhost:8001"        # SSH tunnel
POLL_INTERVAL=15
MAX_BACKOFF=300  # 5 min max
BACKOFF=15
TARGET="mac-mini"
LOG="/tmp/worker.log"
SPACES_DIR="$HOME/spaces"
ROUTING_FILE="$HOME/.claude/model-routing.json"

# Вибрати доступний API
detect_api() {
  if curl -s --connect-timeout 2 "${API_PRIMARY}/health" > /dev/null 2>&1; then
    echo "$API_PRIMARY"
  else
    echo "$API_FALLBACK"
  fi
}

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }

# ── Відправити heartbeat (мак живий) ──
send_heartbeat() {
  local api
  api=$(detect_api)
  curl -s --connect-timeout 3 "${api}/heartbeat?source=mac-mini" > /dev/null 2>&1 || true
}

# ── Відправити результат на сервер ──
report_result() {
  local task_id="$1" result="$2" success="$3"
  local escaped api
  api=$(detect_api)
  escaped=$(echo "$result" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))" 2>/dev/null || echo '""')
  curl -s -X POST "${api}/task/result" \
    -H "Content-Type: application/json" \
    -d "{\"task_id\":\"${task_id}\",\"result\":${escaped},\"success\":${success}}" \
    > /dev/null 2>&1 || true
}

# ── Знайти найкращого агента в просторі ──
# Пріоритет: шукаємо ключові слова в тексті задачі → матчимо роль агента
find_best_agent() {
  local space_dir="$1" task_text="$2"
  local best_agent="" best_score=0

  for agent_dir in "$space_dir/agents"/*/; do
    [[ -d "$agent_dir" ]] || continue
    local agent_name
    agent_name=$(basename "$agent_dir")
    [[ "$agent_name" == _* ]] && continue

    local ag_md="$agent_dir/AGENTS.md"
    local soul_md="$agent_dir/SOUL.md"
    [[ -f "$ag_md" ]] || continue

    # Читаємо роль агента
    local role
    role=$(grep "^role:" "$ag_md" 2>/dev/null | cut -d: -f2- | xargs || echo "$agent_name")

    # Скор на основі збігу ключових слів у ролі із задачею
    local score=0
    local lower_task
    lower_task=$(echo "$task_text" | tr '[:upper:]' '[:lower:]')
    local lower_role
    lower_role=$(echo "$role" | tr '[:upper:]' '[:lower:]')

    # Співпадіння слів ролі в задачі
    for word in $lower_role; do
      [[ ${#word} -lt 4 ]] && continue  # пропускаємо короткі слова
      if echo "$lower_task" | grep -q "$word" 2>/dev/null; then
        score=$((score + 3))
      fi
    done

    # Бонуси за конкретні патерни задачі (grep-based, сумісний з bash 3.2)
    bonus_match() { echo "$lower_task" | grep -qE "$1" 2>/dev/null; }

    if bonus_match 'тест|test|перевір'; then
        [[ "$agent_name" == "tester" ]] && score=$((score + 10))
    fi
    if bonus_match 'архітектур|architecture|design|структур'; then
        [[ "$agent_name" == "architect" ]] && score=$((score + 10))
    fi
    if bonus_match 'review|огляд|перевір|якість'; then
        [[ "$agent_name" == "reviewer" ]] && score=$((score + 10))
    fi
    if bonus_match 'deploy|деплой|сервер|server|ssh'; then
        [[ "$agent_name" == "ops" ]] && score=$((score + 10))
    fi
    if bonus_match 'legal|юрид|recht|gericht|widerspruch|OLRB|OHSA|DFR|суд'; then
        [[ "$agent_name" == "legal-analyst" ]] && score=$((score + 10))
    fi
    if bonus_match 'лист|brief|schreiben|email|draft|афідевіт|affidavit'; then
        [[ "$agent_name" == "email-drafter" ]] && score=$((score + 10))
    fi
    if bonus_match 'документ|document|ocr'; then
        [[ "$agent_name" == "doc-reviewer" ]] && score=$((score + 10))
    fi
    if bonus_match 'аналіз|lab|кров|blood|показник'; then
        [[ "$agent_name" == "lab-analyst" ]] && score=$((score + 10))
    fi
    if bonus_match 'діагноз|симптом|symptom|diagnos'; then
        [[ "$agent_name" == "diagnostician" ]] && score=$((score + 10))
    fi
    if bonus_match 'дослід|research|pubmed|статт|paper'; then
        [[ "$agent_name" == "researcher" ]] && score=$((score + 10))
    fi
    if bonus_match 'код|code|script|bash|python|розроб|dev'; then
        [[ "$agent_name" == "dev" ]] && score=$((score + 10))
    fi

    if [[ $score -gt $best_score ]]; then
      best_score=$score
      best_agent="$agent_name"
    fi
  done

  # fallback: default агент для простору (якщо scorе=0 у всіх)
  if [[ -z "$best_agent" ]]; then
    case "$(basename "$space_dir")" in
      legal)    best_agent="legal-analyst" ;;
      medicine) best_agent="lab-analyst" ;;
      coding)   best_agent="dev" ;;
    esac
  fi

  # absolute fallback: перший доступний (не _)
  if [[ -z "$best_agent" ]]; then
    for agent_dir in "$space_dir/agents"/*/; do
      local aname
      aname=$(basename "$agent_dir")
      [[ "$aname" == _* ]] && continue
      [[ -f "$agent_dir/AGENTS.md" ]] && { best_agent="$aname"; break; }
    done
  fi

  echo "$best_agent"
}

# ── Отримати модель з model-routing.json ──
get_agent_model() {
  local agent_name="$1"
  local model

  if [[ -f "$ROUTING_FILE" ]]; then
    # jq: per_agent_overrides → by_task → defaults
    model=$(jq -r ".per_agent_overrides[\"${agent_name}\"].model // empty" "$ROUTING_FILE" 2>/dev/null || echo "")
    if [[ -n "$model" && "$model" != "null" ]]; then
      echo "$model"
      return
    fi
  fi

  # absolute fallback
  echo "nvidia/nemotron-3-super-120b-a12b:free"
}

get_agent_provider() {
  local agent_name="$1"
  local provider

  if [[ -f "$ROUTING_FILE" ]]; then
    provider=$(jq -r ".per_agent_overrides[\"${agent_name}\"].provider // empty" "$ROUTING_FILE" 2>/dev/null || echo "")
    if [[ -n "$provider" && "$provider" != "null" ]]; then
      echo "$provider"
      return
    fi
  fi

  echo "openrouter"
}

# ── Виконати задачу ──
process_task() {
  local task_id="$1" task_text="$2" space="$3"

  # Якщо простір не вказано — coding за замовчуванням
  [[ -z "$space" || "$space" == "null" ]] && space="coding"

  local SPACE_DIR="$HOME/spaces/$space"
  if [[ ! -d "$SPACE_DIR" ]]; then
    log "⚠️  Простір '$space' не існує → пробую знайти..."
    # Спробуємо вгадати за ключовими словами
    local lower
    lower=$(echo "$task_text" | tr '[:upper:]' '[:lower:]')
    if echo "$lower" | grep -qE 'legal|recht|gericht|widerspruch|olrb|ohsa|dfr|суд|юр|адвокат'; then
      space="legal"
    elif echo "$lower" | grep -qE 'медиц|аналіз|кров|симптом|діагноз|health|medical|doctor'; then
      space="medicine"
    else
      space="coding"
    fi
    SPACE_DIR="$HOME/spaces/$space"
    log "   → визначено простір: $space"
  fi

  # Знаходимо найкращого агента
  local agent
  agent=$(find_best_agent "$SPACE_DIR" "$task_text")
  if [[ -z "$agent" ]]; then
    log "❌ Немає агентів у просторі '$space' — пропускаю #${task_id}"
    report_result "$task_id" "Простір '$space' не має агентів" "false"
    return
  fi

  # Модель і провайдер з model-routing.json
  local agent_model agent_provider
  agent_model=$(get_agent_model "$agent")
  agent_provider=$(get_agent_provider "$agent")

  log "📋 #${task_id} → ${space}/${agent} | ${agent_model} | ${task_text:0:100}..."

  # Читаємо контекст агента
  local agent_role agent_soul
  agent_role=$(cat "$SPACE_DIR/agents/$agent/AGENTS.md" 2>/dev/null || echo "Роль: $agent")
  agent_soul=$(cat "$SPACE_DIR/agents/$agent/SOUL.md" 2>/dev/null || echo "")

  # Правила простору
  local space_rules=""
  for rule in "$SPACE_DIR/rules"/*.md; do
    [[ -f "$rule" ]] && space_rules+="$(cat "$rule")\n\n"
  done

  local outfile="/tmp/task-${task_id}.out"
  local rc=0

  # Запускаємо Claude У ПРОСТОРІ з ПОВНИМ КОНТЕКСТОМ
  cd "$SPACE_DIR"

  /opt/homebrew/bin/claude -p "$(cat <<PROMPT
<this is a request from a parent process>

Ти — агент **${agent}** у просторі **${space}** на mac-mini.
Твоя робоча директорія: ${SPACE_DIR}

## Твоя роль
${agent_role}

## SOUL
${agent_soul}

## Правила простору
${space_rules}

## ЗАВДАННЯ
${task_text}

## ІНСТРУКЦІЯ
1. Виконай завдання згідно з роллю.
2. Відповідай українською, коротко, по суті.
3. Якщо потрібно делегувати — використовуй launch_agent.
4. Якщо потрібен доступ до БРАУЗЕРА — кажи мені (оркестратору), я запущу browser agent.
PROMPT
)" --model "$agent_model" --max-turns 12 --output-format text > "$outfile" 2>&1 || rc=$?

  local result
  result=$(tail -500 "$outfile" 2>/dev/null || echo "(empty)")
  local success="false"
  [[ $rc -eq 0 ]] && success="true"

  report_result "$task_id" "$result" "$success"
  rm -f "$outfile"
  log "✅ #${task_id} done (rc=$rc, ${space}/${agent})"
}

# ── Головний цикл ──
log "🚀 Worker v2 started (target=${TARGET}, interval=${POLL_INTERVAL}s)"
log "   primary: ${API_PRIMARY}"
log "   fallback: ${API_FALLBACK}"
log "   spaces: $(ls -d "$SPACES_DIR"/*/ 2>/dev/null | xargs -I{} basename {} | grep -v '^_' | tr '\n' ' ')"

server_online=false
heartbeat_counter=0

while true; do
  api=$(detect_api)

  # Heartbeat кожні 60s
  heartbeat_counter=$((heartbeat_counter + POLL_INTERVAL))
  if [[ $heartbeat_counter -ge 60 ]]; then
    send_heartbeat
    heartbeat_counter=0
  fi

  resp=$(curl -s --connect-timeout 5 "${api}/task/claim/${TARGET}" 2>/dev/null || echo "")

  if [[ -z "$resp" ]]; then
    if $server_online; then
      log "🔴 Сервер недоступний — чекаю..."
      server_online=false
      BACKOFF=15
    fi
    # Exponential backoff: 15→30→60→120→240→max 300
    log "⏳ Backoff ${BACKOFF}s..."
    sleep "$BACKOFF"
    BACKOFF=$(( BACKOFF * 2 ))
    [ "$BACKOFF" -gt "$MAX_BACKOFF" ] && BACKOFF="$MAX_BACKOFF"
    continue
  fi

  # Server is back — reset backoff
  BACKOFF=15

  if ! $server_online; then
    log "🟢 Сервер онлайн (via ${api})"
    server_online=true
  fi

  # Парсимо відповідь
  task_id=$(echo "$resp" | jq -r '.id // empty' 2>/dev/null)
  task_text=$(echo "$resp" | jq -r '.payload.task // .payload // empty' 2>/dev/null)
  space=$(echo "$resp" | jq -r '.space // empty' 2>/dev/null)

  if [[ -z "$task_id" || "$task_id" == "null" ]]; then
    sleep "$POLL_INTERVAL"
    continue
  fi

  process_task "$task_id" "$task_text" "$space"
done
