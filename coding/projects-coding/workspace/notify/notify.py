#!/usr/bin/env python3
"""Cross-platform desktop notifications.

Supports macOS (osascript), Linux (notify-send/zenity), and Windows (PowerShell
Toast). Falls back to print() when no native tool is available. No external
dependencies — stdlib only.

Usage:
    from notify import notify, info, warn, error

    notify("Deploy", "v1.2.3 deployed to staging")
    info("Server started on port 8080")
    warn("Disk usage at 85%")
    error("Connection refused — retrying...")

CLI:
    python3 notify.py "Title" "Message"
    python3 notify.py "Disk" "Almost full" --level warn
"""

from __future__ import annotations

import argparse
import logging
import platform
import shutil
import subprocess
import sys
from typing import Callable, Optional

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# ---------------------------------------------------------------------------
# Provider cache — detected once per session
# ---------------------------------------------------------------------------

_PROVIDER: Optional[Callable[[str, str], None]] = None


# ---------------------------------------------------------------------------
# Escape helpers (security: prevents injection in shell commands)
# ---------------------------------------------------------------------------

def _escape_applescript(text: str) -> str:
    """Escape text for safe inclusion in an AppleScript string literal.

    Args:
        text: Raw text to escape.

    Returns:
        Escaped text safe for AppleScript double-quoted strings.
    """
    # Remove control characters that would break the -e argument.
    sanitised = text.replace("\n", " ").replace("\r", "")
    return sanitised.replace("\\", "\\\\").replace('"', '\\"')


def _escape_ps(text: str) -> str:
    """Escape text for safe inclusion in a PowerShell single-quoted string.

    Args:
        text: Raw text to escape.

    Returns:
        Escaped text safe for PowerShell single-quoted strings.
    """
    return text.replace("'", "''")


# ---------------------------------------------------------------------------
# Platform-specific senders
# ---------------------------------------------------------------------------

def _send_macos(title: str, message: str) -> None:
    """Send a notification via osascript on macOS.

    Args:
        title: Notification title.
        message: Notification body.
    """
    script = (
        f'display notification "{_escape_applescript(message)}"'
        f' with title "{_escape_applescript(title)}"'
    )
    cmd = ["osascript", "-e", script]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        logger.warning("osascript not found — falling back to print()")
        _send_fallback(title, message)
    except subprocess.SubprocessError as exc:
        logger.warning("osascript failed: %s — falling back to print()", exc)
        _send_fallback(title, message)


def _send_linux_notify_send(title: str, message: str) -> None:
    """Send a notification via notify-send on Linux.

    Args:
        title: Notification title.
        message: Notification body.
    """
    cmd = ["notify-send", title, message]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        logger.warning("notify-send not found — trying zenity")
        _send_linux_zenity(title, message)
    except subprocess.SubprocessError as exc:
        logger.warning("notify-send failed: %s — falling back to print()", exc)
        _send_fallback(title, message)


def _send_linux_zenity(title: str, message: str) -> None:
    """Send a notification via zenity on Linux (fallback for notify-send).

    Args:
        title: Notification title.
        message: Notification body.
    """
    cmd = ["zenity", "--notification", "--text", f"{title}\n{message}"]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        logger.warning("zenity not found — falling back to print()")
        _send_fallback(title, message)
    except subprocess.SubprocessError as exc:
        logger.warning("zenity failed: %s — falling back to print()", exc)
        _send_fallback(title, message)


def _send_windows(title: str, message: str) -> None:
    """Send a notification via PowerShell Toast on Windows.

    Uses the Windows.UI.Notifications API to show a native toast.

    Args:
        title: Notification title.
        message: Notification body.
    """
    ps_script = (
        "$null = [Windows.UI.Notifications.ToastNotificationManager, "
        "Windows.UI.Notifications, ContentType = WindowsRuntime];"
        "$tpl = [Windows.UI.Notifications.ToastNotificationManager]"
        "::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]"
        "::ToastText02]);"
        f"$tpl.GetElementsByTagName('text')[0].AppendChild("
        f"$tpl.CreateTextNode('{_escape_ps(title)}')) | Out-Null;"
        f"$tpl.GetElementsByTagName('text')[1].AppendChild("
        f"$tpl.CreateTextNode('{_escape_ps(message)}')) | Out-Null;"
        "$toast = [Windows.UI.Notifications.ToastNotification]::new($tpl);"
        "$appId = 'Python Notify';"
        "[Windows.UI.Notifications.ToastNotificationManager]"
        "::CreateToastNotifier($appId).Show($toast)"
    )
    cmd = ["powershell", "-NoProfile", "-Command", ps_script]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        logger.warning("powershell not found — falling back to print()")
        _send_fallback(title, message)
    except subprocess.SubprocessError as exc:
        logger.warning("PowerShell toast failed: %s — falling back to print()", exc)
        _send_fallback(title, message)


def _send_fallback(title: str, message: str) -> None:
    """Fallback notification — prints to stderr.

    Args:
        title: Notification title.
        message: Notification body.
    """
    print(f"[{title}] {message}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Provider detection
# ---------------------------------------------------------------------------

def _detect_provider() -> Callable[[str, str], None]:
    """Detect the appropriate notification handler for the current OS.

    Checks for available tools in PATH and returns the best-matching sender
    function.  Falls back to ``_send_fallback`` when no native tool is found.

    Returns:
        A callable ``(title: str, message: str) -> None``.
    """
    system = platform.system()

    if system == "Darwin":
        if shutil.which("osascript"):
            logger.debug("Provider: macOS / osascript")
            return _send_macos
    elif system == "Linux":
        if shutil.which("notify-send"):
            logger.debug("Provider: Linux / notify-send")
            return _send_linux_notify_send
        if shutil.which("zenity"):
            logger.debug("Provider: Linux / zenity (fallback)")
            return _send_linux_zenity
    elif system == "Windows":
        if shutil.which("powershell"):
            logger.debug("Provider: Windows / PowerShell Toast")
            return _send_windows

    logger.warning(
        "No native notification tool detected on %s — using print() fallback",
        system,
    )
    return _send_fallback


def _get_provider() -> Callable[[str, str], None]:
    """Return the cached notification provider, detecting it once.

    Returns:
        The active notification handler callable.
    """
    global _PROVIDER
    if _PROVIDER is None:
        _PROVIDER = _detect_provider()
    return _PROVIDER


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def notify(title: str, message: str) -> None:
    """Send a cross-platform desktop notification.

    Detects the OS automatically and uses the best available native
    notification mechanism.  Falls back to ``print()`` on stderr when no
    native tool is installed.

    Args:
        title: Notification title.
        message: Notification body text.

    Examples:
        >>> notify("Build", "Compilation completed successfully")
        >>> notify("CI/CD", "Pipeline #42 passed")
    """
    _get_provider()(title, message)


def info(msg: str) -> None:
    """Send an informational notification (ℹ️ prefix).

    Args:
        msg: The informational message.
    """
    notify("ℹ️ Info", msg)


def warn(msg: str) -> None:
    """Send a warning notification (⚠️ prefix).

    Args:
        msg: The warning message.
    """
    notify("⚠️ Warning", msg)


def error(msg: str) -> None:
    """Send an error notification (❌ prefix).

    Args:
        msg: The error message.
    """
    notify("❌ Error", msg)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI entry point for cross-platform desktop notifications.

    Usage::

        python3 notify.py "Title" "Message"
        python3 notify.py "Disk" "Almost full" --level warn

    Enable verbose logging with ``-v``.
    """
    parser = argparse.ArgumentParser(
        description="Send cross-platform desktop notifications",
    )
    parser.add_argument(
        "title",
        help="Notification title",
    )
    parser.add_argument(
        "message",
        nargs="?",
        default="",
        help="Notification message (optional when --level is used)",
    )
    parser.add_argument(
        "--level",
        choices=["info", "warn", "error"],
        default=None,
        help="Predefined notification level (sets title automatically)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(levelname)s:%(name)s: %(message)s",
        )

    if args.level == "info":
        info(args.message)
    elif args.level == "warn":
        warn(args.message)
    elif args.level == "error":
        error(args.message)
    else:
        notify(args.title, args.message)


if __name__ == "__main__":
    main()
