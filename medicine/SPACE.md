# Медицина

- **Type**: specialized
- **Node**: mac-mini
- **Created**: 2026-07-28

## Agents

> Моделі: [rules/model-routing.md](~/.claude/rules/model-routing.md)

| Name | Role |
|------|------|
| `lab-analyst` | Аналіз результатів лабораторії |
| `diagnostician` | Діагностика на основі симптомів |
| `researcher` | Пошук медичної інформації |

## Memory
- Qdrant: `space_medicine`
- Files: `memory/`

## Resources
- Max agents: 5
- Cost limit: $5/mo
