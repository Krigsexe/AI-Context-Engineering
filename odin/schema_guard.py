from __future__ import annotations

# Validateur JSON ultra-léger :
# - types de base
# - champs requis
# - enums

def validate(obj, schema: dict) -> tuple[bool, list[str]]:
    errors = []
    req = schema.get("required", [])
    for r in req:
        if r not in obj:
            errors.append(f"Missing required: {r}")
    props = schema.get("properties", {})
    for k, v in obj.items():
        if k in props:
            t = props[k].get("type")
            if t and not _is_type(v, t):
                errors.append(f"Wrong type for {k}: expected {t}")
            enum = props[k].get("enum")
            if enum and v not in enum:
                errors.append(f"Invalid value for {k}: {v} not in {enum}")
    return (len(errors) == 0, errors)

def _is_type(v, t: str) -> bool:
    return (
        (t == "string" and isinstance(v, str)) or
        (t == "number" and isinstance(v, (int, float))) or
        (t == "integer" and isinstance(v, int)) or
        (t == "boolean" and isinstance(v, bool)) or
        (t == "array" and isinstance(v, list)) or
        (t == "object" and isinstance(v, dict))
    )
