# Orchestrator Inbox

Cross-space task requests land here.

## Format

File: `{timestamp}-{space}-{id}.json`

```json
{
  "id": "unique-task-id",
  "from": "source-space",
  "to": "target-space",
  "task": "description",
  "priority": "low|normal|high|critical",
  "deadline": "iso8601 or null",
  "context": {},
  "created": "iso8601"
}
```

## Lifecycle

1. Space A writes request → inbox
2. Orchestrator reads → dispatches to Space B
3. Space B executes → writes result to outbox
4. Space A reads result from outbox

## Rules

- One file per request
- Never edit another space's request
- Clean up processed requests (move to `archive/`)
