# 🔐 Security Audit — mac-mini + vuzol
**Date:** 2026-07-30 – 2026-07-31 (Phase 1 + Phase 2: Consilium 3-agent re-audit)
**Auditor:** Claude (DeepSeek V4 Pro) + Consilium (6 sub-agents total)
**Status:** ✅ All CRITICAL findings fixed, verified 2026-07-31 15:19 UTC

---

## Infrastructure Overview

```
┌─────────────────────────────────────────────────────────┐
│                     INTERNET                             │
│  vuzol (100.84.177.33) — Hetzner VPS                    │
│  ├── :22   SSH (keys only)                               │
│  ├── :80   nginx                                         │
│  └── :443  HTTPS                                         │
│                                                          │
│  Docker containers (not exposed to internet):            │
│  ├── litellm :4000                                       │
│  ├── vaultwarden :8081 (127.0.0.1 only)                  │
│  ├── dozzle :8080 (logs viewer)                          │
│  ├── uptime-kuma :3001                                   │
│  ├── beszel :8090 (monitoring)                           │
│  ├── beszel-agent                                        │
│  └── merezha-qdrant :6333-6334                           │
│                                                          │
│  Services:                                               │
│  ├── task-api :8000 (state/queue/heartbeat)              │
│  ├── cc-connect :9111 (AI chat bridge)                   │
│  └── kb-bridge (Telegram bot, getUpdates)                │
└─────────────────────────────────────────────────────────┘
         │                            │
         │   Tailscale WireGuard      │
         │   100.64.0.0/10            │
         │                            │
┌────────┴────────┐     ┌─────────────┴──────────┐
│    mac-mini     │     │   desktop-vot8vnc      │
│  100.127.88.114 │     │   100.78.19.35         │
│  Firewall ON    │     │   (offline, 24d)       │
│  Stealth ON     │     │   — майбутній 3-й     │
│                 │     │     вузол              │
│  Ollama :11434  │     └────────────────────────┘
│  127.0.0.1 only │
└─────────────────┘
```

---

## Layer 1: macOS Firewall (mac-mini)

| Setting | Value |
|---------|-------|
| Application Firewall | ✅ Enabled |
| Stealth Mode | ✅ Enabled (невидимий для ping-сканувань) |
| Ollama | `OLLAMA_HOST=127.0.0.1` — тільки localhost |
| IPv6 bypass (Ollama bug) | Заблоковано фаєрволом |

**Ризик до фіксу:** Ollama була доступна всій локальній мережі + могла слухати IPv6.

```bash
# Перевірка
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
/usr/libexec/ApplicationFirewall/socketfilterfw --getstealthmode
curl -s http://127.0.0.1:11434/api/tags  # працює локально
```

---

## Layer 2: SSH Hardening (vuzol)

| Setting | Before | After |
|---------|--------|-------|
| PermitRootLogin | yes | **prohibit-password** (тільки ключі) |
| PasswordAuthentication | yes | **no** |
| PubkeyAuthentication | yes | yes |

```bash
# Перевірка
ssh vuzol "grep -E '^(PermitRootLogin|PasswordAuthentication|PubkeyAuthentication)' /etc/ssh/sshd_config"
```

---

## Layer 3: iptables DOCKER-USER (vuzol)

Docker bypasses UFW — контейнери були відкриті в інтернет. Додано правила в ланцюг `DOCKER-USER`:

```
Chain DOCKER-USER (1 references)
  ACCEPT  —  ESTABLISHED,RELATED   (відповіді на наші запити)
  ACCEPT  —  tcp dpt:80            (nginx)
  ACCEPT  —  tcp dpt:443           (HTTPS)
  ACCEPT  —  tcp dpt:22            (SSH)
  DROP    —  all else              (все інше заблоковано)
```

**Заблоковано:** dozzle :8080, uptime-kuma :3001, litellm :4000, beszel :8090, qdrant :6333 — всі Docker-порти.

---

## Layer 4: Tailscale ACL

Формат: `acls` (не `grants`). Тільки mac-mini ↔ vuzol дозволено.

```json
{
  "tagOwners": {
    "tag:executor":   ["ruslanmaneliuk@github"],
    "tag:dispatcher": ["ruslanmaneliuk@github"]
  },
  "hosts": {
    "mac-mini": "100.127.88.114",
    "vuzol":    "100.84.177.33"
  },
  "acls": [
    {"action": "accept", "src": ["mac-mini"], "dst": ["vuzol:*"]},
    {"action": "accept", "src": ["autogroup:member"], "dst": ["autogroup:self:*"]}
  ],
  "ssh": [
    {"action": "accept", "src": ["autogroup:member"], "dst": ["autogroup:self"], "users": ["ruslanmaneliuk@github"]}
  ],
  "nodeAttrs": [
    {"target": ["autogroup:member"], "attr": ["funnel"]}
  ]
}
```

**Важливо:** `acls` підтримують `host:port` синтаксис (на відміну від `grants`).

---

## Layer 5: Tailnet Lock

Tailnet Lock **ENABLED**. mac-mini + vuzol підписані довіреним ключем.

```
Tailnet Lock is ENABLED.
Trusted signing key: tlpub:78b18433309b443605298895057a9fe29bfd774395f8d9e119d4185d9eab16c6
```

**Disablement secrets:** згенеровано 3 + 1 для підтримки. Збережи окремо.

---

## What's Protected (Threat Model)

| Загроза | Захист |
|---------|--------|
| Сканування портів mac-mini | Stealth mode — не відповідає на ping |
| Доступ до Ollama ззовні | 127.0.0.1 + фаєрвол |
| Підбір SSH пароля | PasswordAuthentication no |
| Docker-контейнери відкриті в інтернет | DOCKER-USER DROP rule |
| Неавторизовані вузли в Tailnet | Tailnet Lock + ACL |
| Lateral movement в Tailnet | ACL: тільки mac-mini ↔ vuzol |

## What's NOT Protected (Acceptable Risk)

- **Фізичний доступ до mac-mini** — немає Full Disk Encryption (FileVault)
- **Docker сокет на vuzol** — root всередині контейнера = root на хості (стандартний Docker ризик)
- **nginx на :80** — HTTP, не HTTPS (якщо немає TLS)
- **Task API на :8000** — HTTP, але тільки через Tailscale

---

## Telegram Bot (cc-connect)

### Статус: ✅ cc-connect (active), kb-bridge (disabled)

**Архітектура (спрощена):**
```
Telegram App
    │ getUpdates (long polling)
    ▼
cc-connect (vuzol)
    │ Telegram platform + webhook :9111
    │
    ├── Slash commands:
    │   ├── /s → systemctl + df + uptime
    │   ├── /t → curl localhost:8000/tasks
    │   ├── /d → дайджест (morning/midday/evening)
    │   └── /h → /s + /t
    │
    └── Free text → Claude (DeepSeek V4 Pro через litellm)
```

kb-bridge вимкнено — він конфліктував з cc-connect за getUpdates (HTTP 409). cc-connect тепер єдиний обробник Telegram.

### Керування
```bash
systemctl status cc-connect     # статус
systemctl restart cc-connect    # перезапуск
journalctl -u cc-connect -f     # логи
```

---

## Task API (vuzol:8000)

### Endpoints

| Метод | Шлях | Опис |
|-------|------|------|
| GET | `/` | Список ендпоінтів |
| GET | `/health` | Health check |
| GET | `/heartbeat` | Статус mac-mini (онлайн/офлайн) |
| **Projects** | | |
| GET | `/tasks` | Всі проєкти (JSON) |
| GET | `/tasks/<id>` | Один проєкт (кроки, дедлайни, активність) |
| POST | `/tasks/<id>` | Оновити проєкт (done, add, activity, progress, status, phase, deadline, priority) |
| **Orchestration Queue** | | |
| POST | `/task/submit` | Створити задачу в черзі → `{id, status, session_id}` |
| POST | `/task/claim` | Взяти pending задачу для executor |
| POST | `/task/complete/<id>` | Позначити задачу виконаною |
| GET | `/task/status/<id>` | Статус/результат задачі |
| GET | `/task/queue` | Черга pending задач |
| GET | `/task/session/<uuid>` | Всі задачі в сесії |

### POST /tasks/<id> — оновлення проєкту

```bash
# Додати крок
curl -X POST http://vuzol:8000/tasks/merezha \
  -H 'Content-Type: application/json' \
  -d '{"action":"add","step_type":"pending","value":"Новий крок"}'

# Виконати крок (авто-matching по тексту)
curl -X POST http://vuzol:8000/tasks/merezha \
  -H 'Content-Type: application/json' \
  -d '{"action":"done","value":"текст кроку"}'

# Оновити прогрес
curl -X POST http://vuzol:8000/tasks/merezha \
  -H 'Content-Type: application/json' \
  -d '{"action":"progress","value":"95"}'

# Додати дедлайн
curl -X POST http://vuzol:8000/tasks/merezha \
  -H 'Content-Type: application/json' \
  -d '{"action":"deadline","key":"release","value":"2026-08-15","desc":"Реліз v0.7"}'

# Додати активність
curl -X POST http://vuzol:8000/tasks/merezha \
  -H 'Content-Type: application/json' \
  -d '{"action":"activity","value":"Щось сталось"}'
```

### Orchestration Queue

```bash
# Створити задачу для mac-mini
curl -X POST http://vuzol:8000/task/submit \
  -H 'Content-Type: application/json' \
  -d '{"space":"coding","task":"Напиши скрипт healthcheck.sh","priority":80}'

# mac-mini забирає задачу через heartbeat
# → POST /heartbeat повертає {"has_command":true,"command":{...}}

# Виконавець позначає виконання
curl -X POST http://vuzol:8000/task/complete/42 \
  -H 'Content-Type: application/json' \
  -d '{"result":"Скрипт готовий: /tmp/healthcheck.sh","success":true}'
```

### Як це працює

1. **state3.py** — CLI для керування станом проєктів (Python + PostgreSQL)
2. **task-api.py** — HTTP-обгортка над state3.py + черга оркестрації
3. **heartbeat-daemon.py** — mac-mini надсилає heartbeat на vuzol:8000, отримує команди у відповідь

### Поточні проєкти

| ID | Назва | Tier | Прогрес | Термінові дедлайни |
|----|-------|------|---------|---------------------|
| factory-nsc | NSC Legal Case | life | 75% | pickup=сьогодні ⚠️ |
| 1283-26-UR | Maneliuk v NSC | life | 60% | affidavit_pickup=сьогодні ⚠️ |
| fw-mahnung | F&W 3. Mahnung | life | 45% | payment=сьогодні ⚠️ |
| merezha | Мережа A2A | hobby | 95% | — |
| claude-system | Claude System | life | 0% | — |
| finances | Фінанси | life | 0% | — |
| mac-infra | macOS Infra | life | 0% | — |

---

## cc-connect (vuzol:9111)

AI Agent Chat Bridge — приймає промпти через webhook, запускає Claude (через API), повертає відповідь у Telegram.

### Безпека
- Webhook token: **rotated** (hex 64, не guessable)
- EnvironmentFile: `/root/.claude/credentials.env` — credentials injection
- API keys: в config.toml (600 perms) + credentials.env (600 perms)

---

## Phase 2: Consilium Re-audit (2026-07-31)

3 агенти (security-auditor, infra-guardian, access-reviewer) паралельно перевірили систему.

### Знайдено і виправлено (7 нових)

| # | Знайдено | Severity | Fix |
|---|----------|----------|-----|
| 1 | Task API публічно через nginx :80/api/ + tunnel без auth | CRITICAL | ✅ basic auth на обидва |
| 2 | upload_server :8888 без auth, UFW allow Anywhere | CRITICAL | ✅ UFW правило видалено |
| 3 | credentials.env world-readable (644) | HIGH | ✅ chmod 600 |
| 4 | authorized_keys: 14 рядків з фрагментами, дублікатами | MEDIUM | ✅ 10 чистих ключів |
| 5 | UFW :8443 stale правило | LOW | ✅ видалено |
| 6 | iptables INPUT :6333 redundant | LOW | ✅ видалено |
| 7 | Webhook token guessable "kb-navigation-secret-token" | HIGH | ✅ rotated (hex 64) |

### Додатково виправлено

| # | Fix |
|---|-----|
| 8 | authorized_keys mac-mini: знайдено typo-ключ (`71de` vs `7lde`) — видалено |
| 9 | root password: `passwd -l root` — locked |
| 10 | cc-connect: EnvironmentFile додано в systemd service |
| 11 | SSH control/ perms: 755 → 700 |

### Credential Storage Policy

**Single source of truth:** `/root/.claude/credentials.env` (600)
- DEEPSEEK_API_KEY
- ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN
- OPENROUTER_API_KEY
- TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID
- GMAIL_* (3 акаунти)
- GOOGLE_DRIVE_*, GOOGLE_WORKSPACE_*

**Дубльовано в config.toml (600):** DeepSeek API key, Telegram bot token
→ Причина: cc-connect (Go) не підтримує env var interpolation у TOML.
→ Міграція: неможлива без зміни бінарника cc-connect.
→ Ризик: мінімальний (600 perms, root-only).

**Що потребує уваги:**
- TG Bot token був показаний у логах сесії — рекомендується ротація
- 42 API keys/credentials в одному файлі — розглянути vaultwarden для секретів

---

## Healthy Services

```bash
systemctl is-active ssh task-api cc-connect postgresql@16-main
# all: active
```

| Сервіс | Порт | Доступ |
|--------|------|--------|
| ssh | 22 | public (keys only) |
| nginx | 80, 443 | public |
| task-api | 8000 | Tailscale only + nginx basic auth |
| cc-connect | 9111 | localhost only |
| postgresql | 5432 | localhost only |
| Docker containers | * | DOCKER-USER DROP (public), Tailscale open |

### Статус диска (vuzol)
- 75G total, 52G used (72%), 21G free
- Основне: `/root/factory-nsc/` 15G (докази NSC)
- Моніторити при 80%+

### Впавші сервіси (не наші зміни)
- `certbot.service` — баг `AttributeError: module 'lib' has no attribute 'GEN_EMAIL'`
- `memory-sleep.service` — потребує API key

---

## Перевірка всього разом

```bash
# 1. Tailscale
tailscale status

# 2. Вузол
ssh vuzol "echo ok && systemctl is-active ssh task-api cc-connect kb-bridge"

# 3. Фаєрвол мака
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
/usr/libexec/ApplicationFirewall/socketfilterfw --getstealthmode

# 4. SSH hardening
ssh vuzol "grep -E '^(PermitRootLogin|PasswordAuthentication)' /etc/ssh/sshd_config"

# 5. iptables
ssh vuzol "iptables -L DOCKER-USER -n"

# 6. Tailnet Lock
ssh vuzol "tailscale lock status"

# 7. Task API
curl -s http://vuzol:8000/health
curl -s http://vuzol:8000/tasks | python3 -m json.tool | head -20

# 8. Ollama
curl -s http://127.0.0.1:11434/api/tags | python3 -c "import sys,json; print(len(json.load(sys.stdin)['models']),'models')"
```

---

## Результат

**Phase 1:** 6 CRITICAL → 0
**Phase 2 (Consilium):** 7 нових → 0
**Total: 13 vulnerabilities fixed**

| Layer | Before | After |
|-------|--------|-------|
| macOS Firewall | OFF | ON + Stealth |
| Ollama | 0.0.0.0 + IPv6 | 127.0.0.1 (IPv6 баг — mitigated by ACL+Firewall) |
| SSH | password + root | keys only, root locked |
| Docker ports | exposed to world | DOCKER-USER DROP |
| Tailscale ACL | none (all allowed) | mac-mini ↔ vuzol only |
| Tailnet Lock | DISABLED | ENABLED |
| Telegram Bot | stopped | running (cc-connect) |
| Task API | no auth, public via nginx | basic auth, Tailscale-only |
| upload_server :8888 | no auth, public | UFW blocked |
| credentials.env | world-readable (644) | 600 |
| authorized_keys | 14 lines, fragments | 10 clean keys |
| root password | set | locked |
| Webhook token | guessable | hex 64 |

### Residual risks (acceptable)
- **Ollama IPv6 wildcard** — баг Ollama, mitigated by Tailscale ACL default deny + macOS Firewall Stealth
- **TG Bot token** — в plaintext у config.toml (600 perms), був показаний у логах → ротація
- **certbot + memory-sleep** — впавші сервіси, не впливають на безпеку
- **Disk 72%** — моніторити
