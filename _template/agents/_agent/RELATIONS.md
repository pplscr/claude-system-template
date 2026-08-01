# Relations — {AGENT_NAME}

## A2A Communication Map
<!-- Which agents does this agent communicate with? -->

### Same-Space
| Agent | Relationship | Protocol | Trust | Purpose |
|-------|-------------|----------|-------|---------|
| {AGENT_1} | delegates-to | file (A2A) | high | {WHY} |
| {AGENT_2} | receives-from | prompt | high | {WHY} |

### Cross-Space (only if needed)
| Agent | Space | Relationship | Protocol | Trust | Purpose |
|-------|-------|-------------|----------|-------|---------|
| {AGENT_3} | {SPACE_3} | consults | memory (Qdrant) | medium | {WHY} |
| {AGENT_4} | {SPACE_4} | delegates-to | A2A inbox | medium | {WHY} |

---

## Relationship Types
- **delegates-to**: sends work to another agent (expects result)
- **receives-from**: receives work from another agent
- **reviews**: checks output quality (read-only)
- **consults**: asks for domain expertise (does not delegate work)

---

## Trust Levels & Cross-Space Rules

### Trust Levels
| Level | Same-Space | Cross-Space | Auto-Execute | Needs Approval |
|-------|-----------|-------------|:---:|:---:|
| **high** | ✅ full access | ❌ never | ✅ | ❌ |
| **medium** | ✅ full access | ✅ read-only (memory) | ❌ | ✅ per-request |
| **low** | ✅ limited | ❌ never | ❌ | ✅ always |

### Cross-Space Communication Protocol
```
1. Agent A (coding/dev) needs legal review
2. Agent A → memory search: ssh vuzol ... --search "NDA review" --space legal
3. If memory has relevant info → use it (pull-based, read-only)
4. If agent needs ACTIVE work from legal agent:
   a. Write request to: /tmp/a2a/legal-doc-reviewer/inbox/request-{id}.json
   b. Wait for response in: /tmp/a2a/coding-dev/inbox/response-{id}.json
   c. Timeout: 300s → escalate to user
```

### JSON Message Format (A2A)
```json
{
  "id": "uuid",
  "from": "coding/dev",
  "to": "legal/doc-reviewer",
  "type": "request",
  "priority": "high|medium|low",
  "payload": {
    "task": "review this contract",
    "context": "summary or file path",
    "deadline": "ISO timestamp"
  },
  "timestamp": "ISO",
  "ttl": 300
}
```

---

## Cross-Space Data Access Matrix

| This Space | Can READ memory of | Can DELEGATE to | Can REVIEW output of |
|-----------|-------------------|-----------------|---------------------|
| coding | all (read-only) | legal, security | all |
| finance | finance only | coding (scripts) | coding |
| legal | legal only | coding (tools) | coding |
| medicine | medicine only | — | coding (tools) |
| security | all (read-only) | coding (patches) | all |

> **Principle**: Read memory across spaces (pull-based). Delegate work only where trust allows.
> **Never**: Write to another space's files. Modify another agent's MEMORY.md. Access finance/items without permission.

---

## Inbox/Outbox (A2A Protocol)
- **Inbox**: `/tmp/a2a/{AGENT_NAME}/inbox/`
- **Outbox**: `/tmp/a2a/{AGENT_NAME}/outbox/`
- **Processed**: `/tmp/a2a/{AGENT_NAME}/processed/` (archive)
- **Cleanup**: messages older than 24h auto-deleted

## Escalation Path
1. Same-space architect — when task is ambiguous
2. Cross-space agent (via memory/A2A) — when domain expertise needed
3. User — when both fail, or trust level = low
