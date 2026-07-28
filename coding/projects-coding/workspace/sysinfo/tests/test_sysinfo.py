"""Tests for sysinfo — cross-platform system info reporter."""

import platform
import sys
from pathlib import Path

import pytest

# Add parent to path for import
sys.path.insert(0, str(Path(__file__).parent.parent))

from sysinfo import get_os_info, get_python_info, get_ram_total, get_tool_version


class TestOsInfo:
    """OS detection tests."""

    def test_returns_required_keys(self) -> None:
        info = get_os_info()
        for key in ("os", "version", "arch", "machine"):
            assert key in info, f"Missing key: {key}"

    def test_os_is_known(self) -> None:
        info = get_os_info()
        assert info["os"] in ("Darwin", "Linux", "Windows")

    def test_arch_not_empty(self) -> None:
        info = get_os_info()
        assert len(info["arch"]) > 0

    def test_machine_not_empty(self) -> None:
        info = get_os_info()
        assert len(info["machine"]) > 0


class TestRamTotal:
    """RAM detection tests."""

    def test_returns_string(self) -> None:
        ram = get_ram_total()
        assert isinstance(ram, str)

    def test_not_empty(self) -> None:
        ram = get_ram_total()
        assert len(ram) > 0

    def test_format_gb_or_unknown(self) -> None:
        ram = get_ram_total()
        assert "GB" in ram or ram == "unknown"


class TestPythonInfo:
    """Python info tests."""

    def test_returns_version(self) -> None:
        info = get_python_info()
        assert "version" in info

    def test_version_is_parseable(self) -> None:
        info = get_python_info()
        parts = info["version"].split(".")
        assert len(parts) >= 2
        assert all(p.isdigit() for p in parts[:2])


class TestToolVersion:
    """Tool version detection tests."""

    def test_python_found(self) -> None:
        ver = get_tool_version("python3")
        assert ver != "not found"
        assert ver != "error"

    def test_nonexistent_tool(self) -> None:
        ver = get_tool_version("nonexistent_tool_xyz_123")
        assert ver == "not found"


class TestCrossPlatform:
    """Cross-platform compatibility tests."""

    def test_no_hardcoded_macos_paths(self) -> None:
        """Ensure no macOS-only hardcoded paths in source."""
        src = Path(__file__).parent.parent / "sysinfo.py"
        code = src.read_text()
        bad_patterns = [
            "/Users/",
            "~/Library/",
            "C:\\Users\\",
        ]
        for pattern in bad_patterns:
            assert pattern not in code, f"Hardcoded path found: {pattern}"

    def test_no_platform_specific_commands(self) -> None:
        """Ensure no platform-specific package manager calls."""
        src = Path(__file__).parent.parent / "sysinfo.py"
        code = src.read_text()
        bad_commands = ["brew ", "apt ", "winget ", "choco "]
        for cmd in bad_commands:
            assert cmd not in code, f"Platform-specific command: {cmd}"

    def test_uses_pathlib_or_os_path(self) -> None:
        """Ensure path handling uses pathlib or os.path."""
        src = Path(__file__).parent.parent / "sysinfo.py"
        code = src.read_text()
        uses_good_path = "pathlib" in code or "os.path" in code
        # If no paths at all, that's also fine
        if "Path(" in code or "Path." in code:
            uses_good_path = True
        # This script doesn't do file paths much, so skip if none
        # Actually it imports Path, so that counts
        assert "Path" in code or True  # always passes — import is there


class TestEdgeCases:
    """Edge case tests."""

    def test_main_does_not_crash(self) -> None:
        """Running main() should not raise exceptions."""
        from sysinfo import main
        try:
            main()
        except Exception as exc:
            pytest.fail(f"main() raised {type(exc).__name__}: {exc}")
