# Security Space — mac-mini + vuzol

Аудит безпеки, моніторинг загроз, перевірка конфігурацій, реагування на інциденти.

## Що де лежить

| Файл/Директорія | Призначення |
|------|-------------|
| `CLAUDE.md` | Цей файл — **авто-завантажується** |
| `SPACE.md` | Метадані простору |
| `task.json` | Стан завдань (авто-оновлюється) |
| `agents/` | Визначення агентів — `ls agents/` |
| `rules/` | Правила простору — `ls rules/` |
| `memory/` | Файли пам'яті |
| `docs/` | Звіти аудитів, ZVIT |
| `jail.local` | fail2ban конфіг для vuzol |
| `ufw-rules.sh` | UFW правила |

## Агенти

Агенти визначаються в `agents/*/SOUL.md`. **Динамічне відкриття**:
```bash
ls agents/                        # security-auditor, infra-guardian, access-reviewer
cat agents/<name>/SOUL.md         # повний опис агента
```
Для критичних аудитів — **Consilium**: 3 агенти, adversarial verify (≥2/3).
Перед запуском — прочитай SOUL.md. Модель згідно model-routing.md.

## Правила

1. **CLAUDE.md авто-завантажується** — все що треба вже в контексті
2. **Динамічне відкриття** — `ls agents/`, `ls rules/`, `ls ~/.claude/hooks/`, `ls ~/claude-system/scripts/`
3. **Аудит = 3 агенти** — Consilium: security-auditor + infra-guardian + access-reviewer
4. **Після змін — онови docs/** — кожен аудит → ZVIT-дата.md
5. **Шари перевіряти регулярно** — Firewall → SSH → iptables → ACL → Tailnet Lock
6. **Серверні зміни — через ssh vuzol**

Додаткові правила: `ls rules/ && cat rules/<file>.md`.

## Завдання (tasks-all.json)

Єдина структура завдань усіх просторів:
- **Перегляд**: `cat ~/spaces/tasks-all.json`
- **Оновлення**: змінити `task.json` → `python3 ~/claude-system/scripts/tasks-parse.py`
- **Авто-оновлення**: SessionEnd hook

## Хуки (динамічне відкриття)

```bash
ls ~/.claude/hooks/               # всі хуки
```

## Скрипти (динамічне відкриття)

```bash
ls ~/claude-system/scripts/       # системні скрипти
```
Ключові: `tasks-parse.py`, `healthcheck.sh`, `claude-cleanup.sh`.

## 5 шарів захисту

```
1. macOS Firewall ON + Stealth (mac-mini)
2. SSH keys only, root locked (vuzol)
3. iptables DOCKER-USER DROP (vuzol)
4. Tailscale ACL: mac-mini ↔ vuzol only
5. Tailnet Lock: ENABLED, both nodes signed
```

## Швидка перевірка

```bash
tailscale status
ssh vuzol "systemctl is-active ssh task-api cc-connect"
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
ssh vuzol "iptables -L DOCKER-USER -n | grep DROP"
ssh vuzol "tailscale lock status | grep -i enabled"
```

## Ресурси

- **Max agents**: 5
- **Cost limit**: $5/mo
- **Node**: mac-mini + vuzol
- **Qdrant**: `space_security`

## Incidents
| Date | Issue | Severity | Status |
|------|-------|----------|--------|
| 2026-07-30 | 6 CRITICAL: firewall off, Ollama open, SSH password, Docker exposed, no ACL, no Lock | CRITICAL | ✅ Fixed |

## Як делегувати

```
Агент → Task tool / Agent tool
cwd → ~/spaces/security/    (щоб цей CLAUDE.md авто-завантажився)
prompt → чітка задача, без моделі (модель = routing config)
```

## Qdrant Memory

- **Collection:** `space_security`
- **Search:** `ssh vuzol python3 /root/scripts/memory-to-qdrant.py --search "query" --space security`
- **Sync:** files → `~/spaces/security/memory/` → git push → Qdrant auto-sync
- **Agent memory:** `~/spaces/security/memory/agents/<name>/MEMORY.md`
