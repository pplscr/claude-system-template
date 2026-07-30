# Архітектура Case State Management — v2.0 (PostgreSQL)

**Дата:** 2026-07-30
**Сервер:** vuzol (100.84.177.33) — PostgreSQL 16, `orchestrator` DB

## Проблема: три системи, що перетинаються

До уніфікації існувало **три системи**, які частково дублювали одне одного:

| Система | Де | Тип | Дані |
|---|---|---|---|
| **state.py** | mac-mini → vuzol | JSON файли (`~/.claude/projects/`) | 9 проєктів (fw-mahnung, factory-nsc, cibc...) |
| **case_db.py** | vuzol | PostgreSQL (`orchestrator`) | 2 юр. справи (1283-26-UR, F&W-3M) |
| **task-api.py** | vuzol :8000 | HTTP + subprocess→state.py | Обгортка над state.py + heartbeat + task queue |

**Дублювання:** `factory-nsc` був і в state.py (JSON, progress=70%, deadline=29.07 — застарілий), і в case_db.py (PostgreSQL, progress=75%, deadline=31.07 — актуальний). `fw-debt`/`fw-mahnung` — аналогічно.

## Рішення: єдина PostgreSQL-архітектура

**Одна БД, один CLI, один API.**

```
┌─────────────────────────────────────────────────────────┐
│                  vuzol (100.84.177.33)                   │
│                                                         │
│  PostgreSQL 16 — orchestrator DB (ЄДИНЕ ДЖЕРЕЛО ПРАВДИ) │
│  ┌──────────────────────────────────────────────────┐   │
│  │ projects          — всі проєкти + юр. справи      │   │
│  │ project_deadlines — дедлайни (days_left авто)     │   │
│  │ project_steps     — кроки (completed/pending)     │   │
│  │ project_activity  — audit log (хто/що/коли)       │   │
│  │ project_parties   — сторони (для юр. справ)       │   │
│  │ project_notes     — критичні нотатки              │   │
│  │ tasks             — черга завдань (вже є)         │   │
│  │ agent_executions  — метрики агентів (вже є)       │   │
│  └──────────────────────────────────────────────────┘   │
│                         ▲                               │
│  ┌──────────────────────┴──────────────────────────┐   │
│  │ state3.py — єдиний CLI (замінює state.py +      │   │
│  │             case_db.py)                          │   │
│  │  list | show | deadlines | done | add |          │   │
│  │  progress | status | phase | deadline |          │   │
│  │  activity | note | conf | init | priority        │   │
│  └─────────────────────────────────────────────────┘   │
│                         ▲                               │
│  ┌──────────────────────┴──────────────────────────┐   │
│  │ task-api.py (port 8000) — єдиний REST API       │   │
│  │  GET  /health, /heartbeat                        │   │
│  │  GET  /projects, /projects/:id                   │   │
│  │  POST /projects/:id/activity                     │   │
│  │  POST /projects/:id/done                         │   │
│  │  GET  /tasks, POST /task/submit                  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└──────────────────────────┬──────────────────────────────┘
                           │ SSH / HTTP
┌──────────────────────────┴──────────────────────────────┐
│                    mac-mini (M4)                         │
│                                                         │
│  Claude Code                                            │
│  ├── ~/spaces/legal/case-db → SSH wrapper до state3.py  │
│  ├── Native Task tool → локальні таски сесії             │
│  └── case.json → локальний кеш (sync з БД)              │
│                                                         │
│  Інші сервіси:                                          │
│  ├── morning digest → GET /projects (HTTP)              │
│  └── web UI → GET /projects/:id (HTTP)                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Компоненти

### 1. PostgreSQL — `orchestrator` DB

```sql
-- Основна таблиця
projects (id, project_id, name, tier, status, phase, priority,
          progress_pct, description, filed_date, confirmation_numbers,
          contact, last_activity, last_updated, created_at)

-- Дедлайни (з авто-розрахунком days_left = deadline_date - CURRENT_DATE)
project_deadlines (id, project_id, deadline_key, deadline_date,
                   description, status, created_at)

-- Кроки (completed/pending)
project_steps (id, project_id, step_text, step_type, sort_order,
               done_at, created_at)

-- Audit log
project_activity (id, project_id, activity_text, source, created_at)

-- Сторони (юр. справи)
project_parties (id, project_id, party_role, party_name,
                 party_email, party_extra)

-- Нотатки
project_notes (id, project_id, note_type, note_text, created_at)
```

### 2. state3.py — єдиний CLI

Замінює `state.py` (JSON) + `case_db.py` (DB). Всі команди:

```bash
# Перегляд
python3 /root/scripts/state3.py list              # всі проєкти + дедлайни
python3 /root/scripts/state3.py show <id>         # повний стан одного
python3 /root/scripts/state3.py deadlines          # всі дедлайни (сортовані)

# Мутації
python3 /root/scripts/state3.py done <id> "<step>"     # крок → completed
python3 /root/scripts/state3.py add <id> pending|completed "<step>"
python3 /root/scripts/state3.py progress <id> <0-100>
python3 /root/scripts/state3.py status <id> <active|paused|done|blocked>
python3 /root/scripts/state3.py phase <id> <phase>
python3 /root/scripts/state3.py deadline <id> <key> <YYYY-MM-DD> "<desc>"
python3 /root/scripts/state3.py activity <id> "<text>"
python3 /root/scripts/state3.py note <id> <type> "<text>"
python3 /root/scripts/state3.py conf <id> <key> <value>
python3 /root/scripts/state3.py priority             # авто-пріоритети

# Управління
python3 /root/scripts/state3.py init <id> "<name>" <tier>   # новий проєкт
python3 /root/scripts/state3.py migrate              # JSON → DB міграція
```

### 3. task-api.py — єдиний REST API (port 8000)

```bash
# Існуючі (без змін)
GET  /health                    # {"status":"ok"}
GET  /heartbeat                 # статус mac-mini
POST /heartbeat                 # записати heartbeat
POST /task/submit               # додати задачу в чергу
GET  /task/status/:id           # статус задачі

# Нові (замість subprocess→state.py)
GET  /projects                  # всі проєкти (state3.py list --json)
GET  /projects/:id              # один проєкт (state3.py show)
POST /projects/:id/activity     # оновити активність
POST /projects/:id/done         # завершити крок
POST /projects/:id/update       # оновити будь-яке поле

# Аліаси
GET  /cases                     # → /projects (фільтр: тільки юр. справи)
GET  /cases/:id                 # → /projects/:id
```

### 4. mac-mini: локальні обгортки

```bash
# Для Claude Code (швидкий доступ):
~/spaces/legal/case-db -> ssh vuzol python3 /root/scripts/state3.py "$@"

# Локальний кеш (sync з БД):
~/spaces/legal/factory-nsc/case.json  # оновлювати через state3.py show > case.json
```

## Як це працює в реальному часі

```
1. Claude заходить у справу
   → case-db show 1283-26-UR
   → бачить: 75%, афідевіт завтра, RTC через 6 днів

2. Claude створює draft
   → case-db activity 1283-26-UR "Created draft motion for X"
   → БД: last_activity оновлено, activity log поповнено

3. Користувач виконав крок
   → case-db done 1283-26-UR "Pick up notarized affidavit"
   → БД: крок moved pending→completed, progress_pct перераховано

4. Morning digest (cron на vuzol)
   → curl http://localhost:8000/projects
   → бачить всі проєкти з актуальними дедлайнами

5. Інша сесія Claude (на вузлі)
   → curl http://localhost:8000/cases/1283-26-UR
   → бачить той самий стан, що й mac-mini
```

## Міграція (state.py JSON → PostgreSQL)

1. Прочитати всі `~/.claude/projects/*.json`
2. Для кожного: створити запис у `projects`
3. Мігрувати `deadlines` → `project_deadlines`
4. Мігрувати `next_steps` → `project_steps` (type=pending)
5. Мігрувати `last_activity` → `project_activity`
6. Видалити старі записи `cases` які конфліктують з `projects` (factory-nsc = 1283-26-UR)

## To-Do

- [ ] Створити `state3.py` (merge state.py + case_db.py)
- [ ] Оновити `task-api.py` (state3.py замість state.py + /cases endpoints)
- [ ] Мігрувати дані з `~/.claude/projects/*.json` у PostgreSQL
- [ ] Оновити `case-db` wrapper на mac-mini
- [ ] Оновити CLAUDE.md інструкції
