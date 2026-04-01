"""ChatKitServer subclass — bridges ChatKit frontend to our Agents SDK agents."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from agents import InputGuardrailTripwireTriggered, Runner
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import (
    ErrorEvent,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
)

from .agents import CustomerContext, triage_agent
from .store import MemoryStore

MAX_RECENT_ITEMS = 40


class CustomerServiceServer(ChatKitServer[dict[str, Any]]):
    """Handles every ChatKit request: thread CRUD, message streaming, etc."""

    def __init__(self) -> None:
        self.store = MemoryStore()
        super().__init__(self.store)

    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        # 1. Load recent conversation history from the store
        items_page = await self.store.load_thread_items(
            thread.id,
            after=None,
            limit=MAX_RECENT_ITEMS,
            order="asc",
            context=context,
        )

        # 2. Convert ChatKit thread items → Agents SDK input format
        agent_input = await simple_to_agent_input(items_page.data)

        # 3. Build the AgentContext bridge
        #    - request_context carries our CustomerContext for tools
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        # 4. Run the triage agent with streaming
        result = Runner.run_streamed(
            triage_agent,
            agent_input,
            context=agent_context,
        )

        # 5. Stream events back to the ChatKit frontend
        try:
            async for event in stream_agent_response(agent_context, result):
                yield event
        except InputGuardrailTripwireTriggered:
            yield ErrorEvent(
                message=(
                    "Your message was flagged as inappropriate. "
                    "Please rephrase your request respectfully."
                ),
            )
