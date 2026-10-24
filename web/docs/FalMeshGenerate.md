# 3D: Generate

Runs any fal model that makes a 3D model, from images, a prompt, or another
model. It outputs every 3D file the model made and the fal link of every file.
The links include the textures and previews.

## Inputs

| Input        | What it takes                                                                                                 |
| ------------ | ------------------------------------------------------------------------------------------------------------- |
| `files`      | Images or a model from **File: Add**, each under the model's field name, such as `image_url`.                 |
| `options`    | Settings from **Request Options**.                                                                            |
| `model`      | The model's ID on fal, such as `fal-ai/hunyuan-3d/v3.1/rapid/image-to-3d`. The default is `fal-ai/trellis-2`. |
| `run_number` | Change it to send the same request again.                                                                     |
| `prompt`     | The text sent as the model's `prompt`, for a model that makes 3D from text. Leave it empty otherwise.         |
| `arguments`  | The model's other settings as JSON, under fal's names, such as `{"resolution": 512}`.                         |

Copy the model ID and its field names from the model's page on fal, or read
them with **Model: Info**. A setting left out takes fal's default.

## Outputs

| Output     | What it carries                                                                   |
| ---------- | --------------------------------------------------------------------------------- |
| `model_3d` | Every 3D file, such as GLB or OBJ. Some models make one model in several formats. |
| `files`    | The fal link of every file the model made, among them textures and previews.      |
| `result`   | fal's whole result as JSON.                                                       |

## Use

1. Type the model ID in `model`.
2. Connect **File: Add** with an image of the subject and the model's field
   name, such as `image_url`, to `files`, or write a prompt.
3. Connect `model_3d` to **Save 3D Model**, and select **Run**. A model takes
   from under a minute to several minutes.

Example: `3d-01-turn-a-product-into-a-3d-model`.

If you cancel while the request waits in fal's queue, fal drops it. Once the
request has started, it may still finish, and fal may bill it. This can happen
even if you cancel, ComfyUI restarts, or the request timeout in **fal
Settings** passes. Collect it with **Request: Download**.

[fal 3D models](https://fal.ai/models?categories=image-to-3d)
