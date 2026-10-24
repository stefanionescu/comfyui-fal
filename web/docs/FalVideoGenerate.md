# Video: Generate

Runs any fal model that makes a video: from a prompt, frames, reference
images, video, or audio, and to edit, extend, lip-sync, or upscale a video. It
outputs the video and the fal link of every file the model made.

## Inputs

| Input        | What it takes                                                                                                                     |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| `files`      | Frames, references, video, or audio from **File: Add**, each under the model's field name, such as `start_image_url`.             |
| `options`    | Settings from **Request Options**.                                                                                                |
| `model`      | The model's ID on fal, such as `alibaba/wan-3.0/reference-to-video`. The default is `fal-ai/ltx-2.3-22b/distilled/text-to-video`. |
| `run_number` | Change it to send the same request again.                                                                                         |
| `prompt`     | The text sent as the model's `prompt`.                                                                                            |
| `arguments`  | The model's other settings as JSON, under fal's names, such as `{"resolution": "480p", "duration": 5}`.                           |

Copy the model ID and its field names from the model's page on fal, or read
them with **Model: Info**. Write each value as fal does: Kling's `duration`
is the text `"5"`, Wan 3.0's is the number `5`. A setting left out takes fal's
default, which on some models is the most expensive resolution. A field
ending in `_urls` takes a list: the node sends one voice clip for
`reference_audio_urls` as a list of one.

## Outputs

| Output   | What it carries                                                   |
| -------- | ----------------------------------------------------------------- |
| `video`  | The video, with its sound.                                        |
| `files`  | The fal link of every file the model made, for the next fal node. |
| `result` | fal's whole result as JSON, such as the seed and the duration.    |

## Use

1. Type the model ID in `model`, and write the prompt.
2. Add `resolution`, `duration`, and other settings to `arguments`.
3. Connect **File: Add** with each frame, reference, or clip and its field
   name to `files`.
4. Connect `video` to **Save Video**, and select **Run**. A video takes from
   under a minute to several minutes.

Examples: **video-01-animate-a-host**, **video-02-give-a-host-a-voice**,
**video-03-make-a-talking-avatar**, and **video-04-upscale-a-clip**.

If you cancel while the request waits in fal's queue, fal drops it. Once the
request has started, it may still finish, and fal may bill it. This can happen
even if you cancel, ComfyUI restarts, or the request timeout in **fal
Settings** passes. Collect it with **Request: Download**.

[fal video models](https://fal.ai/models?categories=text-to-video)
