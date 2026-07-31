# Медицина

- **Type**: specialized
- **Node**: mac-mini
- **Created**: 2026-07-28

## Purpose
Аналіз лабораторних результатів, симптомів, медичної літератури. Не ставить діагнозів — рекомендує звернутись до лікаря.

## Agents

> Моделі: [rules/model-routing.md](~/.claude/rules/model-routing.md)
> **Динамічне відкриття**: `ls agents/` → `cat agents/<name>/SOUL.md`

| Name | Tier | Role |
|------|------|------|
| lab-analyst | T2 | Аналіз лабораторних результатів |
| diagnostician | T2 | Діагностика на основі симптомів |
| researcher | T1 | Пошук медичної інформації |

## Memory
- Qdrant: `space_medicine`
- Files: `memory/`

## Tasks
- **tasks-all.json**: `~/spaces/tasks-all.json` — всі завдання з усіх просторів
- **Стан простору**: `task.json`
- **Парсер**: `python3 ~/claude-system/scripts/tasks-parse.py`

## Resources
- Max agents: 5
- Cost limit: $5/mo
