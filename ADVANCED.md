# Advanced Guide

Use this guide for fal model settings, file inputs, request options, and recovery.
For installation, see the [README](README.md). Node help covers
[individual inputs and outputs](README.md#nodes).

## Keys and access

Save your API key in **Extensions > fal > fal Settings** from the
ComfyUI menu. The key stays on the server and out of saved workflows.
`FAL_KEY`, set where ComfyUI starts, overrides the saved key.

Only a direct local, single-user connection can change the key or settings.
For remote access, a reverse proxy, or multi-user mode, set `FAL_KEY`
on the ComfyUI server and restart it.

The extension stores settings, credentials, and task records in this private folder:

| System  | Folder                                        |
| ------- | --------------------------------------------- |
| macOS   | `~/Library/Application Support/FalComfyUI`    |
| Linux   | `${XDG_STATE_HOME:-~/.local/state}/fal-comfy` |
| Windows | `%LOCALAPPDATA%\FalComfyUI`                   |

Set `FAL_COMFY_STATE_DIRECTORY` to use another absolute path outside
the extension and ComfyUI's folders. The extension writes unencrypted files with owner-only permissions.

A fal key contains `key_id:key_secret`. Paste both parts and the colon.

## Settings

Change limits in **fal Settings**. New requests use the saved values;
changing settings does not cancel active work. Model limits also apply.

| Setting                        | Default | Range      | What it limits                                                                                  |
| ------------------------------ | ------- | ---------- | ----------------------------------------------------------------------------------------------- |
| **Request timeout (seconds)**  | 1800    | 10 to 3600 | How long one request may take, from sending to the last download, time in fal's queue included. |
| **Maximum upload size (MB)**   | 100     | 1 to 100   | Each image, mask, audio, or video uploaded to fal.                                              |
| **Maximum download size (MB)** | 512     | 16 to 4096 | The largest result or output file accepted.                                                     |

## Models

Choose the node for the model's output kind. An upscaler or background remover
uses **Image: Generate**; transcription uses **Text: Generate**. Training and
realtime models are not supported.

| Node            | Runs models that make | Default model                                |
| --------------- | --------------------- | -------------------------------------------- |
| Image: Generate | Images                | `fal-ai/flux-2/klein/4b`                     |
| Video: Generate | Video                 | `fal-ai/ltx-2.3-22b/distilled/text-to-video` |
| Audio: Generate | Audio                 | `fal-ai/minimax/speech-2.8-turbo`            |
| Text: Generate  | Text                  | `fal-ai/elevenlabs/speech-to-text/scribe-v2` |
| 3D: Generate    | 3D models             | `fal-ai/trellis-2`                           |

The extension reads each model's public schema once per ComfyUI session.
**Model: Info** shows the inputs, choices, defaults, and outputs without a key
or a paid request. Connect required file inputs even when fal's schema lists a sample file as
their default.

Use named inputs for common settings. Empty text or `default` sends no value;
`custom` sends the number you choose. Other settings go in `arguments` as a
JSON object using the model's exact input names and value types. For example,
`{"resolution": "480p", "duration": 5}` sets those values when their named
inputs remain unset. Do not set the same field twice.

Omitted settings use the provider's defaults. Check those defaults before
running: resolution, duration, and output count affect cost.

## Files and uploads

Use **File: Add** to connect media to a model input. Set `field` to its exact
name, such as `image_url` or `reference_audio_urls`. `file` accepts an HTTPS
link, the `files` output of another fal node, or local ComfyUI image, mask, audio, or video.
Chain **File: Add** nodes and connect the final `files` to the generation node.

Fields ending in `_url` take one file. Fields ending in `_urls` receive a list,
including when you connect only one file. Files keep their chain order.
Do not also set the same file field in `arguments`.

Each request uploads local images as lossless WebP, masks as PNG, audio as WAV,
and video as MP4. The node reuses links from earlier fal outputs without uploading.
The `result` output contains the provider's JSON response.

Uploads and generated files have public links: anyone with a link can open them.
Storage duration depends on account settings. **Request Options** can set
`expiration_duration_seconds` for output files and disable `store_io`.
With `store_io` off, fal removes the request result within about 90 minutes;
collect it promptly if you need request recovery.

## Request options

Connect **Request Options** to control queue priority, start timeout,
provider-side retries/fallbacks, file expiry, and request history.
The extension submits once and defaults to `no_retry` and `disable_fallback`.
Turn those off only if you want fal to retry or use a fallback model.
See the [node fields](web/docs/FalRequestOptions.md).

## Caching and reruns

Change `run_number` to request another generation with unchanged inputs.
Set the named `seed` input to `custom`, or set `seed` in `arguments`, to send
a seed. Leave both unset to use the model's default behavior.
A different effective key invalidates cached results; changing limits does not.

## Recover a request

The extension records each accepted request. Cancellation asks fal to cancel;
a queued request can stop, while a started request can still finish and incur
charges. Requests can also continue after a restart or timeout.

Use **Request: Download** and press R to refresh the recorded requests.
A record leaves the list after download or when fal deletes its result.
Result retention depends on `store_io` and account settings. Recover an existing
request before submitting another paid generation.

## Troubleshooting

| Symptom                                  | Action                                                                           |
| ---------------------------------------- | -------------------------------------------------------------------------------- |
| The key is rejected                      | Paste the complete key and check whether `FAL_KEY` overrides it.                 |
| The key cannot use a model               | Check account credits and the key's permissions on fal.                          |
| A model is missing                       | Copy its ID from the model's page; check it with **Model: Info**.                |
| An input is rejected                     | Check its exact name, required files, value type, and whether it is set twice.   |
| An output image is black                 | Inspect `has_nsfw_concepts` in `result` for the provider's content-check result. |
| A request result has expired             | Check your saved outputs first. A new `run_number` submits a new paid request.   |
| The public model listing is rate-limited | The extension waits within the request timeout; try later if the timeout passes. |
| Settings cannot be changed               | Connect directly from localhost; use `FAL_KEY` for remote or multi-user access.  |

For an unknown setting or an oversized state file:

Stop ComfyUI and back up the affected file in the private state folder.
To reset limits, remove only `settings.json`, then restart. Keep task records
until you have recovered their outputs. Do not delete the whole state folder
to reset a setting.

## Update or remove

To update, replace `custom_nodes/fal-ai`, install its runtime requirements with ComfyUI's Python, and restart
ComfyUI. Open updated examples in a new tab.

To remove the extension, move its folder outside `custom_nodes` and restart.
Private state and saved media remain. Back up state and recover outstanding
tasks before deleting the private folder: that removes the saved key,
settings, and task records. Removing a saved key does not revoke it with the provider.
