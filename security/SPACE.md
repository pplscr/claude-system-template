# Security

- **Type**: specialized
- **Node**: mac-mini + vuzol
- **Created**: 2026-07-30

## Purpose
Аудит безпеки, моніторинг загроз, перевірка конфігурацій, реагування на інциденти.
Охоплює обидва вузли: mac-mini (робоча станція) + vuzol (сервер).

## Architecture
Див. `docs/SECURITY-AUDIT-2026-07-31.md` — повний звіт останнього аудиту.
Див. `CLAUDE.md` — технічні інструкції (UFW, fail2ban, SSH, nginx).

## Agents

> Моделі: [rules/model-routing.md](~/.claude/rules/model-routing.md)
> **Динамічне відкриття**: `ls agents/` → `cat agents/<name>/SOUL.md`

| Name | Tier | Role |
|------|------|------|
| security-auditor | T2 | Аудит безпеки: фаєрвол, порти, SSH, Docker, Tailscale |
| infra-guardian | T2 | Моніторинг загроз, healthcheck, аналіз логів |
| access-reviewer | T2 | Перевірка доступів: ключі, ACL, користувачі, права |

> Для критичних аудитів — Consilium: 3 агенти, adversarial verify (≥2/3).

## Memory
- Qdrant: `space_security`
- Files: `memory/`

## Tasks
- **tasks-all.json**: `~/spaces/tasks-all.json` — всі завдання з усіх просторів
- **Стан простору**: `task.json`
- **Парсер**: `python3 ~/claude-system/scripts/tasks-parse.py`

## Resources
- Max agents: 5
- Cost limit: $5/mo

## Layers (від зовнішнього до внутрішнього)

| # | Layer | mac-mini | vuzol |
|---|-------|----------|-------|
| 1 | Фаєрвол | macOS Firewall + Stealth | iptables DOCKER-USER |
| 2 | SSH | — | keys only, no root password |
| 3 | Сервіси | Ollama 127.0.0.1 | Docker контейнери за iptables |
| 4 | Mesh | Tailscale ACL (mac-mini ↔ vuzol) | Tailscale ACL |
| 5 | Crypto | Tailnet Lock (signed) | Tailnet Lock (signed) |

## Regular Checks

```bash
# Раз на тиждень (або після змін)
bash ~/claude-system/scripts/healthcheck.sh
tailscale status
ssh vuzol "iptables -L DOCKER-USER -n"
ssh vuzol "tailscale lock status"
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
```

## Incidents
| Date | Issue | Severity | Status |
|------|-------|----------|--------|
| 2026-07-30 | 6 CRITICAL: firewall off, Ollama open, SSH password, Docker exposed, no ACL, no Lock | CRITICAL | ✅ Fixed |
