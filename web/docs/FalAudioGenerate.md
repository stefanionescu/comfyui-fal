# Audio: Generate

Runs any fal model that makes audio: speech, voice changes, music, sound
effects, and the stems of a song. It outputs the audio and the fal link of
every file the model made.

## Inputs

| Input           | What it takes                                                                                                |
| --------------- | ------------------------------------------------------------------------------------------------------------ |
| `files`         | Input audio from **File: Add**, under the model's field name, such as `audio_url`.                           |
| `options`       | Settings from **Request Options**.                                                                           |
| `model`         | The model's ID on fal, such as `elevenlabs/tts/eleven-v4`. The default is `fal-ai/minimax/speech-2.8-turbo`. |
| `output_format` | A file type, such as `mp3`. Empty sends nothing.                                                             |
| `seed`          | `default`, or `custom` and a number. The same seed repeats a result.                                         |
| `run_number`    | Change this number to send the same request again.                                                           |
| `voice`         | The voice, by the name or ID the model lists, for a voice model. Empty sends nothing.                        |
| `prompt`        | The text sent as the model's `prompt`. Leave it empty for a model without one.                               |
| `text`          | The words to speak, for a voice model. Empty sends nothing.                                                  |
| `arguments`     | The model's other settings as JSON, under fal's names, such as `{"speed": 1.1}`.                             |

A setting left empty or at `default` sends nothing, so the model uses its own value. A setting you set, and
each text input, goes under its own name, and only a model with a field of that name takes it.

Copy the model ID and its field names from the model's page on fal, or read
them with **Model: Info**. Many voice models take their words as `text`, not
`prompt`. A setting left out takes fal's default.

## Outputs

| Output   | What it carries                                                                          |
| -------- | ---------------------------------------------------------------------------------------- |
| `audio`  | Every audio file, such as each stem of a song, in fal's order. `result` names each stem. |
| `files`  | The fal link of every file the model made, for the next fal node.                        |
| `result` | fal's whole result as JSON, such as timestamps or a new voice ID.                        |

## Use

1. Type the model ID in `model`.
2. Write the words in `prompt`, or in `arguments` as `text`, as the model
   takes them, with any other settings, such as `voice`.
3. To change or split audio, connect **File: Add** with the audio and the
   model's field name, such as `audio_url`, to `files`.
4. Connect `audio` to the `SaveAudioAdvanced` node or to **Preview Audio**,
   and select **Run**.

ComfyUI reads formats such as MP3, WAV, FLAC, and Opus, but not raw PCM,
µ-law, or A-law. Choose one it reads in the model's `output_format`.

Examples: **audio-01-voice-a-script** and **audio-02-split-a-song-into-stems**.

[fal audio models](https://fal.ai/models?categories=text-to-speech)
