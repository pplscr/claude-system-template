# Coding Space — mac-mini

Код, скрипти, архітектурні зміни на маці.

## Що де лежить

| Файл/Директорія | Призначення |
|------|-------------|
| `CLAUDE.md` | Цей файл — **авто-завантажується** |
| `SPACE.md` | Метадані простору |
| `task.json` | Стан завдань (авто-оновлюється) |
| `agents/` | Визначення агентів — `ls agents/` |
| `rules/` | Правила простору — `ls rules/` |
| `.claude/skills/` | Навички (slash-команди) — `ls .claude/skills/` |
| `projects-coding/` | Основний проект |

## Агенти

Агенти визначаються в `agents/*/SOUL.md`. **Динамічне відкриття**:
```bash
ls agents/                        # відкрий актуальний список
cat agents/<name>/SOUL.md         # повний опис агента
```
Перед запуском — прочитай SOUL.md. Модель — згідно `~/.claude/rules/model-routing.md`.

## Правила

1. **CLAUDE.md авто-завантажується** — все що треба вже в контексті
2. **Динамічне відкриття** — `ls agents/`, `ls rules/`, `ls ~/.claude/hooks/`, `ls ~/claude-system/scripts/`
3. **Спочатку архітектура** — `~/claude-system/ARCHITECTURE-MAC.md` перед змінами конфігурації
4. **Не чіпай інші простори** — coding тільки в межах ~/spaces/coding/ та claude-system/
5. **Після змін архітектури** — онови ARCHITECTURE-MAC.md
6. **Серверні зміни** — через `ssh vuzol`, тільки scripts/

Додаткові правила: `ls rules/ && cat rules/<file>.md`.

**UI-задачі**: перед UI-роботою виконай `ls rules/` та прочитай релевантні правила.

## Навички (Slash Commands)

```bash
ls .claude/skills/                # навички простору
ls ~/.claude/skills/              # глобальні навички
```
Перед використанням — `cat .claude/skills/<name>/SKILL.md`.

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
ls ~/claude-system/scripts/       # повний список системних скриптів
```

## Ресурси

- **Max agents**: 10
- **Cost limit**: $5/mo
- **Node**: mac-mini
- **Qdrant**: `space_coding`

## Зв'язок із сервером
```
ssh vuzol → /root/scripts/state.py  (стан задач)
          → /root/cases/            (справи)
          → /root/scripts/          (скрипти)
```

## Як делегувати

```
Агент → Task tool / Agent tool
cwd → ~/spaces/coding/    (щоб цей CLAUDE.md авто-завантажився)
prompt → чітка задача, без моделі (модель = routing config)
```

## Qdrant Memory

- **Collection:** `space_coding`
- **Search:** `ssh vuzol python3 /root/scripts/memory-to-qdrant.py --search "query" --space coding`
- **Sync:** files → `~/spaces/coding/memory/` → git push → Qdrant auto-sync
- **Agent memory:** `~/spaces/coding/memory/agents/<name>/MEMORY.md`
