# Orchestrator Outbox

Task results from cross-space execution.

## Format

File: `{task-id}.md`

```markdown
# Result: {task-id}

- **From**: {source-space}
- **To**: {target-space}
- **Status**: done | failed | partial
- **Completed**: iso8601

## Output
...
```

## Rules

- One file per completed task
- Always include status and timestamp
- Attach output files as references
