#!/usr/bin/env python3
"""JSON Config Validator.

Validates JSON configuration files against a schema specification.
Supports type checking, required keys, and human-readable colored output.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional, Union

# ── Terminal colors ──────────────────────────────────────────────────────────
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[0;33m"
BOLD = "\033[1m"
NC = "\033[0m"  # No Color


class ValidationError:
    """Represents a single validation failure."""

    def __init__(self, path: str, message: str) -> None:
        """Initialize a validation error.

        Args:
            path: JSON path to the problematic field (e.g., "server.port").
            message: Human-readable description of the error.
        """
        self.path = path
        self.message = message

    def __str__(self) -> str:
        """Format error for display."""
        return f"{RED}❌{NC} {BOLD}{self.path}{NC}: {self.message}"


class ValidationWarning:
    """Represents a non-fatal validation warning."""

    def __init__(self, path: str, message: str) -> None:
        """Initialize a validation warning.

        Args:
            path: JSON path to the field.
            message: Human-readable description.
        """
        self.path = path
        self.message = message

    def __str__(self) -> str:
        """Format warning for display."""
        return f"{YELLOW}⚠️{NC}  {BOLD}{self.path}{NC}: {self.message}"


class ValidationResult:
    """Aggregated result of a validation run."""

    def __init__(self, file_path: str) -> None:
        """Initialize a result container.

        Args:
            file_path: Path to the validated file.
        """
        self.file_path = file_path
        self.errors: list[ValidationError] = []
        self.warnings: list[ValidationWarning] = []

    @property
    def is_valid(self) -> bool:
        """True if no errors found."""
        return len(self.errors) == 0

    def add_error(self, path: str, message: str) -> None:
        """Record a validation error."""
        self.errors.append(ValidationError(path, message))

    def add_warning(self, path: str, message: str) -> None:
        """Record a validation warning."""
        self.warnings.append(ValidationWarning(path, message))

    def print_report(self) -> None:
        """Print a human-readable validation report."""
        print(f"\n{BOLD}📋 Validation Report: {self.file_path}{NC}\n")
        print(f"   Errors: {RED}{len(self.errors)}{NC}")
        print(f"   Warnings: {YELLOW}{len(self.warnings)}{NC}")

        if self.errors:
            print(f"\n{BOLD}Errors:{NC}")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print(f"\n{BOLD}Warnings:{NC}")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.is_valid and not self.warnings:
            print(f"\n  {GREEN}✅ Valid — no issues found.{NC}")
        elif self.is_valid:
            print(f"\n  {GREEN}✅ Valid{NC} ({YELLOW}{len(self.warnings)} warning(s){NC})")
        else:
            print(f"\n  {RED}❌ Invalid{NC} — {len(self.errors)} error(s)")

        print()


def _get_type_name(expected_type: str) -> str:
    """Return a human-readable type name."""
    type_map = {
        "string": "str",
        "int": "int",
        "integer": "int",
        "float": "float",
        "number": "float",
        "bool": "bool",
        "boolean": "bool",
        "list": "list",
        "array": "list",
        "dict": "dict",
        "object": "dict",
    }
    return type_map.get(expected_type, expected_type)


def _check_type(value: Any, expected_type: str) -> bool:
    """Check if a value matches the expected JSON Schema type.

    Args:
        value: The value to check.
        expected_type: JSON Schema type name (string, int, bool, list, dict).

    Returns:
        True if the value matches the expected type.
    """
    python_type_map: dict[str, type] = {
        "string": str,
        "int": int,
        "integer": int,
        "float": (int, float),
        "number": (int, float),
        "bool": bool,
        "boolean": bool,
        "list": list,
        "array": list,
        "dict": dict,
        "object": dict,
    }

    expected_python_type = python_type_map.get(expected_type)
    if expected_python_type is None:
        return True  # Unknown types pass

    return isinstance(value, expected_python_type)


def _validate_value(
    value: Any,
    schema: dict[str, Any],
    path: str,
    result: ValidationResult,
) -> None:
    """Recursively validate a value against a schema.

    Args:
        value: The value to validate.
        schema: JSON Schema-like dict with type, required, properties.
        path: Current JSON path for error reporting.
        result: Accumulates errors and warnings.
    """
    expected_type = schema.get("type")
    if expected_type and not _check_type(value, expected_type):
        actual = type(value).__name__
        result.add_error(
            path,
            f"type mismatch: expected {_get_type_name(expected_type)}, got {actual}",
        )
        return

    if expected_type in ("object", "dict") and isinstance(value, dict):
        required_keys: list[str] = schema.get("required", [])
        properties: dict[str, dict[str, Any]] = schema.get("properties", {})

        for key in required_keys:
            if key not in value:
                result.add_error(path, f"missing required key: '{key}'")

        for key, val in value.items():
            child_path = f"{path}.{key}" if path else key
            if key in properties:
                _validate_value(val, properties[key], child_path, result)
            elif not schema.get("additionalProperties", True):
                result.add_warning(
                    child_path,
                    f"unexpected key (schema does not allow additional properties)",
                )

    elif expected_type in ("array", "list") and isinstance(value, list):
        items_schema = schema.get("items")
        if items_schema:
            for idx, item in enumerate(value):
                child_path = f"{path}[{idx}]"
                _validate_value(item, items_schema, child_path, result)


def load_schema(schema_path: Optional[str]) -> Optional[dict[str, Any]]:
    """Load a JSON schema from file.

    Args:
        schema_path: Path to the schema file, or None.

    Returns:
        Parsed schema dict, or None if no schema provided.
    """
    if not schema_path:
        return None

    try:
        with open(schema_path, encoding="utf-8") as f:
            schema = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"{RED}❌ Schema is not valid JSON:{NC} {exc}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"{RED}❌ Schema file not found:{NC} {schema_path}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(schema, dict):
        print(f"{RED}❌ Schema must be a JSON object{NC}", file=sys.stderr)
        sys.exit(1)

    return schema


def validate_file(
    file_path: str,
    schema: Optional[dict[str, Any]] = None,
) -> ValidationResult:
    """Validate a JSON configuration file.

    Args:
        file_path: Path to the JSON file to validate.
        schema: Optional schema dict. If None, only JSON syntax is checked.

    Returns:
        ValidationResult with errors and warnings.
    """
    result = ValidationResult(file_path)

    # ── 1. File exists ──
    path = Path(file_path)
    if not path.exists():
        result.add_error("", f"file not found: {file_path}")
        return result

    # ── 2. Valid JSON ──
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        result.add_error("", f"invalid JSON: {exc}")
        return result

    # ── 3. Schema validation ──
    if schema:
        _validate_value(data, schema, "", result)

    return result


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point for CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv).

    Returns:
        Exit code (0 = valid, 1 = invalid, 2 = error).
    """
    parser = argparse.ArgumentParser(
        prog="validate.py",
        description="Validate JSON configuration files against a schema.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  validate.py config.json
  validate.py config.json --schema schema.json
  validate.py config.json --schema schema.json --quiet""",
    )
    parser.add_argument("file", help="JSON file to validate")
    parser.add_argument("--schema", "-s", help="JSON Schema file (optional)")
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress report, only exit code"
    )
    args = parser.parse_args(argv)

    # ── Load schema ──
    schema: Optional[dict[str, Any]] = None
    if args.schema:
        schema = load_schema(args.schema)

    # ── Validate ──
    result = validate_file(args.file, schema)

    # ── Report ──
    if not args.quiet:
        result.print_report()

    if result.errors:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
