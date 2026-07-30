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

> Моделі: [rules/model-routing.md](~/.claude/rules/model-routing.md)

| Name | Role |
|------|------|
| dev | Розробка коду/скриптів |
| tester | Тестування |
| architect | Архітектурні рішення |
| reviewer | Code review |
| ops | Деплой, сервер |
| monitoring | Моніторинг (Beszel) |
| ui | Design Architect — UI/UX |

## Memory
- Qdrant: `space_coding`
- Files: `memory/`

## Projects
| Project | Dir | Status |
|---------|-----|--------|
| json-validator | `projects-coding/` | done |
| notify | `projects-coding/` | done |
| sysinfo | `projects-coding/` | done |
