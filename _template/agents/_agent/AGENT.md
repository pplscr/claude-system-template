---
# Required
name: {AGENT_NAME}                 # kebab-case, matches directory name
description: {ONE_LINE_DESCRIPTION} # one sentence — what this agent does

# Model & execution
model: claude-sonnet-5             # see routing config (~/claude-system/rules/model-routing.md)
effort: medium                     # low | medium | high | xhigh | max
maxTurns: 50                       # safety limit per session

# Permissions
permissionMode: acceptEdits        # default | acceptEdits | bypassPermissions | plan
tools: []                          # explicit allowlist — reference TOOLS.md
disallowedTools: []                # tools to block (e.g. Bash(git push:*) for safety)

# Integration
mcpServers: []                     # MCP servers this agent can use
hooks: []                          # hooks to attach (PostToolUse, Stop, etc.)
skills: []                         # skills to auto-load (consilium, system-check, etc.)

# Context
initialPrompt: ""                  # pre-pended system instructions
memory: local+qdrant               # local: MEMORY.md | qdrant: agent_{SPACE_NAME}_{AGENT_NAME}
background: false                  # run as background task
isolation: ""                      # worktree | docker | "" (none)
color: "#4A90D9"                   # hex — agent's brand color in UI
---

## Agent: {AGENT_NAME}

#### Role
{ONE_LINE_DESCRIPTION}

#### Model
See routing config: `cat ~/.claude/rules/model-routing.md`

#### Tools
Explicit allowlist — reference `TOOLS.md` in this directory. Leave no tool unlisted.

#### Skills
Dynamic discovery:
```bash
ls ~/.claude/skills/               # global skills
ls skills/ 2>/dev/null              # space-scoped skills
```

#### MCP Servers
Dynamic discovery:
```bash
cat .mcp.json 2>/dev/null           # space-level MCP config
```

#### Hooks
Dynamic discovery:
```bash
ls ~/.claude/hooks/                 # global hooks
```

#### Rules
Dynamic discovery:
```bash
ls ~/.claude/rules/                 # global rules
ls rules/ 2>/dev/null               # space-scoped rules
```

#### Projects, Cases, Tasks (domain awareness)
Dynamic discovery — the agent knows what exists before acting:
```bash
ls ~/spaces/_infra/projects/        # all projects (9 .json files)
cat ~/spaces/tasks-all.json 2>/dev/null | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'tasks: {len(d.get(\"items\",[]))} total')"  # task overview
ls ~/spaces/<space>/<cases|items>/  # space-specific: cases (legal) or items (finance)
ls ~/spaces/<space>/knowledge/ 2>/dev/null  # knowledge base (medicine)
```

#### Memory
- **Local**: `~/spaces/{SPACE_NAME}/memory/agents/{AGENT_NAME}/MEMORY.md`
- **Qdrant**: collection `agent_{SPACE_NAME}_{AGENT_NAME}` on vuzol:6333

#### Startup Checklist (виконуй на початку кожної сесії)
1. `ls ~/spaces/<space>/agents/` — хто ще в просторі?
2. `cat ~/spaces/<space>/SPACE.md` — контекст простору
3. `cat ~/spaces/<space>/task.json` — активні задачі
4. `cat TASKS.md` — свої задачі (active → backlog)
5. `cat IDEAS.md` — ідеї та фідбек
6. `cat VERSIONS.md` — поточна версія та roadmap
7. `ssh vuzol python3 /root/scripts/memory-to-qdrant.py --search "<topic>" --agent <space>/<name>` — свій досвід
8. `ls ~/spaces/_infra/projects/` — які проекти активні?
9. `ls ~/.claude/skills/ && ls skills/ 2>/dev/null` — які скіли доступні?
10. `cat .mcp.json 2>/dev/null` — які MCP сервери?
11. `ls ~/.claude/hooks/` — які хуки активні?
12. `ls ~/.claude/rules/ && ls rules/ 2>/dev/null` — які правила діють?
