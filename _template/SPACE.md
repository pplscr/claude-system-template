# {SPACE_NAME}

- **Type**: {SPACE_TYPE}  (specialized | core)
- **Node**: mac-mini
- **Created**: {DATE}

## Purpose
{ONE_LINE_PURPOSE}

## Agents

> Моделі: [rules/model-routing.md](~/.claude/rules/model-routing.md)
> Відкриття: `ls agents/` → `cat agents/<name>/SOUL.md`

| Name | Tier | Role |
|------|------|------|

## Memory
- Qdrant: `space_{SPACE_NAME}`
- Files: `memory/`

## Tasks
- **tasks-all.json**: `~/spaces/tasks-all.json` — всі завдання з усіх просторів
- **Стан простору**: `task.json`
- **Парсер**: `python3 ~/claude-system/scripts/tasks-parse.py`
- **При змінах**: онови task.json → запусти tasks-parse.py

## Hooks (динамічне відкриття: `ls ~/.claude/hooks/`)

## Scripts (динамічне відкриття: `ls ~/claude-system/scripts/`)

## Resources
- Max agents: 10
- Cost limit: $5/mo
