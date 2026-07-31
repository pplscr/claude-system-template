# Trading Safety Rules

## CRITICAL — NO Autonomous Trading

1. **НІКОЛИ не виконувати трейди без явного дозволу** — Read-only за замовчуванням
2. **НІКОЛИ не змінювати portfolio allocation** без письмового підтвердження
3. **Всі рекомендації — тільки інформаційні** — не financial advice
4. **Stop-loss завжди** — будь-яка пропозиція входу має включати рівень виходу
5. **Максимальний ризик на позицію: 2%** від портфеля (~€155)
6. **Paper trade first** — перед реальними грошима тестувати на demo API

## Anti-patterns

- ❌ "Це точно виросте" — нічого не точно
- ❌ FOMO трейдинг — не входити в позицію без аналізу
- ❌ All-in — ніколи не концентрувати >10% в одній позиції
- ❌ Трейди на основі однієї новини
- ❌ Вхід без exit plan

## Circuit Breakers

- **Daily loss limit**: −5% портфеля (~€387) — стоп на день
- **Weekly loss limit**: −10% портфеля (~€774) — стоп на тиждень
- **Consecutive losses**: 3 поспіль → зменшити risk до 0.5%
- **Max drawdown**: −15% від піку → повний стоп, перегляд стратегії

## Idempotency

- **Кожен ордер має мати унікальний idempotency_key** (UUID)
- Перед відправкою — перевірити чи не дубль
- T212 API не підтримує idempotency нативно → перевіряти pending orders перед submit

## Error Escalation

- **API down >5 хв** → перейти в read-only, сповістити
- **API 429 (rate limit)** → 3 retries з exponential backoff, потім FAIL
- **API 401/403** → НЕ продовжувати, перевірити ключі
- **Data staleness** → кеш >15 хв = примусовий resync перед аналізом

## Order Types

- **Тільки LIMIT ордери** для входу (уникати slippage)
- **Тільки MARKET ордери** для екстреного виходу (stop-loss спрацював)
- **Ніколи STOP/LIMIT** через API (T212 rate limit 1/2s — надто повільно)

## Escalation

Будь-яка пропозиція трейду має пройти:
1. Research → trading-research agent (T2)
2. Verify → finance-analyst (T2)
3. Approve → USER (manual confirmation)
