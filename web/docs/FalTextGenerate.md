# Text: Generate

Runs any fal model that makes text: transcripts of speech, descriptions of and
answers about images and video, and chat answers. It outputs the text, fal's
whole result, and the fal link of any file the model made.

## Inputs

| Input        | What it takes                                                                                                                  |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `files`      | Audio, images, or video from **File: Add**, each under the model's field name, such as `audio_url`.                            |
| `options`    | Settings from **Request Options**.                                                                                             |
| `model`      | The model's ID on fal, such as `fal-ai/moondream3-preview/query`. The default is `fal-ai/elevenlabs/speech-to-text/scribe-v2`. |
| `run_number` | Change it to send the same request again.                                                                                      |
| `prompt`     | The question or instruction sent as the model's `prompt`. Leave it empty for a model without one.                              |
| `arguments`  | The model's other settings as JSON, under fal's names, such as `{"diarize": true}`.                                            |

Copy the model ID and its field names from the model's page on fal, or read
them with **Model: Info**. OpenRouter's models on fal also need the
OpenRouter model to use, in `arguments`, such as
`{"model": "google/gemini-2.5-flash"}`. A setting left out takes fal's
default.

## Outputs

| Output   | What it carries                                                 |
| -------- | --------------------------------------------------------------- |
| `text`   | The model's text: a transcript, a description, or an answer.    |
| `files`  | The fal link of any file the model made, for the next fal node. |
| `result` | fal's whole result as JSON, such as word timings and speakers.  |

## Use

1. Type the model ID in `model`, and write the question in `prompt` if it
   takes one.
2. Connect **File: Add** with the audio, image, or video and the model's field
   name, such as `audio_url`, to `files`.
3. Connect `text` to **Preview as Text** or **Save Text**, and select **Run**.

Examples: **text-01-transcribe-a-voice-note** and
**text-02-describe-a-product-photo**.

[fal speech-to-text and vision models](https://fal.ai/models?categories=speech-to-text)
