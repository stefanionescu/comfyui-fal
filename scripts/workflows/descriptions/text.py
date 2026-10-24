"""The text workflows: transcribe a voice note, and describe a product photo."""

import json

from scripts.nodes.host import HostNode
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.page.config import STAGE_COLOUR, TEXT_PREVIEW
from scripts.workflows.descriptions.image import PHOTO
from scripts.workflows.descriptions.nodes import FILE_ADD, TEXT_GENERATE
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.descriptions.texts import SHARED_TEXTS

MOONDREAM_QUERY = 'fal-ai/moondream3-preview/query'
DESCRIBE_PROMPT = 'Describe this product for a marketplace listing in two sentences. Mention its color and material.'
DESCRIBE_ARGUMENTS = json.dumps({'reasoning': False}, indent=2)
TRANSCRIBE_TEXTS = WORKFLOW_TEXTS['text-01-transcribe-a-voice-note']
DESCRIBE_TEXTS = WORKFLOW_TEXTS['text-02-describe-a-product-photo']

TRANSCRIBE = Subgraph(
    name=SHARED_TEXTS['transcribe'],
    nodes=(
        Node('add', FILE_ADD, {'field': 'audio_url'}),
        Node('listen', TEXT_GENERATE, is_paid=True),
        Node('save', HostNode.SAVE_TEXT, {'filename_prefix': 'text/fal/voice-note'}),
    ),
    links=(('add.files', 'listen.files'), ('listen.text', 'save.text')),
    columns=(('add',), ('listen',), ('save',)),
    inputs=(('audio', 'add.file'),),
    outputs=(('result', 'listen.result'),),
    description=TRANSCRIBE_TEXTS['transcribe_description'],
    previews=(('save', TEXT_PREVIEW),),
)

TRANSCRIBE_NOTE = Workflow(
    slug='text-01-transcribe-a-voice-note',
    nodes=(
        Node('voice_note', HostNode.AUDIO, {'audio': ''}, title=SHARED_TEXTS['voice_note']),
        Node('transcribe', TRANSCRIBE.name),
        Node('words', HostNode.PREVIEW, title=SHARED_TEXTS['words']),
    ),
    links=(('voice_note.AUDIO', 'transcribe.audio'), ('transcribe.result', 'words.source')),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('voice_note',),), note=TRANSCRIBE_TEXTS['input']),),
        (
            Group(
                SHARED_TEXTS['transcribe'],
                (('transcribe',), ('words',)),
                STAGE_COLOUR,
                TRANSCRIBE_TEXTS['transcribe'],
            ),
        ),
    ),
    subgraphs=(TRANSCRIBE,),
)

DESCRIBE = Subgraph(
    name=SHARED_TEXTS['describe'],
    nodes=(
        Node('add', FILE_ADD, {'field': 'image_url'}),
        Node(
            'read',
            TEXT_GENERATE,
            {'model': MOONDREAM_QUERY, 'prompt': DESCRIBE_PROMPT, 'arguments': DESCRIBE_ARGUMENTS},
            is_paid=True,
        ),
        Node('save', HostNode.SAVE_TEXT, {'filename_prefix': 'text/fal/product-description'}),
    ),
    links=(('add.files', 'read.files'), ('read.text', 'save.text')),
    columns=(('add',), ('read',), ('save',)),
    inputs=(('files', 'add.file'),),
    description=DESCRIBE_TEXTS['describe_description'],
    previews=(('save', TEXT_PREVIEW),),
)

DESCRIBE_PHOTO = Workflow(
    slug='text-02-describe-a-product-photo',
    nodes=(
        Node(
            'product',
            HostNode.TEXT_BLOCK,
            {
                'value': (
                    'A stainless steel insulated water bottle, 750 ml, matte sage green with a bamboo lid, on a plain '
                    'white background, soft studio light.'
                )
            },
            title=SHARED_TEXTS['product'],
        ),
        Node('photo', PHOTO.name),
        Node('describe', DESCRIBE.name),
    ),
    links=(('product.STRING', 'photo.product'), ('photo.files', 'describe.files')),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('product',),), note=DESCRIBE_TEXTS['input']),),
        (Group(SHARED_TEXTS['photo'], (('photo',),), STAGE_COLOUR, DESCRIBE_TEXTS['photo']),),
        (Group(SHARED_TEXTS['describe'], (('describe',),), STAGE_COLOUR, DESCRIBE_TEXTS['describe']),),
    ),
    subgraphs=(PHOTO, DESCRIBE),
)

TEXT_WORKFLOWS = (TRANSCRIBE_NOTE, DESCRIBE_PHOTO)

__all__ = ['TEXT_WORKFLOWS']
