"""Validatore JSON Schema minimo, senza dipendenze.

Copre il sottoinsieme usato da engine/schema/progress.schema.json:
type, properties, required, additionalProperties, items, minItems,
uniqueItems, enum, const, minimum, maximum, minLength, pattern, $ref (#/$defs/...).

Ogni errore ha un percorso leggibile (es. missions[3].done) e un messaggio in italiano.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "integer": int,
    "number": (int, float),
    "null": type(None),
}


@dataclass(frozen=True)
class SchemaError:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path or '(radice)'}: {self.message}"


def _is_type(value, name: str) -> bool:
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if name == "boolean":
        return isinstance(value, bool)
    return isinstance(value, _TYPES[name])


def _type_name(value) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if value is None:
        return "null"
    return type(value).__name__


def _resolve_ref(root: dict, ref: str) -> dict:
    if not ref.startswith("#/"):
        raise ValueError(f"$ref non supportato: {ref}")
    node = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def validate(instance, schema: dict, root: dict | None = None, path: str = "") -> list[SchemaError]:
    """Ritorna la lista degli errori. Lista vuota significa valido."""
    root = root if root is not None else schema
    errors: list[SchemaError] = []

    if "$ref" in schema:
        schema = _resolve_ref(root, schema["$ref"])

    if "type" in schema:
        allowed = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is_type(instance, t) for t in allowed):
            want = " o ".join(allowed)
            errors.append(SchemaError(path, f"deve essere {want}, trovato {_type_name(instance)}"))
            return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(SchemaError(path, f"deve essere esattamente {schema['const']!r}"))
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(SchemaError(path, f"deve essere uno tra {schema['enum']!r}"))

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(SchemaError(path, f"non può essere vuoto (minimo {schema['minLength']} caratteri)"))
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(SchemaError(path, f"{instance!r} non rispetta il formato atteso {schema['pattern']}"))

    if _is_type(instance, "number"):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(SchemaError(path, f"deve essere almeno {schema['minimum']}, trovato {instance}"))
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(SchemaError(path, f"deve essere al massimo {schema['maximum']}, trovato {instance}"))

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(SchemaError(path, f"servono almeno {schema['minItems']} elementi, trovati {len(instance)}"))
        if schema.get("uniqueItems"):
            seen = []
            for i, item in enumerate(instance):
                if item in seen:
                    errors.append(SchemaError(f"{path}[{i}]", f"valore duplicato {item!r}"))
                seen.append(item)
        if "items" in schema:
            for i, item in enumerate(instance):
                errors.extend(validate(item, schema["items"], root, f"{path}[{i}]"))

    if isinstance(instance, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(SchemaError(path, f"manca la chiave obbligatoria \"{key}\""))
        for key, value in instance.items():
            child = f"{path}.{key}" if path else key
            if key in props:
                errors.extend(validate(value, props[key], root, child))
            elif schema.get("additionalProperties") is False:
                known = ", ".join(sorted(props))
                errors.append(SchemaError(child, f"chiave sconosciuta \"{key}\" (ammesse: {known})"))

    return errors
