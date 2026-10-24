"""Read fal's OpenAPI documents: follow a property's references and unions, and list an object's properties."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..state import Json

# A chain of references longer than this is a loop in the document, not a schema.
_MAX_REFERENCES = 8
# The keys a property keeps over the component its reference names.
_OUTER_KEYS = ('default', 'description', 'title')
# fal writes a field that it leaves unset as an anyOf with this branch.
_NULL_BRANCH: Json = {'type': 'null'}


def find_value(value: Json, *keys: str) -> Json:
    """Follow keys through nested JSON objects; a missing key or a value that is not an object gives None."""
    found = value
    for key in keys:
        found = found.get(key) if isinstance(found, dict) else None
    return found


def _find_inner(schema: dict[str, Json], components: Mapping[str, Json]) -> tuple[dict[str, Json], str | None] | None:
    """Find the schema one reference, a lone allOf, or an anyOf with a null branch stands for; None when none does.

    A reference also gives the name of the component, which shows the kind of an output file.
    """
    reference = schema.get('$ref')
    if isinstance(reference, str):
        name = reference.rsplit('/', 1)[-1]
        target = components.get(name)
        return (target if isinstance(target, dict) else {}), name
    branches = schema.get('allOf')
    if isinstance(branches, list) and len(branches) == 1 and isinstance(branches[0], dict):
        return branches[0], None
    options = schema.get('anyOf')
    if not isinstance(options, list) or _NULL_BRANCH not in options:
        return None
    kept = [option for option in options if option != _NULL_BRANCH]
    single = kept[0] if len(kept) == 1 else None
    return (single, None) if isinstance(single, dict) else ({**schema, 'anyOf': kept}, None)


def read_property(schema: Json, components: Mapping[str, Json]) -> tuple[dict[str, Json], str | None]:
    """Read a property through its references and unions, keeping its own default, description, and title."""
    current = schema if isinstance(schema, dict) else {}
    outer = {key: current[key] for key in _OUTER_KEYS if key in current}
    name: str | None = None
    for _depth in range(_MAX_REFERENCES):
        found = _find_inner(current, components)
        if found is None:
            break
        current = {**found[0], **outer}
        name = found[1] or name
    return current, name


def list_properties(schema: dict[str, Json]) -> list[tuple[str, Json]]:
    """List an object's properties in fal's intended order; properties it leaves out follow as declared."""
    properties = schema.get('properties')
    found = properties if isinstance(properties, dict) else {}
    order = schema.get('x-fal-order-properties')
    named = [name for name in order if isinstance(name, str) and name in found] if isinstance(order, list) else []
    return [(name, found[name]) for name in (*named, *(name for name in found if name not in named))]


__all__ = ['find_value', 'list_properties', 'read_property']
