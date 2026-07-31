---
name: finance-space-overview
description: "Finance Space — рахунки, підписки, оплати, бюджет. Прямий простір без агентів. Бюджет €200/міс, ціль €50-80."
metadata:
  type: project
  node_type: memory
  space: finance
---

# Finance Space Overview

## Purpose
Рахунки, підписки, оплати, бюджет. Всі фінансові операції.

## Structure
- `items/` — деталі рахунків (кожен окремий JSON)
- Немає спеціалізованих агентів — робота через Claude безпосередньо

## Key Rules
- **НЕ ОПЛАЧУВАТИ** без письмового підтвердження
- Бюджет: €200/міс, ціль €50-80
- Кожен рахунок → `items/<id>.json`
- Після змін → оновити task.json + items/*.json → tasks-parse.py

## Resources
- Max agents: 3
- Cost limit: $3/mo
- Qdrant: space_finance

## Budget Tracking
- Моніторинг через balance-tracker.py
- Щомісячний звіт у ZVIT-YYYY-MM-DD.md
