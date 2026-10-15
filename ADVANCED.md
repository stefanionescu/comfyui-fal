# ComfyUI fal Advanced Guide

## Contents

- [What each node sends](#what-each-node-sends)
- [Keys and access](#keys-and-access)
- [Settings](#settings)
- [Models](#models)
- [Files and uploads](#files-and-uploads)
- [Caching and reruns](#caching-and-reruns)
- [Recover a request](#recover-a-request)
- [Limits](#limits)
- [When a node stops](#when-a-node-stops)
- [Use from another extension](#use-from-another-extension)
- [Update or remove](#update-or-remove)
- [Development](#development)
- [Package and publish](#package-and-publish)
- [Troubleshooting](#troubleshooting)

## What each node sends

- **Image: Generate**, **Video: Generate**, **Audio: Generate**, **Text:
  Generate**, and **3D: Generate** first read the model from fal's public list
  of models, free and once per model while ComfyUI runs. They upload your
  images and masks as PNG, your audio as WAV, and your video as MP4 to fal's
  storage, once per file, and send `prompt`, the settings in `arguments`, and
  the files from **File: Add**, under fal's names. They send one request to
  fal's queue, record it as soon as fal accepts it, and wait for fal to say it
  is done. Then they download the output files and return them with each
  file's fal link in `files` and fal's whole result as JSON in `result`.
  **Text: Generate** returns the model's answer in `text`, from the result
  field that holds it, preferring a field named like `output` or `text`.
- **File: Add** names the model input a file goes to and adds the file: a
  link, an image, a mask, audio, video, or another fal node's files. It sends
  nothing; the paid node uploads what it holds.
- **Request: Download** reads one recorded request's status and result, and
  downloads its files. Status reads and downloads are free.
- **Request Options** adds request options to each connected paid node's
  request: queue priority, a start timeout, fal's retries and fallbacks, how
  long output files last, and whether fal keeps the request's history.
- **Model: Info** reads one model from fal's list of models and returns every
  setting it takes and what it makes, as JSON. It is free and needs no key.

Every request goes out once. Files fal makes are downloaded without the key.

## Keys and access

Save the key in **ComfyUI menu → Extensions → fal → fal Settings**. A fal key
has two parts, `key_id:key_secret`; paste the whole key. It is stored in the
private folder and checked by the first request that uses it. `FAL_KEY`, set
where ComfyUI starts, takes precedence. The key goes only to fal.

The key and settings can be changed only over a direct local connection to the
ComfyUI server. For remote access, a reverse proxy, or multi-user mode, set
`FAL_KEY` instead.

The private folder is:

| System  | Folder                                        |
| ------- | --------------------------------------------- |
| macOS   | `~/Library/Application Support/FalComfyUI`    |
| Linux   | `${XDG_STATE_HOME:-~/.local/state}/fal-comfy` |
| Windows | `%LOCALAPPDATA%\FalComfyUI`                   |

To use another folder, set `FAL_COMFY_STATE_DIRECTORY` to an absolute path
outside the extension and ComfyUI's folders. Files are unencrypted, with
owner-only permissions.

## Settings

Change these in **fal Settings**. New requests use the saved values.

![The fal Settings dialog: Credentials with the fal API key field, Save Key, and Clear Saved Key; and Request limits with Request timeout (seconds), Maximum upload size (MB), Maximum download size (MB), and Save Limits.](docs/images/screenshots/settings-dialog.png)

| Setting                        | Default | Range      | What it limits                                                                                  |
| ------------------------------ | ------- | ---------- | ----------------------------------------------------------------------------------------------- |
| **Request timeout (seconds)**  | 1800    | 10 to 3600 | How long one request may take, from sending to the last download, time in fal's queue included. |
| **Maximum upload size (MB)**   | 100     | 1 to 100   | Each image, mask, audio, or video uploaded to fal.                                              |
| **Maximum download size (MB)** | 512     | 16 to 4096 | The largest result or output file accepted.                                                     |

## Models

Each paid node runs any fal model that makes its kind of output. Type the
model ID in `model`: the model's name on fal, such as
`alibaba/wan-3.0/reference-to-video`. The default is the node's starting
model:

| Node            | Runs models that make | Default model                                |
| --------------- | --------------------- | -------------------------------------------- |
| Image: Generate | Images                | `fal-ai/flux-2/klein/4b`                     |
| Video: Generate | Video                 | `fal-ai/ltx-2.3-22b/distilled/text-to-video` |
| Audio: Generate | Audio                 | `fal-ai/minimax/speech-2.8-turbo`            |
| Text: Generate  | Text                  | `fal-ai/elevenlabs/speech-to-text/scribe-v2` |
| 3D: Generate    | 3D models             | `fal-ai/trellis-2`                           |

A node's kind comes from what the model returns, not from fal's category, so
an upscaler, a background remover, and a lip-sync model each run in the node
for what they make. Model-training models and realtime models are not run.

Before anything is paid, the node reads the model from fal's public list of
models, with its settings and outputs. It reads each model once while ComfyUI
runs, free and without needing the key, and waits when fal asks it to read
more slowly. The checks it makes are in [When a node stops](#when-a-node-stops);
every value is checked by fal itself, and its refusal names the setting and
gives fal's reason.

`arguments` is a JSON object of the model's settings under fal's names, such
as `{"resolution": "480p", "duration": 5}`. A value goes as written: write
`"5"` where fal lists the text `"5"`. Settings you leave out keep fal's
defaults, which are sometimes the most expensive choice, such as 1080p on Wan
3.0. **Model: Info** lists every setting, its choices, and its default.

## Files and uploads

Give a model a file with **File: Add**. Set `field` to the model's file
input under fal's name, such as `image_url` or `reference_audio_urls`, and
connect the file to `file`, or type a link into it. `file` takes:

- A link.
- `files` from another fal node. The link goes on as it is, with no upload,
  so the next model gets fal's original file.
- An image, mask, audio, or video from a ComfyUI node. The paid node uploads
  it to fal first.

Chain **File: Add** nodes for several files, and connect the last `files` to
the paid node's `files`. Files for the same input keep their order in the
chain. A link can also go straight into `arguments`.

An input whose name ends in `_url` takes exactly one file. An input ending in
`_urls` always gets a list, even with one file: one voice clip for
`reference_audio_urls` on Wan 3.0 goes as a list of one. A single link typed
in `arguments` for such an input goes as a list too.

Uploads and the files fal makes are public links: anyone with the link can
open the file. They last as long as your fal account's storage setting says,
at least 7 days by default. Change it on fal's dashboard, or set
`expiration_duration_seconds` in **Request Options** for the files a request
makes. Each request's inputs and result are also kept on fal for 30 days, for
the request history on its dashboard. Turn off `store_io` in **Request
Options** to stop that for a request: fal still lists the request in its
history, with no input or output, and its result is gone within about an hour
and a half.

## Caching and reruns

- Change `run_number` to send the same request again. ComfyUI reuses a
  node's last result while none of its inputs change.
- Unless `arguments` sets `seed`, fal picks a new seed for each request.
- Saving a different key invalidates the cached results; changing settings
  does not.
- Every request is sent once. The extension also asks fal not to run a
  request again after a server error and not to send it to a stand-in model.
  Turn off `no_retry` or `disable_fallback` in **Request Options** to let fal
  do either.
- A file is uploaded once while ComfyUI runs; a rerun sends the same link.
- Cancelling also cancels the request at fal. A request still waiting in fal's
  queue never runs. One that has started may still finish and be billed.

## Recover a request

Every paid node records each request as soon as fal accepts it. The request
keeps running, and may be billed, after a restart or when the **Request
timeout (seconds)** passes, and after a cancel once fal has started it.
Collect it with **Request: Download** (press R to list new requests). A
request leaves the list once its files are downloaded, or when fal no longer
has its result. A finished result stays on fal for a limited time, and one
sent with `store_io` off is gone within about an hour and a half, so collect
it soon.

## Limits

The extension adds no limits of its own to what a request holds. Only your
settings and the model's limits apply: the **Request limits** in **fal
Settings**, and the limits **Model: Info** reports. A request outside the
model's limits is refused by fal, which also runs a limited number of your
requests at once while the rest wait in its queue
([fal's concurrency limits](https://fal.ai/docs/documentation/model-apis/concurrency-limits)).

## When a node stops

Paid nodes check these before uploading or sending anything. Every paid node
stops when:

- `model` is empty, fal has no model with that ID, or the model makes another
  kind of output or nothing a fal node can return.
- `prompt` is set and the model takes no `prompt`, or `arguments` sets
  `prompt` too.
- `arguments` is not a JSON object, or names a setting the model does not
  take.
- **File: Add** names an input the model does not take, one that is not a
  file input, or one `arguments` also sets.
- An input ending in `_url` gets more than one file, or a list holds more
  files than the model takes.
- A required setting or file input has nothing, including a file input fal
  would fill with its own sample file.
- A connected file is a kind the input does not take, such as audio in an
  image input.
- A file is over the upload limit.

**File: Add** stops when `field` is empty or does not end in `_url` or
`_urls`, when nothing is connected and `file` is empty, or when `file` is not
an `https://` link.

**Request: Download** stops when the chosen request is not recorded on this
server.

**Model: Info** stops when `model` is empty or fal has no model with that ID.

## Use from another extension

Another extension can call these nodes instead of copying a model's settings:

```python
clone = nodes.NODE_CLASS_MAPPINGS["FalModelInfo"].PREPARE_CLASS_CLONE(None)
clone.hidden = io.HiddenHolder.from_dict({})
output = await clone.execute(model="alibaba/wan-3.0/reference-to-video")
model = json.loads(output.args[0])
```

- Call a node by its ID on a class clone with an empty hidden holder, as above.
  A called node leaves the calling node's progress bar alone.
- **File: Add** and **Request Options** return at once; await every other
  node.
- A paid node takes `model`, `prompt`, and `arguments` as text, the last a
  JSON object of the model's settings under fal's names. Files go in `files`,
  the output of **File: Add**.
- A paid node takes plain values. **File: Add** takes every input as a list,
  such as `field=["reference_audio_urls"]`, and returns its files as one
  value.
- Read a model's settings, choices, and limits with **Model: Info** instead of
  copying them.
- A failed request raises an error whose `code` names its kind, such as
  `rate_limited`, `timeout`, or `uncertain`. Check `code`, not the message
  text, which can change.
- Do not send a failed paid request again: it may have run and been billed.

## Update or remove

To update, replace the `custom_nodes/fal-ai` folder, install its
`requirements.txt` with ComfyUI's Python, and restart. Open the updated
examples in a new tab.

To remove it, move the folder out of `custom_nodes` and restart. The
[private folder](#keys-and-access) stays; delete it to remove the saved key,
settings, and request records.

## Development

### Setup

Point the checks at ComfyUI in `.mise.local.toml`, which Git ignores:

```toml
[env]
COMFYUI_PATH = "/path/to/ComfyUI"
COMFYUI_PYTHON = "/path/to/ComfyUI/.venv/bin/python"
```

Then install the tools, dependencies, Semgrep rules, and Git hooks:

```shell
mise trust && mise run repo:setup
```

### Generated files

```shell
mise run repo:deps:export          # Regenerate requirements.txt from pyproject.toml
mise run comfy:frontend:build      # Build the browser files
mise run comfy:workflows:build     # Build the example workflows
```

The example workflows are generated from `scripts/workflows/descriptions/`:
one module per category, the group notes in `notes.py`, and the titles in
`texts.py`. The build reads the node definitions through ComfyUI's Python. It
also writes every subgraph to `subgraphs/`, which ComfyUI lists under
**Subgraph Blueprints** in its node library.

### Full check

```shell
mise run repo:check                # Run every check below
```

This runs `repo:deps:verify`, `repo:format:check`, `repo:lint`, `repo:type`,
`comfy:frontend:check`, `comfy:nodes:check`, `comfy:workflows:check`,
`repo:security`, `repo:licenses`, and `repo:links:external`.

### Format

```shell
mise run repo:format               # Format Python, pyproject.toml, web, and Markdown files
mise run repo:format:check         # List files that need formatting
```

This uses Ruff for Python, pyproject-fmt for `pyproject.toml`, and Prettier for
web and Markdown files.

### Lint

```shell
mise run repo:lint                 # Run every linter
```

- `repo:lint:policy`: repository structure, naming, and function rules.
- `repo:lint:python`: Ruff, the custom Python rules, import-linter, pydoclint,
  interrogate, deptry, and vulture.
- `repo:lint:frontend`: ESLint, naming, stylelint, knip, madge, and jscpd.
- `repo:lint:shell`, `repo:lint:hooks`, and `repo:lint:mise`: shell syntax,
  ShellCheck, shfmt, and the shell rules.
- `repo:lint:docs`: markdownlint, typos, and local links.
- `repo:lint:quality`: the quality tools and their configuration.

### Types

```shell
mise run repo:type                 # Check Python and TypeScript types
```

This runs basedpyright in strict mode against your ComfyUI installation, and
`tsc` for the browser code.

### Generated-file checks

```shell
mise run comfy:frontend:check      # The browser files match their source
mise run comfy:nodes:check         # The help pages and menus match the nodes
mise run comfy:workflows:check     # The workflows match their descriptions, and the README links each one
```

The workflow check also requires every node to appear in at least one
workflow.

### Security and licenses

```shell
mise run repo:security             # Run the secret, code, and dependency scanners
mise run repo:licenses             # Check dependency licenses
```

`repo:security` runs Gitleaks, Bearer, Bandit, the Python and Bun advisory
audits, Semgrep with the pinned rules, and CodeQL for Python and the browser
code.

### Git hooks

`mise run repo:setup` installs the hooks:

- **pre-commit** checks for private files and staged secrets, then runs the
  source, formatting, type, and browser-file checks.
- **commit-msg** checks the [conventional
  commit](https://www.conventionalcommits.org/) format, `type(scope): subject`.
- **pre-push** runs the full check.

To skip a run, set `SKIP_HOOKS=1`. To skip only part of it, set `SKIP_LINT=1`
(the pre-commit checks), `SKIP_ENV_CHECK=1` (the private-file check), or
`SKIP_COMMITLINT=1` (the commit message check).

### Test a change

Testing is manual: restart ComfyUI after Python changes, or rebuild the
browser files and reload after browser changes, then run the affected
workflows with inexpensive models.

### Import rules

Each package imports only the packages below it:

```text
src.nodes
src.comfy
src.fal | src.settings
src.storage
src.types
src.config
```

- ComfyUI is imported only in `src/nodes/`, `src/comfy/`, and the package's
  `__init__.py`.
- All fal requests are in `src/fal/`. `src/fal/transport.py` is the one place
  that sends the API key.
- Every message and every other fixed value, such as a limit, a file name, or
  a route, is a constant in `src/config/`. The dialog text is in
  `web/scripts/text.ts`.
- The import contracts in `pyproject.toml` enforce these rules.
- Node names, descriptions, and tooltips are in each node's `io.Schema` call,
  and the tooltips of the inputs every paid node shares are in
  `src/config/inputs.py`. A model's own settings come from fal, read when a
  node runs.

### Function names

Every function in `src/`, `scripts/`, and `__init__.py` starts with a verb from
the table in `rules/NAMING.md`, or is an `is_` or `has_` predicate. In each
module and class, private functions come first, `__all__` lists no private
name, and a function only its own module uses is private. `repo:lint:policy`
checks all four.

### Images

The README's and this guide's images are in `docs/images/`:

- `brand/banner.svg`, `diagrams/node-map.svg`, and the four `badges/*.svg`
  files are SVG files; edit them as text. They use black `#06080D`, surfaces
  `#10141B`, hairlines `#232A35`, light text `#EEF3FF`, muted text `#8A93A3`,
  accent `#A284FF`, and the violet gradient `#C0B1FF` to `#8553FF`. Headings
  use Helvetica Neue with tight spacing; labels use a monospace font in
  wide-spaced capitals.
- `brand/logo.png` is the extension's mark: a rounded node tile in violet
  `#A284FF` to `#762FF8`, with a lightning bolt cut out and a cyan `#99EDFF`
  output socket on its right edge, at 400 × 400 pixels on a transparent
  background. The banner draws the same mark, and `pyproject.toml` names
  `brand/logo.png` as the Registry icon.
- The node map has one card for each kind of node. A violet square marks a
  node that sends a paid request and a hollow square one that bills nothing.
- The badges under the banner name the ComfyUI, frontend, and Python versions
  and the license, as black pills with a violet value; update them when those
  change.
- `screenshots/video-02-workflow.png` is video-02 at 100% zoom, with link
  midpoint markers off.
- `screenshots/video-generate-node.png` is a new **Video: Generate** node, 420
  pixels wide, at 100% zoom, with `alibaba/wan-3.0/reference-to-video` in
  `model`, a prompt, and `arguments` typed in.
- `screenshots/settings-dialog.png` is the **fal Settings** dialog with
  default settings and a saved key.

No image shows fal's logo. Keep each image under 100 KB, and give it alt
text.

### Change text

- **A message:** edit its constant in `src/config/messages/`, and its entry
  under [troubleshooting](#troubleshooting) if it has one.
- **A node's labels or tooltips:** edit its `io.Schema` call in `src/nodes/`,
  or `TOOLTIPS` in `src/config/inputs.py` for the inputs every paid node
  shares, then its help page in `web/docs/`. A model's own settings and
  descriptions come from fal and are not part of the extension.
- **The dialogs:** edit `web/scripts/text.ts`, then rebuild the browser files.
- **A workflow's notes:** edit `scripts/workflows/descriptions/notes.py`; for
  titles, `texts.py`; for nodes, models, or prompts, the workflow's module. Then
  rebuild the workflows.
- **A node's default model:** edit `DEFAULT_MODELS` in
  `src/config/models.py`, then the table under [models](#models), the node's
  help page, and the examples that rely on the default.

## Package and publish

The Comfy Registry package is made with
[comfy-cli](https://github.com/Comfy-Org/comfy-cli). These steps use version
1.20.0.

1. Create a publisher and a publishing key in the
   [Comfy Registry](https://docs.comfy.org/registry/publishing).
2. In `pyproject.toml`, set `[tool.comfy].PublisherId` to your publisher ID, add
   `Repository` under `[project.urls]`, and set `[project].version`. Use a new
   version number for each release.
3. Rebuild the generated files:

    ```sh
    mise run repo:deps:export
    mise run comfy:frontend:build
    mise run comfy:workflows:build
    ```

4. Commit everything. The packer takes only files Git tracks, and
   `.comfyignore` leaves out development files.
5. Build and check the package:

    ```sh
    mise run comfy:release:package
    ```

    This runs the full check, builds `node.zip` with `comfy node pack`, lists
    its contents, and scans it for secrets.

6. Publish:

    ```sh
    mise run comfy:release:publish
    ```

    This repeats the package checks, then asks for the publishing key.

7. Install the published version with ComfyUI Manager, and check that the nodes,
   menus, help pages, and templates load.

Publishing rebuilds the archive from the checkout, so publish the same commit
you packaged.

## Troubleshooting

Most messages say what to do. These need more.

### Set your fal API key in fal Settings

Save the key in **fal Settings**, or set `FAL_KEY` where ComfyUI starts and
restart.

### The API key was not accepted by fal

`FAL_KEY` takes precedence over the saved key; check both. Paste the whole key,
both parts and the colon.

### This API key may not make this request on fal

The key may lack permission for this model, or the account may have run out
of credits. Check both on fal's dashboard.

### The model is not on fal

Copy the model ID from the model's page on fal. The model may have been
renamed or removed; **Model: Info** shows what fal lists now.

### The content check on fal refused an input

Change the prompt or the input. An image that fal's check flags after making
it comes back black; `has_nsfw_concepts` in `result` says which.

### This request or its result is no longer on fal

A finished result stays on fal for a limited time. With `store_io` off in
**Request Options**, it is gone within about an hour and a half. Change
`run_number` on the node that made the request to send it again.

### The fal model listing asked to wait

The node reads each model from fal before paying, and nothing was sent. When
fal asks it to read more slowly, the node waits by itself, but only within
the **Request timeout (seconds)**. Run again in a few minutes.

### That fal setting cannot be changed here

Reload the window.

### The fal settings file has an unknown setting

Delete the settings file in the [private folder](#keys-and-access) to return
to the defaults.

### A fal state file is larger than expected

Delete it; a request record can go once you have its files.
