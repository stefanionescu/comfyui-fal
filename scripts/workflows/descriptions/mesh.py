"""The 3D workflow: turn a product into a 3D model."""

from __future__ import annotations

import json
from scripts.nodes.host import HostNode
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.config import STAGE_COLOUR, IMAGE_PREVIEW
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.descriptions.nodes import FILE_ADD, MESH_GENERATE, IMAGE_GENERATE

FRONT_ARGUMENTS = json.dumps({"image_size": "square_hd"}, indent=2)
BUILD_ARGUMENTS = json.dumps({"resolution": 512}, indent=2)
PRODUCT_TEXTS = WORKFLOW_TEXTS["3d-01-turn-a-product-into-a-3d-model"]

FRONT_VIEW = Subgraph(
    name=SHARED_TEXTS["front"],
    nodes=(
        Node(
            "prompt",
            HostNode.FORMAT,
            {
                "f_string": (
                    "Product photo for a 3D model: {a} Three-quarter front view, the whole object in frame, plain "
                    "white background, soft even light, no shadows."
                )
            },
        ),
        Node("draw", IMAGE_GENERATE, {"arguments": FRONT_ARGUMENTS}, is_paid=True),
        Node("look", HostNode.PREVIEW_IMAGE),
    ),
    links=(("prompt.STRING", "draw.prompt"), ("draw.images", "look.images")),
    columns=(("prompt",), ("draw",), ("look",)),
    inputs=(("product", "prompt.values.a"),),
    outputs=(("files", "draw.files"),),
    description=PRODUCT_TEXTS["front_description"],
    previews=(("look", IMAGE_PREVIEW),),
)

PRODUCT_MODEL = Workflow(
    slug="3d-01-turn-a-product-into-a-3d-model",
    nodes=(
        Node(
            "product",
            HostNode.TEXT_BLOCK,
            {"value": "A ceramic coffee mug with a speckled cream glaze and a wooden handle."},
            title=SHARED_TEXTS["product"],
        ),
        Node("front", FRONT_VIEW.name),
        Node("image", FILE_ADD, {"field": "image_url"}),
        Node("mesh", MESH_GENERATE, {"arguments": BUILD_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_MESH, {"filename_prefix": "3d/fal/product"}),
    ),
    links=(
        ("product.STRING", "front.product"),
        ("front.files", "image.file"),
        ("image.files", "mesh.files"),
        ("mesh.model_3d", "save.mesh"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("product",),), note=PRODUCT_TEXTS["input"]),),
        (Group(SHARED_TEXTS["front"], (("front",),), STAGE_COLOUR, PRODUCT_TEXTS["front"]),),
        (Group(SHARED_TEXTS["build"], (("image",), ("mesh",), ("save",)), STAGE_COLOUR, PRODUCT_TEXTS["build"]),),
    ),
    subgraphs=(FRONT_VIEW,),
)

MESH_WORKFLOWS = (PRODUCT_MODEL,)

__all__ = ["MESH_WORKFLOWS"]
