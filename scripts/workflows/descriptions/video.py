"""The video workflows: animate a host, upscale a clip, and recover a video left running."""

from __future__ import annotations

import json
from scripts.nodes.host import HostNode
from src.config.namespace import NODE_PREFIX
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.page.config import STAGE_COLOUR, IMAGE_PREVIEW, VIDEO_PREVIEW
from scripts.workflows.descriptions.nodes import FILE_ADD, IMAGE_GENERATE, VIDEO_GENERATE

WAN_IMAGE = "alibaba/wan-3.0/image-to-video"
SEEDVR_VIDEO = "fal-ai/seedvr/upscale/video"
PORTRAIT_ARGUMENTS = json.dumps({"image_size": "portrait_16_9"}, indent=2)
ANIMATE_ARGUMENTS = json.dumps({"resolution": "480p", "duration": 5}, indent=2)
CLIP_ARGUMENTS = json.dumps({"num_frames": 49}, indent=2)
ENLARGE_ARGUMENTS = json.dumps({"upscale_mode": "target", "target_resolution": "1080p"}, indent=2)
ANIMATE_TEXTS = WORKFLOW_TEXTS["video-01-animate-a-host"]
UPSCALE_TEXTS = WORKFLOW_TEXTS["video-04-upscale-a-clip"]
RECOVER_TEXTS = WORKFLOW_TEXTS["video-05-recover-a-video"]

PORTRAIT = Subgraph(
    name=SHARED_TEXTS["portrait"],
    nodes=(
        Node(
            "prompt",
            HostNode.FORMAT,
            {
                "f_string": (
                    "Waist-up photo of a live-shopping host, vertical frame: {a} Looking at the camera, photorealistic."
                )
            },
        ),
        Node("draw", IMAGE_GENERATE, {"arguments": PORTRAIT_ARGUMENTS}, is_paid=True),
        Node("look", HostNode.PREVIEW_IMAGE),
    ),
    links=(("prompt.STRING", "draw.prompt"), ("draw.images", "look.images")),
    columns=(("prompt",), ("draw",), ("look",)),
    inputs=(("host", "prompt.values.a"),),
    outputs=(("files", "draw.files"),),
    description=ANIMATE_TEXTS["portrait_description"],
    previews=(("look", IMAGE_PREVIEW),),
)

ANIMATE = Subgraph(
    name=SHARED_TEXTS["animate"],
    nodes=(
        Node("add", FILE_ADD, {"field": "start_image_url"}),
        Node("video", VIDEO_GENERATE, {"model": WAN_IMAGE, "arguments": ANIMATE_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/fal/host"}),
    ),
    links=(("add.files", "video.files"), ("video.video", "save.video")),
    columns=(("add",), ("video",), ("save",)),
    inputs=(("files", "add.file"), ("scene", "video.prompt")),
    description=ANIMATE_TEXTS["animate_description"],
    previews=(("save", VIDEO_PREVIEW),),
)

ANIMATE_HOST = Workflow(
    slug="video-01-animate-a-host",
    nodes=(
        Node(
            "host",
            HostNode.TEXT_BLOCK,
            {
                "value": (
                    "A friendly man in his thirties with short curly hair and a denim jacket, standing in a bright "
                    "studio with shelves of sneakers behind him."
                )
            },
            title=SHARED_TEXTS["host"],
        ),
        Node(
            "scene",
            HostNode.TEXT_BLOCK,
            {
                "value": (
                    "He smiles, picks up a sneaker from the shelf, and turns it toward the camera. Slow push-in, warm "
                    "light."
                )
            },
            title=SHARED_TEXTS["scene"],
        ),
        Node("portrait", PORTRAIT.name),
        Node("animate", ANIMATE.name),
    ),
    links=(
        ("host.STRING", "portrait.host"),
        ("portrait.files", "animate.files"),
        ("scene.STRING", "animate.scene"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("host", "scene"),), note=ANIMATE_TEXTS["input"]),),
        (Group(SHARED_TEXTS["portrait"], (("portrait",),), STAGE_COLOUR, ANIMATE_TEXTS["portrait"]),),
        (Group(SHARED_TEXTS["animate"], (("animate",),), STAGE_COLOUR, ANIMATE_TEXTS["animate"]),),
    ),
    subgraphs=(PORTRAIT, ANIMATE),
)

CLIP = Subgraph(
    name=SHARED_TEXTS["clip"],
    nodes=(
        Node("video", VIDEO_GENERATE, {"arguments": CLIP_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/fal/clip"}),
    ),
    links=(("video.video", "save.video"),),
    columns=(("video",), ("save",)),
    inputs=(("shot", "video.prompt"),),
    outputs=(("files", "video.files"),),
    description=UPSCALE_TEXTS["clip_description"],
    previews=(("save", VIDEO_PREVIEW),),
)

ENLARGE = Subgraph(
    name=SHARED_TEXTS["enlarge"],
    nodes=(
        Node("add", FILE_ADD, {"field": "video_url"}),
        Node("up", VIDEO_GENERATE, {"model": SEEDVR_VIDEO, "arguments": ENLARGE_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/fal/clip-1080p"}),
    ),
    links=(("add.files", "up.files"), ("up.video", "save.video")),
    columns=(("add",), ("up",), ("save",)),
    inputs=(("files", "add.file"), ("options", "up.options")),
    description=UPSCALE_TEXTS["enlarge_description"],
    previews=(("save", VIDEO_PREVIEW),),
)

UPSCALE_CLIP = Workflow(
    slug="video-04-upscale-a-clip",
    nodes=(
        Node(
            "shot",
            HostNode.TEXT_BLOCK,
            {
                "value": (
                    "A paper boat drifts across a calm, sunlit pond as a light breeze ripples the water. Low camera "
                    "following it."
                )
            },
            title=SHARED_TEXTS["shot"],
        ),
        Node("clip", CLIP.name),
        Node("low", f"{NODE_PREFIX}RequestOptions", {"queue_priority": "low"}),
        Node("enlarge", ENLARGE.name),
    ),
    links=(("shot.STRING", "clip.shot"), ("clip.files", "enlarge.files"), ("low.options", "enlarge.options")),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("shot",),), note=UPSCALE_TEXTS["input"]),),
        (Group(SHARED_TEXTS["clip"], (("clip",),), STAGE_COLOUR, UPSCALE_TEXTS["clip"]),),
        (Group(SHARED_TEXTS["enlarge"], (("low",), ("enlarge",)), STAGE_COLOUR, UPSCALE_TEXTS["enlarge"]),),
    ),
    subgraphs=(CLIP, ENLARGE),
)

RECOVER_VIDEO = Workflow(
    slug="video-05-recover-a-video",
    nodes=(
        Node("download", f"{NODE_PREFIX}RequestDownload", {"request": ""}),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/fal/recovered"}),
    ),
    links=(("download.video", "save.video"),),
    stacks=((Group(SHARED_TEXTS["recover"], (("download",), ("save",)), STAGE_COLOUR, RECOVER_TEXTS["recover"]),),),
)

VIDEO_WORKFLOWS = (ANIMATE_HOST, UPSCALE_CLIP, RECOVER_VIDEO)

__all__ = ["VIDEO_WORKFLOWS"]
