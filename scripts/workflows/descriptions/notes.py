"""The group notes and subgraph descriptions of the shipped workflows, in plain language."""

KEY_STEP = '1. Set your key in **ComfyUI menu → Extensions → fal → fal Settings**.\n'
RECOVER_NOTE = (
    "If you cancel while the request still waits in fal's queue, fal drops it and bills nothing. A request fal has "
    'already started may still finish and be billed. Collect it with **video-05-recover-a-video**.'
)
MODEL_RECOVER_NOTE = (
    "If you cancel while the request still waits in fal's queue, fal drops it and bills nothing. A request fal has "
    'already started may still finish and be billed. Collect it with **Request: Download** and **Save 3D Model**.'
)

WORKFLOW_TEXTS = {
    'image-01-design-a-host': {
        'input': (
            KEY_STEP + '2. Describe your host in **Host**: how they look and what they wear.\n'
            '3. Press **Run**. Both images are saved under `image/fal`.'
        ),
        'design': (
            'GPT Image 2.5 Sunburst draws the host from the waist up, in a portrait frame. `arguments` holds the '
            "model's own settings, written by the names fal gives them: here `image_size` and `quality`. **Model: "
            'Info** lists every setting a model takes.\n\n'
            "To draw with another model, open **Design** and type another `model`, the model's name on fal."
        ),
        'design_description': 'Draws the host and saves the image.',
        'turn': (
            "**File: Add** passes the host image's fal link, its address on fal storage, to the edit as "
            '`image_urls`, the field where the model takes the images to edit. Nothing is uploaded again. GPT Image '
            '2.5 Sunburst then draws the same person waving.\n\n'
            'Change the prompt in **Turn** to pose the host another way. Set `quality` in `arguments` to `low` or '
            '`medium` for quick drafts.'
        ),
        'turn_description': 'Draws the same host waving and saves the image.',
    },
    'image-02-cut-out-a-product': {
        'input': (
            KEY_STEP + '2. Describe the product in **Product**, and name it in a few words in **Item**.\n'
            '3. Press **Run**. The enlarged photo and the transparent cut-out are saved under `image/fal`.'
        ),
        'photo': (
            "FLUX.2 klein, the image node's default model, draws the product photo. Its `files` output passes the "
            "photo's fal link, its address on fal storage, on to **Upscale**.\n\n"
            "To start from your own photo, add **Load Image** and connect it to **Upscale**'s `files` input. The "
            'pack uploads it to fal storage, so the model can read it.'
        ),
        'photo_description': 'Draws the product photo.',
        'upscale': (
            '**File: Add** gives Topaz the photo as `image_url`, the field where it takes its image. Topaz enlarges '
            'the photo two times and keeps edges sharp, then saves it as a PNG. Raise `upscale_factor` in '
            '`arguments` up to 4 for print.'
        ),
        'upscale_description': 'Enlarges the product photo and saves it.',
        'cut_out': (
            'Bria Extract Object cuts out the object **Item** names. It returns two images: the cut-out and a '
            'black-and-white mask. **Get Item From List** takes the cut-out and its mask from `masks`, and **Join '
            'Image with Alpha** gives the cut-out back its transparency, so the saved PNG has a clear background.'
        ),
        'cut_out_description': 'Cuts out the product and saves it with a clear background.',
    },
    'image-03-make-a-poster-series': {
        'input': (
            KEY_STEP + '2. Describe the series in **Brief**. Start with how many you want, such as "Generate 4 '
            'posters".\n'
            '3. Press **Run**. Up to four posters are saved under `image/fal`.'
        ),
        'model': (
            "**Model: Info** shows what fal says a model takes: each setting by fal's name, its choices, and its "
            'limits. It is free and needs no key. **Info** shows Seedream 5.0 lite. Copy the settings you want into '
            "a node's `arguments`, the model's own settings.\n\n"
            'Seedream has two counts. `num_images` makes separate images, and `max_images` lets one generation make '
            'up to that many related images. **Series** sets `max_images`, so the posters share one style.'
        ),
        'series': (
            'Seedream 5.0 lite draws the posters as one related series, so the style and the typeface match. It '
            'decides how many to make from the prompt, up to the four `max_images` allows, and each poster it makes '
            'is billed.'
        ),
        'series_description': 'Draws the poster series and saves it.',
    },
    'audio-01-voice-a-script': {
        'input': (
            KEY_STEP + '2. In **Script**, write what the host says after `"text":`, inside the quotation marks.\n'
            '3. In **Sound**, describe the background sound the same way.\n'
            '4. Press **Run**. The voice, the background, and the two mixed are saved under `audio/fal`.'
        ),
        'voice': (
            "ElevenLabs v4 reads the script aloud. **Script** holds its `arguments`, the model's own settings by "
            'fal\'s names: ElevenLabs takes its words as `text`, not `prompt`. Add `"voice"` with another '
            'ElevenLabs voice name to change the voice; **Model: Info** lists every setting it takes.'
        ),
        'voice_description': 'Reads the script aloud and saves the voice.',
        'ambience': (
            'ElevenLabs sound effects makes eight seconds of background sound from **Sound**. Change '
            '`duration_seconds` there for up to 22 seconds.'
        ),
        'ambience_description': 'Makes the background sound and saves it.',
        'mix': (
            "**Merge Audio**, one of ComfyUI's own nodes, lays the voice over the background and cuts the background "
            "to the voice's length."
        ),
        'mix_description': 'Mixes the voice over the background and saves it.',
    },
    'audio-02-split-a-song-into-stems': {
        'input': (
            KEY_STEP + '2. Describe the music in **Song**: its style, its instruments, and its speed.\n'
            '3. Press **Run**. The song and one clip per instrument are saved under `audio/fal`.'
        ),
        'compose': (
            'Stable Audio 3 small makes a 20-second instrumental from **Song**. `duration` in `arguments`, the '
            "model's own settings, sets the length. Its `files` output passes the song's fal link, its address on "
            'fal storage, on to **Split**, so it is not uploaded again.'
        ),
        'compose_description': 'Makes the song and saves it.',
        'split': (
            '**File: Add** gives Demucs the song as `audio_url`. Demucs splits it into one clip per instrument (a '
            'stem): vocals, drums, bass, guitar, piano, and everything else. `audio` holds the six clips, and **Save '
            'Audio (Advanced)** saves each. To get fewer, put `stems` in `arguments`, such as '
            '`{"stems": ["vocals", "drums"]}`.'
        ),
        'split_description': 'Splits the song into one clip per instrument and saves each.',
    },
    'video-01-animate-a-host': {
        'input': (
            KEY_STEP + '2. Describe your host in **Host**, and what they do in **Scene**.\n'
            '3. Press **Run**. The video is saved under `video/fal`.'
        ),
        'portrait': (
            "FLUX.2 klein draws the host in a vertical frame. This image becomes the video's first frame. `files` "
            'passes its fal link, its address on fal storage, on to **Animate**, so nothing is uploaded again.'
        ),
        'portrait_description': 'Draws the host.',
        'animate': (
            '**File: Add** gives Wan 3.0 the host as `start_image_url`, the field for the first frame. Wan starts on '
            'the host and makes a five-second 480p video with sound. `arguments` sets `resolution` and `duration`, '
            "because Wan's own default is 1080p. Raise `duration` for up to 30 seconds.\n\n" + RECOVER_NOTE
        ),
        'animate_description': 'Turns the host into a video and saves it.',
    },
    'video-02-give-a-host-a-voice': {
        'input': (
            KEY_STEP + '2. Describe the host in **Host** and the product in **Product**.\n'
            '3. In **Voice**, write any sentence after `"text":`, inside the quotation marks. The host will sound '
            'like this clip.\n'
            "4. In **Scene**, say what happens, and put the host's words in double quotation marks.\n"
            '5. Press **Run**. The voice clip and the video are saved under `audio/fal` and `video/fal`.'
        ),
        'cast': (
            "FLUX.2 klein draws the host in a vertical frame. `files` passes the image's fal link, its address on "
            'fal storage, on to **References**.'
        ),
        'cast_description': 'Draws the host.',
        'packshot': 'FLUX.2 klein draws the product on a plain background.',
        'packshot_description': 'Draws the product.',
        'speak': (
            "ElevenLabs v4 reads the sentence in **Voice** aloud. **Voice** holds the model's `arguments`, its own "
            "settings by fal's names, and ElevenLabs takes its words as `text`. Wan copies the sound of this voice, "
            "not its words. To use a recording of a real voice, connect **Load Audio** to the last **File: Add**'s "
            '`file` instead.'
        ),
        'speak_description': 'Reads the voice sample aloud and saves it.',
        'references': (
            'Three **File: Add** nodes hand Wan its files. Each names the field, the name Wan gives that input: the '
            'host, then the product, go to `reference_image_urls`, and the voice clip to `reference_audio_urls`. '
            '**Scene** calls them Image 1, Image 2, and Audio 1, in this order. Chain more **File: Add** nodes for up '
            'to 10 images and five clips.'
        ),
        'film': (
            'Wan 3.0 films the host with the product, five seconds at 480p in a 9:16 frame, speaking the words in '
            '**Scene** in the voice from **Speak**. `reference_audio_urls` is a list on fal, so the one clip goes as '
            'a list of one.\n\n' + RECOVER_NOTE
        ),
        'film_description': "Films the host with the product, in the host's voice, and saves the video.",
    },
    'video-03-make-a-talking-avatar': {
        'input': (
            KEY_STEP + '2. Describe the person in **Person**.\n'
            '3. In **Line**, write what they say.\n'
            '4. Press **Run**. The voice and the talking video are saved under `audio/fal` and `video/fal`.'
        ),
        'face': (
            'FLUX.2 klein draws the person facing the camera. A clear, front-facing face works best for lip sync.'
        ),
        'face_description': 'Draws the person.',
        'speech': (
            "MiniMax Speech 2.8 Turbo, the audio node's default model, reads **Line** aloud as its `prompt`. To "
            "choose another voice, set `voice_setting` in `arguments`, the model's own settings by fal's names; "
            '**Model: Info** lists them.'
        ),
        'speech_description': 'Reads the line aloud and saves it.',
        'talk': (
            'Two **File: Add** nodes give FlashTalk the face as `image_url` and the voice as `audio_url`. FlashTalk '
            "moves the person's lips and face to match the voice. The video is as long as the voice clip.\n\n"
            + RECOVER_NOTE
        ),
        'talk_description': 'Makes the person speak the line and saves the video.',
    },
    'video-04-upscale-a-clip': {
        'input': (
            KEY_STEP + '2. Describe the shot in **Shot**.\n'
            '3. Press **Run**. The short clip and its 1080p version are saved under `video/fal`.'
        ),
        'clip': (
            "LTX 2.3, the video node's default model, makes a two-second clip: `num_frames` 49 in `arguments`, at 24 "
            'frames a second. Raise `num_frames` for a longer clip.'
        ),
        'clip_description': 'Makes the short clip and saves it.',
        'enlarge': (
            '**File: Add** gives SeedVR the clip as `video_url`. SeedVR enlarges it to 1080p. **Request Options** '
            'sends this request at low priority: when other requests of yours wait for the same model on fal, they '
            'go first. It changes nothing else.\n\n' + RECOVER_NOTE
        ),
        'enlarge_description': 'Enlarges the clip to 1080p and saves it.',
    },
    'video-05-recover-a-video': {
        'recover': (
            'Use this after you cancel a video that fal had already started, after a run times out, or after '
            'ComfyUI restarts while a video is being made. fal keeps working on the request, and the pack keeps a '
            'record of it.\n\n' + KEY_STEP + '2. In `request`, choose the video. Each entry shows its request ID, its '
            'model, and when it started, in UTC. Press R to list requests started after the page loaded.\n'
            '3. Press **Run**. The video is saved under `video/fal`.\n\n'
            "A request leaves the list once its video is saved. fal keeps a finished request's result for a limited "
            'time, and the node says so when it is gone.'
        ),
    },
    'text-01-transcribe-a-voice-note': {
        'input': (
            KEY_STEP + '2. Upload a voice note in **Voice Note**.\n'
            '3. Press **Run**. The transcript is saved under `text/fal`.'
        ),
        'transcribe': (
            "**File: Add** gives ElevenLabs Scribe v2, the text node's default model, the voice note as `audio_url`. "
            'The pack uploads the note to fal storage first, so the model can read it. Scribe writes down what is '
            'said and tells speakers apart.\n\n'
            '**Words** shows the full result: each word with its start and end time and its speaker.'
        ),
        'transcribe_description': 'Transcribes the voice note and saves the transcript.',
    },
    'text-02-describe-a-product-photo': {
        'input': (
            KEY_STEP + '2. Describe the product in **Product**.\n'
            '3. Press **Run**. The description is saved under `text/fal`.'
        ),
        'photo': (
            'FLUX.2 klein draws the product photo. To describe your own photo, connect **Load Image** to '
            "**Describe**'s `files` input instead."
        ),
        'describe': (
            '**File: Add** gives Moondream 3 the photo as `image_url`. Moondream looks at it and answers the question '
            'in `prompt` with a two-sentence description. Change `prompt` to ask anything else about the photo.'
        ),
        'describe_description': 'Describes the photo and saves the text.',
    },
    '3d-01-turn-a-product-into-a-3d-model': {
        'input': (
            KEY_STEP + '2. Describe the product in **Product**.\n'
            '3. Press **Run**. The 3D model is saved as a GLB file under `3d/fal`.'
        ),
        'front': (
            'FLUX.2 klein draws the product on a plain white background, the kind of image 3D models work best from.'
        ),
        'front_description': 'Draws the product for the 3D model.',
        'build': (
            "**File: Add** gives TRELLIS 2, the 3D node's default model, the image as `image_url`. TRELLIS 2 turns it "
            'into a textured 3D model at its quickest setting, `resolution` 512 in `arguments`. **Save 3D Model** '
            'saves it and shows it.\n\n' + MODEL_RECOVER_NOTE
        ),
    },
}

__all__ = ['WORKFLOW_TEXTS']
