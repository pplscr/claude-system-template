# Скрипти vuzol

Ключові скрипти для роботи диспетчера.

## Основні

| Скрипт | Призначення |
|--------|-------------|
| `state.py` | Управління проектами, дедлайни, статус |
| `task-api.py` | HTTP API (:8000) + heartbeat mac-mini |
| `memory-to-qdrant.py` | Синхронізація пам'яті файли → Qdrant |
| `heartbeat-daemon.py` | Моніторинг активності mac-mini |
| `watchdog.sh` | Перевірка здоров'я всіх сервісів |
| `backup.sh` | Бекапи конфігурацій |

## Встановлення

```bash
mkdir -p /root/scripts
cp scripts/*.py scripts/*.sh /root/scripts/
chmod +x /root/scripts/*.sh
pip3 install psycopg2-binary qdrant-client  # залежності
```
