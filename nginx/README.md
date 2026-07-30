# nginx — Reverse Proxy для vuzol

Два server blocks:
1. **:80** — публічний (публічний IP або Tailscale)
2. **:8880** — внутрішній (для Cloudflare Tunnel)

## Встановлення

```bash
cp site.conf /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

## Роути

| Шлях | Куди | Доступ |
|------|------|--------|
| `/` | → outgoing/ (статика) | публічний |
| `/api/` | → Task API :8000 | публічний |
| `/upload/` | → Upload Server :8000 | публічний |
| `/terminal/` | → ttyd :7681 | basic auth |
| `/monitor/` | → Uptime Kuma :3001 | публічний |
| `/logs/` | → Dozzle :8080 | публічний |
| `/vault/` | → Vaultwarden :8081 | basic auth |
