---
name: security-space-overview
description: "Security Space — аудит безпеки, моніторинг загроз, перевірка конфігурацій. 3 агенти: security-auditor, infra-guardian, access-reviewer. 5-layer defense model."
metadata:
  type: project
  node_type: memory
  space: security
---

# Security Space Overview

## Defense Model (5 Layers)
1. **Perimeter** — UFW, Tailscale, fail2ban
2. **Access** — SSH keys, 600 permissions, no root login
3. **Application** — env vars for secrets, no hardcoded keys
4. **Data** — encrypted backups, no secrets in git
5. **Monitoring** — watchdog, healthcheck, incident response

## Agents (3)
- **security-auditor** — повний аудит безпеки (T2, deepseek-v4-pro)
- **infra-guardian** — захист інфраструктури: ufw, fail2ban, ssh (T1, deepseek-v4-flash)
- **access-reviewer** — перевірка прав доступу, ключів, permissions (T2, claude-sonnet-5)

## Key Rules
- Ніколи не комітити secrets, API keys, credentials
- Всі SSH ключі — password-protected
- Права на файли: 600 для приватних ключів
- Перевіряти перед зміною, не після

## Past Incidents
- 2026-07-30: CRITICAL — виправлено

## Resources
- Qdrant: space_security
- Cost limit: $5/mo
- Node: mac-mini + vuzol
