# Image: Generate

Runs any fal model that makes images: generating, editing, upscaling, and
cutting out. It outputs the images, a mask for each, and the fal link of every
file the model made.

## Inputs

| Input                 | What it takes                                                                                                  |
| --------------------- | -------------------------------------------------------------------------------------------------------------- |
| `files`               | Input images from **File: Add**, each under the model's field name, such as `image_urls`.                      |
| `options`             | Settings from **Request Options**.                                                                             |
| `model`               | The model's ID on fal, such as `openai/gpt-image-2.5/sunburst/edit`. The default is `fal-ai/flux-2/klein/4b`.  |
| `aspect_ratio`        | `default`, or `custom` and a shape, such as `16:9`.                                                            |
| `resolution`          | `default`, or `custom` and a size, such as `1K` or `720p`, as the model writes it.                             |
| `num_images`          | `default`, or `custom` and how many images to make.                                                            |
| `output_format`       | `default`, or `custom` and a file type, such as `png`.                                                         |
| `guidance_scale`      | `default`, or `custom` and how closely the image follows the prompt; higher follows it more.                   |
| `num_inference_steps` | `default`, or `custom` and how many steps the model takes; more is slower and often finer.                     |
| `seed`                | `default`, or `custom` and a number. The same seed repeats a result.                                           |
| `run_number`          | Change this number to send the same request again.                                                             |
| `prompt`              | The text sent as the model's `prompt`. Leave it empty for a model without one.                                 |
| `negative_prompt`     | What to leave out, for a model that takes it. Empty sends nothing.                                             |
| `arguments`           | The model's other settings as JSON, under fal's names, such as `{"image_size": "square_hd", "num_images": 2}`. |

Each setting at `default` sends nothing, so the model uses its own value. A setting at `custom`, and each
text input, goes under its own name, and only a model with a field of that name takes it.

Copy the model ID and its field names from the model's page on fal, or read
them with **Model: Info**. A setting left out takes fal's default. The node
checks the model and its fields with fal before it pays.

## Outputs

| Output   | What it carries                                                                                    |
| -------- | -------------------------------------------------------------------------------------------------- |
| `images` | Every image, each at its own size, in fal's order. Masks a model returns as pictures are here too. |
| `masks`  | One mask per image, from its transparency. White is transparent; opaque images are all black.      |
| `files`  | The fal link of every file the model made, for the next fal node.                                  |
| `result` | fal's whole result as JSON, such as the seed.                                                      |

## Use

1. Type the model ID in `model`, and write the prompt.
2. Add other settings to `arguments`, such as `{"image_size": "square_hd"}`.
3. To edit an image, connect **File: Add** with the model's image field,
   such as `image_url`, to `files`.
4. Connect `images` to **Save Image**, and select **Run**.

An image fal's safety checker flags comes back black.

Examples: **image-01-design-a-host**, **image-02-cut-out-a-product**, and
**image-03-make-a-poster-series**.

[fal image models](https://fal.ai/models?categories=text-to-image)
