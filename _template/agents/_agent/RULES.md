# Rules — {AGENT_NAME}

## Agent-Specific Rules
<!-- Rules that apply ONLY to this agent. Not duplicates of global/space rules. -->

### {RULE_1_NAME}
- **Rule**: {WHAT}
- **Why**: {RATIONALE}
- **Enforcement**: {hook | prompt | tool} — how this rule is enforced

### {RULE_2_NAME}
- **Rule**: {WHAT}
- **Why**: {RATIONALE}
- **Enforcement**: {hook | prompt | tool}

## Domain Boundaries
<!-- What this agent NEVER touches -->
- ❌ {BOUNDARY_1}
- ❌ {BOUNDARY_2}

## Dynamic Rule Discovery
> `ls ~/.claude/rules/` — global rules
> `ls rules/ 2>/dev/null` — space rules
> These are IN ADDITION to agent-specific rules above
