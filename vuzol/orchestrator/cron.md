# Cron — автоматизація vuzol

## Повний crontab

```cron
# ── Моніторинг ─────────────────────────────────
*/5 * * * * /root/scripts/watchdog.sh >> /tmp/watchdog-cron.log 2>&1

# ── Digest pipeline ────────────────────────────
0  7  * * * /usr/bin/python3 /root/scripts/digest/morning.py >> /tmp/digest-morning.log 2>&1
0 12  * * * /usr/bin/python3 /root/scripts/digest/midday.py >> /tmp/digest-midday.log 2>&1
0 20  * * * /usr/bin/python3 /root/scripts/digest/evening.py >> /tmp/digest-evening.log 2>&1
0 10  * * 0 /usr/bin/python3 /root/scripts/digest/weekly.py >> /tmp/digest-weekly.log 2>&1
10  *  * * * /root/scripts/digest/hourly-pipeline.sh >> /tmp/pipeline-cron.log 2>&1

# ── Email ──────────────────────────────────────
7 * * * * /usr/bin/python3 /root/scripts/digest/email-agent.py --account all >> /var/log/email-agent.log 2>&1

# ── Обслуговування ─────────────────────────────
0  3  * * * /root/scripts/cleanup.sh >> /tmp/cleanup-cron.log 2>&1
0  2  * * * /root/scripts/backup.sh >> /tmp/backup-cron.log 2>&1
30 3  * * * /root/scripts/digest/db-maintenance.sh >> /tmp/db-maintenance.log 2>&1

# ── Ресурси ────────────────────────────────────
13,43 * * * * bash /root/scripts/resource-watchdog.sh >> /tmp/resource-watchdog-cron.log 2>&1

# ── Синхронізація ──────────────────────────────
*/3 * * * * /usr/bin/python3 /root/scripts/sync-pg-to-qdrant.py >> /tmp/pg-qdrant-sync.log 2>&1
*/2 * * * * /usr/bin/python3 /root/scripts/generate-status.py >> /tmp/status-gen.log 2>&1
```

## Встановлення

```bash
crontab -e  # вставити вміст вище
```

## Логування

Всі логи → `/tmp/`. Перевірка: `ls -la /tmp/*.log`

Перегляд через Dozzle: `https://<tunnel>/logs/`
