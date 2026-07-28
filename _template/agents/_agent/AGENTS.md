# Agent: {AGENT_NAME}

## Role
{ONE_LINE_DESCRIPTION}

## Model
- **Provider**: deepseek
- **Model**: deepseek-v4-flash
- **Fallback**: deepseek-v4-pro[1m]

## Tools
- Read, Bash, Grep, WebSearch

## Memory
- `memory/` — довготривала
- `sessions/` — сесії

## Communication
- Inbox: `/tmp/a2a/{AGENT_NAME}/inbox/`
- Outbox: `/tmp/a2a/{AGENT_NAME}/outbox/`
