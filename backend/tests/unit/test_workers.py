import asyncio

from app.workers.in_process_queue import InProcessTaskQueue


async def test_in_process_queue_runs_enqueued_coroutine() -> None:
    queue = InProcessTaskQueue()
    ran = asyncio.Event()

    async def _job() -> None:
        ran.set()

    await queue.enqueue(_job)
    await asyncio.wait_for(ran.wait(), timeout=1)
    assert ran.is_set()
