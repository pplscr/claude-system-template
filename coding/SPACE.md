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

| Name | Role | Model | Provider |
|------|------|-------|----------|
| dev | Розробка коду/скриптів | auto | auto |
| tester | Тестування | auto | auto |
| architect | Архітектурні рішення | auto | auto |
| reviewer | Code review | auto | auto |
| ops | Деплой, сервер | auto | auto |

## Memory
- Qdrant: `space_coding`
- Files: `memory/`

## Projects
| Project | Dir | Status |
|---------|-----|--------|
| json-validator | `projects-coding/` | done |
| notify | `projects-coding/` | done |
| sysinfo | `projects-coding/` | done |
