# Claude System Template

Шаблон Claude-системи: два вузли, одна пам'ять, багато агентів.

## Архітектура

```
┌──────────────────────────────────────────────────────────────┐
│                     Tailscale Mesh (VPN)                       │
│                                                               │
│  ┌─────────────────────────┐   ┌──────────────────────────┐  │
│  │  🧠 mac-mini            │   │  🖥️ vuzol                │  │
│  │  macOS, M4, 16GB        │   │  Ubuntu 24.04, 8GB       │  │
│  │                         │   │                          │  │
│  │  Claude Code (DeepSeek) │   │  Claude Code (DeepSeek)  │  │
│  │  РОЛЬ: Стратег          │   │  РОЛЬ: Диспетчер         │  │
│  │                         │   │                          │  │
│  │  ~/CLAUDE.md            │   │  /root/CLAUDE.md         │  │
│  │  ~/AGENTS.md            │   │  /root/AGENTS.md         │  │
│  │  ~/.claude/rules/       │   │                          │  │
│  │  ~/spaces/              │   │                          │  │
│  └──────────┬──────────────┘   └───────────┬──────────────┘  │
│             │                              │                  │
│             │  SSH + Qdrant :6333          │                  │
│             │  + Task API :8000            │                  │
│             │  + PostgreSQL :5432          │                  │
│             └──────────────┬───────────────┘                  │
│                            │                                  │
│                     ┌──────┴──────┐                          │
│                     │  🧠 Пам'ять  │                          │
│                     │  Qdrant      │                          │
│                     │  PostgreSQL  │                          │
│                     │  Файли .md   │                          │
│                     └─────────────┘                          │
└──────────────────────────────────────────────────────────────┘
```

## Два вузли — дві ролі

| | mac-mini | vuzol |
|---|---|---|
| **Роль** | Стратег + Виконавець | Диспетчер 24/7 |
| **Рішення** | Приймає | НЕ приймає |
| **Агенти** | Запускає (через простори) | Не запускає |
| **Пам'ять** | Файли .md → синхронізація | Qdrant + PostgreSQL |
| **Канали** | CLI, TG (через vuzol) | Telegram (cc-connect) |

## Потік задачі

```
Користувач → Telegram → cc-connect (vuzol)
                            │
                            ▼
                    vuzol Claude (диспетчер)
                      │  аналізує задачу
                      │  класифікує → простір
                      ▼
                    Task API (PostgreSQL tasks)
                      │
                      ▼
                    mac-mini poll + dispatcher.sh
                      │  визначає агента
                      │  читає model-routing.json
                      ▼
                    Claude в просторі (агент)
                      │
                      ▼
                    Результат → Telegram
```

## Структура репозиторію

```
├── README.md               ← цей файл
├── config/                 ← CLAUDE.md для обох вузлів
├── rules/                  ← 4 глобальні правила
├── spaces/                 ← система просторів + шаблон
├── memory/                 ← трирівнева архітектура пам'яті
├── scripts/                ← ключові скрипти
├── docker/                 ← docker-compose (Qdrant + моніторинг)
├── nginx/                  ← reverse proxy конфіг
├── systemd/                ← cloudflared, ttyd, cc-connect
├── security/               ← UFW, fail2ban
├── digest/                 ← автономні дайджести
└── cron.md                 ← повний crontab
```

## Розгортання

1. **vuzol** — підняти сервіси: `docker compose up -d`, nginx, systemd
2. **mac-mini** — симлінки: `ln -sf claude-system/config/CLAUDE.md ~/CLAUDE.md`
3. **Пам'ять** — PostgreSQL: `psql -f docker/init.sql`
4. **Cron** — `crontab -e` → скопіювати з `cron.md`
