# Hooks — {AGENT_NAME}

> **Dynamic discovery**: `ls ~/.claude/hooks/`
> **Active hooks**: check `cat ~/.claude/settings.json | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin).get('hooks',{}), indent=2))"`

## Agent Lifecycle Hooks
<!-- Hooks specific to this agent's lifecycle -->

### {EVENT_NAME}
- **Event**: PreToolUse | PostToolUse | SessionStart | Stop | SubagentStop
- **Matcher**: {Bash | Edit | Write | *}
- **Type**: command | http | prompt
- **Command**: {SCRIPT_PATH}
- **Timeout**: {SECONDS}s
- **On Block**: exit 2 = deny

## Guardrails (Hard Safety Hooks)
<!-- Must never be removed -->
- {GUARDRAIL_1}
- {GUARDRAIL_2}

## Hook Events Reference
| Event | Fires | Use For |
|-------|-------|---------|
| SessionStart | Once per session | Init, health check |
| PreToolUse | Before every tool call | Block dangerous operations |
| PostToolUse | After every tool call | Audit, lint, validate |
| Stop | Session end | Checkpoint, cleanup |
| SubagentStop | Subagent finishes | Chain to next agent |
