#!/usr/bin/env python3
"""Minimal Task API v2 — wraps state.py for project management + heartbeat.
Zero dependencies beyond Python 3 stdlib. Port 8000."""

import json
import os
import re
import subprocess
import sys
import psycopg2
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8000
HEARTBEAT_FILE = "/tmp/mac-heartbeat.json"
HEARTBEAT_TIMEOUT = 180   # seconds — mac-mini offline after this
STATE_PY = "/root/scripts/state.py"


# ── helpers ──────────────────────────────────────────────────

def _run(args):
    """Run a command and return (stdout, stderr, returncode)."""
    r = subprocess.run(args, capture_output=True, text=True, timeout=15)
    return r.stdout.strip(), r.stderr.strip(), r.returncode


def _parse_json_output(text):
    """state.py may print a status line before JSON; extract the JSON object."""
    idx = text.find("{")
    if idx == -1:
        return None
    try:
        return json.loads(text[idx:])
    except json.JSONDecodeError:
        return None


def read_heartbeat():
    """Return (data_dict_or_None, seconds_ago_or_None)."""
    try:
        with open(HEARTBEAT_FILE) as f:
            data = json.load(f)
        # Support both 'last_heartbeat' and 'timestamp' keys
        ts = data.get('last_heartbeat') or data.get('timestamp')
        if not ts:
            return None, None
        last = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        ago = (datetime.now(timezone.utc).astimezone() - last).total_seconds()
        return data, round(ago)
    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
        return None, None


def write_heartbeat(source="mac-mini"):
    """Record a heartbeat. Returns the written data dict."""
    now = datetime.now(timezone.utc).astimezone()
    data = {
        "last_heartbeat": now.isoformat(),
        "source": source,
        "status": "ok",
        "timeout_seconds": HEARTBEAT_TIMEOUT,
    }
    with open(HEARTBEAT_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False)
    return data


def mac_mini_online():
    _, ago = read_heartbeat()
    if ago is None:
        return False
    return ago <= HEARTBEAT_TIMEOUT


# ── Orchestration task queue (PostgreSQL) ────────────────────

DB = "dbname=orchestrator user=postgres"


def db_submit(space, payload, target="mac-mini", priority=50):
    """Submit a task to the orchestrator queue. Returns task ID or None."""
    try:
        conn = psycopg2.connect(DB)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (space, target, priority, status, payload) "
            "VALUES (%s, %s, %s, 'pending', %s) RETURNING id",
            (space, target, priority, json.dumps(payload, ensure_ascii=False)),
        )
        tid = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return tid
    except Exception as e:
        print(f"db_submit error: {e}", file=sys.stderr)
        return None


def db_status(task_id):
    """Get task status and result. Returns None if not found."""
    try:
        conn = psycopg2.connect(DB)
        cur = conn.cursor()
        cur.execute(
            "SELECT id, space, target, priority, status, payload, result, error, "
            "created_at, done_at FROM tasks WHERE id = %s",
            (task_id,),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return None
        return {
            "id": row[0], "space": row[1], "target": row[2],
            "priority": row[3], "status": row[4],
            "payload": row[5], "result": row[6], "error": row[7],
            "created_at": row[8].isoformat() if row[8] else None,
            "done_at": row[9].isoformat() if row[9] else None,
        }
    except Exception as e:
        print(f"db_status error: {e}", file=sys.stderr)
        return None


# ── HTTP handler ─────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):

    def _json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    # ── GET ──────────────────────────────────────────────────

    def do_GET(self):
        p = self.path

        # / — endpoint listing
        if p == "/":
            self._json({
                "service": "task-api v2",
                "endpoints": {
                    "GET /": "this listing",
                    "GET /health": "health check → {\"status\":\"ok\"}",
                    "GET /heartbeat": "last mac-mini heartbeat",
                    "GET /tasks": "all projects (state.py list --json)",
                    "GET /tasks/<id>": "one project (state.py get <id>)",
                    "POST /tasks/<id>": "update project (body: {\"field\":\"...\", \"value\":\"...\"})",
                    "POST /heartbeat": "record heartbeat from mac-mini",
                    "POST /task/submit": "submit orchestration task -> {\"id\": N}",
                    "GET /task/status/<id>": "check orchestration task status/result",
                },
                "docs": "state.py wraps ~/.claude/projects/ JSON files",
            })

        # /health
        elif p == "/health":
            self._json({"status": "ok"})

        # /heartbeat
        elif p == "/heartbeat":
            hb, ago = read_heartbeat()
            online = mac_mini_online()
            self._json({
                "status": "ok",
                "heartbeat": hb,
                "mac_mini_online": online,
                "seconds_ago": ago,
                "timeout_seconds": HEARTBEAT_TIMEOUT,
            })

        # /tasks
        elif p == "/tasks":
            out, err, rc = _run([sys.executable, STATE_PY, "list", "--json"])
            if rc != 0:
                self._json({"error": "state.py failed", "detail": err}, 500)
                return
            data = _parse_json_output(out)
            if data is None:
                self._json({"error": "invalid JSON from state.py", "raw": out[:500]}, 500)
                return
            self._json(data)

        # /task/status/<id>  — orchestration task result
        elif m := re.match(r'^/task/status/(\d+)$', p):
            tid = int(m.group(1))
            data = db_status(tid)
            if data is None:
                self._json({"error": f"task {tid} not found"}, 404)
                return
            self._json(data)

        # /tasks/<id>
        elif m := re.match(r'^/tasks/([a-zA-Z0-9_-]+)$', p):
            proj_id = m.group(1)
            out, err, rc = _run([sys.executable, STATE_PY, "get", proj_id])
            if rc != 0:
                self._json({"error": f"project '{proj_id}' not found", "detail": err}, 404)
                return
            data = _parse_json_output(out)
            if data is None:
                self._json({"error": "invalid JSON from state.py", "raw": out[:500]}, 500)
                return
            self._json(data)

        else:
            self._json({"error": "not found"}, 404)

    # ── POST ─────────────────────────────────────────────────

    def do_POST(self):
        p = self.path

        # POST /task/submit  — submit orchestration task
        if p == "/task/submit":
            body = self._read_body()
            space = body.get("space", "")
            task_text = body.get("task", "")
            target = body.get("target", "mac-mini")
            priority = body.get("priority", 50)

            if not space or not task_text:
                self._json({"error": "missing 'space' or 'task' in JSON body"}, 400)
                return

            payload = {
                "task": task_text,
                "submitted_via": "task-api",
                "submitted_at": datetime.now(timezone.utc).astimezone().isoformat(),
            }
            tid = db_submit(space, payload, target=target, priority=priority)
            if tid is None:
                self._json({"error": "failed to insert task into database"}, 500)
                return
            self._json({"id": tid, "status": "pending", "space": space}, 201)

        # POST /heartbeat
        elif p == "/heartbeat":
            body = self._read_body()
            source = body.get("source", "mac-mini")
            hb = write_heartbeat(source)
            online = mac_mini_online()
            _, ago = read_heartbeat()
            self._json({
                "status": "ok",
                "role": "dispatcher",
                "source": source,
                "mac_mini_online": online,
                "seconds_ago": ago,
                "heartbeat": hb,
            })

        # POST /tasks/<id>  — update field
        elif m := re.match(r'^/tasks/([a-zA-Z0-9_-]+)$', p):
            proj_id = m.group(1)
            body = self._read_body()
            field = body.get("field", "")
            value = body.get("value", "")
            if not field:
                self._json({"error": "missing 'field' in JSON body"}, 400)
                return
            out, err, rc = _run([sys.executable, STATE_PY, "set", proj_id, field, str(value)])
            if rc != 0:
                self._json({"error": f"state.py set failed: {err}", "detail": out[:500]}, 400)
                return
            data = _parse_json_output(out)
            if data is None:
                self._json({"error": "invalid JSON from state.py", "raw": out[:500]}, 500)
                return
            self._json(data)

        else:
            self._json({"error": "not found"}, 404)

    def log_message(self, *args):
        pass  # quiet


# ── main ─────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"task-api v2 listening on :{PORT}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
