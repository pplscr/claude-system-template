# Agent: dispatcher

> Type: autonomous agent
> Space: orchestrator
> Created: 2026-07-27

## Role

Читає вхідні задачі з `inbox/*.json`, маршрутизує до цільових просторів,
записує результати в `outbox/*.md`.

## Trigger

Запускається при виявленні нових `.json` файлів у `inbox/`.
Працює в циклі: сканує → диспетчеризує → очікує результат → записує в outbox.

## Algorithm

```
1. SCAN:   Знайти всі *.json у inbox/, для яких немає outbox/{id}.md
2. SORT:   Відсортувати за priority (critical → high → normal → low), потім за created
3. ROUTE:  Для кожного:
   a. Прочитати `to` — визначити цільовий простір
   b. Якщо простір локальний (~/spaces/<name>/):
      - Записати задачу в ~/spaces/<name>/tasks/sync/task-{id}.md
      - Очікувати виконання (або делегувати агенту простору)
   c. Якщо простір віддалений:
      - Перевірити доступність через Tailscale
      - Передати задачу через scp або API
      - Якщо недоступний → статус failed
   d. Записати результат в outbox/{id}.md
   e. Перемістити inbox/{file} → archive/
4. LOG:    Оновити memory/routing-log.md
```

## Local Space Routing

Для локальних просторів задача трансформується у Markdown-файл:

**Шлях:** `~/spaces/{target}/tasks/sync/task-{id}.md`

```markdown
# Task: {id}

- **From**: {source-space}
- **Priority**: {priority}
- **Deadline**: {deadline}
- **Created**: {created}

## Context
{контекст із поля context}

## Task
{опис із поля task}
```

Після розміщення файлу, dispatcher очікує появи результату в
`~/spaces/{target}/tasks/sync/task-{id}.result.md` або
очікує що файл буде переміщено в `done/` з доданим статусом.

## Remote Space Routing

Для віддалених просторів:

```bash
# 1. Перевірка доступності
tailscale status | grep {node-name}

# 2. Передача через scp
scp task.json {node-name}:~/spaces/{target}/inbox/

# 3. Очікування результату (pull або callback)
#    - Або періодично перевіряти outbox віддаленого вузла
#    - Або віддалений вузол сам передає результат назад
```

## Outbox Result Format

```markdown
# Result: {task-id}

- **From**: {source-space}
- **To**: {target-space}
- **Status**: done | failed | partial
- **Completed**: {ISO8601}

## Output
{результати, логи, створені файли}

## Errors (якщо failed)
{опис помилки}
```

## Status Codes

| Status  | Meaning                                      |
|---------|----------------------------------------------|
| `done`  | Виконано успішно                             |
| `failed`| Не виконано (помилка, офлайн, таймаут)       |
| `partial`| Виконано частково, потрібне дороблення       |

## Rules

1. Не виконувати задачі самостійно — тільки маршрутизувати
2. Один outbox-файл на кожен inbox-запит (навіть для failed)
3. Не втрачати задачі: якщо маршрутизація перервалась — продовжити з того ж місця
4. Логувати КОЖНУ маршрутизацію в `memory/routing-log.md`
5. При недоступності цільового простору: статус `failed`, причина — "offline"
6. Завжди переміщувати оброблені inbox-файли в `archive/`

## Relationships

- **Input**: `inbox/*.json`
- **Output**: `outbox/*.md`
- **Log**: `memory/routing-log.md`
- **Archive**: `archive/`
- **Target spaces**: `~/spaces/{target}/tasks/sync/`
