# Legal

- **Type**: specialized
- **Node**: mac-mini
- **Created**: 2026-07-28

## Agents

| Name | Role | Model | Provider |
|------|------|-------|----------|
| legal-analyst | Аналіз справ, Widerspruch, прецеденти | auto | auto |
| email-drafter | Чернетки листів німецькою/англійською | auto | auto |
| doc-reviewer | Перевірка документів на дефекти | auto | auto |

## Memory
- Qdrant: `space_legal`
- Files: `memory/`

## Cases

| Case | Dir | Amount | Status | Deadline |
|------|-----|--------|--------|----------|
| F&W Fördern & Wohnen | `fw-debt/` | €13.166 | active | 31.07 / 17.08.2026 |

## Rules
- Усі листи німецькою — перевіряти граматику через native-speaker перевірку
- "Ohne Anerkennung einer Rechtspflicht" — завжди додавати
- Не платити без письмової угоди
- Звіти — в корені справи: `ZVIT-{date}.md`
