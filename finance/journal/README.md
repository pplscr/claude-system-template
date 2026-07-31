# Trading Journal — self-learning from wins & losses

## Purpose
Записувати ВСІ трейд-рішення: вхід, вихід, результат, аналіз.

## Entry Format (JSON)
```json
{
  "id": "uuid",
  "date": "2026-07-31T22:00:00Z",
  "ticker": "AAPL_US_EQ",
  "action": "buy|sell|hold|rebalance",
  "reason": "чому прийнято рішення",
  "source": "agent:trading-research|manual|agent:news-research",
  "amount_eur": 100.00,
  "price": 195.50,
  "quantity": 0.51,
  "stop_loss": 185.00,
  "take_profit": 215.00,
  "exit_date": null,
  "exit_price": null,
  "pnl_eur": null,
  "pnl_pct": null,
  "review": null,
  "lessons": null
}
```

## Self-Learning Loop
1. Entry → записати чому
2. Exit → записати результат
3. Review (weekly) → що спрацювало, що ні
4. Update rules → покращити trading-safety.md

## Storage
- **mac-mini:** `~/spaces/finance/journal/entries/*.json`
- **vuzol:** `/root/finance/journal/entries/*.json` (backup)
- **Sync:** `scp` щоденно через cron/launchd
