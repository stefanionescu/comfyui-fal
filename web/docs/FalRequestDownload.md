# Request: Download

Downloads what fal made for a request after a run stopped: you cancelled it
while fal was already running it, ComfyUI restarted, or it waited longer than
the request timeout. It bills nothing.

## Inputs

| Input     | What it takes                                                                    |
| --------- | -------------------------------------------------------------------------------- |
| `request` | A request started on this server, shown as its ID, model, and start time in UTC. |

## Outputs

| Output     | What it carries                                                 |
| ---------- | --------------------------------------------------------------- |
| `images`   | Every image the request made.                                   |
| `masks`    | The mask of every image, such as a cut-out's transparency.      |
| `video`    | Every video the request made.                                   |
| `audio`    | Every audio file the request made.                              |
| `text`     | The text the request made, such as a transcript.                |
| `model_3d` | Every 3D model the request made.                                |
| `files`    | Every file the request made, as fal links for another fal node. |
| `result`   | Everything fal returned, as JSON.                               |

## Use

1. Choose the request in `request`. Press R to list requests started after
   the page loaded.
2. Connect the output you need, such as `video` to **Save Video**.
3. Select **Run**.

A request leaves the list once its files are downloaded, or when fal no
longer has its result. Outputs the request did not make stop the nodes
connected to them. Example: **video-05-recover-a-video**.

[fal queue documentation](https://fal.ai/docs/documentation/model-apis/inference/queue)
