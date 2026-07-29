# vuzol — Диспетчер (24/7)

Ubuntu 24.04 | 8GB RAM | Python 3.12 | Docker | PostgreSQL 16 | Nginx

## Роль

Тримати сервіси 24/7. Обслуговувати запити mac-mini. НЕ приймати рішень.

## Сервіси

| Сервіс | Порт | Що робить |
|--------|------|-----------|
| Qdrant | :6333 | Векторна БД — семантичний пошук пам'яті |
| PostgreSQL 16 | :5432 | ACID — метрики, черга, стан |
| Task API | :8000 | HTTP API — heartbeat mac-mini + черга задач |
| Nginx | :80, :8880 | Reverse proxy + статика |
| Cloudflare Tunnel | — | Публічний доступ без відкритих портів |
| ttyd | :7681 | Web-термінал |
| cc-connect | — | Telegram-міст для Claude Code |

## Встановлення з нуля

```bash
# 1. Базові пакети
apt install nginx postgresql python3-pip docker.io

# 2. Docker-сервіси
cd /root/мережа && docker compose up -d

# 3. Systemd-сервіси
cp systemd/*.service /etc/systemd/system/
systemctl daemon-reload && systemctl enable --now cloudflared-tunnel ttyd

# 4. Скрипти
cp scripts/* /root/scripts/

# 5. Конфігурація Claude
cp config/CLAUDE.md /root/CLAUDE.md
```

## Безпека

- UFW: тільки 22, 80, 443
- fail2ban на SSH
- Nginx basic auth на внутрішні сервіси
- Cloudflare Tunnel замість відкритих портів
