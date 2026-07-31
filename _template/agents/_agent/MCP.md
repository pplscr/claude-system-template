# MCP — {AGENT_NAME}

> **Dynamic discovery**: `cat .mcp.json 2>/dev/null`
> **Global MCP** (from ~/.claude/settings.json): maps-osrm, maps-google, browser

## Agent-Specific MCP Servers
<!-- Add if agent needs dedicated MCP servers beyond global/space -->

### {SERVER_NAME}
- **Command**: {COMMAND}
- **Args**: [{ARGS}]
- **Env**: {ENV_VARS}
- **Transport**: stdio | http | sdk

## MCP Tools Available
| Tool | Server | readOnly | destructive | Purpose |
|------|--------|----------|-------------|---------|
| {TOOL_NAME} | {SERVER} | {yes/no} | {yes/no} | {WHAT_IT_DOES} |

## MCP Transport Notes
- **stdio**: local subprocess (default for CLI tools)
- **http**: Streamable HTTP (preferred for remote since 2025-03-26)
- **sdk**: in-process (Claude Agent SDK)
- **sse**: deprecated — do not use for new implementations
