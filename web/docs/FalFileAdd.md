# File: Add

Gives a fal model a file: a public `https://` link, images, masks, audio, or
video from ComfyUI, or another fal node's files. You name the model's file
input in `field`, exactly as fal writes it, such as `image_url`. Chain several
of these nodes to give a model several files. It sends nothing; the fal node
uploads local files when it runs.

## Inputs

| Input   | What it takes                                                                                         |
| ------- | ----------------------------------------------------------------------------------------------------- |
| `files` | Files from another **File: Add**. The new files go after them.                                        |
| `field` | The model's file input, such as `image_url` or `reference_audio_urls`.                                |
| `file`  | A public `https://` link typed here, or a connected image, mask, audio, video, or fal node's `files`. |

## Outputs

| Output  | What it carries                                 |
| ------- | ----------------------------------------------- |
| `files` | The earlier files, then the new ones, in order. |

## Use

1. Type the model's file input into `field`. **Model: Info** lists them.
2. Connect what you want to add to `file`, or type a link into it.
3. Connect `files` to the `files` input of a fal node, or to another
   **File: Add** to add more.

An input whose name ends in `_urls` takes a list, in order; one that ends in
`_url` takes exactly one file. Some models read a list by position, such as
"the person in Image 1". Example: **image-01-design-a-host**.

[fal file inputs](https://fal.ai/docs/documentation/model-apis/fal-cdn)
