# Безпека vuzol

## UFW (firewall)

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow 22        # SSH
ufw allow 80        # HTTP (Tailscale)
ufw allow 443       # HTTPS (Tailscale)
ufw enable
```

## fail2ban

Захист SSH від брутфорсу. Конфіг: `jail.local`

```bash
apt install fail2ban
cp jail.local /etc/fail2ban/jail.local
systemctl restart fail2ban
```

## SSH hardening

- Заборонити root login з паролем: `PermitRootLogin prohibit-password`
- Тільки ключі: `PasswordAuthentication no`
- Нестандартний порт (опціонально)

## Nginx basic auth

```bash
apt install apache2-utils
htpasswd -c /etc/nginx/.htpasswd admin
```
