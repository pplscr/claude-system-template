# Security Rules

## Audit Methodology
1. **Consilium**: 3 агенти (security-auditor, infra-guardian, access-reviewer)
2. **Adversarial verify**: ≥2/3 мають підтвердити знахідку
3. **Шари**: перевіряти від зовнішнього до внутрішнього (firewall → SSH → iptables → ACL → Lock)

## Response Protocol
| Severity | Response |
|----------|----------|
| CRITICAL | Негайний фікс + звіт |
| HIGH | Фікс протягом 24h |
| MEDIUM | Запланувати в task.json |
| LOW | Задокументувати, виправити при нагоді |

## Tools
- `ssh vuzol` — всі серверні перевірки
- `tailscale status` — mesh health
- `systemctl is-active <service>` — статус сервісів
- `iptables -L DOCKER-USER -n` — Docker фаєрвол
- `ufw status` — UFW правила
- `/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate` — macOS фаєрвол

## Never
- ❌ Не відкривати порти без auth
- ❌ Не зберігати secrets в world-readable файлах
- ❌ Не видаляти ключі без бєкапу
- ❌ Не змінювати factory-nsc (простір legal)
