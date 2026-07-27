# Space: system

> System tasks, health monitoring, maintenance. Created: 2026-07-27.

## Purpose

This space handles all system-level operations on mac-mini:
- Health checks and monitoring
- Software updates and maintenance
- Backup management
- Service management (Tailscale, SSH tunnel, launchd jobs)

## Agents

| Agent | Role |
|-------|------|
| `worker` | General system tasks |
| `explorer` | File system exploration |

## Memory

System state, update history, known issues → `memory/`

## Tasks

Active work → `tasks/active/`
Backlog → `tasks/backlog/`
Done → `tasks/done/`

## Rules

1. Don't modify system configs without logging to memory/
2. Health checks run daily (cron or manual)
3. Updates documented in memory/updates.md
4. Critical issues → notify orchestrator immediately
