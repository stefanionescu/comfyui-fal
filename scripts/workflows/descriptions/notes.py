"""The group notes and subgraph descriptions of the shipped workflows, in plain language."""

KEY_STEP = "1. Set your key in **ComfyUI menu → Extensions → fal → fal Settings**.\n"

WORKFLOW_TEXTS = {
    "image-01-design-a-host": {
        "input": (
            KEY_STEP + "2. Describe your host in **Host**: how they look and what they wear.\n"
            "3. Press **Run**. Both images are saved under `image/fal`."
        ),
        "design": (
            "GPT Image 2.5 Sunburst draws the host from the waist up, in a portrait frame. `arguments` holds the "
            "model's own settings, written by the names fal gives them: here `image_size` and `quality`. **Model: "
            "Info** lists every setting a model takes.\n\n"
            "To draw with another model, open **Design** and type another `model`, the model's name on fal."
        ),
        "design_description": "Draws the host and saves the image.",
        "turn": (
            "**File: Add** passes the host image's fal link, its address on fal storage, to the edit as "
            "`image_urls`, the field where the model takes the images to edit. Nothing is uploaded again. GPT Image "
            "2.5 Sunburst then draws the same person waving.\n\n"
            "Change the prompt in **Turn** to pose the host another way. Set `quality` in `arguments` to `low` or "
            "`medium` for quick drafts."
        ),
        "turn_description": "Draws the same host waving and saves the image.",
    },
    "image-02-cut-out-a-product": {
        "input": (
            KEY_STEP + "2. Describe the product in **Product**, and name it in a few words in **Item**.\n"
            "3. Press **Run**. The enlarged photo and the transparent cut-out are saved under `image/fal`."
        ),
        "photo": (
            "FLUX.2 klein, the image node's default model, draws the product photo. Its `files` output passes the "
            "photo's fal link, its address on fal storage, on to **Upscale**.\n\n"
            "To start from your own photo, add **Load Image** and connect it to **Upscale**'s `files` input. The "
            "pack uploads it to fal storage, so the model can read it."
        ),
        "photo_description": "Draws the product photo.",
        "upscale": (
            "**File: Add** gives Topaz the photo as `image_url`, the field where it takes its image. Topaz enlarges "
            "the photo two times and keeps edges sharp, then saves it as a PNG. Raise `upscale_factor` in "
            "`arguments` up to 4 for print."
        ),
        "upscale_description": "Enlarges the product photo and saves it.",
        "cut_out": (
            "Bria Extract Object cuts out the object **Item** names. It returns two images: the cut-out and a "
            "black-and-white mask. **Get Item From List** takes the cut-out and its mask from `masks`, and **Join "
            "Image with Alpha** gives the cut-out back its transparency, so the saved PNG has a clear background."
        ),
        "cut_out_description": "Cuts out the product and saves it with a clear background.",
    },
    "image-03-make-a-poster-series": {
        "input": (
            KEY_STEP + '2. Describe the series in **Brief**. Start with how many you want, such as "Generate 4 '
            'posters".\n'
            "3. Press **Run**. Up to four posters are saved under `image/fal`."
        ),
        "model": (
            "**Model: Info** shows what fal says a model takes: each setting by fal's name, its choices, and its "
            "limits. It is free and needs no key. **Info** shows Seedream 5.0 lite. Copy the settings you want into "
            "a node's `arguments`, the model's own settings.\n\n"
            "Seedream has two counts. `num_images` makes separate images, and `max_images` lets one generation make "
            "up to that many related images. **Series** sets `max_images`, so the posters share one style."
        ),
        "series": (
            "Seedream 5.0 lite draws the posters as one related series, so the style and the typeface match. It "
            "decides how many to make from the prompt, up to the four `max_images` allows, and each poster it makes "
            "is billed."
        ),
        "series_description": "Draws the poster series and saves it.",
    },
}

__all__ = ["WORKFLOW_TEXTS"]
