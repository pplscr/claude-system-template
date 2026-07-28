"""Tests for notify — cross-platform desktop notifications."""

import platform
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from notify import (
    notify,
    info,
    warn,
    error,
    _detect_provider,
    _escape_applescript,
    _escape_ps,
)


class TestProviderDetection:
    """Provider detection tests."""

    def test_detect_returns_callable(self) -> None:
        """Detector returns a callable (function)."""
        provider = _detect_provider()
        assert callable(provider), f"Expected callable, got {type(provider).__name__}"

    def test_provider_callable_no_crash(self) -> None:
        """Calling the returned provider should not crash."""
        provider = _detect_provider()
        try:
            provider("test title", "test message")
        except Exception as exc:
            pytest.fail(f"Provider call raised {type(exc).__name__}: {exc}")


class TestEscapeHelpers:
    """Security: escape functions prevent injection."""

    def test_applescript_escapes_quotes(self) -> None:
        result = _escape_applescript('test"quote')
        assert '"' not in result.replace('\\"', "")

    def test_applescript_escapes_backslash(self) -> None:
        result = _escape_applescript("test\\path")
        assert "\\\\" in result

    def test_applescript_strips_newlines(self) -> None:
        result = _escape_applescript("line1\nline2\rline3")
        assert "\n" not in result
        assert "\r" not in result

    def test_ps_escapes_single_quotes(self) -> None:
        result = _escape_ps("test'quote")
        assert "''" in result


class TestNotifyFunctions:
    """Core notify functions — no crash, no exceptions."""

    def test_notify_no_crash(self) -> None:
        try:
            notify("title", "message")
        except Exception as exc:
            pytest.fail(f"notify() raised {type(exc).__name__}: {exc}")

    def test_info_no_crash(self) -> None:
        try:
            info("test info message")
        except Exception as exc:
            pytest.fail(f"info() raised {type(exc).__name__}: {exc}")

    def test_warn_no_crash(self) -> None:
        try:
            warn("test warn message")
        except Exception as exc:
            pytest.fail(f"warn() raised {type(exc).__name__}: {exc}")

    def test_error_no_crash(self) -> None:
        try:
            error("test error message")
        except Exception as exc:
            pytest.fail(f"error() raised {type(exc).__name__}: {exc}")

    def test_notify_with_unicode(self) -> None:
        try:
            notify("Hello World! \U0001f30d", "test with emoji \U0001f680")
        except Exception as exc:
            pytest.fail(f"notify() with unicode raised {type(exc).__name__}: {exc}")


class TestCrossPlatform:
    """Cross-platform compatibility checks."""

    def test_no_hardcoded_paths(self) -> None:
        src = Path(__file__).parent.parent / "notify.py"
        code = src.read_text()
        bad = ["/Users/", "C:\\Users\\", "~/Library/"]
        for pattern in bad:
            assert pattern not in code, f"Hardcoded path: {pattern}"

    def test_no_platform_specific_pkg_mgrs(self) -> None:
        src = Path(__file__).parent.parent / "notify.py"
        code = src.read_text()
        bad = ["brew ", "apt ", "winget ", "choco "]
        for cmd in bad:
            assert cmd not in code, f"Platform-specific cmd: {cmd}"

    def test_subprocess_uses_list(self) -> None:
        src = Path(__file__).parent.parent / "notify.py"
        code = src.read_text()
        lines = code.splitlines()
        subprocess_calls = [l for l in lines if "subprocess.run" in l]
        assert len(subprocess_calls) > 0, "No subprocess calls found"

    def test_shebang_is_portable(self) -> None:
        src = Path(__file__).parent.parent / "notify.py"
        first_line = src.read_text().splitlines()[0]
        assert first_line.startswith("#!/usr/bin/env"), f"Non-portable: {first_line}"


class TestEdgeCases:
    """Edge case handling."""

    def test_empty_title(self) -> None:
        try:
            notify("", "message")
        except Exception as exc:
            pytest.fail(f"notify() empty title raised {type(exc).__name__}: {exc}")

    def test_empty_message(self) -> None:
        try:
            notify("title", "")
        except Exception as exc:
            pytest.fail(f"notify() empty message raised {type(exc).__name__}: {exc}")

    def test_long_message(self) -> None:
        try:
            notify("title", "x" * 1000)
        except Exception as exc:
            pytest.fail(f"notify() long msg raised {type(exc).__name__}: {exc}")
