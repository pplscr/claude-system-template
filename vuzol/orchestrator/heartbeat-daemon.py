#!/usr/bin/env python3
"""
Heartbeat Daemon — OpenClaw HEARTBEAT.md pattern.

Reads config from /root/.claude/agents/heartbeat-config.json.
Loops every check_interval_seconds, matches tasks against current time (±1 min),
runs the script, sends output to Telegram. Respects quiet hours.
"""

import sys, os, json, subprocess, time, logging, signal
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "digest"))
from lib import send_tg, creds

CONFIG_PATH = "/root/.claude/agents/heartbeat-config.json"
LOG_PATH = "/root/scripts/heartbeat.log"


def setup_logging():
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logging.getLogger().addHandler(console)


def load_config():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Config load failed: {e}")
        raise


def in_quiet_hours(cfg, now):
    start_s, end_s = cfg["quiet_hours"]["start"], cfg["quiet_hours"]["end"]
    t = now.time()
    start = datetime.strptime(start_s, "%H:%M").time()
    end = datetime.strptime(end_s, "%H:%M").time()
    if start <= end:
        return start <= t <= end
    return t >= start or t <= end


def day_matches(task, now):
    days = task.get("days", "daily")
    if days == "daily":
        return True
    if days == "weekday":
        return now.weekday() < 5
    if days == "weekend":
        return now.weekday() >= 5
    day_map = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
               "friday": 4, "saturday": 5, "sunday": 6}
    return day_map.get(days) == now.weekday()


def time_matches(schedule, now):
    target = datetime.strptime(schedule, "%H:%M").time()
    diff = abs((now.hour * 60 + now.minute) - (target.hour * 60 + target.minute))
    return diff <= 1


def run_script(script_path):
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True, text=True, timeout=120,
    )
    output = result.stdout
    if result.stderr:
        output += f"\n[STDERR]\n{result.stderr}"
    if result.returncode != 0:
        output += f"\n[EXIT CODE: {result.returncode}]"
    return output


def send_telegram(text, chat_id=None):
    if chat_id is None:
        chat_id = creds().get("TELEGRAM_CHAT_ID")
    if not chat_id:
        logging.error("TELEGRAM_CHAT_ID not found in credentials")
        return False
    ok = send_tg(chat_id, text)
    if not ok:
        logging.warning("Telegram send failed, retrying once in 5s...")
        time.sleep(5)
        chat_id = creds().get("TELEGRAM_CHAT_ID") or chat_id
        ok = send_tg(chat_id, text)
    return ok


def main_loop():
    cfg = load_config()
    interval = cfg.get("check_interval_seconds", 300)
    tz_str = cfg.get("timezone", "Europe/Berlin")

    os.environ["TZ"] = tz_str
    time.tzset()

    logging.info(f"Heartbeat daemon started  interval={interval}s  tz={tz_str}")
    logging.info(f"Tasks: {len(cfg.get('tasks', []))}")

    # Warm up TG chat_id once
    chat_id = creds().get("TELEGRAM_CHAT_ID")
    logging.info(f"Telegram chat_id={'set' if chat_id else 'MISSING'}")

    while True:
        try:
            now = datetime.now()

            if in_quiet_hours(cfg, now):
                time.sleep(interval)
                continue

            for task in cfg.get("tasks", []):
                schedule = task.get("schedule", "")
                script = task.get("script", "")
                task_type = task.get("type", "unknown")

                if not schedule or not script:
                    continue
                if not time_matches(schedule, now) or not day_matches(task, now):
                    continue

                logging.info(f"RUN  {task_type}  schedule={schedule}  script={script}")

                try:
                    output = run_script(script)
                    logging.info(f"OK   {task_type}  output={len(output)} chars")

                    header = f"❤️‍🔥 **{task_type}** ({now.strftime('%H:%M')})"
                    msg = f"{header}\n\n{output[:3500]}"
                    ok = send_telegram(msg, chat_id)
                    logging.info(f"TG   {task_type}  {'OK' if ok else 'FAILED'}")

                except subprocess.TimeoutExpired:
                    logging.error(f"TO   {task_type}  script timed out (>120s)")
                    send_telegram(f"❤️‍🔥 **{task_type}** ⏰ timeout (>120s)", chat_id)

                except FileNotFoundError:
                    logging.error(f"NF   {task_type}  script not found: {script}")
                    send_telegram(f"❤️‍🔥 **{task_type}** ❌ script not found: {script}", chat_id)

                except Exception as e:
                    logging.error(f"ERR  {task_type}  {e}")
                    try:
                        send_telegram(f"❤️‍🔥 **{task_type}** ❌ {e}", chat_id)
                    except Exception:
                        logging.error(f"ERR  {task_type}  notification send also failed")

        except Exception as e:
            logging.error(f"LOOP error: {e}")

        time.sleep(interval)


if __name__ == "__main__":
    setup_logging()
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    try:
        main_loop()
    except KeyboardInterrupt:
        logging.info("Heartbeat daemon stopped (SIGINT)")
    except Exception as e:
        logging.error(f"Fatal: {e}")
        sys.exit(1)
