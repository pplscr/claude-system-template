# TOOLS — agent-architect

## Allowed
- ✅ Read, Bash, Write, Edit, Grep, Glob
- ✅ WebSearch, WebFetch
- ✅ Agent (subagents для паралельного дослідження)
- ✅ TaskCreate, TaskUpdate

## Forbidden
- ❌ rm, sudo, git push --force
- ❌ Edit інших просторів без явного дозволу
- ❌ Створювати агенти без фази Research

## Research Subagents (динамічні, не хардкоджені)

### Мінімум (simple агент)
| # | Назва | Тип | Що досліджує |
|---|-------|-----|-------------|
| 1 | Local Infra | Explore | A1-A9: простори, шаблон, скрипти, хуки, скіли, правила, MCP, routing, memory |
| 2 | Target Space | Explore | B1-B12: вміст простору, агенти, правила, скіли, MCP, task.json, пам'ять |
| 3 | Qdrant Memory | Explore | D1-D7: статистика, системні патерни, пам'ять простору, досвід агентів |

### Середній (medium агент) — +інші простори
| # | Назва | Тип | Що досліджує |
|---|-------|-----|-------------|
| 4 | Cross-Space Patterns | Explore | C1-C7: всі SOUL.md, AGENT.md, TOOLS.md, SPACE.md, .mcp.json, rules, skills |
| 5 | GitHub Patterns | general-purpose | E1-E10: Claude Code агенти, frontmatter, шаблони, MCP, хуки, скіли, інструменти |

### Повний (complex агент) — +зовнішній світ
| # | Назва | Тип | Що досліджує |
|---|-------|-----|-------------|
| 6 | Internet Methodology | general-purpose | F1-F9: agent design, methodology, model selection, memory, anti-patterns |
| 7 | Domain Research | general-purpose | F10: домен-специфічні патерни для ролі агента |

### Динамічне розширення
Після отримання результатів — якщо знайдено прогалини:
| # | Назва | Тип | Що досліджує |
|---|-------|-----|-------------|
| 8+ | Gap Filling | general-purpose | Конкретний аспект, якого не вистачає |

## Agent Dispatch

```
Дослідження:
  simple:  3 суб-агенти паралельно (мінімум)
  medium:  5 суб-агентів (3 + cross-space + GitHub)
  complex: 7 суб-агентів (5 + internet + domain)

Створення:
  1 агент (agent-architect сам) — дизайн + імплементація

Перевірка:
  1 агент (coding/reviewer) — adversarial verify
```

## Space-specific
- Working directory: ~/spaces/coding/
- Не чіпай інші простори без потреби
- Після створення агента → онови SPACE.md + git commit
- Перед дослідженням → `ls` відповідні директорії (динамічне відкриття)
