# test-000916 — Specialized Space — domain-specific functionality

Specialized space for test-000916 domain

## Що де лежить

| Файл/Директорія | Призначення |
|------|-------------|
| `CLAUDE.md` | Цей файл — **авто-завантажується** |
| `SPACE.md` | Метадані простору |
| `task.json` | Стан завдань (авто-оновлюється) |
| `agents/` | Визначення агентів — `ls agents/` |
| `rules/` | Правила простору — `ls rules/` |
| `memory/` | Файли пам'яті |

## Агенти

Агенти визначаються в `agents/*/SOUL.md`. **Динамічне відкриття**:
```bash
ls agents/                        # всі агенти простору
cat agents/<name>/SOUL.md         # повний опис агента
```
Перед запуском агента — прочитай його SOUL.md. Модель — згідно model-routing.md (не пиши модель в prompt).

## Правила

1. **CLAUDE.md авто-завантажується** — все що треба вже в контексті
2. **Динамічне відкриття** — `ls agents/`, `ls rules/`, `ls ~/.claude/hooks/`, `ls ~/claude-system/scripts/`
3. **Не чіпай інші простори** — працюй тільки в межах ~/spaces/test-000916/
4. 5. **Доменна експертиза** — працюй тільки в межах домену test-000916.

Додаткові правила — в `rules/*.md`. Щоб побачити: `ls rules/ && cat rules/<file>.md`.

## Завдання (tasks-all.json)

Єдина структура завдань усіх просторів:
- **Перегляд**: `cat ~/spaces/tasks-all.json`
- **Оновлення**: змінити `task.json` (або `items/*.json`) → `python3 ~/claude-system/scripts/tasks-parse.py`
- **Авто-оновлення**: SessionEnd hook запускає `tasks-parse.py`

## Skills (динамічне відкриття)

```bash
ls ~/.claude/skills/              # глобальні skills (consilium, dispatch, system-check, ...)
ls skills/ 2>/dev/null            # skills простору (якщо є)
```
Глобальні: consilium (cross-agent analysis), system-check (health), workflow-authoring, workflow-patterns.
Просторові: додаються тільки якщо потрібна спеціалізація (див. legal/factory-nsc/.claude/skills/).

## Хуки (динамічне відкриття)

```bash
ls ~/.claude/hooks/               # всі хуки
cat ~/.claude/settings.json | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin)['hooks'], indent=2))"  # активні хуки
```

## Скрипти (динамічне відкриття)

```bash
ls ~/claude-system/scripts/       # системні скрипти
ls scripts/ 2>/dev/null           # скрипти простору (якщо є)
```
Ключові: `tasks-parse.py` (завдання), `healthcheck.sh` (здоров'я), `claude-cleanup.sh` (зомбі).

## Ресурси

- **Max agents**: 5
- **Cost limit**: $5/mo
- **Node**: mac-mini

## Пам'ять (Qdrant)

**Колекція**: `space_test-000916` на vuzol:6333 (авто-створюється при першому push)

### Перед роботою — пошук контексту

```bash
# Знайти релевантні знання в пам'яті простору
ssh vuzol python3 /root/scripts/memory-to-qdrant.py --search "ключові слова" --space test-000916

# Статистика всіх колекцій
ssh vuzol python3 /root/scripts/memory-to-qdrant.py --stats
```

### Після роботи — збереження

```bash
# 1. Створити .md файл у memory/<name>.md з frontmatter:
#    ---
#    name: short-kebab-name
#    description: "Одне речення — що це"
#    tags: [tag1, tag2]
#    type: space
#    ---

# 2. Синхронізувати з Qdrant:
cd ~/.claude/projects/-Users-ruslanmaneliuk/memory
git add -A && git commit -m "memory(test-000916): опис змін" && git push vuzol main
```

**Що зберігати**: важливі рішення (+обґрунтування), знайдені патерни, результати аналізу, контекст для наступної сесії.

Детальний стандарт — `rules/memory.md` (створити з [[memory-template]] якщо немає).

## Як делегувати

```
Агент → Task tool / Agent tool
cwd → ~/spaces/test-000916/    (щоб цей CLAUDE.md авто-завантажився)
prompt → чітка задача, без моделі (модель = routing config)
```

## Qdrant Memory

- **Collection:** `space_test-000916`
- **Search:** `ssh vuzol python3 /root/scripts/memory-to-qdrant.py --search "query" --space test-000916`
- **Sync:** files → `~/spaces/test-000916/memory/` → git push → Qdrant auto-sync
- **Agent memory:** `~/spaces/test-000916/memory/agents/<name>/MEMORY.md`
