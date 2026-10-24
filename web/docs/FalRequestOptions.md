# Request Options

Sets fal's request options for any number of paid nodes: queue priority,
retries, fallbacks, how long output files stay, and payload storage. At its
defaults it changes nothing: fal's retries and fallbacks stay off, as they
are for a node with no Request Options.

## Inputs

| Input                         | What it takes                                                                                   |
| ----------------------------- | ----------------------------------------------------------------------------------------------- |
| `queue_priority`              | `normal` sends nothing; `low` lets your other requests to the same model go first.              |
| `request_start_timeout`       | Seconds fal waits for a runner before it drops the request, unbilled; 0 means no limit.         |
| `no_retry`                    | On, the default, asks fal not to run the request again after a server error. Off lets it retry. |
| `disable_fallback`            | On, the default, keeps fal from sending the request to another model. Off allows it.            |
| `expiration_duration_seconds` | Seconds before fal deletes the files the request makes; 0 keeps your account's setting.         |
| `store_io`                    | Off asks fal to keep no copy of the prompt and result.                                          |

## Outputs

| Output    | What it carries                            |
| --------- | ------------------------------------------ |
| `options` | The settings, for a paid node's `options`. |

## Use

1. Change the options you need, and leave the rest at their defaults.
2. Connect `options` to the `options` input of one or more paid nodes.

A model's own settings go in `arguments` on the paid node, not here. With
`disable_fallback` off, fal may run and bill another model. With `store_io`
off, **Request: Download** can collect a request only for a short time.
Example: **video-04-upscale-a-clip**.

[fal request headers](https://fal.ai/docs/documentation/development/request-headers)
