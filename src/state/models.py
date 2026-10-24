"""What the pack knows about one fal model, read from fal's listing."""

from typing import Literal
from dataclasses import dataclass

from . import Json, Kind, Reply

type MediaKind = Literal['image', 'mask', 'video', 'audio', 'mesh']
type FieldInput = Literal['enum', 'integer', 'number', 'boolean', 'string', 'json', 'file', 'const']
type ModelStatus = Literal['active', 'deprecated', 'unlisted']
type LeftOutReason = Literal['training', 'no_schema', 'no_output']


@dataclass(frozen=True, slots=True)
class ModelField:
    """One input field of a fal model.

    Attributes:
        name: fal's exact field name.
        input: The kind of value: a choice, a number, a boolean, text, JSON, a link, or a fixed value.
        schema_type: The type as fal's schema writes it, a union's types joined by " | " without null; None for none.
        is_list: Whether the field takes a JSON array; for a file field, a list of links.
        media: For a file field, the ComfyUI media it takes; None when its name shows no media, and for other fields.

        required: Whether fal requires it, or it is a media file field whose default is a fal sample.
        has_sample: Whether it is a media file field whose schema default is a fal playground sample.
        default: fal's default as JSON; None when there is none, and for every file field.

        choices: A choice's values exactly as fal lists them, or a preset union's preset names.
        minimum: fal's lower bound for a number.
        maximum: fal's upper bound for a number.
        max_items: fal's largest number of items for a list.
        max_length: fal's longest text, in characters.
        description: fal's description as plain text.

    """

    name: str
    input: FieldInput
    schema_type: str | None
    is_list: bool
    media: MediaKind | None
    required: bool
    has_sample: bool
    default: Json
    choices: tuple[Json, ...]
    minimum: float | None
    maximum: float | None
    max_items: int | None
    max_length: int | None
    description: str


@dataclass(frozen=True, slots=True)
class ModelOutput:
    """One top-level field of a fal model's result.

    Attributes:
        name: fal's exact field name.
        schema_type: The type as fal's schema writes it, a union's types joined by " | " without null; None for none.
        is_file: Whether the field carries a file object, one with a url.
        kind: The kind of file the field carries; None for a field that carries no file, or a file of no known kind.
        is_list: Whether the field holds a list.

    """

    name: str
    schema_type: str | None
    is_file: bool
    kind: Kind | None
    is_list: bool


@dataclass(frozen=True, slots=True)
class FalModel:
    """One fal model as its listing and schema describe it.

    Attributes:
        model_id: The endpoint ID.
        display_name: fal's name for the model.
        description: fal's description of the model.
        category: fal's category, such as text-to-image; None for an unlisted model.
        kind: The kind of node that runs it; None when no node can.
        left_out: Why no node can run it; None when one can.
        status: Active, deprecated, or served but missing from the listing.
        updated_at: When fal last changed the listing entry.
        docs_url: The model's page on fal: its API documentation, else its playground, else its model page.
        fields: The input fields in fal's order.
        outputs: The result's top-level fields in fal's order.
        text_field: For a text model, the result field Text: Generate reads; None otherwise.

    """

    model_id: str
    display_name: str
    description: str
    category: str | None
    kind: Kind | None
    left_out: LeftOutReason | None
    status: ModelStatus
    updated_at: str | None
    docs_url: str
    fields: tuple[ModelField, ...]
    outputs: tuple[ModelOutput, ...]
    text_field: str | None


class ListedMetadata(Reply):
    """The listing's description of one model.

    Attributes:
        display_name: fal's name for the model.
        category: fal's category.
        description: fal's description.
        status: Active or deprecated.
        updated_at: When fal last changed the entry.

    """

    display_name: str
    category: str
    description: str = ''
    status: Literal['active', 'deprecated']
    updated_at: str


class ListedModel(Reply):
    """One entry of fal's model listing, with its OpenAPI document.

    Attributes:
        endpoint_id: The endpoint ID.
        metadata: The listing's description; absent for a model fal serves but does not list.
        openapi: The model's OpenAPI document, or an error object when fal failed to expand it.

    """

    endpoint_id: str
    metadata: ListedMetadata | None = None
    openapi: Json = None


class ListingReply(Reply):
    """A page of fal's model listing.

    Attributes:
        models: The entries on the page.

    """

    models: tuple[ListedModel, ...]


__all__ = ['FalModel', 'ListedMetadata', 'ListedModel', 'ListingReply', 'ModelField', 'ModelOutput']
