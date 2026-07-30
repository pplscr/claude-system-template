# {{SPACE_NAME}}

**Призначення:** {{ONE_LINE_PURPOSE}}

## Агенти

| Агент | Файл | Роль | Модель |
|-------|------|------|--------|
| {{AGENT_NAME}} | `agents/{{agent-slug}}.md` | {{ROLE}} | DS Flash |

## Правила простору

1. {{RULE_1}}
2. {{RULE_2}}
3. {{RULE_3}}

## Пам'ять простору

- Qdrant collection: `{{space_collection}}`
- Локальні файли: `memory/{{space_slug}}/`

## Створення нового простору

```bash
cp -r spaces/_template spaces/{{NEW_SPACE_NAME}}
# Відредагуй SPACE.md, CLAUDE.md, AGENTS.md
```
