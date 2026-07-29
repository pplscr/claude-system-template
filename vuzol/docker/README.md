# Docker — Моніторинг + Бази даних

Запуск: `docker compose up -d`

## Сервіси

| Сервіс | Порт | Призначення |
|--------|------|-------------|
| Qdrant | :6333/:6334 | Векторна БД для семантичного пошуку |
| Uptime Kuma | :3001 | Моніторинг доступності |
| Dozzle | :8080 | Логи Docker в реальному часі |
| Beszel | :8090 | Системний моніторинг |
| Vaultwarden | :8081 | Менеджер паролів |

## Створення `.htpasswd` для Nginx

```bash
apt install apache2-utils
htpasswd -c /etc/nginx/.htpasswd admin
```
