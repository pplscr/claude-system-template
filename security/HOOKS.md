# Hook Infrastructure — Unified Structure

**Date:** 2026-07-31
**Scope:** mac-mini + vuzol

---

## Directory Convention — ЄДИНИЙ СТАНДАРТ

| Node | Hook scripts | Config |
|------|-------------|--------|
| **mac-mini** | `~/.claude/hooks/` | `~/.claude/settings.json` |
| **vuzol** | `~/.claude/hooks/` | `~/.claude/settings.json` |

> **2026-07-31:** vuzol мігрував з `scripts/` → `hooks/`. Обидві машини тепер використовують єдиний шлях.
> `~/.claude/scripts/` на vuzol залишився для MCP-скриптів (`mcp-cache.sh`, `mcp-search.sh`) — це не хуки.

---

## Hook Types & Flow

```
SessionStart → session-init.sh
    │
    ├─ PreToolUse → security-guard.sh, protect-files.sh
    │
    ├─ PreCompact → precompact-save.sh  (~~15s timeout)
    │     └─ Зберігає snapshot: tasks, connectivity, balance, rules
    │
    ├─ PostCompact → postcompact-restore.sh  (~~10s)
    │     └─ Відновлює контекст із snapshot
    │
    ├─ Stop → session-checkpoint.sh, subagent-cleanup.sh
    │
    └─ SessionEnd → session-end.sh
```

---

## Auto-Compact Configuration

### mac-mini
```json
{
  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "60",
    "CLAUDE_CODE_AUTO_COMPACT_MODEL_AWARE": "1"
  },
  "hooks": {
    "PreCompact":  [{"command": "bash ~/.claude/hooks/precompact-save.sh", "timeout": 15}],
    "PostCompact": [{"command": "bash ~/.claude/hooks/postcompact-restore.sh", "timeout": 10}]
  }
}
```

### vuzol
```json
{
  "autoCompactEnabled": true,
  "autoCompactWindow": 500000,
  "env": {
    "DISABLE_AUTO_COMPACT": "0",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "60"
  },
  "hooks": {
    "PreCompact":  [{"command": "/root/.claude/hooks/precompact-save.sh"}],
    "PostCompact": [{"command": "/root/.claude/hooks/postcompact-restore.sh"}]
  }
}
```

**Параметри:**
- `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=60` — компакт при 60% контексту (замість дефолтних ~90%)
- `autoCompactWindow=500000` (vuzol) — ~500k токенів вікно
- `autoCompactEnabled=true` (vuzol)

---

## PreCompact: Snapshot Content

Snapshots зберігаються в:
- mac-mini: `~/.claude/compact-snapshot.md`
- vuzol: `/root/.claude/compact-snapshot.md`

**Що зберігається:**
- Session ID
- Connectivity (Tailscale peers, vuzol reachable)
- Active tasks (через Task API `GET /tasks`)
- Critical rules (FREE FIRST, делегування, adversarial verify, etc.)
- Last balance

**Фікс 2026-07-31:** mac-mini precompact-save.sh використовував `state.py list` (deprecated JSON). Виправлено на `curl vuzol:8000/tasks` (Task API, PostgreSQL).

---

## PostCompact: Context Restoration

PostCompact читає snapshot і повертає його як `systemMessage` — Claude бачить критичний контекст після компакту.

---

## Security Hooks

### security-guard.sh
Блокує небезпечні команди:
- `rm -rf /` (окрім `/tmp`)
- `git push --force main/master`
- Попереджає про `chmod 777`

### protect-files.sh
Блокує Edit/Write на protected файли:
- `.env`, `credentials.env`, `credentials.json`
- `id_rsa`, `id_ed25519`
- `service-account.json`

---

## Session Lifecycle

### session-init.sh
- Генерує session ID (UUID)
- Перевіряє health (Tailscale, vuzol)
- Мовчить якщо все ОК

### session-checkpoint.sh (Stop)
- Зберігає checkpoint стану
- Throttle: не частіше 5 хвилин
- Lock: запобігає паралельному виконанню
- Flag: `/tmp/checkpoint-dirty.flag` → heartbeat daemon синхронізує на vuzol

### session-end.sh
- Оновлює `session-state.json`
- Запускає subagent-cleanup.sh

### subagent-cleanup.sh
3 стратегії очищення orphan-процесів:
1. Kill за PGID (найнадійніше)
2. Kill PPID=1 orphans (крашнуті сесії)
3. Kill idle claude children (>6h session files)

---

## Перевірка

```bash
# mac-mini
ls ~/.claude/hooks/
cat ~/.claude/compact-snapshot.md | head -10
grep 'CLAUDE_AUTOCOMPACT' ~/.claude/settings.json

# vuzol
ssh vuzol "ls /root/.claude/scripts/"
ssh vuzol "ls /root/.claude/settings.json | xargs grep autoCompact"
```

---

## Fix Log

| Date | Issue | Fix |
|------|-------|-----|
| 2026-07-31 | mac-mini PreCompact used `state.py` (deprecated) | Changed to `curl vuzol:8000/tasks` (Task API) |
| 2026-07-31 | vuzol PreToolUse used `state.py set root activity` | Changed to `state3.py activity mac-infra` |
| 2026-07-31 | No `state.py` references remain on either node | ✅ Clean |
