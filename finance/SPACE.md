# Фінанси

- **Type**: core
- **Node**: mac-mini
- **Created**: 2026-07-31
- **Updated**: 2026-07-31 (Trading 212 + агенти)

## Purpose
Рахунки, підписки, оплати, бюджет, інвестиції (Trading 212).

## Agents

> Моделі: [rules/model-routing.md](~/.claude/rules/model-routing.md)

| Name | Tier | Model | Role |
|------|------|-------|------|
| t212-sync | T1 | deepseek-v4-flash | Синхронізація Trading 212 даних |
| finance-analyst | T2 | deepseek-v4-pro | Аналіз портфеля, транзакцій, бюджету |
| trading-research | T2 | deepseek-v4-pro | Дослідження ринку, сканування можливостей |

## Trading 212

- **Портфель:** €7 742 | 60 позицій | PPL: −€190
- **API:** REST Basic Auth, live.trading212.com
- **Конектор:** `trading212/connector.py` (stdlib-only)
- **Дані:** `trading212/*.json` (cash, positions, transactions, orders, dividends)
- **Docs:** https://t212public-api-docs.redoc.ly/

## Memory
- Qdrant: `space_finance`
- Files: `memory/`

## Tasks
- **tasks-all.json**: `~/spaces/tasks-all.json` — всі завдання з усіх просторів
- **Стан простору**: `task.json`
- **Деталі**: `items/<id>.json` — конкретний рахунок/підписка
- **Парсер**: `python3 ~/claude-system/scripts/tasks-parse.py`
- **При змінах**: онови task.json + items/*.json → запусти tasks-parse.py

## Resources
- Max agents: 3
- Cost limit: $5/mo

## Items
| ID | Type | Amount | Status | Deadline |
|----|------|--------|--------|----------|
| justcom-260707 | invoice | €298.00 | pending_payment | 2026-08-07 |
| trading212 | portfolio | €7 742 | active | ongoing |

## Rules
- Бюджет: €200/міс, ціль €50-80
- Не оплачувати без письмового підтвердження
- Усі рахунки — в `items/`
- **НЕ виконувати трейди автономно** — див. `rules/trading-safety.md`
