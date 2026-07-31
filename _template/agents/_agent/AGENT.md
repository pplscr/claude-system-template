---
name: {AGENT_NAME}
role: {ONE_LINE_DESCRIPTION}
model: claude-sonnet-5
provider: openrouter
effort: medium
space: {SPACE_NAME}
---

# Agent: {AGENT_NAME}

## Role
{ONE_LINE_DESCRIPTION}

## Tools
→ TOOLS.md — явний allowlist (не залишай порожнім)

## Skills
→ `ls ~/.claude/skills/` та `ls skills/` — динамічне відкриття

## Memory
- Local: `~/spaces/{SPACE_NAME}/memory/agents/{AGENT_NAME}/MEMORY.md`
- Qdrant: `agent_{SPACE_NAME}_{AGENT_NAME}` collection on vuzol:6333
