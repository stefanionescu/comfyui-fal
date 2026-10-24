"""Run requests with ComfyUI's progress bar and its cancel."""

from __future__ import annotations

from typing import TYPE_CHECKING
import asyncio
from functools import partial

from comfy_api.latest import ComfyAPI
from comfy.model_management import InterruptProcessingException, throw_exception_if_processing_interrupted

from .runtime import get_runtime
from ..config.fal import DASHBOARD_URLS
from ..state.errors import FalError, ErrorCode
from ..config.execution import PROGRESS_STEPS, CANCELLATION_POLL_SECONDS
from ..config.messages.run import REQUEST_TIMEOUT

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from comfy_api.latest import io

    from ..fal.operation import Progress
    from ..state.settings import Configuration


async def _wait_shielded[T](task: asyncio.Task[T]) -> bool:
    """Wait until the task settles despite cancellation, and report whether cancellation arrived."""
    cancelled = False
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            cancelled = True
        except Exception:  # noqa: BLE001 # reason: The caller reads the settled task's failure after resolving cancellation.
            break
    return cancelled


async def wait_for_thread[T](work: Callable[[], T]) -> T:
    """Run blocking work in a thread, and finish it before letting a cancel through."""
    task = asyncio.create_task(asyncio.to_thread(work))
    if await _wait_shielded(task):
        task.exception()
        raise asyncio.CancelledError
    return task.result()


async def wait_for_request[T](task: asyncio.Task[T]) -> T:
    """Forward ComfyUI's cancel to the owned asyncio task that sends a request."""
    try:
        while not task.done():
            throw_exception_if_processing_interrupted()
            await asyncio.wait({task}, timeout=CANCELLATION_POLL_SECONDS)
        return await task
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)


async def send_request[Result](
    send: Callable[[Configuration, Progress | None], Coroutine[object, object, Result]],
    build_outputs: Callable[[Result], io.NodeOutput],
    node_id: str | None,
) -> io.NodeOutput:
    """Send the request with the configuration and build the node outputs, showing only the ComfyUI progress bar.

    The bar belongs to this node: a node that another node or pack calls has no ID, so it leaves the bar of the calling
    node alone. The send reports each step it reaches. Building the outputs decodes media, which blocks, so it runs in a
    worker thread.
    """
    progress: Progress | None = None
    if node_id is not None:
        progress = partial(ComfyAPI().execution.set_progress, max_value=PROGRESS_STEPS['TOTAL'], node_id=node_id)
        await progress(0)
    configuration = await asyncio.to_thread(get_runtime().configuration.read_configuration)
    try:
        result = await wait_for_request(asyncio.create_task(send(configuration, progress)))
        outputs = await wait_for_thread(lambda: build_outputs(result))
    except FalError as error:
        if error.code is ErrorCode.INTERRUPTED:
            raise InterruptProcessingException from None
        raise
    except TimeoutError:
        seconds = configuration.settings.request_timeout_seconds
        raise FalError(ErrorCode.TIMEOUT, REQUEST_TIMEOUT.format(seconds=seconds, **DASHBOARD_URLS)) from None
    if progress is not None:
        await progress(PROGRESS_STEPS['TOTAL'])
    return outputs


__all__ = ['send_request', 'wait_for_request', 'wait_for_thread']
