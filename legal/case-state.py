#!/usr/bin/env python3
"""
Case State Helper — read/update case.json files in ~/spaces/legal/

Usage:
  python3 case-state.py get <case-dir>                    # show case state
  python3 case-state.py get <case-dir> --field deadlines  # show specific field
  python3 case-state.py set <case-dir> status <value>     # update status
  python3 case-state.py set <case-dir> phase <value>      # update phase
  python3 case-state.py set <case-dir> progress <0-100>   # update progress %
  python3 case-state.py add <case-dir> completed "<text>" # add completed step
  python3 case-state.py add <case-dir> pending "<text>"   # add pending step
  python3 case-state.py done <case-dir> "<step text>"     # move step from pending → completed
  python3 case-state.py deadline <case-dir> <key> <YYYY-MM-DD> "<desc>"  # add/update deadline
  python3 case-state.py activity <case-dir> "<text>"      # update last_activity
  python3 case-state.py drafts <case-dir> <location>      # update drafts info
  python3 case-state.py touch <case-dir>                  # recalculate days_remaining
  python3 case-state.py list                              # list all cases
  python3 case-state.py template <new-case-dir>           # create case.json from template

Examples:
  python3 case-state.py get factory-nsc
  python3 case-state.py set factory-nsc progress 80
  python3 case-state.py done factory-nsc "Pick up notarized affidavit"
  python3 case-state.py deadline factory-nsc hearing 2026-09-15 "Preliminary hearing"
"""

import os, sys, json
from datetime import datetime, date

SPACES_DIR = os.path.expanduser("~/spaces")
LEGAL_DIR = os.path.join(SPACES_DIR, "legal")
TEMPLATE = os.path.join(LEGAL_DIR, "case-template.json")

# ── helpers ──

def _find_case(name: str) -> str | None:
    """Find case.json by case directory name."""
    # Direct match in legal space
    path = os.path.join(LEGAL_DIR, name, "case.json")
    if os.path.exists(path):
        return path
    # Search deeper
    for root, dirs, files in os.walk(LEGAL_DIR):
        if "case.json" in files and os.path.basename(root) == name:
            return os.path.join(root, "case.json")
    return None

def _load(path: str) -> dict:
    with open(path) as f:
        return json.load(f)

def _save(path: str, data: dict):
    data["last_updated"] = datetime.now().isoformat()
    # Recalculate days_remaining
    today = date.today()
    for key, dl in data.get("deadlines", {}).items():
        try:
            dl_date = datetime.strptime(dl["date"], "%Y-%m-%d").date()
            dl["days_remaining"] = (dl_date - today).days
        except (ValueError, KeyError):
            dl["days_remaining"] = None
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _template() -> dict:
    if os.path.exists(TEMPLATE):
        return _load(TEMPLATE)
    return {"_schema": "1.0"}

# ── commands ──

def cmd_list():
    print(f"{'Case':<25} {'Status':<10} {'Progress':<10} {'Deadlines':<20} {'Last Activity'}")
    print("-" * 100)
    for root, dirs, files in os.walk(LEGAL_DIR):
        if "case.json" in files:
            path = os.path.join(root, "case.json")
            try:
                c = _load(path)
            except Exception:
                continue
            name = os.path.basename(root)
            status = c.get("status", "?")
            progress = f"{c.get('progress', {}).get('percentage', 0)}%"
            deadlines = ", ".join(
                f"{k}={v.get('date','?')} ({v.get('days_remaining','?')}d)"
                for k, v in c.get("deadlines", {}).items()
            ) or "—"
            activity = str(c.get("last_activity", ""))[:40]
            print(f"{name:<25} {status:<10} {progress:<10} {deadlines:<20} {activity}")
    print()

def cmd_get(path: str, field: str | None = None):
    c = _load(path)
    if field:
        print(json.dumps(c.get(field, {}), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(c, ensure_ascii=False, indent=2))

def cmd_set(path: str, field: str, value: str):
    c = _load(path)
    if field == "progress":
        c.setdefault("progress", {})["percentage"] = int(value)
    elif field == "status":
        c["status"] = value
    elif field == "phase":
        c["phase"] = value
    elif field == "activity":
        c["last_activity"] = value
    elif field == "drafts":
        c.setdefault("drafts", {})["location"] = value
    else:
        c[field] = value
    _save(path, c)
    print(f"✅ {field} = {value}")

def cmd_add(path: str, list_name: str, text: str):
    c = _load(path)
    if list_name in ("completed", "pending"):
        c.setdefault("progress", {}).setdefault(list_name, []).append(text)
    _save(path, c)
    print(f"✅ Added to {list_name}: {text}")

def cmd_done(path: str, text: str):
    """Move a step from pending → completed (fuzzy match)."""
    c = _load(path)
    pending = c.get("progress", {}).get("pending", [])
    matched = None
    for item in pending:
        if text.lower() in item.lower():
            matched = item
            break
    if matched:
        pending.remove(matched)
        c["progress"].setdefault("completed", []).append(matched)
        # Recalculate progress
        done = len(c["progress"]["completed"])
        total = done + len(pending)
        c["progress"]["percentage"] = round(done / total * 100) if total > 0 else 0
        _save(path, c)
        print(f"✅ Done: {matched}")
    else:
        print(f"⚠️  Not found in pending: {text}")

def cmd_deadline(path: str, key: str, date_str: str, desc: str = ""):
    c = _load(path)
    c.setdefault("deadlines", {})[key] = {
        "date": date_str,
        "description": desc,
        "status": "pending"
    }
    _save(path, c)
    print(f"✅ Deadline {key} = {date_str} ({desc})")

def cmd_touch(path: str):
    """Recalculate days_remaining only."""
    c = _load(path)
    _save(path, c)
    print(f"✅ days_remaining recalculated")

def cmd_template(target_dir: str):
    """Create a new case.json from template."""
    target_path = os.path.join(LEGAL_DIR, target_dir, "case.json")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    t = _template()
    t["last_updated"] = datetime.now().isoformat()
    t["last_activity"] = f"Case created: {target_dir}"
    with open(target_path, "w") as f:
        json.dump(t, f, ensure_ascii=False, indent=2)
    print(f"✅ Created: {target_path}")

# ── main ──

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "list":
        cmd_list()

    elif cmd == "template" and len(sys.argv) >= 3:
        cmd_template(sys.argv[2])

    elif cmd == "touch":
        name = sys.argv[2]
        path = _find_case(name)
        if not path:
            print(f"❌ Case not found: {name}")
            sys.exit(1)
        cmd_touch(path)

    elif cmd in ("get", "set", "add", "done", "deadline", "activity", "drafts"):
        name = sys.argv[2]
        path = _find_case(name)
        if not path:
            print(f"❌ Case not found: {name}")
            sys.exit(1)

        if cmd == "get":
            field = sys.argv[3] if len(sys.argv) >= 4 and sys.argv[3] == "--field" and len(sys.argv) >= 5 else None
            if field:
                field = sys.argv[4]
            cmd_get(path, field)
        elif cmd == "set":
            cmd_set(path, sys.argv[3], " ".join(sys.argv[4:]))
        elif cmd == "add":
            cmd_add(path, sys.argv[3], " ".join(sys.argv[4:]))
        elif cmd == "done":
            cmd_done(path, " ".join(sys.argv[3:]))
        elif cmd == "deadline":
            desc = sys.argv[5] if len(sys.argv) >= 6 else ""
            cmd_deadline(path, sys.argv[3], sys.argv[4], desc)
        elif cmd in ("activity", "drafts"):
            cmd_set(path, cmd, " ".join(sys.argv[3:]))
    else:
        print(__doc__)
