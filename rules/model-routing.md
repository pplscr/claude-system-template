# 🧠 Model Routing

FREE FIRST: Nemotron 🆓 → 429 → DS Flash ($0.27) → DS Pro ($1.10) → Opus 5 ($15, critique only).

❌ GPT 5.6 Sol. Budget: €200/mo, target €50-80.

## Model Selection by Task

| Task | Primary | Fallback |
|------|---------|----------|
| Simple (read, grep, explain) | Nemotron 🆓 | DS Flash |
| Medium (write code, refactor) | DS Flash ($0.27) | DS Pro |
| Complex (architecture, planning) | DS Pro ($1.10) | Opus 5 |
| Critique (review, verify) | Opus 5 ($15) | DS Pro |

## Nemotron Strategy

Nemotron is free — always try it first:
1. Send to Nemotron
2. If 429 (rate limit) → fallback to DS Flash
3. If response quality low → escalate to DS Pro

## Budget Tracking

- Monitor: total tokens per session, cost per model
- Target: €50-80/month
- Hard cap: €200/month
- Alert if daily spend exceeds €3

## Model Routing Config

See `config/model-routing.json` for machine-readable routing rules used by dispatcher.sh.
