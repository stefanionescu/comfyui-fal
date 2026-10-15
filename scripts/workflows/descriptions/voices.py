"""The video workflows that give a person a voice: a host filmed with a product, and a talking avatar."""

from __future__ import annotations

import json
from scripts.nodes.host import HostNode
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.page.config import STAGE_COLOUR, AUDIO_PREVIEW, IMAGE_PREVIEW, VIDEO_PREVIEW
from scripts.workflows.descriptions.nodes import (
    FILE_ADD,
    ELEVEN_V4,
    AUDIO_GENERATE,
    IMAGE_GENERATE,
    VIDEO_GENERATE,
)

WAN_REFERENCE = "alibaba/wan-3.0/reference-to-video"
FLASHTALK = "fal-ai/flashtalk"
CAST_ARGUMENTS = json.dumps({"image_size": "portrait_16_9"}, indent=2)
PACKSHOT_ARGUMENTS = json.dumps({"image_size": "square_hd"}, indent=2)
VOICE_ARGUMENTS = json.dumps(
    {"text": "Hi everyone, it's so good to see you. I've got something special to show you today."}, indent=2
)
FILM_ARGUMENTS = json.dumps({"resolution": "480p", "duration": 5, "aspect_ratio": "9:16"}, indent=2)
FACE_ARGUMENTS = json.dumps({"image_size": "portrait_4_3"}, indent=2)
SCENE_PROMPT = (
    'The host from Image 1 holds up the sneakers from Image 2 and says: "These just dropped, and they are going '
    'fast." She speaks in the voice from Audio 1. Bright studio, slow push-in.'
)
VOICE_TEXTS = WORKFLOW_TEXTS["video-02-give-a-host-a-voice"]
AVATAR_TEXTS = WORKFLOW_TEXTS["video-03-make-a-talking-avatar"]

CAST = Subgraph(
    name=SHARED_TEXTS["cast"],
    nodes=(
        Node("draw", IMAGE_GENERATE, {"arguments": CAST_ARGUMENTS}, is_paid=True),
        Node("look", HostNode.PREVIEW_IMAGE),
    ),
    links=(("draw.images", "look.images"),),
    columns=(("draw",), ("look",)),
    inputs=(("host", "draw.prompt"),),
    outputs=(("files", "draw.files"),),
    description=VOICE_TEXTS["cast_description"],
    previews=(("look", IMAGE_PREVIEW),),
)

PACKSHOT = Subgraph(
    name=SHARED_TEXTS["packshot"],
    nodes=(
        Node("draw", IMAGE_GENERATE, {"arguments": PACKSHOT_ARGUMENTS}, is_paid=True),
        Node("look", HostNode.PREVIEW_IMAGE),
    ),
    links=(("draw.images", "look.images"),),
    columns=(("draw",), ("look",)),
    inputs=(("product", "draw.prompt"),),
    outputs=(("files", "draw.files"),),
    description=VOICE_TEXTS["packshot_description"],
    previews=(("look", IMAGE_PREVIEW),),
)

SPEAK = Subgraph(
    name=SHARED_TEXTS["speak"],
    nodes=(
        Node("speak", AUDIO_GENERATE, {"model": ELEVEN_V4}, is_paid=True),
        Node("save", HostNode.SAVE_AUDIO, {"filename_prefix": "audio/fal/host-voice"}),
    ),
    links=(("speak.audio", "save.audio"),),
    columns=(("speak",), ("save",)),
    inputs=(("voice", "speak.arguments"),),
    outputs=(("files", "speak.files"),),
    description=VOICE_TEXTS["speak_description"],
    previews=(("save", AUDIO_PREVIEW),),
)

FILM = Subgraph(
    name=SHARED_TEXTS["film"],
    nodes=(
        Node("video", VIDEO_GENERATE, {"model": WAN_REFERENCE, "arguments": FILM_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/fal/host-voice"}),
    ),
    links=(("video.video", "save.video"),),
    columns=(("video",), ("save",)),
    inputs=(("files", "video.files"), ("scene", "video.prompt")),
    description=VOICE_TEXTS["film_description"],
    previews=(("save", VIDEO_PREVIEW),),
)

GIVE_HOST_VOICE = Workflow(
    slug="video-02-give-a-host-a-voice",
    nodes=(
        Node(
            "host",
            HostNode.TEXT_BLOCK,
            {
                "value": (
                    "A cheerful woman in her late twenties with shoulder-length auburn hair and a mustard knit "
                    "sweater, in a bright studio."
                )
            },
            title=SHARED_TEXTS["host"],
        ),
        Node(
            "product",
            HostNode.TEXT_BLOCK,
            {
                "value": (
                    "A pair of white canvas sneakers with red laces, on a plain white background, soft studio light."
                )
            },
            title=SHARED_TEXTS["product"],
        ),
        Node("voice", HostNode.TEXT_BLOCK, {"value": VOICE_ARGUMENTS}, title=SHARED_TEXTS["voice"]),
        Node("scene", HostNode.TEXT_BLOCK, {"value": SCENE_PROMPT}, title=SHARED_TEXTS["scene"]),
        Node("cast", CAST.name),
        Node("packshot", PACKSHOT.name),
        Node("speak", SPEAK.name),
        Node("host_file", FILE_ADD, {"field": "reference_image_urls"}),
        Node("product_file", FILE_ADD, {"field": "reference_image_urls"}),
        Node("voice_file", FILE_ADD, {"field": "reference_audio_urls"}),
        Node("film", FILM.name),
    ),
    links=(
        ("host.STRING", "cast.host"),
        ("product.STRING", "packshot.product"),
        ("voice.STRING", "speak.voice"),
        ("cast.files", "host_file.file"),
        ("packshot.files", "product_file.file"),
        ("host_file.files", "product_file.files"),
        ("speak.files", "voice_file.file"),
        ("product_file.files", "voice_file.files"),
        ("voice_file.files", "film.files"),
        ("scene.STRING", "film.scene"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("host", "product"), ("voice", "scene")), note=VOICE_TEXTS["input"]),),
        (Group(SHARED_TEXTS["cast"], (("cast",),), STAGE_COLOUR, VOICE_TEXTS["cast"]),),
        (Group(SHARED_TEXTS["packshot"], (("packshot",),), STAGE_COLOUR, VOICE_TEXTS["packshot"]),),
        (Group(SHARED_TEXTS["speak"], (("speak",),), STAGE_COLOUR, VOICE_TEXTS["speak"]),),
        (
            Group(
                SHARED_TEXTS["references"],
                (("host_file",), ("product_file",), ("voice_file",)),
                STAGE_COLOUR,
                VOICE_TEXTS["references"],
            ),
        ),
        (Group(SHARED_TEXTS["film"], (("film",),), STAGE_COLOUR, VOICE_TEXTS["film"]),),
    ),
    subgraphs=(CAST, PACKSHOT, SPEAK, FILM),
)

FACE = Subgraph(
    name=SHARED_TEXTS["face"],
    nodes=(
        Node("draw", IMAGE_GENERATE, {"arguments": FACE_ARGUMENTS}, is_paid=True),
        Node("look", HostNode.PREVIEW_IMAGE),
    ),
    links=(("draw.images", "look.images"),),
    columns=(("draw",), ("look",)),
    inputs=(("person", "draw.prompt"),),
    outputs=(("files", "draw.files"),),
    description=AVATAR_TEXTS["face_description"],
    previews=(("look", IMAGE_PREVIEW),),
)

SPEECH = Subgraph(
    name=SHARED_TEXTS["speech"],
    nodes=(
        Node("speak", AUDIO_GENERATE, is_paid=True),
        Node("save", HostNode.SAVE_AUDIO, {"filename_prefix": "audio/fal/avatar-line"}),
    ),
    links=(("speak.audio", "save.audio"),),
    columns=(("speak",), ("save",)),
    inputs=(("line", "speak.prompt"),),
    outputs=(("files", "speak.files"),),
    description=AVATAR_TEXTS["speech_description"],
    previews=(("save", AUDIO_PREVIEW),),
)

TALK = Subgraph(
    name=SHARED_TEXTS["talk"],
    nodes=(
        Node("face_file", FILE_ADD, {"field": "image_url"}),
        Node("voice_file", FILE_ADD, {"field": "audio_url"}),
        Node("talk", VIDEO_GENERATE, {"model": FLASHTALK}, is_paid=True),
        Node("save", HostNode.SAVE_VIDEO, {"filename_prefix": "video/fal/talking-avatar"}),
    ),
    links=(
        ("face_file.files", "voice_file.files"),
        ("voice_file.files", "talk.files"),
        ("talk.video", "save.video"),
    ),
    columns=(("face_file", "voice_file"), ("talk",), ("save",)),
    inputs=(("face", "face_file.file"), ("speech", "voice_file.file")),
    description=AVATAR_TEXTS["talk_description"],
    previews=(("save", VIDEO_PREVIEW),),
)

TALKING_AVATAR = Workflow(
    slug="video-03-make-a-talking-avatar",
    nodes=(
        Node(
            "person",
            HostNode.TEXT_BLOCK,
            {
                "value": (
                    "A friendly man in his thirties with short curly hair and a denim jacket, looking straight at the "
                    "camera, plain studio background."
                )
            },
            title=SHARED_TEXTS["person"],
        ),
        Node(
            "line",
            HostNode.TEXT_BLOCK,
            {"value": "Thanks for watching. Tap the link below to grab your pair before they sell out."},
            title=SHARED_TEXTS["line"],
        ),
        Node("face", FACE.name),
        Node("speech", SPEECH.name),
        Node("talk", TALK.name),
    ),
    links=(
        ("person.STRING", "face.person"),
        ("line.STRING", "speech.line"),
        ("face.files", "talk.face"),
        ("speech.files", "talk.speech"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("person", "line"),), note=AVATAR_TEXTS["input"]),),
        (Group(SHARED_TEXTS["face"], (("face",),), STAGE_COLOUR, AVATAR_TEXTS["face"]),),
        (Group(SHARED_TEXTS["speech"], (("speech",),), STAGE_COLOUR, AVATAR_TEXTS["speech"]),),
        (Group(SHARED_TEXTS["talk"], (("talk",),), STAGE_COLOUR, AVATAR_TEXTS["talk"]),),
    ),
    subgraphs=(FACE, SPEECH, TALK),
)

VOICE_WORKFLOWS = (GIVE_HOST_VOICE, TALKING_AVATAR)

__all__ = ["VOICE_WORKFLOWS"]
