# systemd — Сервіси vuzol

Список кастомних systemd unit-файлів.

## Встановлення

```bash
cp *.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now cloudflared-tunnel ttyd cc-connect
```
