# Legal Space — mac-mini

Юридичні справи: Widerspruch, афідевіти, OLRB, OHSA, DFR, борги, прецеденти.

## Що де лежить

| Файл/Директорія | Призначення |
|------|-------------|
| `CLAUDE.md` | Цей файл — **авто-завантажується** |
| `SPACE.md` | Метадані простору |
| `task.json` | Стан завдань (авто-оновлюється) |
| `case.json` | Стан справи (в кожній директорії) |
| `agents/` | Визначення агентів — `ls agents/` |
| `knowledge/` | Прецеденти, дослідження |
| `memory/` | Файли пам'яті |

## Агенти

Агенти визначаються в `agents/*/SOUL.md`. **Динамічне відкриття**:
```bash
ls agents/                        # legal-analyst, email-drafter, doc-reviewer
cat agents/<name>/SOUL.md         # повний опис агента
```
Перед запуском — прочитай SOUL.md. Модель згідно model-routing.md.

## Правила

1. **CLAUDE.md авто-завантажується** — все що треба вже в контексті
2. **Динамічне відкриття** — `ls agents/`, `ls ~/.claude/hooks/`, `ls ~/claude-system/scripts/`
3. **Усі листи німецькою** — перевіряти граматику через native-speaker перевірку
4. **"Ohne Anerkennung einer Rechtspflicht"** — завжди додавати
5. **Не платити без письмової угоди**
6. **Звіти** — в корінь справи: `ZVIT-{date}.md`
7. **Стан на сервері** — `ssh vuzol python3 /root/scripts/state.py set fw-mahnung ...`

## Структура справи
```
fw-debt/
├── CASE.md              ← головний файл справи
├── ZVIT-YYYY-MM-DD.md   ← звіти
├── drafts/              ← чернетки листів
├── correspondence/      ← вхідна/вихідна кореспонденція
├── evidence/            ← докази
├── knowledge/           ← прецеденти, дослідження
└── memory/              ← пам'ять агентів
```

## Завдання (tasks-all.json)

Єдина структура завдань усіх просторів:
- **Перегляд**: `cat ~/spaces/tasks-all.json`
- **Оновлення**: змінити `case.json` у справі → `python3 ~/claude-system/scripts/tasks-parse.py`
- **Авто-оновлення**: SessionEnd hook

## Хуки (динамічне відкриття)

```bash
ls ~/.claude/hooks/               # всі хуки
```

## Скрипти (динамічне відкриття)

```bash
ls ~/claude-system/scripts/       # системні скрипти
```
Ключові: `tasks-parse.py`, `healthcheck.sh`.

## Ресурси

- **Max agents**: 5
- **Cost limit**: $10/mo
- **Node**: mac-mini
- **Qdrant**: `space_legal`

## Джерела на сервері
`/root/cases/fw-debt/` — основні файли, листи, докази

## Як делегувати

```
Агент → Task tool / Agent tool
cwd → ~/spaces/legal/    (щоб цей CLAUDE.md авто-завантажився)
prompt → чітка задача, без моделі (модель = routing config)
```

## Qdrant Memory

- **Collection:** `space_legal`
- **Search:** `ssh vuzol python3 /root/scripts/memory-to-qdrant.py --search "query" --space legal`
- **Sync:** files → `~/spaces/legal/memory/` → git push → Qdrant auto-sync
- **Agent memory:** `~/spaces/legal/memory/agents/<name>/MEMORY.md`
