# Space: orchestrator

> Cross-space communication hub. Routes tasks between spaces via inbox/outbox.
> Created: 2026-07-27.

## Purpose

Orchestrator — це центральний диспетчер для всіх просторів mac-mini.
Він не виконує задачі самостійно, а маршрутизує їх до потрібного простору.

## How It Works

```
Space A → inbox/{id}.json → orchestrator (read+route) → Space B → outbox/{id}.md → Space A
```

## Inbox (JSON)

Вхідні завдання з інших просторів. Кожен файл — окремий запит.

**Шлях:** `inbox/{timestamp}-{source}-{id}.json`

**Формат:**
```json
{
  "id": "string — унікальний ідентифікатор",
  "from": "string — простір-відправник (напр., system)",
  "to": "string — цільовий простір (напр., hp-pavilion)",
  "task": "string — опис завдання",
  "priority": "low | normal | high | critical",
  "deadline": "ISO8601 або null",
  "context": {},
  "created": "ISO8601"
}
```

## Outbox (Markdown)

Результати виконання. Кожен файл — звіт про виконане завдання.

**Шлях:** `outbox/{task-id}.md`

**Формат:**
```markdown
# Result: {task-id}

- **From**: {source-space}
- **To**: {target-space}
- **Status**: done | failed | partial
- **Completed**: ISO8601

## Output
... (результати, логи, файли)
```

## Routing Rules

1. Прочитай `inbox/` — знайди нові `.json` файли (без відповідного результату в `outbox/`)
2. Визнач цільовий простір із поля `"to"`
3. Передай задачу в цільовий простір:
   - Якщо простір локальний (`~/spaces/<name>/`) — скеруй у його `tasks/active/`
   - Якщо простір на іншому вузлі — передай через Tailscale/SSH
4. Коли цільовий простір виконає задачу — запиши результат в `outbox/{task-id}.md`
5. Перемісти оброблений inbox-файл у `archive/`

## Available Spaces

| Space | Path | Node | Status |
|-------|------|------|--------|
| `system` | `~/spaces/system/` | mac-mini | 🟢 active |
| `orchestrator` | `~/spaces/orchestrator/` | mac-mini | 🟢 active |
| `hp-pavilion` | (remote) | hp-pavilion | 🔴 offline |
| `vuzol` | (remote) | vuzol | 🟢 active |

## Priority Handling

1. `critical` — негайно, перервати поточні задачі
2. `high` — наступна в черзі після critical
3. `normal` — стандартна черга FIFO
4. `low` — виконувати коли немає інших задач

## Rules

1. Orchestrator не виконує задачі — тільки маршрутизує
2. Кожен inbox-запит отримує результат в outbox (done, failed, або partial)
3. Не змінюй чужі inbox-файли — тільки читай
4. Архівуй оброблені: `inbox/` → `archive/`
5. Якщо цільовий простір офлайн — помічай статус `failed` і повідом відправника
6. Логуй усі маршрутизації в `memory/routing-log.md`
| `projects-coding` | `~/spaces/projects-coding/` | mac-mini | 🟢 active |
