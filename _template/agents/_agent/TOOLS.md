# TOOLS — {AGENT_NAME}

## Allowed
- ✅ Read, Write, Edit, Grep, Glob
- ✅ Bash(ls:*, cat:*, find:*, grep:*, git:status,git:diff,git:log, python3:*, ssh:vuzol, curl:*)
- ✅ WebSearch, WebFetch
- ✅ Agent (if agent spawns sub-agents)

## Forbidden
- ❌ rm, sudo, git push --force
- ❌ chmod 777, chmod -R
- ❌ Write/Edit outside ~/spaces/{SPACE_NAME}/

## MCP Tools (dynamic)
> Discovery: `cat .mcp.json 2>/dev/null`
> Global MCP: maps-osrm, maps-google, browser

## Space-specific
- Working directory: ~/spaces/{SPACE_NAME}/
- Never touch other spaces without explicit permission
