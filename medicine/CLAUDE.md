# Медицина — mac-mini

Аналіз лабораторних результатів, симптомів, медичної літератури. Не ставить діагнозів.

## Що де лежить

| Файл/Директорія | Призначення |
|------|-------------|
| `CLAUDE.md` | Цей файл — **авто-завантажується** |
| `SPACE.md` | Метадані простору |
| `task.json` | Стан завдань (авто-оновлюється) |
| `agents/` | Визначення агентів — `ls agents/` |
| `knowledge/` | Медична література, гайдлайни |
| `memory/` | Файли пам'яті |

## Агенти

Агенти визначаються в `agents/*/SOUL.md`. **Динамічне відкриття**:
```bash
ls agents/                        # lab-analyst, diagnostician, researcher
cat agents/<name>/SOUL.md         # повний опис агента
```
Перед запуском — прочитай SOUL.md. Модель згідно model-routing.md.

## Правила

1. **CLAUDE.md авто-завантажується** — все що треба вже в контексті
2. **Динамічне відкриття** — `ls agents/`, `ls ~/.claude/hooks/`, `ls ~/claude-system/scripts/`
3. **lab-analyst** → аналізи крові/сечі, референсні значення, відхилення
4. **diagnostician** → симптоми → 3-5 можливих причин (НЕ остаточний діагноз)
5. **researcher** → PubMed, гайдлайни, статті
6. **Українською** — всі відповіді користувачу
7. **Безпека** — завжди: «це не медична консультація, звернись до лікаря»

## Завдання (tasks-all.json)

Єдина структура завдань усіх просторів:
- **Перегляд**: `cat ~/spaces/tasks-all.json`
- **Оновлення**: змінити `task.json` → `python3 ~/claude-system/scripts/tasks-parse.py`
- **Авто-оновлення**: SessionEnd hook

## Хуки (динамічне відкриття)

```bash
ls ~/.claude/hooks/               # всі хуки
```

## Скрипти (динамічне відкриття)

```bash
ls ~/claude-system/scripts/       # системні скрипти
```
Ключові: `tasks-parse.py`.

## Ресурси

- **Max agents**: 5
- **Cost limit**: $5/mo
- **Node**: mac-mini
- **Qdrant**: `space_medicine`

## Як делегувати

```
Агент → Task tool / Agent tool
cwd → ~/spaces/medicine/    (щоб цей CLAUDE.md авто-завантажився)
prompt → чітка задача, без моделі (модель = routing config)
```

## Qdrant Memory

- **Collection:** `space_medicine`
- **Search:** `ssh vuzol python3 /root/scripts/memory-to-qdrant.py --search "query" --space medicine`
- **Sync:** files → `~/spaces/medicine/memory/` → git push → Qdrant auto-sync
- **Agent memory:** `~/spaces/medicine/memory/agents/<name>/MEMORY.md`
