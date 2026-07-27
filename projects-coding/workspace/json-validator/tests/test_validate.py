"""Tests for JSON Config Validator."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validate import ValidationResult, validate_file


def _write_temp(name: str, content: str) -> str:
    """Write content to a temp file and return path."""
    tmp = Path(tempfile.gettempdir()) / f"test-{name}"
    tmp.write_text(content, encoding="utf-8")
    return str(tmp)


def test_valid_json_no_schema() -> None:
    """Valid JSON without schema should pass."""
    path = _write_temp("valid.json", json.dumps({"host": "localhost", "port": 8080}))
    result = validate_file(path)
    assert result.is_valid, f"Expected valid, got errors: {result.errors}"
    assert len(result.errors) == 0


def test_invalid_json_syntax() -> None:
    """Invalid JSON syntax should fail."""
    path = _write_temp("invalid.json", "{bad json")
    result = validate_file(path)
    assert not result.is_valid
    assert any("invalid JSON" in e.message for e in result.errors)


def test_missing_required_key() -> None:
    """Schema with required keys should detect missing ones."""
    path = _write_temp("missing-key.json", json.dumps({"host": "localhost"}))
    schema = {
        "type": "object",
        "required": ["host", "port"],
        "properties": {
            "host": {"type": "string"},
            "port": {"type": "int"},
        },
    }
    result = validate_file(path, schema)
    assert not result.is_valid
    assert any("missing required key: 'port'" in e.message for e in result.errors)


def test_type_mismatch() -> None:
    """Type mismatch should be detected."""
    path = _write_temp(
        "type-mismatch.json",
        json.dumps({"host": "localhost", "port": "8080"}),
    )
    schema = {
        "type": "object",
        "required": ["host", "port"],
        "properties": {
            "host": {"type": "string"},
            "port": {"type": "int"},
        },
    }
    result = validate_file(path, schema)
    assert not result.is_valid
    assert any("type mismatch" in e.message.lower() for e in result.errors)


def test_all_valid_with_schema() -> None:
    """Fully compliant JSON should pass schema validation."""
    path = _write_temp(
        "all-valid.json",
        json.dumps({"host": "localhost", "port": 8080, "debug": False}),
    )
    schema = {
        "type": "object",
        "required": ["host", "port"],
        "properties": {
            "host": {"type": "string"},
            "port": {"type": "int"},
            "debug": {"type": "bool"},
        },
    }
    result = validate_file(path, schema)
    assert result.is_valid, f"Expected valid: {result.errors}"


def test_file_not_found() -> None:
    """Non-existent file should error."""
    result = validate_file("/tmp/nonexistent-file-12345.json")
    assert not result.is_valid
    assert any("file not found" in e.message for e in result.errors)


def test_nested_objects() -> None:
    """Nested object schema should validate recursively."""
    path = _write_temp(
        "nested.json",
        json.dumps({
            "server": {"host": "0.0.0.0", "port": 443},
            "logging": {"level": "info"},
        }),
    )
    schema = {
        "type": "object",
        "required": ["server"],
        "properties": {
            "server": {
                "type": "object",
                "required": ["host", "port"],
                "properties": {
                    "host": {"type": "string"},
                    "port": {"type": "int"},
                },
            },
            "logging": {
                "type": "object",
                "properties": {"level": {"type": "string"}},
            },
        },
    }
    result = validate_file(path, schema)
    assert result.is_valid, f"Expected valid: {result.errors}"


def test_array_items_validation() -> None:
    """Array items should be validated against items schema."""
    path = _write_temp(
        "array.json",
        json.dumps({"ports": [8080, 8443]}),
    )
    schema = {
        "type": "object",
        "properties": {
            "ports": {
                "type": "array",
                "items": {"type": "int"},
            },
        },
    }
    result = validate_file(path, schema)
    assert result.is_valid, f"Expected valid: {result.errors}"


def run_all() -> int:
    """Run all tests and return exit code."""
    tests = [
        ("valid JSON (no schema)", test_valid_json_no_schema),
        ("invalid JSON syntax", test_invalid_json_syntax),
        ("missing required key", test_missing_required_key),
        ("type mismatch (str vs int)", test_type_mismatch),
        ("all valid with schema", test_all_valid_with_schema),
        ("file not found", test_file_not_found),
        ("nested objects", test_nested_objects),
        ("array items validation", test_array_items_validation),
    ]

    passed = 0
    failed = 0

    print("\n🧪 Running tests...\n")
    for name, fn in tests:
        try:
            fn()
            print(f"  {name:40s} ✅ PASS")
            passed += 1
        except AssertionError as exc:
            print(f"  {name:40s} ❌ FAIL: {exc}")
            failed += 1
        except Exception as exc:
            print(f"  {name:40s} 💥 ERROR: {exc}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all())
