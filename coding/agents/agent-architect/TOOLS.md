# TOOLS — agent-architect

## Allowed
- ✅ Read, Bash, Write, Edit, Grep, Glob
- ✅ WebSearch, WebFetch
- ✅ Agent (subagents for research)
- ✅ TaskCreate, TaskUpdate

## Forbidden
- ❌ rm, sudo, git push --force
- ❌ Edit інших просторів без явного дозволу

## Research Subagents (використовуй Agent tool)

| Фаза | Subagent | Ціль | Тип |
|------|----------|------|-----|
| 1. Server | `ssh vuzol` memory search | Qdrant: агенти, патерни, помилки | Explore |
| 2. Mac | local file exploration | _template, існуючі агенти, CLAUDE.md | Explore |
| 3. GitHub | WebSearch + WebFetch | Claude Code agent patterns, best practices | general-purpose |
| 4. Internet | WebSearch | Agent design: SOUL, TOOLS, memory patterns | general-purpose |

## Space-specific
- Working directory: ~/spaces/coding/
- Не чіпай інші простори без потреби
- Після створення агента → онови SPACE.md (таблицю агентів)
