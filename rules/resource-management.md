# 🖥️ Resource Management

## Nodes

| Node | Specs | Max Sessions |
|------|-------|-------------|
| mac-mini | M4, 16GB | 3 |
| vuzol | 8GB | 2 |

## Rules

- `/exit` after each task (not `/clear`)
- `/compact` every 90-120 minutes
- Check zombies: `bash ~/claude-system/scripts/claude-cleanup.sh`
- ⚠️ NEVER `grep claude | xargs kill`!
- Keep >10 GB free on vuzol disk
- Monitor memory: `free -h` before launching agents

## Session Management

```bash
# Health check
bash ~/claude-system/scripts/healthcheck.sh

# Cleanup (dry-run first)
bash ~/claude-system/scripts/claude-cleanup.sh --dry-run
```
