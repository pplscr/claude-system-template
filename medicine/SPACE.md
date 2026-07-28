# medicine

- **Type**: specialized
- **Node**: mac-mini
- **Created**: 2026-07-28

## Agents

| Name | Role | Model | Provider |
|------|------|-------|----------|
| `lab-analyst` | Аналіз результатів лабораторії | deepseek-v4-pro[1m] | deepseek |
| `diagnostician` | Діагностика на основі симптомів | deepseek-v4-pro[1m] | deepseek |
| `researcher` | Пошук медичної інформації | deepseek-v4-flash | deepseek |

## Memory
- Qdrant: `space_medicine`
- Files: `memory/`

## Resources
- Max agents: 5
- Cost limit: $5/mo
