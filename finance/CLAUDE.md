# Finance Space — mac-mini

Рахунки, підписки, оплати, бюджет, інвестиції (Trading 212).

## Динамічне відкриття

**Нічого не хардкоджено.** Все відкривається через `ls`:

```bash
ls agents/          # агенти → читати SOUL.md для Tier/Model/Role
ls rules/           # правила → застосовувати
ls skills/          # скіли → тригерити по keywords
ls hooks/           # хуки → виконувати
ls scripts/         # скрипти → запускати
ls items/           # рахунки (JSON, schema 2.0)
ls memory/          # пам'ять простору
ls trading212/      # API конектор + дані
ls news/            # новинний модуль
ls journal/         # трейд-журнал
ls reports/         # звіти
ls logs/            # логи
```

**Як дізнатися про агента:** `ls agents/` → `cat agents/<name>/SOUL.md` → Tier, Model, Effort, Purpose, Capabilities, Rules — все всередині.

**Escalation:** Research (trading-research / news-research) → Verify (finance-analyst) → User approve.

## Правила

1. **НЕ виконувати трейди автономно** — див. `rules/trading-safety.md`
2. **НЕ оплачувати без письмового підтвердження**
3. **Бюджет:** €200/міс, ціль €50-80
4. **Кожен рахунок → `items/<id>.json`** (схема 2.0, шаблон: `~/.claude/_template/ITEM.json`)
5. **Після змін → `python3 ~/claude-system/scripts/tasks-parse.py`**
6. **Dynamic discovery:** `ls` замість хардкоду — нові агенти/скрипти/правила з'являються автоматично

## Trading 212

- **Портфель:** `trading212/snapshot.json` (live) + `/root/finance/snapshots/` на vuzol (daily)
- **API:** REST Basic Auth, `https://live.trading212.com/api/v0/equity`
- **Конектор:** `trading212/connector.py` (stdlib-only, rate-limit-aware, max 3 retries)
- **Синк:** `trading212/sync.py --quick` (5min TTL) | `--full` (все)
- **Новини:** `news/collector.py` — Google News + Yahoo Finance RSS + Reddit
- **Паперовий трейдинг:** `scripts/paper_trader.py` — predict, list, outcomes, stats
- **Витрати:** `scripts/expense_sync.py` — sync, report, categorize
- **Docs:** https://t212public-api-docs.redoc.ly/

## Memory

- **Local:** `memory/` — файли пам'яті (авто-відкриття через `ls memory/`)
- **Qdrant:** `space_finance` колекція на vuzol:6333
- **Search:** `ssh vuzol python3 /root/scripts/memory-to-qdrant.py --search "query" --space finance`
- **Agent memory:** `memory/agents/<name>/MEMORY.md` — decisions, patterns, errors

## Ресурси

- **Node:** mac-mini (execution) + vuzol (persistence)
- **PostgreSQL:** vuzol:5432 (orchestrator DB, 13 tables)
- **Qdrant:** vuzol:6333 (11 collections, `space_finance` active)
- **LiteLLM:** vuzol:4000 (17 моделей, 6 tiers)

## Qdrant Memory

- **Collection:** `space_finance`
- **Search:** `ssh vuzol python3 /root/scripts/memory-to-qdrant.py --search "query" --space finance`
- **Sync:** files → `~/spaces/finance/memory/` → git push → Qdrant auto-sync
- **Agent memory:** `~/spaces/finance/memory/agents/<name>/MEMORY.md`
