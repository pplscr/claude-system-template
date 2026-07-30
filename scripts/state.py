#!/usr/bin/env python3
"""
Project State CLI v2 — mac-mini (джерело правди).
Об'єднує: проєктний менеджмент (з vuzol) + метрики агентів + sync vuzol ↔ mac-mini.

Usage:
  python3 state.py list                           # всі проєкти
  python3 state.py list --json                    # машиночитний JSON
  python3 state.py get <project-id>               # один проєкт
  python3 state.py set <project-id> <field> <value>  # оновити поле
  python3 state.py priority                       # перерахувати пріоритети (dry-run)
  python3 state.py priority --apply               # застосувати
  python3 state.py sync                           # синхронізувати з vuzol (двостороння)
  python3 state.py sync --push                    # відправити на vuzol
  python3 state.py sync --pull                    # отримати з vuzol
  python3 state.py spaces                         # показати простори + агенти
  python3 state.py metrics                        # метрики агентів (останні 15)
  python3 state.py balance                        # баланс API ключів
  python3 state.py init                           # ініціалізувати всі проєкти

Поля для set:
  status      — active | paused | done | blocked
  priority    — critical | high | medium | low
  progress    — 0-100 (число)
  deadline    — YYYY-MM-DD (основний дедлайн)
  deadline_*  — будь-який іменований дедлайн (напр: deadline_payment)
  next_step   — додати наступний крок (можна кілька)
  blocked_by  — що блокує (через кому)
  contact     — контактна особа/телефон
  activity    — остання активність (текст)
  description — опис проєкту
  clear_steps — очистити всі next_steps
"""

import os, sys, json, subprocess
from datetime import datetime, date, timezone, timedelta
from typing import Optional, Tuple

# ── Шляхи ──────────────────────────────────────────────────
PROJECTS_DIR = os.path.expanduser("~/.claude/projects")
MAC_STATE_FILE = os.path.expanduser("~/.claude/mac-state.json")
BALANCE_FILE = os.path.expanduser("~/balance-history.jsonl")
CREDS_FILE = os.path.expanduser("~/.claude/credentials.env")
SPACES_DIR = os.path.expanduser("~/spaces")
VUZOL = "vuzol"

# ── Реєстр проєктів ───────────────────────────────────────
PROJECTS = {
    "fw-mahnung": {
        "name": "F&W 3. Mahnung",
        "priority": "critical",
        "tier": "life",
        "description": "€13 166.05 борг за проживання (2022-06 – 2024-05), Гамбург",
        "contact": "Joana Ramos, joana.ramos@foerdernundwohnen.de, 040 428 35 38 13",
        "vuzol_dir": "/root/cases/fw-debt",
        "mac_dir": None,
    },
    "factory-nsc": {
        "name": "NSC Legal Case",
        "priority": "high",
        "tier": "life",
        "description": "Юридичний кейс проти National Steel Car — OLRB, DFR, OHSA, MECP",
        "vuzol_dir": "/root/factory-nsc",
        "mac_dir": None,
    },
    "cibc": {
        "name": "CIBC Credit Recovery",
        "priority": "critical",
        "tier": "life",
        "description": "Втрачений телефон → немає 2FA → пропущений платіж → скоринг -200",
        "contact": "CIBC: +1-902-420-2422 (24/7)",
        "vuzol_dir": None,
        "mac_dir": None,
    },
    "finances": {
        "name": "Фінанси",
        "priority": "high",
        "tier": "life",
        "description": "Бюджет, API ключі, підписки, витрати",
        "vuzol_dir": "/root/finances",
        "mac_dir": None,
    },
    "merezha": {
        "name": "Мережа A2A Orchestrator",
        "priority": "medium",
        "tier": "hobby",
        "description": "Agent-to-Agent комунікація L0-L3, Python 3.12+, v0.4.0",
        "vuzol_dir": "/root/мережа",
        "mac_dir": None,
    },
    "pantheon": {
        "name": "Pantheon Office",
        "priority": "low",
        "tier": "hobby",
        "description": "FastAPI + Next.js monorepo, AI-платформа",
        "vuzol_dir": "/root/pantheon_office_v2.5",
        "mac_dir": None,
    },
    "setup-gmail-orchestrator": {
        "name": "Gmail MCP Orchestrator",
        "priority": "medium",
        "tier": "hobby",
        "description": "Налаштувати Gmail доступ для оркестратора",
        "vuzol_dir": None,
        "mac_dir": None,
    },
    "mac-infra": {
        "name": "mac-mini Infrastructure",
        "priority": "high",
        "tier": "life",
        "description": "CLAUDE.md, rules, scripts, healthcheck, backup to vuzol",
        "vuzol_dir": None,
        "mac_dir": os.path.expanduser("~/.claude"),
    },
    "claude-system": {
        "name": "Claude System Management",
        "priority": "medium",
        "tier": "life",
        "description": "Керування claude-system скриптами, state tracking, sync з vuzol",
        "vuzol_dir": None,
        "mac_dir": os.path.expanduser("~/claude-system"),
    },
}

# ── Auto-priority helpers ─────────────────────────────────

PRIORITY_LABELS = {
    "critical": "‼ CRITICAL",
    "high": "⚠ HIGH",
    "medium": "MEDIUM",
    "low": "LOW",
}


def calc_days_remaining(deadlines: dict) -> dict:
    """Calculate days remaining for each deadline key."""
    today = date.today()
    result = {}
    for key, dl_str in (deadlines or {}).items():
        try:
            dl_date = datetime.strptime(dl_str, "%Y-%m-%d").date()
            result[key] = (dl_date - today).days
        except (ValueError, TypeError):
            result[key] = None
    return result


def calc_auto_priority(deadlines: dict, tier: str = "life") -> Optional[str]:
    """Calculate auto-priority from the closest deadline.
    Hobby tier capped at 'medium' (never critical or high).
    """
    if not deadlines:
        return None
    days_map = calc_days_remaining(deadlines)
    valid_days = [d for d in days_map.values() if d is not None]
    if not valid_days:
        return None

    min_days = min(valid_days)
    if min_days <= 3:
        auto = "critical"
    elif min_days <= 7:
        auto = "high"
    elif min_days <= 14:
        auto = "medium"
    else:
        auto = "low"

    if tier == "hobby" and auto in ("critical", "high"):
        auto = "medium"
    return auto


def find_urgent(days_remaining: dict) -> Tuple[Optional[str], Optional[int]]:
    """Return (urgent_key, urgent_days) for the closest deadline."""
    if not days_remaining:
        return None, None
    urgent_key, urgent_days = None, None
    for key, days in days_remaining.items():
        if days is not None and (urgent_days is None or days < urgent_days):
            urgent_days = days
            urgent_key = key
    return urgent_key, urgent_days


# ── State path / load / save ──────────────────────────────

def _state_path(project_id: str) -> str:
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    return os.path.join(PROJECTS_DIR, f"{project_id}.json")


def _load(project_id: str) -> dict:
    proj = PROJECTS.get(project_id)
    if not proj:
        return {}

    path = _state_path(project_id)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)

    return {
        "id": project_id,
        "name": proj["name"],
        "status": "active",
        "priority": proj["priority"],
        "progress": 0,
        "description": proj["description"],
        "deadlines": {},
        "next_steps": [],
        "blocked_by": [],
        "contact": proj.get("contact"),
        "last_activity": None,
        "tier": proj.get("tier", "life"),
    }


def _save(project_id: str, state: dict):
    state["last_updated"] = datetime.now().isoformat()
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    with open(_state_path(project_id), "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ── Formatting ─────────────────────────────────────────────

def _days_str(days: Optional[int]) -> str:
    if days is None:
        return "?"
    if days < 0:
        return f"{-days}д ПРОСТРОЧЕНО‼"
    if days == 0:
        return "сьогодні‼"
    return f"{days}д"


def _deadlines_display(deadlines: dict) -> str:
    if not deadlines:
        return "—"
    days_map = calc_days_remaining(deadlines)
    parts = []
    for key, dl_str in deadlines.items():
        d = days_map.get(key)
        parts.append(f"{key}={dl_str} ({_days_str(d)})")
    return ", ".join(parts)


# ── Commands ──────────────────────────────────────────────

def cmd_list(json_mode: bool = False):
    if json_mode:
        return _cmd_list_json()

    def _urgency_sort_key(pid: str) -> tuple:
        s = _load(pid)
        dl = s.get("deadlines", {})
        if not dl:
            return (1, 0, pid)
        days_map = calc_days_remaining(dl)
        _, urgent_days = find_urgent(days_map)
        if urgent_days is None:
            return (1, 0, pid)
        return (0, urgent_days, pid)

    sorted_pids = sorted(PROJECTS.keys(), key=_urgency_sort_key)

    print(f"{'ID':<25} {'Tier':<6} {'Статус':<8} {'Прогрес':<8} {'Пріоритет':<12} {'Авто':<12} {'Дедлайни'}")
    print("-" * 130)
    for pid in sorted_pids:
        s = _load(pid)
        tier = PROJECTS[pid].get("tier", "life")
        status = s.get("status", "?")
        progress = f"{s.get('progress', 0)}%"
        static_prio = s.get("priority", "?")
        deadlines = s.get("deadlines", {})

        auto_prio = calc_auto_priority(deadlines, tier=tier)
        if auto_prio is None:
            auto_display = "—"
        elif auto_prio != static_prio:
            auto_display = PRIORITY_LABELS.get(auto_prio, auto_prio)
        else:
            auto_display = f"✓ {auto_prio}"

        print(f"{pid:<25} {tier:<6} {status:<8} {progress:<8} {static_prio:<12} {auto_display:<12} {_deadlines_display(deadlines)}")


def _cmd_list_json():
    result = {"projects": [], "generated_at": datetime.now().isoformat()}
    for pid in PROJECTS:
        s = _load(pid)
        tier = PROJECTS[pid].get("tier", "life")
        deadlines = s.get("deadlines", {})
        days_map = calc_days_remaining(deadlines)
        auto_prio = calc_auto_priority(deadlines, tier=tier)
        urgent_key, urgent_days = find_urgent(days_map)

        result["projects"].append({
            "id": pid,
            "name": s.get("name", ""),
            "tier": tier,
            "status": s.get("status", "active"),
            "priority": s.get("priority", ""),
            "auto_priority": auto_prio,
            "progress": s.get("progress", 0),
            "deadlines": deadlines,
            "days_remaining": days_map,
            "urgent_deadline": urgent_key,
            "urgent_days": urgent_days,
            "next_steps": s.get("next_steps", []),
            "blocked_by": s.get("blocked_by", []),
            "contact": s.get("contact"),
            "last_activity": s.get("last_activity"),
        })
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_get(project_id: str):
    s = _load(project_id)
    if not s:
        print(f"Project '{project_id}' not found.")
        return
    print(json.dumps(s, ensure_ascii=False, indent=2))


def cmd_set(project_id: str, field: str, value: str):
    s = _load(project_id)
    if not s:
        print(f"Project '{project_id}' not found.")
        return

    if field == "progress":
        s["progress"] = int(value)
    elif field == "status":
        s["status"] = value
    elif field == "priority":
        s["priority"] = value
    elif field.startswith("deadline_"):
        dl_key = field.replace("deadline_", "")
        s.setdefault("deadlines", {})[dl_key] = value
    elif field == "deadline":
        s.setdefault("deadlines", {})["default"] = value
    elif field == "next_step":
        if value == "clear":
            s["next_steps"] = []
        else:
            s.setdefault("next_steps", []).append(value)
    elif field == "clear_steps":
        s["next_steps"] = []
    elif field == "blocked_by":
        s["blocked_by"] = [b.strip() for b in value.split(",") if b.strip()]
    elif field == "contact":
        s["contact"] = value
    elif field == "activity":
        s["last_activity"] = value
    elif field == "description":
        s["description"] = value
    else:
        print(f"Unknown field: {field}")
        return

    _save(project_id, s)
    print(f"✅ {project_id}.{field} = {value}")
    cmd_get(project_id)


def cmd_priority(apply_changes: bool = False):
    changes = []
    for pid in PROJECTS:
        s = _load(pid)
        tier = PROJECTS[pid].get("tier", "life")
        static_prio = s.get("priority", "")
        deadlines = s.get("deadlines", {})
        auto_prio = calc_auto_priority(deadlines, tier=tier)
        if auto_prio is None:
            continue
        if auto_prio != static_prio:
            days_map = calc_days_remaining(deadlines)
            urgent_key, urgent_days = find_urgent(days_map)
            changes.append({
                "id": pid, "name": s.get("name", pid), "tier": tier,
                "static": static_prio, "auto": auto_prio,
                "urgent_deadline": urgent_key, "urgent_days": urgent_days,
            })

    if not changes:
        print("✅ Всі пріоритети актуальні — змін не потрібно.")
        return

    if not apply_changes:
        print("🔍 Dry-run — будуть змінені:")
        print(f"{'Проєкт':<25} {'Tier':<6} {'Поточний':<12} {'Авто':<12} {'Дедлайн':<20} {'Днів'}")
        print("-" * 95)
        for c in changes:
            dl_label = str(c['urgent_deadline']) if c['urgent_deadline'] else "?"
            print(f"{c['id']:<25} {c['tier']:<6} {c['static']:<12} {PRIORITY_LABELS.get(c['auto'], c['auto']):<12} {dl_label:<20} {_days_str(c['urgent_days'])}")
        print(f"\nВсього змін: {len(changes)}")
        print('Запустіть "python3 state.py priority --apply" щоб застосувати.')
    else:
        for c in changes:
            s = _load(c["id"])
            s["priority"] = c["auto"]
            _save(c["id"], s)
            print(f"  ✅ {c['id']}: {c['static']} → {c['auto']}")
        print(f"Застосовано {len(changes)} змін.")


# ── Sync ───────────────────────────────────────────────────

def cmd_sync(direction: str = "both"):
    if direction in ("push", "both"):
        _sync_push()
    if direction in ("pull", "both"):
        _sync_pull()


VUZOL_PROJECTS_DIR = "/root/.claude/projects"


def _sync_push():
    """Відправити всі проєктні state-файли на vuzol у /root/.claude/projects/."""
    print("📤 PUSH mac-mini → vuzol")
    # Ensure vuzol dir exists
    subprocess.run(["ssh", VUZOL, f"mkdir -p {VUZOL_PROJECTS_DIR}"],
                   capture_output=True, timeout=5)
    count = 0
    for pid in PROJECTS:
        local_path = _state_path(pid)
        if not os.path.exists(local_path):
            continue
        remote_path = f"{VUZOL_PROJECTS_DIR}/{pid}.json"

        try:
            result = subprocess.run(
                ["scp", local_path, f"{VUZOL}:{remote_path}"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                count += 1
                print(f"  ✅ {pid}")
            else:
                print(f"  ⚠️ {pid}: {result.stderr.strip()}")
        except Exception as e:
            print(f"  ❌ {pid}: {e}")
    print(f"Відправлено: {count}/{len(PROJECTS)}")


def _sync_pull():
    """Отримати проєктні state-файли з vuzol."""
    print("📥 PULL vuzol → mac-mini")
    count = 0
    for pid in PROJECTS:
        remote_path = f"{VUZOL_PROJECTS_DIR}/{pid}.json"
        local_path = _state_path(pid)
        try:
            result = subprocess.run(
                ["scp", f"{VUZOL}:{remote_path}", local_path],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                count += 1
                print(f"  ✅ {pid}")
        except Exception:
            pass
    print(f"Отримано: {count}/{len(PROJECTS)}")


# ── Spaces ─────────────────────────────────────────────────

def cmd_spaces():
    print(f"{'Простір':<20} {'Агенти':<50}")
    print("-" * 70)
    if not os.path.isdir(SPACES_DIR):
        print("  (немає ~/spaces/)")
        return
    for name in sorted(os.listdir(SPACES_DIR)):
        path = os.path.join(SPACES_DIR, name)
        if not os.path.isdir(path) or name.startswith("_") or name.startswith("."):
            continue
        agents_dir = os.path.join(path, "agents")
        agents = []
        if os.path.isdir(agents_dir):
            for a in sorted(os.listdir(agents_dir)):
                if os.path.isdir(os.path.join(agents_dir, a)) and not a.startswith("_"):
                    agents.append(a)
        agents_str = ", ".join(agents) if agents else "—"
        print(f"{name:<20} {agents_str:<50}")


# ── Metrics ────────────────────────────────────────────────

def cmd_metrics():
    if not os.path.exists(MAC_STATE_FILE):
        print("Немає mac-state.json")
        return
    with open(MAC_STATE_FILE) as f:
        state = json.load(f)
    logs = state.get("agent_log", [])
    if not logs:
        print("Немає записів.")
        return

    print(f"{'Час':<22} {'Простір':<12} {'Агент':<14} {'Модель':<18} {'Статус':<8} {'Токени':<12} {'$'}")
    print("-" * 110)
    for entry in logs[-15:]:
        ts = entry.get("ts", "")[:19].replace("T", " ")
        space = entry.get("space", "")
        agent = entry.get("agent", "")
        model = entry.get("model", "")[:17]
        status = entry.get("status", "")
        tokens = f"in:{entry.get('tokens_in',0)} out:{entry.get('tokens_out',0)}"
        cost = f"${entry.get('cost', 0):.4f}"
        print(f"{ts:<22} {space:<12} {agent:<14} {model:<18} {status:<8} {tokens:<12} {cost}")


def cmd_balance():
    if not os.path.exists(BALANCE_FILE):
        print("Немає balance-history.jsonl")
        return

    entries = []
    with open(BALANCE_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not entries:
        print("Записів немає.")
        return

    now = datetime.now(timezone.utc)
    cutoff_7d = now - timedelta(days=7)
    cutoff_30d = now - timedelta(days=30)

    by_provider = {}
    total_all, total_7d, total_30d = 0.0, 0.0, 0.0

    for e in entries:
        p = e.get("provider", "unknown")
        cost = e.get("cost_usd", 0.0)
        ts_str = e.get("ts", "")

        if p not in by_provider:
            by_provider[p] = {"cost_total": 0.0, "cost_7d": 0.0, "cost_30d": 0.0, "count": 0}

        by_provider[p]["cost_total"] += cost
        by_provider[p]["count"] += 1
        total_all += cost

        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                continue
            if ts >= cutoff_30d:
                by_provider[p]["cost_30d"] += cost
                total_30d += cost
                if ts >= cutoff_7d:
                    by_provider[p]["cost_7d"] += cost
                    total_7d += cost

    print(f"{'Provider':<20} {'Total':>10} {'7 days':>10} {'30 days':>10} {'Calls':>8}")
    print("-" * 60)
    for p in sorted(by_provider.keys()):
        d = by_provider[p]
        print(f"{p:<20} ${d['cost_total']:>9.4f} ${d['cost_7d']:>9.4f} ${d['cost_30d']:>9.4f} {d['count']:>8}")
    print("-" * 60)
    print(f"{'OVERALL':<20} ${total_all:>9.4f} ${total_7d:>9.4f} ${total_30d:>9.4f}")


# ── Init ───────────────────────────────────────────────────

def cmd_init():
    """Ініціалізувати всі проєкти, мігрувавши дані з vuzol active-tasks.json."""
    vuzol_projects = {}
    try:
        result = subprocess.run(
            ["ssh", VUZOL, "cat /root/scripts/active-tasks.json"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            vuzol_data = json.loads(result.stdout)
            vuzol_projects = {p["id"]: p for p in vuzol_data.get("projects", [])}
    except Exception as e:
        print(f"⚠️  Не вдалося отримати дані з vuzol: {e}")

    for pid, proj in PROJECTS.items():
        s = _load(pid)
        vp = vuzol_projects.get(pid)

        if vp:
            if not s.get("next_steps") and vp.get("next_steps"):
                s["next_steps"] = vp["next_steps"]
            if not s.get("blocked_by") and vp.get("blocked_by"):
                s["blocked_by"] = vp["blocked_by"]
            if not s.get("progress") and vp.get("progress"):
                s["progress"] = vp["progress"]
            if not s.get("last_activity") and vp.get("recent_activity"):
                s["last_activity"] = vp["recent_activity"]

            # Міграція дедлайнів
            deadlines = {}
            if vp.get("deadline"):
                deadlines["default"] = vp["deadline"]
            if vp.get("deadline_payment"):
                deadlines["payment"] = vp["deadline_payment"]
            if vp.get("deadline_widerspruch"):
                deadlines["widerspruch"] = vp["deadline_widerspruch"]
            for k, v in deadlines.items():
                if k not in s.get("deadlines", {}):
                    s.setdefault("deadlines", {})[k] = v

        _save(pid, s)
        steps_n = len(s.get("next_steps", []))
        dl_n = len(s.get("deadlines", {}))
        print(f"  ✅ {pid:<25} steps={steps_n} deadlines={dl_n}")

    print(f"\nІніціалізовано {len(PROJECTS)} проєктів у {PROJECTS_DIR}/")


# ── Main ──────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "list":
        cmd_list(json_mode="--json" in sys.argv)
    elif cmd == "get" and len(sys.argv) >= 3:
        cmd_get(sys.argv[2])
    elif cmd == "set" and len(sys.argv) >= 5:
        cmd_set(sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]))
    elif cmd == "priority":
        cmd_priority(apply_changes="--apply" in sys.argv)
    elif cmd == "sync":
        if "--push" in sys.argv:
            cmd_sync("push")
        elif "--pull" in sys.argv:
            cmd_sync("pull")
        else:
            cmd_sync("both")
    elif cmd == "spaces":
        cmd_spaces()
    elif cmd == "metrics":
        cmd_metrics()
    elif cmd == "balance":
        cmd_balance()
    elif cmd == "init":
        cmd_init()
    else:
        print(__doc__)
