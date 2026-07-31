#!/usr/bin/env python3
"""Paper Trading Engine — predictions without real money.

Uses: PostgreSQL on vuzol for storage, local news cache for data.
Budget: €200 virtual.

Usage:
  python3 paper_trader.py predict MSFT_US_EQ --up --confidence 0.7 --reason "..."
  python3 paper_trader.py list                     # active predictions
  python3 paper_trader.py outcomes                  # check completed
  python3 paper_trader.py stats                     # win rate, P&L
"""

import sys
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
FINANCE = HOME / "spaces" / "finance"
SNAPSHOT = FINANCE / "trading212" / "snapshot.json"
NEWS_CACHE = FINANCE / "news" / "news_cache.json"

# PostgreSQL via SSH (uses stdin to avoid shell escaping issues)
def pg_query(sql: str) -> str:
    """Run SQL on vuzol orchestrator DB via stdin."""
    result = subprocess.run(
        ["ssh", "vuzol", "sudo", "-u", "postgres", "psql", "-d", "orchestrator",
         "--no-align", "--tuples-only", "-q"],
        input=sql, capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        raise RuntimeError(f"PG error: {result.stderr.strip()[:300]}")
    return result.stdout.strip()


def get_current_price(ticker: str) -> float:
    """Get current price from local snapshot."""
    with open(SNAPSHOT) as f:
        snap = json.load(f)
    for pos in snap["positions"]:
        if pos["instrument"]["ticker"] == ticker:
            return pos["currentPrice"]
    return 0.0


def predict(ticker: str, direction: str, confidence: float,
            reason: str, timeframe_days: int = 7,
            target_pct: float = 5.0, stop_pct: float = 3.0) -> int:
    """Make a prediction and store in DB.

    Args:
        ticker: e.g., MSFT_US_EQ
        direction: 'up', 'down', or 'neutral'
        confidence: 0.0 to 1.0
        reason: why this prediction
        timeframe_days: when to check outcome
        target_pct: target price % change
        stop_pct: stop loss % change
    """
    current = get_current_price(ticker)
    if current <= 0:
        raise ValueError(f"Cannot find price for {ticker}")

    if direction == 'up':
        target = current * (1 + target_pct / 100)
        stop = current * (1 - stop_pct / 100)
    elif direction == 'down':
        target = current * (1 - target_pct / 100)
        stop = current * (1 + stop_pct / 100)
    else:
        target = current
        stop = current

    # Load news headlines for this ticker
    news_data = {}
    if NEWS_CACHE.exists():
        with open(NEWS_CACHE) as f:
            cache = json.load(f)
        ticker_news = cache.get("news", {}).get(ticker, [])
        news_data = {
            "count": len(ticker_news),
            "headlines": [n["title"][:120] for n in ticker_news[:3]],
            "sources": list(set(n["source"] for n in ticker_news)),
        }

    sql = f"""
    INSERT INTO paper_predictions
        (ticker, prediction_type, confidence, current_price,
         target_price, stop_loss, timeframe_days, reason,
         news_sources, news_headlines, agent_source)
    VALUES
        ('{ticker}', '{direction}', {confidence}, {current},
         {target}, {stop}, {timeframe_days},
         '{reason.replace(chr(39), chr(39)+chr(39))}',
         '{json.dumps(news_data).replace(chr(39), chr(39)+chr(39))}',
         '{json.dumps(news_data.get("headlines", [])).replace(chr(39), chr(39)+chr(39))}',
         'mac-mini')
    RETURNING id;
    """
    result = pg_query(sql)
    pred_id = int(result) if result else 0
    print(f"✅ Prediction #{pred_id}: {ticker} → {direction.upper()} "
          f"(confidence: {confidence:.0%}, timeframe: {timeframe_days}d)")
    print(f"   Entry: €{current:.2f} | Target: €{target:.2f} | Stop: €{stop:.2f}")
    if news_data:
        print(f"   News: {news_data['count']} items from {', '.join(news_data['sources'])}")
    return pred_id


def list_active():
    """Show active (unresolved) predictions."""
    sql = """
    SELECT id, ticker, prediction_type, confidence, current_price,
           target_price, stop_loss, predicted_at,
           timeframe_days - EXTRACT(DAY FROM NOW() - predicted_at)::int AS days_left
    FROM paper_predictions
    WHERE outcome_correct IS NULL
    ORDER BY predicted_at DESC;
    """
    result = pg_query(sql)
    if not result:
        print("No active predictions.")
        return
    print(f"{'ID':<5} {'Ticker':<15} {'Dir':<5} {'Conf':<6} {'Entry':<8} {'Target':<8} {'Stop':<8} {'Days':<5}")
    print("-" * 70)
    for line in result.split("\n"):
        parts = line.split("|")
        if len(parts) >= 9:
            print(f"{parts[0]:<5} {parts[1]:<15} {parts[2]:<5} {parts[3]:<6} "
                  f"€{parts[4]:<7} €{parts[5]:<7} €{parts[6]:<7} {parts[8]:<5}")


def check_outcomes():
    """Check resolved predictions and update DB."""
    sql = """
    SELECT id, ticker, prediction_type, current_price, target_price, stop_loss, predicted_at
    FROM paper_predictions
    WHERE outcome_correct IS NULL
      AND predicted_at < NOW() - INTERVAL '1 day' * timeframe_days;
    """
    result = pg_query(sql)
    if not result:
        print("No predictions ready for outcome check.")
        return

    for line in result.split("\n"):
        parts = line.split("|")
        if len(parts) < 7:
            continue
        pred_id, ticker, ptype, entry_str, target_str, stop_str, _ = parts[:7]
        entry = float(entry_str)
        target = float(target_str)
        stop = float(stop_str)
        current = get_current_price(ticker)

        if current <= 0:
            continue

        pnl_pct = ((current - entry) / entry) * 100
        if ptype == 'down':
            pnl_pct = -pnl_pct  # invert for short predictions

        correct = None
        if ptype == 'up' and current >= target:
            correct = True
        elif ptype == 'down' and current <= target:
            correct = True
        elif current <= stop:
            correct = False  # stopped out
        elif abs(pnl_pct) > 0.1:
            correct = pnl_pct > 0  # if moved meaningfully

        if correct is not None:
            update_sql = f"""
            UPDATE paper_predictions
            SET outcome_at = NOW(), outcome_price = {current},
                outcome_pnl_pct = {pnl_pct:.4f},
                outcome_correct = {str(correct).lower()},
                outcome_notes = 'auto-checked'
            WHERE id = {pred_id};
            """
            pg_query(update_sql)
            emoji = "✅" if correct else "❌"
            print(f"{emoji} #{pred_id} {ticker}: {ptype.upper()} "
                  f"€{entry:.2f} → €{current:.2f} ({pnl_pct:+.1f}%)")


def stats():
    """Show paper trading statistics."""
    sql = """
    SELECT
        COUNT(*) AS total,
        COUNT(outcome_correct) AS resolved,
        COUNT(CASE WHEN outcome_correct THEN 1 END) AS wins,
        ROUND(AVG(CASE WHEN outcome_correct THEN outcome_pnl_pct END)::numeric, 2) AS avg_win_pct,
        ROUND(AVG(CASE WHEN NOT outcome_correct THEN outcome_pnl_pct END)::numeric, 2) AS avg_loss_pct
    FROM paper_predictions;
    """
    result = pg_query(sql)
    print("📊 Paper Trading Stats")
    print(result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: paper_trader.py [predict|list|outcomes|stats] ...")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "predict" and len(sys.argv) >= 6:
        ticker = sys.argv[2]
        direction = sys.argv[3]
        confidence = float(sys.argv[4])
        reason = sys.argv[5]
        timeframe = int(sys.argv[6]) if len(sys.argv) > 6 else 7
        predict(ticker, direction, confidence, reason, timeframe)
    elif cmd == "list":
        list_active()
    elif cmd == "outcomes":
        check_outcomes()
    elif cmd == "stats":
        stats()
    else:
        print("Unknown command or missing args")
