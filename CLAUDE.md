# Spaces Index — mac-mini

> Worker context: `~/.claude/CLAUDE.md`
> Loading strategy: `~/.claude/agents/LOADING.md`

One space = one directory = one responsibility.

## Active Spaces
- `system/` → health, maintenance, infra tasks
- `orchestrator/` → cross-space routing hub

## Creating New Space
```bash
cp -r _template <name>
# Fill SPACE.md (name, purpose, node, status)
# Fill CLAUDE.md (instructions for this space)
# Create agents in agents/
# Register in this index + orchestrator
```

## Cross-Space Communication
```
Space A → orchestrator/inbox/{id}.json
       → orchestrator routes
       → Space B executes
       → orchestrator/outbox/{id}.md
```

## Rules
- Isolate: don't cross space boundaries directly
- Template: `_template/` — copy when creating new
- Register: add new space to this index + orchestrator
- `projects-coding/` → кодинг, розробка (Python/JS/TS)
