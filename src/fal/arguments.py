"""Build a request input from the text inputs, named settings, arguments, and files of a paid node.

This module makes every refusal before the pack uploads or pays for anything, and refuses locally what fal misreads.
fal checks value types, choices, and ranges: a wrong value comes back as a 422 that names the field, and contract run 10
found such a refusal unbilled.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..state.errors import FalError, ErrorCode
from ..state.parsing import parse_json
from ..config.messages.inputs import (
    FIELD_MEDIA,
    FIELD_TWICE,
    FILE_SAMPLE,
    JSON_SHAPES,
    MEDIA_NAMES,
    TEXT_UNUSED,
    FILE_REQUIRED,
    FIELD_NOT_FILE,
    FIELD_ONE_FILE,
    FIELD_REQUIRED,
    FIELD_TOO_MANY,
    TEXT_NOT_TAKEN,
    ARGUMENTS_SHAPE,
    PROMPT_REQUIRED,
    SETTING_UNKNOWN,
    ARGUMENT_UNKNOWN,
    ARGUMENTS_INVALID,
    FILE_FIELD_MISSING,
    FILE_FIELD_UNKNOWN,
)
from ..config.messages.requests import JSON_SYNTAX

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ..state import Json
    from ..state.files import FalFile, FieldValue
    from ..state.models import FalModel, ModelField

# The name of the field the prompt input fills.
_PROMPT = 'prompt'
# How a refusal names a JSON value by its Python type; bool comes before int, which it subclasses.
_SHAPES: tuple[tuple[type, str], ...] = ((bool, 'boolean'), (list, 'array'), (str, 'string'), (int, 'number'))


def _parse_arguments_text(text: str) -> dict[str, Json]:
    """Read the arguments box as one JSON object; empty text is an empty object."""
    if not text.strip():
        return {}
    try:
        value = parse_json(text)
    except FalError as error:
        if str(error) != JSON_SYNTAX:
            raise
        raise FalError(ErrorCode.INVALID_INPUT, ARGUMENTS_INVALID.format()) from None
    if not isinstance(value, dict):
        shape = next(
            (name for kind, name in _SHAPES if isinstance(value, kind)), 'number' if value is not None else 'null'
        )
        raise FalError(ErrorCode.INVALID_INPUT, ARGUMENTS_SHAPE.format(shape=JSON_SHAPES[shape]))
    return value


def _add_text(model: FalModel, name: str, text: str, values: dict[str, Json]) -> None:
    """Add one text input under its own name, refusing an input the model has no field for, or one arguments sets."""
    model_id = model.model_id
    if name in values:
        raise FalError(ErrorCode.INVALID_INPUT, FIELD_TWICE.format(field=name, source=f'the {name} input'))
    if not any(field.name == name for field in model.fields):
        texts = [field.name for field in model.fields if field.input == 'string']
        message = TEXT_UNUSED.format(model=model_id, field=name, fields=', '.join(texts)) if texts else None
        raise FalError(ErrorCode.INVALID_INPUT, message or TEXT_NOT_TAKEN.format(model=model_id, field=name))
    values[name] = text


def _add_setting(field: ModelField | None, name: str, value: Json, values: dict[str, Json], model_id: str) -> None:
    """Add one named setting under its own name, as the type the field of the model takes.

    A number goes as text to a field that takes only text, such as a duration that fal lists as the text 5.
    """
    if field is None:
        raise FalError(ErrorCode.INVALID_INPUT, SETTING_UNKNOWN.format(model=model_id, field=name))
    if name in values:
        raise FalError(ErrorCode.INVALID_INPUT, FIELD_TWICE.format(field=name, source=f'the {name} input'))
    types = set((field.schema_type or '').split(' | '))
    is_text_only = 'string' in types and not types & {'integer', 'number'}
    values[name] = str(value) if is_text_only and isinstance(value, int) and not isinstance(value, bool) else value


def _validate_count(model: FalModel, field: ModelField, count: int) -> None:
    """Refuse more than one file on a single field, and more files than a list field takes."""
    maximum = field.max_items
    if not field.is_list and count > 1:
        raise FalError(ErrorCode.INVALID_INPUT, FIELD_ONE_FILE.format(field=field.name, count=count))
    if maximum is not None and count > maximum:
        extra = count - maximum
        text = FIELD_TOO_MANY.format(field=field.name, maximum=maximum, model=model.model_id, count=count, extra=extra)
        raise FalError(ErrorCode.INVALID_INPUT, text)


def _validate_file(model: FalModel, field: ModelField | None, file: FalFile, arguments: Mapping[str, Json]) -> None:
    """Refuse a file for a field the model lacks, that takes no file, that arguments sets, or of the wrong media."""
    names = {'model': model.model_id, 'field': file.field}
    if field is None:
        raise FalError(ErrorCode.INVALID_INPUT, FILE_FIELD_UNKNOWN.format(**names))
    if field.input != 'file':
        raise FalError(ErrorCode.INVALID_INPUT, FIELD_NOT_FILE.format(**names))
    if field.name in arguments:
        raise FalError(ErrorCode.INVALID_INPUT, FIELD_TWICE.format(field=field.name, source='File: Add'))
    media = field.media
    # A link is fal's to check; a local file must be the field's media, and a mask field also takes an image.
    if file.url is None and media is not None and file.kind not in {media, 'image' if media == 'mask' else media}:
        text = FIELD_MEDIA.format(
            field=field.name, media=MEDIA_NAMES[media], other=MEDIA_NAMES.get(file.kind, file.kind)
        )
        raise FalError(ErrorCode.INVALID_INPUT, text)


def _build_file_groups(
    model: FalModel, files: Sequence[FalFile], arguments: Mapping[str, Json]
) -> dict[str, tuple[FalFile, ...]]:
    """Group File: Add's files by the field each names, in the order they arrived, checking each against the model."""
    fields = {field.name: field for field in model.fields}
    groups: dict[str, list[FalFile]] = {}
    for file in files:
        if file.field is None:
            raise FalError(ErrorCode.INVALID_INPUT, FILE_FIELD_MISSING)
        _validate_file(model, fields.get(file.field), file, arguments)
        groups.setdefault(file.field, []).append(file)
    for name, items in groups.items():
        _validate_count(model, fields[name], len(items))
    return {name: tuple(items) for name, items in groups.items()}


def _build_file_value(model: FalModel, field: ModelField, value: Json) -> Json:
    """Put a link typed in arguments in the shape fal reads: a list for a list field, one link for a single one."""
    if field.is_list and isinstance(value, str):
        value = [value]
    if not field.is_list and isinstance(value, list) and len(value) == 1:
        value = value[0]
    _validate_count(model, field, len(value) if isinstance(value, list) else 1)
    return value


def _describe_missing(model: FalModel, field: ModelField) -> str:
    """Say what a required field nothing sets needs: a prompt, a file, or a value in arguments."""
    names = {'model': model.model_id, 'field': field.name}
    if field.name == _PROMPT:
        return PROMPT_REQUIRED.format(**names)
    if field.input != 'file':
        return FIELD_REQUIRED.format(**names)
    return (FILE_SAMPLE if field.has_sample else FILE_REQUIRED).format(**names)


def _find_constants(model: FalModel, fields: Mapping[str, object]) -> dict[str, Json]:
    """Refuse a required field nothing sets, and return each required fixed field with the value the request sends."""
    constants: dict[str, Json] = {}
    for field in model.fields:
        if not field.required or field.name in fields:
            continue
        if field.input != 'const':
            raise FalError(ErrorCode.INVALID_INPUT, _describe_missing(model, field))
        constants[field.name] = field.default
    return constants


def parse_arguments(
    model: FalModel, texts: Mapping[str, str | None], settings: Mapping[str, Json], arguments: str | None
) -> dict[str, Json]:
    """Make the checks that need no files: the arguments JSON, its field names, the text inputs, and the settings.

    A None text or arguments is an input fed by a link, known only when the node runs, so its checks wait for then.
    Returns the arguments first, then the text inputs and the named settings.
    """
    values = _parse_arguments_text(arguments) if arguments is not None else {}
    fields = {field.name: field for field in model.fields}
    unknown = next((name for name in values if name not in fields), None)
    if unknown is not None:
        raise FalError(ErrorCode.INVALID_INPUT, ARGUMENT_UNKNOWN.format(model=model.model_id, field=unknown))
    for name, text in texts.items():
        if text is not None and text.strip():
            _add_text(model, name, text, values)
    for name, value in settings.items():
        _add_setting(fields.get(name), name, value, values, model.model_id)
    return values


def build_arguments(
    model: FalModel,
    texts: Mapping[str, str],
    settings: Mapping[str, Json],
    arguments: str,
    files: Sequence[FalFile],
) -> dict[str, FieldValue]:
    """Build the request input by fal field name, and refuse at the first problem before any upload or payment.

    A file field holds one file for a *_url field and a tuple for a *_urls field, as the live fal schema shapes it.
    The request therefore sends one voice clip on a list field as a list.
    """
    fields = parse_arguments(model, texts, settings, arguments)
    groups = _build_file_groups(model, files, fields)
    shapes = {field.name: field for field in model.fields if field.input == 'file'}
    values: dict[str, FieldValue] = {
        name: _build_file_value(model, shapes[name], value) if name in shapes else value
        for name, value in fields.items()
    }
    for name, items in groups.items():
        values[name] = items if shapes[name].is_list else items[0]
    values.update(_find_constants(model, values))
    return values


__all__ = ['build_arguments', 'parse_arguments']
