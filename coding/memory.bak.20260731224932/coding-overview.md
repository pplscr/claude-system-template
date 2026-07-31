---
name: coding-space-overview
description: "Coding Space — код, скрипти, архітектурні зміни на mac-mini. 7 агентів: dev, tester, architect, reviewer, ops, monitoring, ui."
metadata:
  type: project
  node_type: memory
  space: coding
---

# Coding Space Overview

## Purpose
Код, скрипти, архітектурні зміни на mac-mini.

## Agents (7)
- **dev** (T2, claude-sonnet-5) — написання коду, реалізація
- **tester** (T1, claude-haiku-4.5) — тестування, перевірка
- **architect** (T2, deepseek-v4-pro) — планування архітектури
- **reviewer** (T2, claude-sonnet-5) — код-рев'ю
- **ops** (T1, deepseek-v4-flash) — операційні задачі
- **monitoring** (T1, deepseek-v4-flash) — моніторинг
- **ui** (T2, claude-sonnet-5) — інтерфейси

## Key Rules
- Спочатку архітектура → ARCHITECTURE-MAC.md перед змінами конфігурації
- Не чіпати інші простори — тільки ~/spaces/coding/ та claude-system/
- Після змін архітектури → оновити ARCHITECTURE-MAC.md
- Серверні зміни → через `ssh vuzol`, тільки scripts/

## Resources
- Max agents: 10
- Cost limit: $5/mo
- Qdrant: space_coding

## Delegation
```
Агент → Task tool / Agent tool
cwd → ~/spaces/coding/
```
