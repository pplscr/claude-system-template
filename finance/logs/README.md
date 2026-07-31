# Finance Logs

## What goes where

| Type | mac-mini | vuzol | TTL |
|------|----------|-------|-----|
| Sync logs | `trading212/sync.log` | `/root/finance/logs/` | 30 days |
| News fetch logs | `news/collector.log` | `/root/finance/logs/` | 7 days |
| Trade journal | `journal/entries/*.json` | `/root/finance/journal/` | permanent |
| Portfolio snapshots | в S3/Qdrant | `/root/finance/snapshots/` | permanent |
| News archive | кеш 2h | `/root/finance/news/` | 90 days |
| Agent transcripts | `.claude/projects/` | не синхронізується | managed by Claude |
| Error logs | `logs/errors.log` | `/root/finance/logs/` | 30 days |
