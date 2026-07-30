# Crontab — vuzol (диспетчер)

```cron
# ── Watchdog: перевірка здоров'я системи ──
*/5 * * * * /root/scripts/watchdog.sh

# ── Digest pipeline ──
0 7 * * * cd /root/digest && python3 morning.py
0 12 * * * cd /root/digest && python3 midday.py
0 20 * * * cd /root/digest && python3 evening.py
0 10 * * 0 cd /root/digest && python3 weekly.py

# ── Hourly pipeline (синхронізація, очистка) ──
7 * * * * /root/digest/hourly-pipeline.sh

# ── Email agent (перевірка пошти) ──
*/30 * * * * /root/scripts/email-agent.sh

# ── Backup (щодня о 03:00) ──
0 3 * * * /root/scripts/backup.sh

# ── Cleanup (щодня о 04:00) ──
0 4 * * * /root/scripts/cleanup.sh

# ── Resource watchdog (перевірка RAM/диску) ──
*/10 * * * * /root/scripts/resource-watchdog.sh

# ── Sync memory files → Qdrant (щогодини) ──
13 * * * * python3 /root/scripts/memory-to-qdrant.py

# ── Status generation (оновлення state.json) ──
*/15 * * * * python3 /root/scripts/state.py list --json > /tmp/state.json

# ── Database maintenance (щотижня) ──
0 2 * * 1 psql -U postgres -d orchestrator -c "VACUUM ANALYZE;"
```

## Встановлення

```bash
crontab -e
# Скопіювати вміст вище
crontab -l  # перевірити
```
