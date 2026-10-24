"""Choose fal's request headers once, for any number of fal nodes."""

from __future__ import annotations

from typing import override

from comfy_api.latest import io

from ..state.options import Options
from ..config.options import QUEUE_PRIORITIES
from ..config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES


class RequestOptions(io.ComfyNode):
    """Output fal's request headers for the paid nodes; at its defaults it changes no request."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Offer the queue priority, start timeout, retry and fallback switches, file lifetime, and payload storage."""
        inputs: list[io.Input] = [
            io.Combo.Input(
                'queue_priority',
                options=list(QUEUE_PRIORITIES),
                default=QUEUE_PRIORITIES[0],
                tooltip='low lets your other requests to the same model go first. It changes only the order of your '
                'own queue.',
            ),
            io.Int.Input(
                'request_start_timeout',
                default=0,
                min=0,
                tooltip='Drops the request on fal, unbilled, if no runner starts it within this many seconds. 0 means '
                'no limit.',
            ),
            io.Boolean.Input(
                'no_retry',
                default=True,
                tooltip='On, the default, asks fal not to run the request again after a server error. Off lets fal '
                'retry; fal never bills server errors.',
            ),
            io.Boolean.Input(
                'disable_fallback',
                default=True,
                tooltip='On, the default, keeps fal from sending the request to another model when this one keeps '
                'failing. Off allows it, and the other model is billed.',
            ),
            io.Int.Input(
                'expiration_duration_seconds',
                default=0,
                min=0,
                tooltip="Deletes the files this request makes on fal after this many seconds. 0 keeps your account's "
                'setting.',
            ),
            io.Boolean.Input(
                'store_io',
                default=True,
                tooltip='Off asks fal to keep no copy of the prompt and result. Request: Download can then collect the '
                'request only for a short time.',
            ),
        ]
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='Request Options',
            category=MENUS['SHARED'],
            description="Choose fal's queue priority, retries, fallbacks, file lifetime, and payload storage for any "
            'fal node.',
            inputs=inputs,
            outputs=[io.Custom(SOCKET_TYPES['OPTIONS']).Output('options', display_name='options')],
        )

    @classmethod
    @override
    def execute(  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI calls execute with the inputs the schema declares.
        cls,
        *,
        queue_priority: str,
        request_start_timeout: int,
        no_retry: bool,
        disable_fallback: bool,
        expiration_duration_seconds: int,
        store_io: bool,
    ) -> io.NodeOutput:
        """Turn the choices into a record; a value that sends nothing, such as normal or 0, becomes None."""
        options = Options(
            queue_priority=None if queue_priority == QUEUE_PRIORITIES[0] else queue_priority,
            request_start_timeout=request_start_timeout or None,
            can_retry=not no_retry,
            can_switch_model=not disable_fallback,
            expiration_duration_seconds=expiration_duration_seconds or None,
            can_store_payloads=store_io,
        )
        return io.NodeOutput(options)


__all__ = ['RequestOptions']
