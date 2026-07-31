# Coding

- **Type**: core
- **Node**: mac-mini
- **Created**: 2026-07-27

## Purpose
Код, скрипти, архітектурні зміни на маці. Коли потрібно щось змінити
в конфігурації mac-mini або просторах — викликається coding.

## Architecture
Див. `~/claude-system/ARCHITECTURE-MAC.md` — повна архітектура мака.

## Agents

> Моделі: `~/.claude/rules/model-routing.md`
> Відкриття: `ls agents/` → `cat agents/<name>/SOUL.md`

| Name | Tier | Effort | Role |
|------|------|--------|------|
| architect | T2 | high | Архітектурне планування, дизайн систем |
| dev | T2 | medium | Розробка коду та скриптів |
| reviewer | T2 | medium | Рецензія коду, adversarial verify |
| tester | T1 | low | Тестування, граничні випадки |
| ops | T1 | low | DevOps, деплой, інфраструктура |
| monitoring | T1 | low | Моніторинг, healthcheck, логування |
| ui | T2 | medium | UI/UX дизайн, верстка, візуалізація |
| agent-architect | T2 | high | Дослідження → дизайн → створення агентів |

Перед запуском агента читай його SOUL.md. Модель — згідно routing config, не пиши модель у prompt.

## Memory
- Qdrant: `space_coding`
- Files: `memory/`

## Tasks
- **tasks-all.json**: `~/spaces/tasks-all.json` — всі завдання з усіх просторів
- **Стан простору**: `task.json`
- **Парсер**: `python3 ~/claude-system/scripts/tasks-parse.py`
- **При змінах**: онови task.json → запусти tasks-parse.py

## Resources
- Max agents: 10
- Cost limit: $5/mo

## Projects

**Динамічне відкриття**: `ls projects-coding/` — кожна директорія = окремий проект.
Статус проекту — в його `task.json`.
