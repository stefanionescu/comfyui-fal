"""Turn one fal listing entry and its OpenAPI document into what the pack knows about the model.

Nothing here sends a request.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, cast
from dataclasses import replace

from .references import find_value, read_property, list_properties
from ..state.models import FalModel, ModelField, ModelOutput
from ..config.models import (
    CATEGORY_KINDS,
    MODEL_PAGE_URL,
    FIELD_HINT_KINDS,
    TEXT_FIELD_NAMES,
    OUTPUT_FILE_KINDS,
    MEDIA_FIELD_TOKENS,
    OUTPUT_KIND_TOKENS,
    LEFT_OUT_CATEGORIES,
    NON_TEXT_FIELD_NAMES,
    NON_MEDIA_FIELD_TOKENS,
)
from ..config.patterns import FILE_FIELD_PATTERN, DESCRIPTION_PATTERNS

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..state import Json, Kind
    from ..state.models import MediaKind, FieldInput, ListedModel

_FILE_FIELD = re.compile(FILE_FIELD_PATTERN)
_LINK = re.compile(DESCRIPTION_PATTERNS['LINK'])
_MARK = re.compile(DESCRIPTION_PATTERNS['MARK'])
# The JSON types that are each one kind of field.
_SCALAR_INPUTS: dict[str, FieldInput] = {
    'integer': 'integer',
    'number': 'number',
    'boolean': 'boolean',
    'string': 'string',
}
# The path of a model's result, under the model's own path.
_RESULT_PATH = '/requests/{request_id}'


def _choose_value_input(schema: dict[str, Json]) -> tuple[FieldInput, bool]:
    """Choose the kind of a field that is not a file or a fixed value, and whether it takes a list."""
    kind = schema.get('type')
    if isinstance(schema.get('enum'), list):
        return 'enum', False
    if isinstance(kind, str) and kind in _SCALAR_INPUTS:
        return _SCALAR_INPUTS[kind], False
    options = schema.get('anyOf')
    types = [find_value(option, 'type') for option in options] if isinstance(options, list) else []
    if sorted(str(found) for found in types) == ['integer', 'number']:
        return 'number', False
    return 'json', kind == 'array'


def _choose_input(name: str, schema: dict[str, Json], components: Mapping[str, Json]) -> tuple[FieldInput, bool]:
    """Choose a field's kind, and whether it takes a list; the file suffix counts only for text and lists of text."""
    enum = schema.get('enum')
    if 'const' in schema or (isinstance(enum, list) and len(enum) == 1):
        return 'const', False
    if _FILE_FIELD.search(name):
        items = read_property(schema.get('items'), components)[0]
        if schema.get('type') == 'string':
            return 'file', False
        if schema.get('type') == 'array' and items.get('type') == 'string':
            return 'file', True
    return _choose_value_input(schema)


def _find_hint(schema: dict[str, Json]) -> str | None:
    """Find fal's own media hint on a property, its items, or one of its union branches."""
    options = schema.get('anyOf')
    for candidate in (schema, schema.get('items'), *(options if isinstance(options, list) else ())):
        ui = candidate.get('ui') if isinstance(candidate, dict) else None
        hint = ui.get('field') if isinstance(ui, dict) else find_value(candidate, '_fal_ui_field')
        if isinstance(hint, str) and hint in FIELD_HINT_KINDS:
            return hint
    return None


def _choose_media(name: str, raw: dict[str, Json], schema: dict[str, Json]) -> MediaKind | None:
    """Choose a file field's media: fal's own hint first, then the words of its name."""
    hint = _find_hint(raw) or _find_hint(schema)
    if hint is not None:
        return cast('MediaKind | None', FIELD_HINT_KINDS[hint])
    words = set(_FILE_FIELD.sub('', name).split('_'))
    if words & set(NON_MEDIA_FIELD_TOKENS):
        return None
    found = next((kind for kind, tokens in MEDIA_FIELD_TOKENS.items() if words & set(tokens)), None)
    return cast('MediaKind | None', found)


def _read_choices(field_input: FieldInput, schema: dict[str, Json], components: Mapping[str, Json]) -> tuple[Json, ...]:
    """Read a choice's values as fal lists them, or the preset names of a union of presets and objects."""
    enum = schema.get('enum')
    if field_input == 'enum':
        return tuple(enum) if isinstance(enum, list) else ()
    options = schema.get('anyOf')
    for option in options if field_input == 'json' and isinstance(options, list) else ():
        presets = read_property(option, components)[0].get('enum')
        if isinstance(presets, list):
            return tuple(presets)
    return ()


def _read_bounds(schema: dict[str, Json]) -> tuple[float | None, float | None]:
    """Read the bounds of a number; keep an exclusive bound as the bound."""
    bounds: list[float | None] = []
    for inclusive, exclusive in (('minimum', 'exclusiveMinimum'), ('maximum', 'exclusiveMaximum')):
        value = schema.get(inclusive, schema.get(exclusive))
        bounds.append(float(value) if isinstance(value, int | float) and not isinstance(value, bool) else None)
    return bounds[0], bounds[1]


def _describe_type(schema: dict[str, Json], components: Mapping[str, Json]) -> str | None:
    """Write a type as fal's schema does: its type, or a union's types joined by " | " without null; None for none."""
    kind = schema.get('type')
    if isinstance(kind, str):
        return kind
    options = schema.get('anyOf')
    branches = (
        [read_property(option, components)[0].get('type') for option in options] if isinstance(options, list) else []
    )
    names = [str(branch) for branch in branches if isinstance(branch, str) and branch != 'null']
    return ' | '.join(dict.fromkeys(names)) or None


def _describe_field(schema: dict[str, Json]) -> str:
    """Read fal's description, or its title, as plain text: links keep their text, and markup goes."""
    text = schema.get('description') or schema.get('title')
    if not isinstance(text, str):
        return ''
    return ' '.join(_MARK.sub('', _LINK.sub(r'\1', text)).split())


def _build_field(name: str, raw: Json, required: Json, components: Mapping[str, Json]) -> ModelField:
    """Build one input field.

    A file field never keeps the fal default: many defaults are playground samples, which fal runs and bills when the
    request leaves the field out. This function therefore marks a media file field with a default as required and
    drops its default.
    """
    schema = read_property(raw, components)[0]
    field_input, is_list = _choose_input(name, schema, components)
    media = _choose_media(name, raw if isinstance(raw, dict) else {}, schema) if field_input == 'file' else None
    has_sample = media is not None and schema.get('default') is not None
    if field_input == 'const':
        enum = schema.get('enum')
        default = schema.get('const', enum[0] if isinstance(enum, list) and enum else None)
    else:
        default = None if field_input == 'file' else schema.get('default')
    max_items = schema.get('maxItems')
    max_length = schema.get('maxLength')
    return ModelField(
        name,
        field_input,
        _describe_type(schema, components),
        is_list,
        media,
        (isinstance(required, list) and name in required) or has_sample,
        has_sample,
        default,
        _read_choices(field_input, schema, components),
        *_read_bounds(schema),
        max_items if isinstance(max_items, int) and not isinstance(max_items, bool) else None,
        max_length if isinstance(max_length, int) and not isinstance(max_length, bool) else None,
        _describe_field(schema),
    )


def _is_file(schema: dict[str, Json]) -> bool:
    """Say whether a schema is one of fal's file objects, which always require a url."""
    properties = schema.get('properties')
    required = schema.get('required')
    return isinstance(properties, dict) and 'url' in properties and isinstance(required, list) and 'url' in required


def _find_file(
    schema: dict[str, Json], component: str | None, components: Mapping[str, Json]
) -> tuple[bool, str | None]:
    """Say whether a result field carries a file, and the schema name that shows which kind.

    A file can be the field itself, one branch of a union, or one of several files in an object, such as model_urls.
    """
    if _is_file(schema):
        return True, component
    options = schema.get('anyOf')
    for option in options if isinstance(options, list) else ():
        branch, name = read_property(option, components)
        if _is_file(branch):
            return True, name
    properties = schema.get('properties')
    values = properties.values() if isinstance(properties, dict) else ()
    return any(_is_file(read_property(value, components)[0]) for value in values), None


def _build_output(name: str, raw: Json, components: Mapping[str, Json]) -> ModelOutput:
    """Build one result field; take the kind of file it carries from its schema name or the words of its name."""
    schema, component = read_property(raw, components)
    is_list = schema.get('type') == 'array'
    target, target_name = read_property(schema.get('items'), components) if is_list else (schema, component)
    carries, file_name = _find_file(target, target_name, components)
    words = set(name.split('_'))
    named = next((kind for kind, tokens in OUTPUT_KIND_TOKENS.items() if words & set(tokens)), None)
    kind = OUTPUT_FILE_KINDS.get(file_name or '', named) if carries else None
    return ModelOutput(name, _describe_type(schema, components), carries, cast('Kind | None', kind), is_list)


def _choose_text_field(schema: dict[str, Json], inputs: set[str], components: Mapping[str, Json]) -> str | None:
    """Choose the result field that holds the model's text, such as output or text, and never an input's echo.

    Among the string fields in the fal order, a field named like text comes first. Otherwise, the first field that is
    not a status or a language wins, because for Moondream, fal lists finish_reason ahead of the output field.
    """
    names: list[str] = []
    for name, raw in list_properties(schema):
        resolved = read_property(raw, components)[0]
        options = resolved.get('anyOf')
        branches = options if isinstance(options, list) else []
        types = [resolved.get('type'), *(find_value(branch, 'type') for branch in branches)]
        if 'string' in types and name not in inputs:
            names.append(name)
    named = next((name for name in names if name in TEXT_FIELD_NAMES), None)
    return named or next((name for name in names if name not in NON_TEXT_FIELD_NAMES), None)


def _read_model(
    model: FalModel, request: dict[str, Json], result: dict[str, Json], components: Mapping[str, Json]
) -> FalModel:
    """Read the fields, the result fields, the kind, and the text field of a model with a request schema.

    The kind is the first result field that carries a kind of file; else the kind of its fal category; else text when
    the result has a text field. The function leaves out a model that gives none of these.
    """
    schema = read_property(request, components)[0]
    required = schema.get('required')
    fields = tuple(_build_field(name, raw, required, components) for name, raw in list_properties(schema))
    output = read_property(result, components)[0]
    outputs = tuple(_build_output(name, raw, components) for name, raw in list_properties(output))
    text_field = _choose_text_field(output, {field.name for field in fields}, components)
    kind = next((item.kind for item in outputs if item.kind is not None), None)
    kind = kind or cast('Kind | None', CATEGORY_KINDS.get(model.category or '')) or ('text' if text_field else None)
    return replace(
        model,
        kind=kind,
        left_out=None if kind else 'no_output',
        fields=fields,
        outputs=outputs,
        text_field=text_field if kind == 'text' else None,
    )


def _find_schemas(document: Json) -> tuple[dict[str, Json], dict[str, Json], dict[str, Json]] | None:
    """Find the request schema, the result schema, and the components; None when fal published no request schema."""
    paths = find_value(document, 'paths')
    items = list(paths.items()) if isinstance(paths, dict) else []
    request = next(
        (
            find_value(item, 'post', 'requestBody', 'content', 'application/json', 'schema')
            for _path, item in items
            if find_value(item, 'post') is not None
        ),
        None,
    )
    result = next(
        (
            find_value(item, 'get', 'responses', '200', 'content', 'application/json', 'schema')
            for path, item in items
            if path.endswith(_RESULT_PATH)
        ),
        None,
    )
    components = find_value(document, 'components', 'schemas')
    if not isinstance(request, dict):
        return None
    return request, result if isinstance(result, dict) else {}, components if isinstance(components, dict) else {}


def _find_docs_url(entry: ListedModel) -> str:
    """Find the model's page on fal: its API documentation, else its playground, else the model page by its ID."""
    pages = find_value(entry.openapi, 'info', 'x-fal-metadata')
    links = [find_value(pages, key) for key in ('documentationUrl', 'playgroundUrl')]
    return next((link for link in links if isinstance(link, str) and link.startswith('https://')), None) or (
        MODEL_PAGE_URL.format(model_id=entry.endpoint_id)
    )


def parse_model(entry: ListedModel) -> FalModel:
    """Read one listing entry; mark a trainer or a model without a request schema as left out, with its reason."""
    metadata = entry.metadata
    model = FalModel(
        model_id=entry.endpoint_id,
        display_name=metadata.display_name if metadata else entry.endpoint_id,
        description=metadata.description if metadata else '',
        category=metadata.category if metadata else None,
        kind=None,
        left_out=None,
        status=metadata.status if metadata else 'unlisted',
        updated_at=metadata.updated_at if metadata else None,
        docs_url=_find_docs_url(entry),
        fields=(),
        outputs=(),
        text_field=None,
    )
    if model.category in LEFT_OUT_CATEGORIES:
        return replace(model, left_out='training')
    schemas = _find_schemas(entry.openapi)
    return replace(model, left_out='no_schema') if schemas is None else _read_model(model, *schemas)


__all__ = ['parse_model']
