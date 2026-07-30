# Legal

- **Type**: specialized
- **Node**: mac-mini
- **Created**: 2026-07-28

## Agents

> Моделі: [rules/model-routing.md](~/.claude/rules/model-routing.md)

| Name | Role |
|------|------|
| legal-analyst | Аналіз справ, Widerspruch, прецеденти, OLRB, OHSA, DFR |
| email-drafter | Чернетки листів німецькою/англійською, афідевіти |
| doc-reviewer | Перевірка документів, OCR, організація доказів |

> Спеціалізовані задачі (канадське трудове, афідевіти, докази) — через правильний prompt до цих трьох агентів, не створювати окремих.

## Memory
- Qdrant: `space_legal`
- Files: `memory/`

## Cases

| Case | Dir | Amount | Status | Deadline |
|------|-----|--------|--------|----------|
| F&W Fördern & Wohnen | `fw-debt/` | €13.166 | active | 31.07 / 17.08.2026 |
| Factory NSC | `factory-nsc/` | damages (Braganza $195K) | active | — |

## Rules
- Усі листи німецькою — перевіряти граматику через native-speaker перевірку
- "Ohne Anerkennung einer Rechtspflicht" — завжди додавати
- Не платити без письмової угоди
- Звіти — в корені справи: `ZVIT-{date}.md`
