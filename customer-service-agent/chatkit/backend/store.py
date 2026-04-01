"""In-memory store for ChatKit thread/item persistence (demo only)."""

from __future__ import annotations

import uuid
from collections import defaultdict
from typing import Any

from chatkit.errors import StreamError, ErrorCode
from chatkit.store import Store
from chatkit.types import Page, ThreadItem, ThreadMetadata


class MemoryStore(Store[dict[str, Any]]):
    """Simple dict-backed store. Fine for demos; replace with a DB for prod."""

    def __init__(self) -> None:
        self._threads: dict[str, ThreadMetadata] = {}
        self._items: dict[str, list[ThreadItem]] = defaultdict(list)

    # -- ID generation --------------------------------------------------------

    def generate_thread_id(self, context: dict[str, Any]) -> str:
        return f"thread_{uuid.uuid4().hex[:12]}"

    def generate_item_id(
        self, item_type: str, thread: ThreadMetadata, context: dict[str, Any]
    ) -> str:
        return f"{item_type}_{uuid.uuid4().hex[:12]}"

    # -- Threads --------------------------------------------------------------

    async def load_thread(
        self, thread_id: str, context: dict[str, Any]
    ) -> ThreadMetadata:
        if thread_id not in self._threads:
            raise StreamError(
                message=f"Thread {thread_id} not found",
                code=ErrorCode.THREAD_NOT_FOUND,
            )
        return self._threads[thread_id]

    async def save_thread(
        self, thread: ThreadMetadata, context: dict[str, Any]
    ) -> None:
        self._threads[thread.id] = thread

    async def load_threads(
        self,
        limit: int,
        after: str | None,
        order: str,
        context: dict[str, Any],
    ) -> Page[ThreadMetadata]:
        threads = sorted(
            self._threads.values(),
            key=lambda t: t.created_at,
            reverse=(order == "desc"),
        )
        # Simple cursor pagination
        if after:
            idx = next(
                (i for i, t in enumerate(threads) if t.id == after), len(threads)
            )
            threads = threads[idx + 1 :]
        page = threads[:limit]
        return Page(
            data=page,
            has_more=len(threads) > limit,
            first_id=page[0].id if page else None,
            last_id=page[-1].id if page else None,
        )

    async def delete_thread(
        self, thread_id: str, context: dict[str, Any]
    ) -> None:
        self._threads.pop(thread_id, None)
        self._items.pop(thread_id, None)

    # -- Items ----------------------------------------------------------------

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: dict[str, Any]
    ) -> None:
        self._items[thread_id].append(item)

    async def save_item(
        self, thread_id: str, item: ThreadItem, context: dict[str, Any]
    ) -> None:
        items = self._items[thread_id]
        for i, existing in enumerate(items):
            if existing.id == item.id:
                items[i] = item
                return
        items.append(item)

    async def load_item(
        self, thread_id: str, item_id: str, context: dict[str, Any]
    ) -> ThreadItem:
        for item in self._items.get(thread_id, []):
            if item.id == item_id:
                return item
        raise StreamError(
            message=f"Item {item_id} not found",
            code=ErrorCode.ITEM_NOT_FOUND,
        )

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: dict[str, Any],
    ) -> Page[ThreadItem]:
        items = list(self._items.get(thread_id, []))
        if order == "desc":
            items.reverse()
        if after:
            idx = next(
                (i for i, it in enumerate(items) if it.id == after), len(items)
            )
            items = items[idx + 1 :]
        page = items[:limit]
        return Page(
            data=page,
            has_more=len(items) > limit,
            first_id=page[0].id if page else None,
            last_id=page[-1].id if page else None,
        )

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: dict[str, Any]
    ) -> None:
        self._items[thread_id] = [
            i for i in self._items[thread_id] if i.id != item_id
        ]

    # -- Attachments (not used in this demo) ----------------------------------

    async def load_attachment(self, attachment_id: str, context: dict[str, Any]):
        raise NotImplementedError("Attachments not supported in this demo")

    async def save_attachment(self, attachment, context: dict[str, Any]):
        raise NotImplementedError("Attachments not supported in this demo")

    async def delete_attachment(self, attachment_id: str, context: dict[str, Any]):
        raise NotImplementedError("Attachments not supported in this demo")
