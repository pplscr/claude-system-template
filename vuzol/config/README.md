# cc-connect — Telegram-міст для Claude Code

Конфігурація Telegram-боту, який підключає Claude Code до чату.

## Встановлення

```bash
mkdir -p /root/.cc-connect/data
cp config.toml /root/.cc-connect/config.toml
# → замінити API ключі та токени
systemctl restart cc-connect
```

## Налаштування

1. Створити бота через [@BotFather](https://t.me/BotFather) → отримати токен
2. API ключі: DeepSeek (`api_key`), Anthropic (`api_key`) — в TOML
3. Прив'язати вхідний URL до Cloudflare Tunnel
