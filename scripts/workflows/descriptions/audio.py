"""The audio workflows: voice a script over a background sound, and split a song into stems."""

from __future__ import annotations

import json
from scripts.nodes.host import HostNode
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.config import STAGE_COLOUR, AUDIO_PREVIEW
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.descriptions.nodes import FILE_ADD, ELEVEN_V4, AUDIO_GENERATE

ELEVEN_SOUND = "fal-ai/elevenlabs/sound-effects/v2"
STABLE_AUDIO_MUSIC = "fal-ai/stable-audio-3/small/music/text-to-audio"
DEMUCS = "fal-ai/demucs"
SCRIPT_ARGUMENTS = json.dumps(
    {
        "text": (
            "Welcome back to the show. Today we have three new sneakers, and the first pair is already selling fast."
        )
    },
    indent=2,
)
SOUND_ARGUMENTS = json.dumps(
    {"text": "Busy shopping street ambience, light chatter and footsteps, distant traffic.", "duration_seconds": 8},
    indent=2,
)
SONG_ARGUMENTS = json.dumps({"duration": 20}, indent=2)
SCRIPT_TEXTS = WORKFLOW_TEXTS["audio-01-voice-a-script"]
STEMS_TEXTS = WORKFLOW_TEXTS["audio-02-split-a-song-into-stems"]

VOICE = Subgraph(
    name=SHARED_TEXTS["voice"],
    nodes=(
        Node("speak", AUDIO_GENERATE, {"model": ELEVEN_V4}, is_paid=True),
        Node("save", HostNode.SAVE_AUDIO, {"filename_prefix": "audio/fal/script-voice"}),
    ),
    links=(("speak.audio", "save.audio"),),
    columns=(("speak",), ("save",)),
    inputs=(("script", "speak.arguments"),),
    outputs=(("audio", "speak.audio"),),
    description=SCRIPT_TEXTS["voice_description"],
    previews=(("save", AUDIO_PREVIEW),),
)

AMBIENCE = Subgraph(
    name=SHARED_TEXTS["ambience"],
    nodes=(
        Node("sfx", AUDIO_GENERATE, {"model": ELEVEN_SOUND}, is_paid=True),
        Node("save", HostNode.SAVE_AUDIO, {"filename_prefix": "audio/fal/ambience"}),
    ),
    links=(("sfx.audio", "save.audio"),),
    columns=(("sfx",), ("save",)),
    inputs=(("sound", "sfx.arguments"),),
    outputs=(("audio", "sfx.audio"),),
    description=SCRIPT_TEXTS["ambience_description"],
    previews=(("save", AUDIO_PREVIEW),),
)

MIX = Subgraph(
    name=SHARED_TEXTS["mix"],
    nodes=(
        Node("merge", HostNode.MERGE_AUDIO),
        Node("save", HostNode.SAVE_AUDIO, {"filename_prefix": "audio/fal/script-mixed"}),
    ),
    links=(("merge.AUDIO", "save.audio"),),
    columns=(("merge",), ("save",)),
    inputs=(("voice", "merge.audio1"), ("ambience", "merge.audio2")),
    description=SCRIPT_TEXTS["mix_description"],
    previews=(("save", AUDIO_PREVIEW),),
)

VOICE_SCRIPT = Workflow(
    slug="audio-01-voice-a-script",
    nodes=(
        Node("script", HostNode.TEXT_BLOCK, {"value": SCRIPT_ARGUMENTS}, title=SHARED_TEXTS["script"]),
        Node("sound", HostNode.TEXT_BLOCK, {"value": SOUND_ARGUMENTS}, title=SHARED_TEXTS["sound"]),
        Node("voice", VOICE.name),
        Node("ambience", AMBIENCE.name),
        Node("mix", MIX.name),
    ),
    links=(
        ("script.STRING", "voice.script"),
        ("sound.STRING", "ambience.sound"),
        ("voice.audio", "mix.voice"),
        ("ambience.audio", "mix.ambience"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("script", "sound"),), note=SCRIPT_TEXTS["input"]),),
        (Group(SHARED_TEXTS["voice"], (("voice",),), STAGE_COLOUR, SCRIPT_TEXTS["voice"]),),
        (Group(SHARED_TEXTS["ambience"], (("ambience",),), STAGE_COLOUR, SCRIPT_TEXTS["ambience"]),),
        (Group(SHARED_TEXTS["mix"], (("mix",),), STAGE_COLOUR, SCRIPT_TEXTS["mix"]),),
    ),
    subgraphs=(VOICE, AMBIENCE, MIX),
)

COMPOSE = Subgraph(
    name=SHARED_TEXTS["compose"],
    nodes=(
        Node("music", AUDIO_GENERATE, {"model": STABLE_AUDIO_MUSIC, "arguments": SONG_ARGUMENTS}, is_paid=True),
        Node("save", HostNode.SAVE_AUDIO, {"filename_prefix": "audio/fal/song"}),
    ),
    links=(("music.audio", "save.audio"),),
    columns=(("music",), ("save",)),
    inputs=(("song", "music.prompt"),),
    outputs=(("files", "music.files"),),
    description=STEMS_TEXTS["compose_description"],
    previews=(("save", AUDIO_PREVIEW),),
)

SPLIT = Subgraph(
    name=SHARED_TEXTS["split"],
    nodes=(
        Node("add", FILE_ADD, {"field": "audio_url"}),
        Node("stems", AUDIO_GENERATE, {"model": DEMUCS}, is_paid=True),
        Node("save", HostNode.SAVE_AUDIO, {"filename_prefix": "audio/fal/song-stem"}),
    ),
    links=(("add.files", "stems.files"), ("stems.audio", "save.audio")),
    columns=(("add",), ("stems",), ("save",)),
    inputs=(("files", "add.file"),),
    description=STEMS_TEXTS["split_description"],
    previews=(("save", AUDIO_PREVIEW),),
)

SPLIT_SONG = Workflow(
    slug="audio-02-split-a-song-into-stems",
    nodes=(
        Node(
            "song",
            HostNode.TEXT_BLOCK,
            {
                "value": (
                    "Upbeat funk instrumental with slap bass, tight drums, rhythm guitar, and electric piano, 110 BPM."
                )
            },
            title=SHARED_TEXTS["song"],
        ),
        Node("compose", COMPOSE.name),
        Node("split", SPLIT.name),
    ),
    links=(("song.STRING", "compose.song"), ("compose.files", "split.files")),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("song",),), note=STEMS_TEXTS["input"]),),
        (Group(SHARED_TEXTS["compose"], (("compose",),), STAGE_COLOUR, STEMS_TEXTS["compose"]),),
        (Group(SHARED_TEXTS["split"], (("split",),), STAGE_COLOUR, STEMS_TEXTS["split"]),),
    ),
    subgraphs=(COMPOSE, SPLIT),
)

AUDIO_WORKFLOWS = (VOICE_SCRIPT, SPLIT_SONG)

__all__ = ["AUDIO_WORKFLOWS"]
