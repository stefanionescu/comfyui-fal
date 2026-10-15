"""The image workflows: design a host and pose them again, cut out a product, and make a poster series."""

from __future__ import annotations

import json
from scripts.nodes.host import HostNode
from src.config.namespace import NODE_PREFIX
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.config import STAGE_COLOUR, IMAGE_PREVIEW
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.descriptions.nodes import FILE_ADD, IMAGE_GENERATE

SUNBURST = "openai/gpt-image-2.5/sunburst/text-to-image"
SUNBURST_EDIT = "openai/gpt-image-2.5/sunburst/edit"
TOPAZ_PRECISION = "topaz/upscale/image/precision"
BRIA_EXTRACT = "bria/extract-object"
SEEDREAM_LITE = "bytedance/seedream/v5/lite/text-to-image"
DESIGN_ARGUMENTS = json.dumps({"image_size": "portrait_4_3", "quality": "high"}, indent=2)
TURN_ARGUMENTS = json.dumps({"quality": "high"}, indent=2)
UPSCALE_ARGUMENTS = json.dumps({"upscale_factor": 2, "output_format": "png"}, indent=2)
SERIES_ARGUMENTS = json.dumps({"image_size": "portrait_4_3", "max_images": 4}, indent=2)
TURN_PROMPT = "The same host in a three-quarter view, waving at the camera, with the same outfit, hair, and background."
HOST_TEXTS = WORKFLOW_TEXTS["image-01-design-a-host"]
CUT_OUT_TEXTS = WORKFLOW_TEXTS["image-02-cut-out-a-product"]
SERIES_TEXTS = WORKFLOW_TEXTS["image-03-make-a-poster-series"]

DESIGN = Subgraph(
    name=SHARED_TEXTS["design"],
    nodes=(
        Node(
            "prompt",
            HostNode.FORMAT,
            {
                "f_string": (
                    "Studio portrait of a live-shopping host: {a} Waist up, facing the camera, plain light gray "
                    "background, soft light."
                )
            },
        ),
        Node("draw", IMAGE_GENERATE, {"model": SUNBURST, "arguments": DESIGN_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_IMAGE, {"filename_prefix": "image/fal/host"}),
    ),
    links=(("prompt.STRING", "draw.prompt"), ("draw.images", "save.images")),
    columns=(("prompt",), ("draw",), ("save",)),
    inputs=(("host", "prompt.values.a"),),
    outputs=(("files", "draw.files"),),
    description=HOST_TEXTS["design_description"],
    previews=(("save", IMAGE_PREVIEW),),
)

TURN = Subgraph(
    name=SHARED_TEXTS["turn"],
    nodes=(
        Node("add", FILE_ADD, {"field": "image_urls"}),
        Node(
            "edit",
            IMAGE_GENERATE,
            {"model": SUNBURST_EDIT, "prompt": TURN_PROMPT, "arguments": TURN_ARGUMENTS},
            is_paid=True,
        ),
        Node("save", HostNode.SAVE_IMAGE, {"filename_prefix": "image/fal/host-waving"}),
    ),
    links=(("add.files", "edit.files"), ("edit.images", "save.images")),
    columns=(("add",), ("edit",), ("save",)),
    inputs=(("files", "add.file"),),
    description=HOST_TEXTS["turn_description"],
    previews=(("save", IMAGE_PREVIEW),),
)

DESIGN_HOST = Workflow(
    slug="image-01-design-a-host",
    nodes=(
        Node(
            "host",
            HostNode.TEXT_BLOCK,
            {
                "value": (
                    "A cheerful woman in her late twenties with shoulder-length auburn hair, a mustard knit sweater, "
                    "and small gold hoop earrings."
                )
            },
            title=SHARED_TEXTS["host"],
        ),
        Node("design", DESIGN.name),
        Node("turn", TURN.name),
    ),
    links=(("host.STRING", "design.host"), ("design.files", "turn.files")),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("host",),), note=HOST_TEXTS["input"]),),
        (Group(SHARED_TEXTS["design"], (("design",),), STAGE_COLOUR, HOST_TEXTS["design"]),),
        (Group(SHARED_TEXTS["turn"], (("turn",),), STAGE_COLOUR, HOST_TEXTS["turn"]),),
    ),
    subgraphs=(DESIGN, TURN),
)

PHOTO = Subgraph(
    name=SHARED_TEXTS["photo"],
    nodes=(
        Node("draw", IMAGE_GENERATE, is_paid=True),
        Node("look", HostNode.PREVIEW_IMAGE),
    ),
    links=(("draw.images", "look.images"),),
    columns=(("draw",), ("look",)),
    inputs=(("product", "draw.prompt"),),
    outputs=(("files", "draw.files"),),
    description=CUT_OUT_TEXTS["photo_description"],
    previews=(("look", IMAGE_PREVIEW),),
)

UPSCALE = Subgraph(
    name=SHARED_TEXTS["upscale"],
    nodes=(
        Node("add", FILE_ADD, {"field": "image_url"}),
        Node("up", IMAGE_GENERATE, {"model": TOPAZ_PRECISION, "arguments": UPSCALE_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_IMAGE, {"filename_prefix": "image/fal/product-large"}),
    ),
    links=(("add.files", "up.files"), ("up.images", "save.images")),
    columns=(("add",), ("up",), ("save",)),
    inputs=(("files", "add.file"),),
    outputs=(("files", "up.files"),),
    description=CUT_OUT_TEXTS["upscale_description"],
    previews=(("save", IMAGE_PREVIEW),),
)

CUT_OUT = Subgraph(
    name=SHARED_TEXTS["cut_out"],
    nodes=(
        Node("add", FILE_ADD, {"field": "image_url"}),
        Node("cut", IMAGE_GENERATE, {"model": BRIA_EXTRACT}, is_paid=True),
        Node("first", HostNode.LIST_ITEM),
        Node("first_mask", HostNode.LIST_ITEM),
        Node("join", HostNode.JOIN_ALPHA),
        Node("save", HostNode.SAVE_IMAGE, {"filename_prefix": "image/fal/product-cut-out"}),
    ),
    links=(
        ("add.files", "cut.files"),
        ("cut.images", "first.list"),
        ("cut.masks", "first_mask.list"),
        ("first.*", "join.image"),
        ("first_mask.*", "join.alpha"),
        ("join.IMAGE", "save.images"),
    ),
    columns=(("add",), ("cut",), ("first", "first_mask"), ("join",), ("save",)),
    inputs=(("files", "add.file"), ("item", "cut.prompt")),
    description=CUT_OUT_TEXTS["cut_out_description"],
    previews=(("save", IMAGE_PREVIEW),),
)

CUT_OUT_PRODUCT = Workflow(
    slug="image-02-cut-out-a-product",
    nodes=(
        Node(
            "product",
            HostNode.TEXT_BLOCK,
            {
                "value": (
                    "A pair of white canvas sneakers with red laces, side view, on a plain white background, soft "
                    "studio light."
                )
            },
            title=SHARED_TEXTS["product"],
        ),
        Node("item", HostNode.TEXT, {"value": "white sneakers"}, title=SHARED_TEXTS["item"]),
        Node("photo", PHOTO.name),
        Node("upscale", UPSCALE.name),
        Node("cut_out", CUT_OUT.name),
    ),
    links=(
        ("product.STRING", "photo.product"),
        ("photo.files", "upscale.files"),
        ("upscale.files", "cut_out.files"),
        ("item.STRING", "cut_out.item"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("product", "item"),), note=CUT_OUT_TEXTS["input"]),),
        (Group(SHARED_TEXTS["photo"], (("photo",),), STAGE_COLOUR, CUT_OUT_TEXTS["photo"]),),
        (Group(SHARED_TEXTS["upscale"], (("upscale",),), STAGE_COLOUR, CUT_OUT_TEXTS["upscale"]),),
        (Group(SHARED_TEXTS["cut_out"], (("cut_out",),), STAGE_COLOUR, CUT_OUT_TEXTS["cut_out"]),),
    ),
    subgraphs=(PHOTO, UPSCALE, CUT_OUT),
)

SERIES = Subgraph(
    name=SHARED_TEXTS["series"],
    nodes=(
        Node("draw", IMAGE_GENERATE, {"model": SEEDREAM_LITE, "arguments": SERIES_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_IMAGE, {"filename_prefix": "image/fal/poster-series"}),
    ),
    links=(("draw.images", "save.images"),),
    columns=(("draw",), ("save",)),
    inputs=(("brief", "draw.prompt"),),
    description=SERIES_TEXTS["series_description"],
    previews=(("save", IMAGE_PREVIEW),),
)

POSTER_SERIES = Workflow(
    slug="image-03-make-a-poster-series",
    nodes=(
        Node(
            "brief",
            HostNode.TEXT_BLOCK,
            {
                "value": (
                    "Generate 4 travel posters for the same seaside town, one for each season, in one flat "
                    'illustration style, each with the town\'s name, "Port Ellis", at the top in the same typeface.'
                )
            },
            title=SHARED_TEXTS["brief"],
        ),
        Node("info", f"{NODE_PREFIX}ModelInfo", {"model": SEEDREAM_LITE}),
        Node("row", HostNode.PREVIEW, title=SHARED_TEXTS["info"]),
        Node("series", SERIES.name),
    ),
    links=(("brief.STRING", "series.brief"), ("info.info", "row.source")),
    stacks=(
        (
            Group(SHARED_TEXTS["input"], (("brief",),), note=SERIES_TEXTS["input"]),
            Group(SHARED_TEXTS["model"], (("info",), ("row",)), note=SERIES_TEXTS["model"]),
        ),
        (Group(SHARED_TEXTS["series"], (("series",),), STAGE_COLOUR, SERIES_TEXTS["series"]),),
    ),
    subgraphs=(SERIES,),
)

IMAGE_WORKFLOWS = (DESIGN_HOST, CUT_OUT_PRODUCT, POSTER_SERIES)

__all__ = ["IMAGE_WORKFLOWS", "PHOTO"]
