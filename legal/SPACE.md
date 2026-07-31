# Legal

- **Type**: specialized
- **Node**: mac-mini
- **Created**: 2026-07-28

## Purpose
Юридичні справи: Widerspruch, афідевіти, OLRB, OHSA, DFR, борги, прецеденти.

## Agents

> Моделі: [rules/model-routing.md](~/.claude/rules/model-routing.md)
> **Динамічне відкриття**: `ls agents/` → `cat agents/<name>/SOUL.md`

| Name | Tier | Role |
|------|------|------|
| legal-analyst | T2 | Аналіз справ, Widerspruch, прецеденти, OLRB, OHSA, DFR |
| email-drafter | T1 | Чернетки листів німецькою/англійською, афідевіти |
| doc-reviewer | T2 | Перевірка документів, OCR, організація доказів |

> Спеціалізовані задачі — через prompt до цих трьох, не створювати окремих агентів.

## Memory
- Qdrant: `space_legal`
- Files: `memory/`

## Cases

| Case | Dir | Amount | Status | Deadline |
|------|-----|--------|--------|----------|
| F&W Fördern & Wohnen | `fw-debt/` | €13.166 | active | 31.07 / 17.08.2026 |
| Factory NSC | `factory-nsc/` | damages (Braganza $195K) | active | — |

## Tasks
- **tasks-all.json**: `~/spaces/tasks-all.json` — всі завдання з усіх просторів
- **Стан простору**: `task.json` (авто-генерується `tasks-parse.py --per-space`)
- **Стан справи**: `case.json` у кожній справі
- **Парсер**: `python3 ~/claude-system/scripts/tasks-parse.py` — перезібрати після змін
- **При змінах**: онови case.json → запусти tasks-parse.py

## Resources
- Max agents: 5
- Cost limit: $10/mo

## Rules
- Усі листи німецькою — перевіряти граматику через native-speaker перевірку
- "Ohne Anerkennung einer Rechtspflicht" — завжди додавати
- Не платити без письмової угоди
- Звіти — в корені справи: `ZVIT-{date}.md`
