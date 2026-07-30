#!/usr/bin/env bash
# ufw-rules.sh — налаштування фаєрволу для vuzol
set -euo pipefail

ufw default deny incoming
ufw default allow outgoing

# Відкриті порти
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP (Tailscale + локальна мережа)
ufw allow 443/tcp   # HTTPS (Tailscale)

# Cloudflare Tunnel приймає трафік тільки через CF
# Прямий доступ до :8888 закритий — усе через nginx :8880

ufw enable
ufw status verbose
