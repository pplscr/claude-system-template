# Relations — {AGENT_NAME}

## A2A Communication Map
<!-- Which agents does this agent communicate with? -->

| Agent | Relationship | Protocol | Trust | Purpose |
|-------|-------------|----------|-------|---------|
| {AGENT_1} | delegates-to | file (A2A) | high | {WHY} |
| {AGENT_2} | receives-from | prompt | medium | {WHY} |

## Relationship Types
- **delegates-to**: this agent sends work to another
- **receives-from**: this agent receives work from another
- **reviews**: this agent checks another's output
- **consults**: this agent asks another for advice

## Trust Levels
- **high**: autonomous execution allowed
- **medium**: requires verification of output
- **low**: human review required before action

## Inbox/Outbox (A2A Protocol)
<!-- If using file-based A2A protocol -->
- **Inbox**: `/tmp/a2a/{AGENT_NAME}/inbox/`
- **Outbox**: `/tmp/a2a/{AGENT_NAME}/outbox/`

## Escalation Path
<!-- Who to escalate to when stuck -->
1. {ESCALATION_1} — when {CONDITION}
2. {ESCALATION_2} — when {CONDITION}
3. User — when all else fails
