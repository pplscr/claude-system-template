# vuzol — Диспетчер (24/7)

Ubuntu 24.04 | 8GB RAM | Python 3.12 | Docker | PostgreSQL 16 | Nginx

## Роль

Тримати сервіси 24/7. Класифікувати задачі. Розподіляти по просторах.
Обслуговувати запити mac-mini. **НЕ приймати рішень.**

## Сервіси

| Сервіс | Порт | Що робить |
|--------|------|-----------|
| Qdrant | :6333 | Векторна БД — семантичний пошук пам'яті |
| PostgreSQL 16 | :5432 | ACID — черга задач, метрики, архів |
| Task API | :8000 | HTTP API — heartbeat + черга |
| Nginx | :80, :8880 | Reverse proxy + статика |
| Cloudflare Tunnel | — | Публічний доступ без відкритих портів |
| ttyd | :7681 | Web-термінал |
| cc-connect | — | Telegram-міст для Claude Code |

## Диспетчеризація

```
Telegram → cc-connect → vuzol (Claude) → Task API (PostgreSQL tasks)
                                            ↓
                                        Черга (pending)
                                            ↓
                                   mac-mini poll + виконання
```

Деталі: `orchestrator/README.md`

## Структура папки

| Папка | Що всередині |
|-------|-------------|
| `nginx/` | Reverse proxy конфіг (:80 + :8880 тунель) |
| `systemd/` | cloudflared, ttyd, cc-connect unit-файли |
| `docker/` | docker-compose (Qdrant + моніторинг) |
| `scripts/` | state.py, task-api.py, memory-to-qdrant.py, watchdog |
| `config/` | CLAUDE.md + cc-connect.toml (без ключів) |
| `security/` | UFW + fail2ban |
| `orchestrator/` | Диспетчер задач, digest pipeline, cron, PG schema |

## Встановлення з нуля

```bash
# 1. Система
apt install nginx postgresql python3-pip docker.io

# 2. PostgreSQL
sudo -u postgres psql -f orchestrator/init.sql

# 3. Docker-сервіси
cd docker && docker compose up -d

# 4. Systemd
cp systemd/*.service /etc/systemd/system/ && systemctl daemon-reload

# 5. Скрипти
cp scripts/* /root/scripts/ && chmod +x /root/scripts/*.sh

# 6. Конфіги
cp config/CLAUDE.md /root/CLAUDE.md
cp config/cc-connect.toml /root/.cc-connect/config.toml
# → замінити API ключі

# 7. Nginx
cp nginx/site.conf /etc/nginx/sites-enabled/ && nginx -t && systemctl reload nginx

# 8. Безпека
bash security/ufw-rules.sh
cp security/jail.local /etc/fail2ban/jail.local

# 9. Cron
crontab -e  # скопіювати з orchestrator/cron.md
```
