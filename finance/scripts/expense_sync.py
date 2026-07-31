#!/usr/bin/env python3
"""Expense Tracker — auto-sync T212 card transactions via CSV export.

Uses T212 CSV export API for merchant names (not available in REST API).
Caches CSV → parses merchants → categorizes → reports.

Usage:
  python3 expense_sync.py --sync        # fetch latest CSV from T212
  python3 expense_sync.py --report      # monthly report from cache
  python3 expense_sync.py --top N       # top N merchants
"""

import csv
import json
import sys
import subprocess
import io
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

HOME = Path.home()
FINANCE = HOME / "spaces" / "finance"
CARD_CACHE = FINANCE / "trading212" / "card_expenses.json"
CSV_CACHE = FINANCE / "trading212" / "t212_full_export.csv"

# Category rules: merchant name patterns → category
MERCHANT_CATEGORIES = {
    "ALDI|LIDL|REWE|EDEKA|NETTO|PENNY|Kaufland|Rossmann|dm-drogerie|BUDNI": "🍔 Продукти",
    "Flix|bahn|hvv|bus|taxi|uber|Deutschlandticket|HVV": "🚇 Транспорт",
    "Amazon|Zalando|Otto|Saturn|Media.?Markt|eBay|cyberport|JUSTCOM": "🛒 Покупки",
    "Netflix|Spotify|Apple.*bill|iCloud|Google.*sub|YouTube": "📱 Підписки",
    "Restaurant|McDonalds|Burger|Pizza|Döner|Liefer|Backwerk|Bäckerei": "🍽️ Харчування",
    "Apotheke|Pharmacy|Arzt|Doctor|Hospital|Krankenhaus|Zahnarzt": "🏥 Здоров'я",
    "Therme|Schwimmbad|Fitness|Gym|Sport": "🏊 Розваги",
    "DeepSeek|OpenRouter|Anthropic|OpenAI|api|LiteLLM|Github": "🤖 AI/API",
    "Telekom|Vodafone|O2|Mobil|Internet|SIM": "📶 Зв'язок",
    "Versicherung|Insurance|Haftpflicht|ADAC": "🛡️ Страхування",
    "Tankstelle|JET|TotalEnergie|Aral|Shell|ESSO|HEM": "⛽ Пальне",
    "TABAKWAREN|Tabak|Shisha": "🚬 Тютюн",
    "IRCC|Amt|Behörde|Gebühr|Bußgeld": "🏛️ Збори",
    "V\. Wiedemann|Wiedemann": "🍔 Продукти",
}

MONTHLY_BUDGET = 200.00

MONTHLY_BUDGET = 200.00
AI_BUDGET = 80.00


def load_transactions() -> list:
    """Load all transactions from cache."""
    if not TRANSACTIONS.exists():
        return []
    with open(TRANSACTIONS) as f:
        data = json.load(f)
    return data.get("items", [])


def categorize(description: str, amount: float) -> str:
    """Auto-categorize a transaction based on description."""
    desc = description.lower() if description else ""
    for pattern, category in CATEGORY_RULES.items():
        import re
        if re.search(pattern, desc, re.IGNORECASE):
            return category
    # Default: by amount
    if amount > 0:
        return "💵 Дохід"
    return "❓ Інше"


def sync_expenses():
    """Sync and categorize all expenses."""
    txns = load_transactions()
    if not txns:
        print("No transactions loaded. Run sync first.")
        return

    # Load existing categories
    categories = {}
    if CATEGORIES_FILE.exists():
        with open(CATEGORIES_FILE) as f:
            categories = json.load(f)

    expenses = []
    for t in txns:
        txn_id = t.get("reference", str(t.get("dateTime", "")))
        cat = categories.get(txn_id) or categorize(
            t.get("reference", ""), t.get("amount", 0)
        )
        expenses.append({
            "id": txn_id,
            "date": t.get("dateTime", ""),
            "type": t.get("type", ""),
            "amount": t.get("amount", 0),
            "currency": t.get("currency", "EUR"),
            "category": cat,
            "reference": t.get("reference", ""),
        })

    # Save
    with open(EXPENSES_CACHE, "w") as f:
        json.dump(expenses, f, indent=2, ensure_ascii=False, default=str)

    # Summary
    withdraws = [e for e in expenses if e["type"] == "WITHDRAW"]
    deposits = [e for e in expenses if e["type"] == "DEPOSIT"]
    interest = [e for e in expenses if e["type"] == "INTEREST_ON_FREE_CASH"]

    print(f"💸 Expenses synced: {len(expenses)} total")
    print(f"   Deposits: {len(deposits)} (€{sum(d['amount'] for d in deposits):,.2f})")
    print(f"   Withdrawals: {len(withdraws)} (€{sum(abs(d['amount']) for d in withdraws):,.2f})")
    print(f"   Interest: {len(interest)} (€{sum(i['amount'] for i in interest):,.2f})")

    return expenses


def monthly_report():
    """Generate monthly spending report."""
    if not EXPENSES_CACHE.exists():
        print("Run --sync first")
        return

    with open(EXPENSES_CACHE) as f:
        expenses = json.load(f)

    now = datetime.now()
    this_month = [e for e in expenses if e["date"][:7] == now.strftime("%Y-%m")]
    withdraws = [e for e in this_month if e["type"] == "WITHDRAW"]

    # By category
    by_cat = defaultdict(float)
    for e in withdraws:
        by_cat[e["category"]] += abs(e["amount"])

    total_spent = sum(by_cat.values())
    ai_spent = by_cat.get("🤖 AI/API", 0)

    print(f"\n💰 Витрати за {now.strftime('%B %Y')}")
    print("=" * 40)
    for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1]):
        pct = amt / total_spent * 100 if total_spent > 0 else 0
        bar = "█" * int(pct / 5)
        print(f"  {cat:15} €{amt:7.2f}  {bar}")
    print("=" * 40)
    print(f"  {'Разом':15} €{total_spent:7.2f}")
    print(f"  {'Бюджет':15} €{MONTHLY_BUDGET:7.2f}")
    if total_spent > MONTHLY_BUDGET:
        print(f"  ⚠️ Перевищення на €{total_spent - MONTHLY_BUDGET:.2f}!")
    else:
        print(f"  ✅ Залишок: €{MONTHLY_BUDGET - total_spent:.2f}")
    print(f"\n  🤖 AI/API: €{ai_spent:.2f} / €{AI_BUDGET:.2f} бюджет")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or "--sync" in args:
        sync_expenses()
    if "--report" in args or not args:
        monthly_report()
    if "--categorize" in args:
        # Interactive categorization for uncategorized
        print("TODO: interactive categorize mode")
