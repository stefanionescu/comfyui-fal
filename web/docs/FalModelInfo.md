# Model: Info

Shows what any fal model takes and makes, as JSON: every input with its type,
default, choices, range, and text length limit, and every output. Use it to write a paid node's
`arguments` and a **File: Add**'s `field`. It reads fal's model listing, so it
is free and needs no key.

## Inputs

| Input   | What it takes                                                                               |
| ------- | ------------------------------------------------------------------------------------------- |
| `model` | A model ID, such as `alibaba/wan-3.0/reference-to-video`; the model's page on fal shows it. |

## Outputs

| Output | What it carries                                              |
| ------ | ------------------------------------------------------------ |
| `info` | The model's inputs and outputs as JSON, with the keys below. |

| Key         | What it holds                                                                                                      |
| ----------- | ------------------------------------------------------------------------------------------------------------------ |
| model       | The ID as typed. Paid nodes send exactly this ID.                                                                  |
| name        | fal's name for the model.                                                                                          |
| kind        | What the model makes: `image`, `video`, `audio`, `text`, or `mesh` (a 3D model).                                   |
| node        | The paid node that runs it, such as `Video: Generate`.                                                             |
| category    | fal's category, such as `image-to-video`.                                                                          |
| status      | `active`, `deprecated`, or `unlisted` by fal.                                                                      |
| updated     | When fal last updated the model.                                                                                   |
| docs        | The model's page on fal.                                                                                           |
| description | fal's description.                                                                                                 |
| inputs      | Every input: its name, type, whether it is required, default, choices, range, list size, and whether it is a file. |
| outputs     | Every output, which ones are files, and which one `text` reads.                                                    |

For example, one input of `alibaba/wan-3.0/reference-to-video`:

```json
{
    "field": "reference_audio_urls",
    "type": "array",
    "required": false,
    "default": null,
    "choices": null,
    "minimum": null,
    "maximum": null,
    "list": true,
    "max_items": 5,
    "max_length": null,
    "file": true,
    "media": "audio",
    "description": "Up to 5 reference audio URLs totaling at most 15 seconds."
}
```

`max_length` is the longest text allowed, in characters. It is `null` when fal
lists no text length limit.

## Use

1. Type or connect the model ID.
2. Connect `info` to **Preview as Text** to read it, or to **Extract Text
   from JSON** to use one key.

A file input, such as `reference_audio_urls`, takes files through **File:
Add**; every other input goes in the paid node's `arguments` under its
`field` name. Another extension can run the node and read `info` instead of
copying a model's inputs; the advanced guide explains how. Example:
**image-03-make-a-poster-series**.

[fal models](https://fal.ai/models)
