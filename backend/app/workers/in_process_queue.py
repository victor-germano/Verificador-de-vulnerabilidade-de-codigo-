import asyncio
from collections.abc import Awaitable, Callable


class InProcessTaskQueue:
    """`TaskQueue` implementation that runs tasks as asyncio background
    tasks inside the API process itself - no external broker required."""

    def __init__(self) -> None:
        self._background_tasks: set[asyncio.Task] = set()

    async def enqueue(self, coro_factory: Callable[[], Awaitable[None]]) -> None:
        task = asyncio.create_task(coro_factory())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
