#!/usr/bin/env python3
"""Trading 212 Sync — fetch full history and save to local JSON files.

Usage:
    python3 sync.py              # Full sync (all endpoints)
    python3 sync.py --quick      # Cash + positions only (fast)
    python3 sync.py --transactions --orders  # Specific endpoints
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Allow running from any directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
from connector import T212Client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("t212.sync")

DATA_DIR = Path(__file__).resolve().parent
CACHE_FILE = DATA_DIR / "snapshot.json"
TRANSACTIONS_FILE = DATA_DIR / "transactions.json"
ORDERS_FILE = DATA_DIR / "orders.json"
DIVIDENDS_FILE = DATA_DIR / "dividends.json"
POSITIONS_FILE = DATA_DIR / "positions.json"


def save_json(data, path: Path):
    """Save data to JSON file with timestamp."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    size = path.stat().st_size
    log.info("Saved %s (%s bytes)", path.name, size)


def load_json(path: Path) -> dict | list | None:
    """Load JSON file if it exists."""
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def sync_full(client: T212Client):
    """Fetch all data and save to files."""
    snapshot = client.full_snapshot()

    # Save individual files
    save_json(snapshot["cash"], DATA_DIR / "cash.json")
    save_json(snapshot["positions"], POSITIONS_FILE)
    save_json(snapshot["transactions"], TRANSACTIONS_FILE)
    save_json(snapshot["dividends"], DIVIDENDS_FILE)
    save_json(snapshot["orders_history"], ORDERS_FILE)
    save_json(snapshot["orders_pending"], DATA_DIR / "orders_pending.json")

    # Save combined snapshot
    snapshot["synced_at"] = datetime.now().isoformat()
    save_json(snapshot, CACHE_FILE)

    # Summary
    cash = snapshot["cash"]
    positions = snapshot["positions"]
    transactions = snapshot["transactions"]
    orders = snapshot["orders_history"]
    dividends = snapshot["dividends"]

    total_value = cash.get("total", 0)
    free = cash.get("free", 0)
    invested = cash.get("invested", 0)
    ppl = cash.get("ppl", 0)

    print(f"\n{'='*50}")
    print(f"📊 Trading 212 — синхронізовано {snapshot.get('synced_at', '?')}")
    print(f"{'='*50}")
    print(f"💵 Баланс:     €{total_value:,.2f}")
    print(f"   Вільно:     €{free:,.2f}")
    print(f"   Інвестовано: €{invested:,.2f}")
    print(f"   PPL:        €{ppl:,.2f}")
    print(f"📈 Позицій:    {len(positions)}")
    print(f"💸 Транзакцій: {len(transactions)}")
    print(f"📋 Ордерів:    {len(orders)}")
    print(f"💰 Дивідендів: {len(dividends)}")
    print(f"{'='*50}")

    return snapshot


def main():
    client = T212Client()

    args = sys.argv[1:]
    if not args or "--full" in args:
        sync_full(client)
    elif "--quick" in args:
        cash = client.account_cash()
        positions = client.positions()
        save_json(cash, DATA_DIR / "cash.json")
        save_json(positions, POSITIONS_FILE)
        total = cash.get("total", 0)
        ppl = cash.get("ppl", 0)
        print(f"💰 €{total:,.2f} | PPL: €{ppl:,.2f} | {len(positions)} positions")
    else:
        if "--transactions" in args:
            tx = client.transactions()
            save_json(tx, TRANSACTIONS_FILE)
            print(f"💸 {len(tx)} transactions saved")
        if "--orders" in args:
            orders = client.orders_history()
            save_json(orders, ORDERS_FILE)
            print(f"📋 {len(orders)} orders saved")
        if "--dividends" in args:
            divs = client.dividends()
            save_json(divs, DIVIDENDS_FILE)
            print(f"💰 {len(divs)} dividends saved")


if __name__ == "__main__":
    main()
