# 🎯 Оркестрація — диспетчеризація задач

## Як працює

```
Користувач (Telegram)
       │
       ▼
   cc-connect
       │
       ▼
   vuzol (Claude)
       │  аналізує задачу
       │  класифікує → простір
       ▼
   Task API (PostgreSQL tasks)
       │
       │  POST /api/task/create
       │  {"space": "legal", "payload": {"task": "апеляція OHSA s.50"}}
       ▼
   Черга (status=pending)
       │
       │  mac-mini poll: GET /api/task/claim/mac-mini
       ▼
   mac-mini (dispatcher.sh)
       │  визначає агента (legal → legal-analyst)
       │  читає model-routing.json → модель
       │  запускає Claude в просторі
       ▼
   Результат → POST /api/task/result
```

## База даних: `orchestrator`

```sql
CREATE TYPE task_status AS ENUM ('pending', 'claimed', 'running', 'done', 'failed');

CREATE TABLE tasks (
    id            SERIAL PRIMARY KEY,
    space         VARCHAR(64) NOT NULL,          -- coding | legal | medicine
    target        VARCHAR(64) DEFAULT 'mac-mini', -- хто виконує
    priority      SMALLINT DEFAULT 0,
    status        task_status DEFAULT 'pending',
    payload       JSONB NOT NULL DEFAULT '{}',   -- {"task": "..."}
    result        TEXT,
    error         TEXT,
    created_at    TIMESTAMPTZ DEFAULT now(),
    claimed_at    TIMESTAMPTZ,
    started_at    TIMESTAMPTZ,
    done_at       TIMESTAMPTZ,
    retries       SMALLINT DEFAULT 0,
    max_retries   SMALLINT DEFAULT 3
);
```

## Простори → Агенти

| Простір | Агенти | Для чого |
|---------|--------|----------|
| `coding` | dev, tester, architect, reviewer, ops | Код, скрипти, деплой |
| `legal` | legal-analyst, email-drafter, doc-reviewer | Юридичні справи |
| `medicine` | diagnostician, lab-analyst, researcher | Медичні кейси |

## API ендпоінти

| Метод | Шлях | Призначення |
|-------|------|-------------|
| GET | `/health` | Статус сервера |
| GET | `/heartbeat` | Останній heartbeat mac-mini |
| POST | `/heartbeat?source=mac-mini` | Записати heartbeat |
| POST | `/api/task/create` | Створити задачу |
| GET | `/api/task/claim/{target}` | Отримати наступну задачу |
| POST | `/api/task/result` | Зберегти результат |
| GET | `/api/status` | Статус всіх проектів (state.py list --json) |
