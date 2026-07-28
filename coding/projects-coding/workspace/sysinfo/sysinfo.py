#!/usr/bin/env python3
"""Cross-platform system information reporter.

Works on macOS, Linux, and Windows.
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def get_os_info() -> dict[str, str]:
    """Detect OS name, version, and architecture.

    Returns:
        dict with keys: os, version, arch, machine.
    """
    system = platform.system()
    return {
        "os": system,
        "version": platform.version(),
        "arch": platform.machine(),
        "machine": platform.node(),
    }


def get_ram_total() -> str:
    """Return total RAM as a human-readable string.

    Uses platform-specific approaches:
    - macOS/Linux: sysctl / /proc/meminfo
    - Windows: wmic (fallback: "unknown")
    """
    try:
        if sys.platform == "darwin":
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True, text=True, check=True,
            )
            bytes_total = int(result.stdout.strip())
        elif sys.platform.startswith("linux"):
            with open("/proc/meminfo", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        kb_total = int(line.split()[1])
                        bytes_total = kb_total * 1024
                        break
                else:
                    return "unknown"
        elif sys.platform == "win32":
            result = subprocess.run(
                ["wmic", "ComputerSystem", "get", "TotalPhysicalMemory"],
                capture_output=True, text=True, check=True,
            )
            lines = result.stdout.strip().splitlines()
            bytes_total = int(lines[-1].strip())
        else:
            return "unknown"

        gb = bytes_total / (1024 ** 3)
        return f"{gb:.1f} GB"
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return "unknown"


def get_tool_version(tool: str, args: Optional[list[str]] = None) -> str:
    """Return the version of a CLI tool, or 'not found'."""
    if args is None:
        args = ["--version"]
    path = shutil.which(tool)
    if path is None:
        return "not found"
    try:
        result = subprocess.run(
            [tool, *args],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip().splitlines()[0]
    except subprocess.CalledProcessError:
        return "error"


def get_python_info() -> dict[str, str]:
    """Return Python version and executable path."""
    return {
        "version": sys.version.split()[0],
        "executable": sys.executable,
    }


def main() -> None:
    """Print system information to stdout."""
    os_info = get_os_info()
    ram = get_ram_total()

    print("=" * 50)
    print("  SYSTEM INFO")
    print("=" * 50)
    print(f"  OS      : {os_info['os']} ({os_info['arch']})")
    print(f"  Version : {os_info['version']}")
    print(f"  Host    : {os_info['machine']}")
    print(f"  RAM     : {ram}")
    print("-" * 50)
    print(f"  Python  : {get_python_info()['version']}")
    print(f"  Node.js : {get_tool_version('node')}")
    print(f"  Git     : {get_tool_version('git')}")
    print(f"  Docker  : {get_tool_version('docker')}")
    print("=" * 50)


if __name__ == "__main__":
    main()
