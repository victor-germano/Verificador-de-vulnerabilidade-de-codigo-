from collections.abc import Awaitable, Callable
from typing import Protocol


class TaskQueue(Protocol):
    """Extension point for asynchronous scan execution.

    Phase 1 calls `ScanService.run_scan` synchronously from the API request
    (see `api/v1/scans.py`) - simple and predictable for a demo-sized
    workload. Once scans need to run out-of-process (Celery/RQ + Redis, per
    `docs/roadmap.md`), the API would enqueue via this interface instead;
    nothing else in the codebase would need to change.
    """

    async def enqueue(self, coro_factory: Callable[[], Awaitable[None]]) -> None: ...
