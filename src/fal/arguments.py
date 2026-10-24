"""Build a request input from the prompt, arguments, and files of a paid node, refusing locally what fal misreads.

This module makes every refusal before the pack uploads or pays for anything. fal checks value types, choices, and
ranges: a wrong value comes back as a 422 that names the field, and contract run 10 found such a refusal unbilled.
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
    PROMPT_TWICE,
    FILE_REQUIRED,
    PROMPT_UNUSED,
    FIELD_NOT_FILE,
    FIELD_ONE_FILE,
    FIELD_REQUIRED,
    FIELD_TOO_MANY,
    ARGUMENTS_SHAPE,
    PROMPT_REQUIRED,
    ARGUMENT_UNKNOWN,
    PROMPT_NOT_TAKEN,
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


def _validate_prompt(model: FalModel, arguments: Mapping[str, Json]) -> None:
    """Refuse a prompt the model has no field for, naming its text fields, or one arguments sets too."""
    if _PROMPT in arguments:
        raise FalError(ErrorCode.INVALID_INPUT, PROMPT_TWICE)
    if any(field.name == _PROMPT for field in model.fields):
        return
    texts = [field.name for field in model.fields if field.input == 'string']
    message = PROMPT_UNUSED.format(model=model.model_id, fields=', '.join(texts)) if texts else None
    raise FalError(ErrorCode.INVALID_INPUT, message or PROMPT_NOT_TAKEN.format(model=model.model_id))


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
        raise FalError(ErrorCode.INVALID_INPUT, FIELD_TWICE.format(**names))
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


def parse_arguments(model: FalModel, prompt: str | None, arguments: str | None) -> dict[str, Json]:
    """Make the checks that need no files: the arguments JSON, its field names, and the prompt.

    Returns the prompt first, then the arguments in the person's order. A None text is an input fed by a link, known
    only when the node runs, so its checks wait for then.
    """
    values = _parse_arguments_text(arguments) if arguments is not None else {}
    names = {field.name for field in model.fields}
    unknown = next((name for name in values if name not in names), None)
    if unknown is not None:
        raise FalError(ErrorCode.INVALID_INPUT, ARGUMENT_UNKNOWN.format(model=model.model_id, field=unknown))
    fields: dict[str, Json] = {}
    if prompt is not None and prompt.strip():
        _validate_prompt(model, values)
        fields[_PROMPT] = prompt
    fields.update(values)
    return fields


def build_arguments(model: FalModel, prompt: str, arguments: str, files: Sequence[FalFile]) -> dict[str, FieldValue]:
    """Build the request input by fal field name, and refuse at the first problem before any upload or payment.

    A file field holds one file for a *_url field and a tuple for a *_urls field, as the live fal schema shapes it.
    The request therefore sends one voice clip on a list field as a list.
    """
    fields = parse_arguments(model, prompt, arguments)
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
