# ![comfyui-fal: a ComfyUI extension that runs fal models](docs/images/brand/banner.svg)

[![ComfyUI 0.37.2 or later](docs/images/badges/comfyui.svg)](#requirements)
[![Frontend 1.52.7 or later](docs/images/badges/frontend.svg)](#requirements)
[![Python 3.12 or later](docs/images/badges/python.svg)](#requirements)
[![MIT license](docs/images/badges/license.svg)](LICENSE.md)

Run any fal model in ComfyUI with your own API key.

## Contents

- [Requirements](#requirements)
- [Install](#install)
- [Example workflows](#example-workflows)
- [Nodes](#nodes)
- [License](#license)

## Requirements

- Python 3.12 or later.
- ComfyUI 0.37.2 or later, with frontend 1.52.7 or later in the 1.x series.
- A fal API key.

## Install

Put the extension in `ComfyUI/custom_nodes/fal-ai`, install its
`requirements.txt` with ComfyUI's Python, and restart ComfyUI.

### Comfy Desktop

1. In the instance chooser, select the **⋮** icon on the instance card, then
   **Manage**.
2. Under **About**, copy **Location**. In that folder, find the `ComfyUI` folder
   that holds `main.py`, and put the extension in its `custom_nodes` folder.
3. Select **Terminal** in the same panel and run:

```sh
pip install -r custom_nodes/fal-ai/requirements.txt
```

### macOS or Linux

From the ComfyUI folder:

```sh
.venv/bin/python -m pip install -r custom_nodes/fal-ai/requirements.txt
```

With uv:

```sh
uv pip install --python .venv/bin/python -r custom_nodes/fal-ai/requirements.txt
```

### Windows

From the ComfyUI folder, in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\custom_nodes\fal-ai\requirements.txt
```

### Windows portable

From the folder that holds `ComfyUI` and `python_embeded`, in PowerShell:

```powershell
.\python_embeded\python.exe -m pip install -r .\ComfyUI\custom_nodes\fal-ai\requirements.txt
```

## Example workflows

| Workflow                                                                                  | Input                         |
| ----------------------------------------------------------------------------------------- | ----------------------------- |
| [Image: Design a Host](example_workflows/image-01-design-a-host.json)                     | A host description            |
| [Image: Cut Out a Product](example_workflows/image-02-cut-out-a-product.json)             | A product description         |
| [Image: Make a Poster Series](example_workflows/image-03-make-a-poster-series.json)       | A brief                       |
| [Audio: Voice a Script](example_workflows/audio-01-voice-a-script.json)                   | A script and a sound          |
| [Audio: Split a Song into Stems](example_workflows/audio-02-split-a-song-into-stems.json) | A song description            |
| [Video: Animate a Host](example_workflows/video-01-animate-a-host.json)                   | A host and a scene            |
| [Video: Give a Host a Voice](example_workflows/video-02-give-a-host-a-voice.json)         | A host, a product, and a line |
| [Video: Make a Talking Avatar](example_workflows/video-03-make-a-talking-avatar.json)     | A person and a line to say    |
| [Video: Upscale a Clip](example_workflows/video-04-upscale-a-clip.json)                   | A shot                        |
| [Video: Recover a Video](example_workflows/video-05-recover-a-video.json)                 | A request left running        |

They are in **Browse Templates → fal-ai**. Start with each workflow's
**Start Here** note. Most steps are subgraphs. Media inputs start empty, and
most workflows make their own inputs with fal models.

After an update, open the examples in a new tab to get the new versions.

## Nodes

The nodes are under **fal** in the node menu, and each has a help page.

| Node                                                | What it does                                                                         | Paid |
| --------------------------------------------------- | ------------------------------------------------------------------------------------ | ---- |
| [Image: Generate](web/docs/FalImageGenerate.md)     | Makes, edits, upscales, or cuts out images with any fal image model.                 | Yes  |
| [Video: Generate](web/docs/FalVideoGenerate.md)     | Makes, extends, upscales, or lip-syncs video with any fal video model.               | Yes  |
| [Audio: Generate](web/docs/FalAudioGenerate.md)     | Makes voices, music, and sound effects, or changes audio, with any fal audio model.  | Yes  |
| [File: Add](web/docs/FalFileAdd.md)                 | Sends a link, image, mask, audio, or video to a model's file input, by its fal name. | No   |
| [Request: Download](web/docs/FalRequestDownload.md) | Downloads the outputs of a request fal kept running after a run stopped.             | No   |
| [Request Options](web/docs/FalRequestOptions.md)    | Sets fal's request options, such as queue priority and retries, for paid nodes.      | No   |
| [Model: Info](web/docs/FalModelInfo.md)             | Shows every setting a fal model takes and what it makes, as JSON.                    | No   |

## License

[MIT](LICENSE.md).
