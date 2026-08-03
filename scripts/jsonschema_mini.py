#!/usr/bin/env python3
"""A tiny, dependency-free JSON Schema checker for the subset Tashtit uses.

Tashtit runs with no third-party dependencies, so it cannot rely on a full
JSON Schema library. This module implements only the keywords used by the
schemas in `schemas/`: type, enum, pattern, required, properties,
additionalProperties, items, minItems, uniqueItems, minLength, $ref (local
`#/$defs/...` only), and $defs. It raises on any schema keyword it does not
understand, so an unsupported schema fails loudly instead of passing silently.

`validate.py` uses this to check scenario and acceptance files against their
published schemas. Cross-file rules (uniqueness across plugins, sorting, and the
maturity gate) remain in `validate.py`; this module only enforces per-document
structure so the schema files are the canonical structural contract.
"""

from __future__ import annotations

import re
from typing import Any


SUPPORTED_KEYWORDS = {
    "$schema",
    "$id",
    "$ref",
    "$defs",
    "title",
    "description",
    "type",
    "enum",
    "pattern",
    "required",
    "properties",
    "additionalProperties",
    "items",
    "minItems",
    "uniqueItems",
    "minLength",
}

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "number": (int, float),
    "integer": int,
    "null": type(None),
}


class SchemaError(ValueError):
    """Raised when a schema itself uses an unsupported construct."""


def _resolve(root: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise SchemaError(f"only local refs are supported, got {ref!r}")
    node: Any = root
    for token in ref[2:].split("/"):
        if not isinstance(node, dict) or token not in node:
            raise SchemaError(f"unresolvable ref: {ref}")
        node = node[token]
    if not isinstance(node, dict):
        raise SchemaError(f"ref does not point to a schema: {ref}")
    return node


def _check_type(value: Any, expected: str, path: str, errors: list[str]) -> bool:
    if expected not in _TYPES:
        raise SchemaError(f"unsupported type {expected!r}")
    # bool is a subclass of int; keep them distinct for JSON semantics.
    if expected == "integer" and isinstance(value, bool):
        errors.append(f"{path}: expected integer, got boolean")
        return False
    if expected == "number" and isinstance(value, bool):
        errors.append(f"{path}: expected number, got boolean")
        return False
    if not isinstance(value, _TYPES[expected]):
        errors.append(f"{path}: expected {expected}")
        return False
    return True


def _validate(
    value: Any,
    schema: dict[str, Any],
    root: dict[str, Any],
    path: str,
    errors: list[str],
) -> None:
    unsupported = set(schema) - SUPPORTED_KEYWORDS
    if unsupported:
        raise SchemaError(f"unsupported schema keywords: {sorted(unsupported)}")

    if "$ref" in schema:
        _validate(value, _resolve(root, schema["$ref"]), root, path, errors)
        return

    declared_type = schema.get("type")
    if isinstance(declared_type, str):
        if not _check_type(value, declared_type, path, errors):
            return

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']}")

    if "pattern" in schema and isinstance(value, str):
        if not re.search(schema["pattern"], value):
            errors.append(f"{path}: {value!r} does not match {schema['pattern']!r}")

    if "minLength" in schema and isinstance(value, str):
        if len(value) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems {schema['minItems']}")
        if schema.get("uniqueItems") and len(value) != len(
            {repr(item) for item in value}
        ):
            errors.append(f"{path}: items are not unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _validate(item, item_schema, root, f"{path}[{index}]", errors)

    if isinstance(value, dict):
        for field in schema.get("required", []):
            if field not in value:
                errors.append(f"{path}: missing required field {field!r}")
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            if key in properties:
                _validate(item, properties[key], root, f"{path}.{key}", errors)
            elif additional is False:
                errors.append(f"{path}: unexpected field {key!r}")


def validate_instance(value: Any, schema: dict[str, Any]) -> list[str]:
    """Return a list of human-readable validation errors ([] means valid)."""
    errors: list[str] = []
    _validate(value, schema, schema, "$", errors)
    return errors
