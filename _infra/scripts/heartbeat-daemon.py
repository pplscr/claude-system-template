#!/usr/bin/env python3
"""Heartbeat monitor daemon — tracks mac-mini health and alerts on timeout.
Reads config from /root/config/heartbeat-config.json."""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CONFIG_FILE = "/root/config/heartbeat-config.json"
DEFAULT_CONFIG = {
    "timeout_seconds": 180,
    "check_interval_seconds": 60,
    "heartbeat_file": "/tmp/mac-heartbeat.json",
    "quiet_hours": {"start": "23:00", "end": "06:00"},
    "alert_on_missing": True,
    "max_missed_beats": 3,
}


def load_config():
    """Load heartbeat config, falling back to defaults."""
    path = Path(CONFIG_FILE)
    if path.is_file():
        with open(path) as f:
            return json.load(f)
    return DEFAULT_CONFIG


def read_heartbeat(filepath):
    """Read heartbeat file. Returns (data_or_None, seconds_ago_or_None)."""
    try:
        with open(filepath) as f:
            data = json.load(f)
        ts = data.get("last_heartbeat") or data.get("timestamp")
        if not ts:
            return None, None
        last = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc).astimezone()
        ago = (now - last).total_seconds()
        return data, round(ago)
    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
        return None, None


def is_quiet_hours(quiet_config):
    """Check if current time falls within quiet hours."""
    now = datetime.now()
    try:
        start_h, start_m = map(int, quiet_config["start"].split(":"))
        end_h, end_m = map(int, quiet_config["end"].split(":"))
        start_minutes = start_h * 60 + start_m
        end_minutes = end_h * 60 + end_m
        now_minutes = now.hour * 60 + now.minute

        if end_minutes < start_minutes:
            # Overnight quiet hours (e.g., 23:00–06:00)
            return now_minutes >= start_minutes or now_minutes < end_minutes
        else:
            return start_minutes <= now_minutes < end_minutes
    except (ValueError, KeyError):
        return False


def alert(message, channel="telegram"):
    """Send alert. Override with actual alert logic."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] ALERT [{channel}]: {message}", file=sys.stderr)
    # TODO: integrate with cc-connect or Telegram bot API


def main():
    config = load_config()
    timeout = config.get("timeout_seconds", 180)
    interval = config.get("check_interval_seconds", 60)
    heartbeat_file = config.get("heartbeat_file", "/tmp/mac-heartbeat.json")
    max_missed = config.get("max_missed_beats", 3)
    quiet = config.get("quiet_hours", {"start": "23:00", "end": "06:00"})

    missed_count = 0
    quiet_alert_sent = False

    print(f"Heartbeat daemon: timeout={timeout}s, interval={interval}s, file={heartbeat_file}")

    while True:
        _, ago = read_heartbeat(heartbeat_file)

        if ago is None:
            missed_count += 1
            print(f"[{datetime.now():%H:%M:%S}] No heartbeat file, missed={missed_count}/{max_missed}")
        elif ago > timeout:
            missed_count += 1
            print(f"[{datetime.now():%H:%M:%S}] Heartbeat stale ({ago}s ago), missed={missed_count}/{max_missed}")
        else:
            if missed_count > 0:
                print(f"[{datetime.now():%H:%M:%S}] Heartbeat recovered ({ago}s ago)")
            missed_count = 0
            quiet_alert_sent = False

        # Alert logic
        if missed_count >= max_missed and config.get("alert_on_missing", True):
            in_quiet = is_quiet_hours(quiet)
            if in_quiet and not quiet_alert_sent:
                alert(f"mac-mini offline for {missed_count} beats (quiet hours)", channel="log")
                quiet_alert_sent = True
            elif not in_quiet:
                alert(f"mac-mini offline for {missed_count} beats ({ago or 0}s since last beat)")

        time.sleep(interval)


if __name__ == "__main__":
    main()
