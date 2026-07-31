# test-demo

- **Type**: specialized  (specialized | core)
- **Node**: mac-mini
- **Created**: 2026-08-01

## Purpose
Specialized space for test-demo domain

## Agents

> Моделі: [rules/model-routing.md](~/.claude/rules/model-routing.md)
> Відкриття: `ls agents/` → `cat agents/<name>/SOUL.md`

| Name | Tier | Role |
|------|------|------|

## Memory
- Qdrant: `space_test-demo`
- Files: `memory/`

## Tasks
- **tasks-all.json**: `~/spaces/tasks-all.json` — всі завдання з усіх просторів
- **Стан простору**: `task.json`
- **Парсер**: `python3 ~/claude-system/scripts/tasks-parse.py`
- **При змінах**: онови task.json → запусти tasks-parse.py

## Hooks (динамічне відкриття: `ls ~/.claude/hooks/`)

## Scripts (динамічне відкриття: `ls ~/claude-system/scripts/`)

## Resources
- Max agents: 5
- Cost limit: $5/mo
