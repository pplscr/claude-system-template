# Cross-Space Communication

> Як простори та агенти безпечно комунікують між собою.
> Принцип: **pull-based** (агент запитує), не push-based (автоматичний витік).

## Architecture

```
┌──────────────┐     memory search      ┌──────────────┐
│   coding/    │ ←─── Qdrant ────────→  │   legal/     │
│   dev        │    (read-only)          │   reviewer   │
└──────┬───────┘                         └──────┬───────┘
       │                                        │
       │         A2A inbox/outbox               │
       └──────────────→  ←──────────────────────┘
              request.json    response.json
```

## Три рівні комунікації

| Рівень | Механізм | Швидкість | Безпека | Коли |
|--------|----------|:---:|:---:|------|
| **1. Memory Search** | `ssh vuzol memory-to-qdrant.py --search "X" --space Y` | миттєво | ✅ read-only | Знайти існуючі знання |
| **2. A2A Request** | `/tmp/a2a/<agent>/inbox/request.json` | асинхронно | ✅ pull-based | Делегувати задачу |
| **3. Direct Call** | `agent-architect → create-agent.sh` | синхронно | ⚠️ same-space only | Створити/налаштувати |

## Default Isolation (security first)

```
За замовчуванням:
- Кожен простір ізольований
- Агенти бачать ТІЛЬКИ свій простір
- Cross-space доступ = явний дозвіл у RELATIONS.md

Винятки:
- coding/ може читати memory будь-якого простору (архітектор)
- security/ може читати все (аудитор)
- finance/, legal/, medicine/ = ізольовані
```

## Cross-Space Data Access Matrix

| Space | Can READ memory | Can DELEGATE to | Can REVIEW output | Can WRITE files |
|-------|:---:|:---:|:---:|:---:|
| coding | ✅ all | legal, security | ✅ all | ❌ other spaces |
| finance | ❌ other | coding (scripts) | coding | ❌ other |
| legal | ❌ other | coding (tools) | coding | ❌ other |
| medicine | ❌ other | — | coding (tools) | ❌ other |
| security | ✅ all | coding (patches) | ✅ all | ❌ other |

## A2A Protocol

### Message Format
```json
{
  "id": "uuid-v4",
  "from": "space/agent",
  "to": "space/agent",
  "type": "request | response | alert",
  "priority": "high | medium | low",
  "payload": { "task": "...", "context": "...", "deadline": "ISO" },
  "correlation_id": "uuid-of-parent-request",
  "timestamp": "ISO8601",
  "ttl": 300
}
```

### Flow
```
Sender                          Receiver
──────                          ────────
1. Write request.json
   → /tmp/a2a/<to>/inbox/
                                2. Check inbox on startup
                                3. Process request
                                4. Write response.json
                                   → /tmp/a2a/<from>/inbox/
5. Read response
6. Move to processed/
```

### Cleanup
- Messages > 24h → auto-delete
- Processed > 7d → auto-delete
- `/tmp/a2a/` survives reboot? No (tmpfs) → critical requests should also log to memory

## When to Use Which Level

```
"Який закон про оренду?" 
  → Memory Search (legal Qdrant) — READ-ONLY, миттєво

"Перевір цей контракт"
  → A2A Request → legal/doc-reviewer — АСИНХРОННО, з відповіддю

"Створи нового агента для фінансів"
  → Direct Call → coding/agent-architect — СИНХРОННО, same-space

"Скільки грошей на рахунку?"
  → ❌ BLOCKED — finance ізольований, треба явний дозвіл
```

## Security Rules

1. **Pull-based only**: агент запитує → отримує. Ніхто не пушить дані.
2. **Memory search = read-only**: не можна змінити чужу пам'ять
3. **A2A = request/response**: агент сам вирішує чи відповідати
4. **No file writes**: ніколи не писати в інший простір
5. **Trust levels enforced**: medium → потрібен approval, low → тільки через юзера
6. **Audit trail**: всі cross-space запити логуються в MEMORY.md обох агентів
