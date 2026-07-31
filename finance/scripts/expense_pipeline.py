#!/usr/bin/env python3
"""Auto Expense Pipeline — pull T212 CSV, categorize, log to DB + files.

Usage:
  python3 scripts/expense_pipeline.py           # full pipeline
  python3 scripts/expense_pipeline.py --month 7 # specific month
  python3 scripts/expense_pipeline.py --auto    # cron mode (silent)
"""

import csv, json, sys, subprocess, io, time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

HOME = Path.home()
FINANCE = HOME / "spaces" / "finance"
CSV_FILE = FINANCE / "trading212" / "t212_full_export.csv"
CARD_FILE = FINANCE / "trading212" / "card_expenses.json"
MONTHLY_FILE = FINANCE / "trading212" / "monthly_expenses.json"

MERCHANTS = {
    "ALDI|LIDL|REWE|EDEKA|NETTO|PENNY|Kaufland|Rossmann|dm|BUDNI|V\. Wiedemann": ("🍔 Продукти", "groceries"),
    "Flix|bahn|hvv|bus|taxi|uber|Deutschlandticket|HVV|Bahn": ("🚇 Транспорт", "transport"),
    "Amazon|Zalando|Otto|Saturn|Media.?Markt|eBay|cyberport|JUSTCOM": ("🛒 Покупки", "shopping"),
    "Netflix|Spotify|Apple.*bill|iCloud|Google.*sub|YouTube|Disney": ("📱 Підписки", "subscriptions"),
    "Restaurant|McDonalds|Burger|Pizza|Döner|Liefer|Backwerk": ("🍽️ Харчування", "dining"),
    "Apotheke|Pharmacy|Arzt|Doctor|Hospital|Zahnarzt": ("🏥 Здоров'я", "health"),
    "Therme|Schwimmbad|Fitness|Gym|Sport|Kino|Cinema": ("🏊 Розваги", "entertainment"),
    "DeepSeek|OpenRouter|Anthropic|OpenAI|LiteLLM|Github|GitLab": ("🤖 AI/API", "ai_api"),
    "Telekom|Vodafone|O2|Mobil|Internet|SIM|WhatsApp": ("📶 Зв'язок", "telecom"),
    "Versicherung|Insurance|Haftpflicht|ADAC|Allianz": ("🛡️ Страхування", "insurance"),
    "Tankstelle|JET|TotalEnergie|Aral|Shell|ESSO|HEM|Star": ("⛽ Пальне", "fuel"),
    "TABAKWAREN|Tabak|Shisha|YELOE": ("🚬 Тютюн", "tobacco"),
    "IRCC|Amt|Behörde|Gebühr|Bußgeld|Ausländer": ("🏛️ Збори", "fees"),
}

import re

def categorize(merchant: str) -> tuple[str, str]:
    for pattern, (cat, key) in MERCHANTS.items():
        if re.search(pattern, merchant, re.IGNORECASE):
            return cat, key
    return "❓ Інше", "other"


def parse_csv() -> list[dict]:
    if not CSV_FILE.exists():
        print(f"❌ No CSV at {CSV_FILE}")
        return []

    with open(CSV_FILE) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Only card debits
    card = []
    for r in rows:
        if r['Action'] != 'Card debit':
            continue
        merchant = r.get('Merchant name', '') or 'Unknown'
        cat, key = categorize(merchant)
        card.append({
            "date": r['Time (UTC)'][:10],
            "month": r['Time (UTC)'][:7],
            "merchant": merchant,
            "merchant_category": r.get('Merchant category', ''),
            "amount": abs(float(r.get('Gross Total', 0))),
            "currency": r.get('Currency (Gross Total)', 'EUR'),
            "category": cat,
            "category_key": key,
        })

    return card


def monthly_report(card: list[dict], month: str = None):
    if month is None:
        month = datetime.now().strftime("%Y-%m")

    month_txns = [t for t in card if t['month'] == month]
    if not month_txns:
        print(f"Немає транзакцій за {month}")
        return None

    # By category
    by_cat = defaultdict(float)
    for t in month_txns:
        by_cat[t['category']] += t['amount']

    total = sum(by_cat.values())
    avg_per_day = total / 30

    # By merchant
    by_merchant = defaultdict(float)
    for t in month_txns:
        by_merchant[t['merchant']] += t['amount']

    # AI costs
    ai_costs = by_cat.get('🤖 AI/API', 0)

    report = {
        "month": month,
        "total": round(total, 2),
        "avg_per_day": round(avg_per_day, 2),
        "transaction_count": len(month_txns),
        "by_category": {k: round(v, 2) for k, v in sorted(by_cat.items(), key=lambda x: -x[1])},
        "by_merchant": {k: round(v, 2) for k, v in sorted(by_merchant.items(), key=lambda x: -x[1])[:20]},
        "ai_costs": round(ai_costs, 2),
        "budget_status": "over" if total > 200 else "ok",
        "generated_at": datetime.now().isoformat(),
    }

    return report


def save_to_db(report: dict):
    """Save monthly report to PostgreSQL on vuzol."""
    content = f"Monthly expense report {report['month']}: €{report['total']:.2f} in {report['transaction_count']} transactions. "
    content += f"Top: {list(report['by_category'].keys())[:3]}. "
    content += f"AI: €{report['ai_costs']:.2f}. Budget: {'OVER' if report['budget_status'] == 'over' else 'OK'}."

    sql = f"""
    INSERT INTO paper_journal (entry_type, content, tags)
    VALUES ('observation', '{content}', '{json.dumps({"monthly_expense": True, "month": report["month"]})}')
    """
    try:
        subprocess.run(
            ["ssh", "vuzol", "sudo", "-u", "postgres", "psql", "-d", "orchestrator", "-q"],
            input=sql, capture_output=True, text=True, timeout=10
        )
    except Exception as e:
        print(f"  ⚠️ DB save failed: {e}")


def run_pipeline(month: str = None):
    print("📊 Expense Pipeline")
    print("=" * 50)

    # 1. Parse CSV
    card = parse_csv()
    if not card:
        return

    # 2. Save detailed expenses
    with open(CARD_FILE, 'w') as f:
        json.dump({"count": len(card), "items": card}, f, indent=2, ensure_ascii=False)
    print(f"💾 {len(card)} card transactions → {CARD_FILE}")

    # 3. Monthly report
    months = sorted(set(t['month'] for t in card))

    if month:
        months_to_run = [f"2026-{month.zfill(2)}"] if len(month) <= 2 else [month]
    else:
        months_to_run = months

    all_reports = {}
    for m in months_to_run:
        report = monthly_report(card, m)
        if report:
            all_reports[m] = report

            # Print
            print(f"\n{'─'*40}")
            print(f"💰 {m}")
            print(f"{'─'*40}")
            for cat, amt in report['by_category'].items():
                bar = '█' * int(amt / 10)
                print(f"  {cat:15} €{amt:7.2f}  {bar}")
            print(f"  {'─'*30}")
            print(f"  {'Разом':15} €{report['total']:7.2f}")
            if report['budget_status'] == 'over':
                print(f"  ⚠️ ПЕРЕВИТРАТА на €{report['total'] - 200:.2f}!")

            # Save to DB
            save_to_db(report)

    # 4. Save all reports
    with open(MONTHLY_FILE, 'w') as f:
        json.dump(all_reports, f, indent=2, ensure_ascii=False)

    # 5. Summary
    print(f"\n{'='*50}")
    print(f"📊 Всі місяці:")
    all_card = card
    for m in sorted(months):
        mt = [t for t in all_card if t['month'] == m]
        tot = sum(t['amount'] for t in mt)
        ai = sum(t['amount'] for t in mt if t['category_key'] == 'ai_api')
        flag = " ⚠️" if tot > 200 else ""
        print(f"  {m}: €{tot:7.2f} | AI: €{ai:.2f}{flag}")

    # Total AI
    total_ai = sum(t['amount'] for t in all_card if t['category_key'] == 'ai_api')
    print(f"\n🤖 AI/API total: €{total_ai:.2f} (€{total_ai/len(months):.2f}/міс)")


if __name__ == "__main__":
    month = None
    for a in sys.argv[1:]:
        if a.startswith("--month="):
            month = a.split("=", 1)[1]
    run_pipeline(month)
