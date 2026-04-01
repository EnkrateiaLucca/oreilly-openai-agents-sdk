# /// script
# requires-python = ">=3.11"
# dependencies = ["openai-agents==0.13.3", "rich"]
# ///
"""
Demo: Structured Output & Context (Notebook 02)
================================================
Demonstrates two key concepts from the OpenAI Agents SDK:
  1. output_type  → agents return typed Pydantic models, not free-form text
  2. RunContextWrapper → inject user/session state into tools without the LLM seeing it
"""
import asyncio
import os
import getpass
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import print as rprint
from rich.rule import Rule

from agents import Agent, Runner, RunContextWrapper, function_tool

# ── Setup ──────────────────────────────────────────────────────────────────────
console = Console()

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key: ")

# ── PART 1: Structured Output ──────────────────────────────────────────────────

class SupportTicket(BaseModel):
    """A classified support ticket."""
    priority: Literal["low", "medium", "high", "critical"]
    department: Literal["sales", "support", "billing", "technical"]
    sentiment: Literal["positive", "neutral", "negative"]
    summary: str = Field(description="Brief one-sentence summary of the issue")

ticket_classifier = Agent(
    name="TicketClassifier",
    instructions="""You classify support tickets. Analyze the customer message and extract:
    - Priority (based on urgency and impact)
    - Department (who should handle this)
    - Sentiment (how the customer feels)
    - Summary (brief one-sentence description)""",
    model="gpt-4.1",
    output_type=SupportTicket,  # <-- forces structured output
)

# ── PART 2: RunContextWrapper ──────────────────────────────────────────────────

@dataclass
class UserContext:
    """Context injected into tools — NOT sent to the LLM."""
    user_id: str
    user_name: str
    account_type: Literal["free", "premium"]
    open_tickets: int = 0

@function_tool
async def get_user_account_info(wrapper: RunContextWrapper[UserContext]) -> str:
    """Get account details for the current user."""
    ctx = wrapper.context
    if ctx.account_type == "premium":
        return (
            f"{ctx.user_name} is a PREMIUM member. "
            f"They get: 20% off all items, free shipping, priority support. "
            f"Open tickets: {ctx.open_tickets}."
        )
    else:
        return (
            f"{ctx.user_name} is a FREE tier user. "
            f"Standard support SLA applies. "
            f"Open tickets: {ctx.open_tickets}. "
            f"Upsell opportunity: first month of premium at 50% off."
        )

support_agent = Agent(
    name="SupportAgent",
    instructions="""You are a friendly customer support agent.
    Always call get_user_account_info first to personalize your response.
    Be concise — 2-3 sentences max.""",
    model="gpt-4.1",
    tools=[get_user_account_info],
)

# ── Helpers ────────────────────────────────────────────────────────────────────

PRIORITY_COLOR = {
    "low": "green",
    "medium": "yellow",
    "high": "red",
    "critical": "bold red",
}
SENTIMENT_EMOJI = {"positive": "😊", "neutral": "😐", "negative": "😠"}

def render_ticket(ticket: SupportTicket, message: str) -> None:
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Field", style="dim", width=12)
    table.add_column("Value")
    color = PRIORITY_COLOR.get(ticket.priority, "white")
    table.add_row("Priority", f"[{color}]{ticket.priority.upper()}[/{color}]")
    table.add_row("Department", ticket.department)
    table.add_row("Sentiment", f"{SENTIMENT_EMOJI[ticket.sentiment]} {ticket.sentiment}")
    table.add_row("Summary", ticket.summary)
    console.print(Panel(table, title="[bold cyan]SupportTicket (Pydantic model)[/bold cyan]", border_style="cyan"))


def render_context_response(user: UserContext, response: str) -> None:
    badge = "[bold gold1]★ PREMIUM[/bold gold1]" if user.account_type == "premium" else "[dim]FREE tier[/dim]"
    console.print(Panel(
        f"[italic]{response}[/italic]",
        title=f"[bold]{user.user_name}[/bold] {badge}",
        border_style="magenta" if user.account_type == "premium" else "blue",
    ))


# ── Demo Sections ──────────────────────────────────────────────────────────────

async def demo_structured_output() -> None:
    console.print(Rule("[bold cyan]PART 1 — Structured Output[/bold cyan]"))
    console.print(
        "Type a customer support message. The agent will return a [cyan]SupportTicket[/cyan] "
        "Pydantic model instead of free-form text.\n"
        "[dim]Type 'done' to move on.[/dim]\n"
    )
    while True:
        message = Prompt.ask("[bold]Customer message[/bold]")
        if message.strip().lower() in ("done", "exit", "q", ""):
            break
        with console.status("Classifying…"):
            result = await Runner.run(ticket_classifier, message)
        ticket: SupportTicket = result.final_output
        render_ticket(ticket, message)
        rprint(f"\n[dim]Python type: {type(ticket).__name__} | "
               f"dict: {ticket.model_dump()}[/dim]\n")


async def demo_context_wrapper() -> None:
    console.print(Rule("[bold magenta]PART 2 — RunContextWrapper[/bold magenta]"))
    console.print(
        "The [magenta]same agent[/magenta] answers the same question differently "
        "based on the injected [magenta]UserContext[/magenta].\n"
        "[bold yellow]Key:[/bold yellow] The context object is [bold]never sent to the LLM[/bold] — "
        "only the tool's return value is.\n"
        "[dim]Type 'done' to exit.[/dim]\n"
    )

    users = {
        "1": UserContext(user_id="usr_001", user_name="Alice", account_type="premium", open_tickets=2),
        "2": UserContext(user_id="usr_002", user_name="Bob",   account_type="free",    open_tickets=0),
    }

    while True:
        console.print("[bold]Pick a user:[/bold]")
        console.print("  [1] Alice (premium, 2 open tickets)")
        console.print("  [2] Bob   (free tier)")
        console.print("  [Q] Done\n")

        choice = Prompt.ask("Choice", choices=["1", "2", "q", "Q"], default="1")
        if choice.lower() == "q":
            break

        user = users[choice]
        message = Prompt.ask("[bold]Message to support[/bold]")
        if message.strip().lower() in ("done", "exit", ""):
            break

        with console.status(f"Responding as agent (context: {user.user_name})…"):
            result = await Runner.run(support_agent, message, context=user)

        render_context_response(user, result.final_output)
        console.print()


# ── Main ───────────────────────────────────────────────────────────────────────

SAMPLE_MESSAGES = [
    "I've been charged twice for my subscription! This is unacceptable!",
    "How do I export my data to CSV?",
    "Your product is amazing, just wanted to say thanks!",
    "The API keeps returning 500 errors — our production app is down!",
]

async def main() -> None:
    console.print(Panel.fit(
        "[bold]Notebook 02 — Structured Output & RunContextWrapper[/bold]\n"
        "[dim]OpenAI Agents SDK · O'Reilly Live Training[/dim]",
        border_style="green",
    ))

    console.print("\n[bold yellow]Try these sample messages in Part 1:[/bold yellow]")
    for i, msg in enumerate(SAMPLE_MESSAGES, 1):
        console.print(f"  [dim]{i}.[/dim] {msg}")
    console.print()

    console.print("[bold]Sections:[/bold]  [1] Structured Output   [2] Context Wrapper   [A] Both   [Q] Quit\n")
    choice = Prompt.ask("Start with", choices=["1", "2", "a", "A", "q", "Q"], default="a")

    if choice.lower() == "q":
        return

    if choice in ("1", "a", "A"):
        await demo_structured_output()

    if choice in ("2", "a", "A"):
        await demo_context_wrapper()

    console.print(Panel.fit(
        "✅  Key takeaways:\n"
        "  • [cyan]output_type[/cyan] → agent returns a typed Pydantic model, not a string\n"
        "  • [magenta]RunContextWrapper[/magenta] → inject state into tools; LLM never sees the raw object\n"
        "  • Combine both for context-aware, type-safe agents",
        border_style="green",
        title="Summary",
    ))


if __name__ == "__main__":
    asyncio.run(main())
