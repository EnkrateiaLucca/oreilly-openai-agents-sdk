# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an O'Reilly Live Training course repository focused on building AI agents using OpenAI's Agents SDK. The project contains educational Jupyter notebooks demonstrating progressive concepts from basic agent creation to advanced multi-agent workflows, tool integration, and voice capabilities.

## Development Commands

### Environment Setup
```bash
# Complete setup from scratch
make all

# Individual setup steps
make conda-create          # Create conda environment (openai-agents, Python 3.11)
make env-setup            # Setup pip-tools and ipykernel
make repo-setup           # Initialize requirements structure
make notebook-setup       # Install Jupyter kernel
make env-update           # Update dependencies using uv
make freeze               # Freeze current dependencies

# Manual setup
conda activate openai-agents
pip install openai-agents
```

### Testing
```bash
# Run tests
make tests                      # Run all tests
uv run pytest -s -k <test_name>  # Run specific test

# Code quality
make format                     # Apply code formatting
make lint                       # Run linting
make mypy                       # Run type checking
```

### Dependency Management
```bash
# Update dependencies
uv pip compile requirements/requirements.in
make env-update

# Install dependencies
make sync
```

## Architecture Overview

### Core Components

**Notebooks Structure (Sequential Learning Path):**
- `0.0-` to `9.0-` - Main curriculum progression
- `extra-` notebooks for advanced topics
- Each notebook focuses on specific API capabilities

**Python Modules:**
- `agents.py` - Core agent functionality and workflow patterns
- `tools.py` - Tool implementations for function calling
- `app.py` - Application integration examples
- MCP integration modules and voice capabilities
- Integration modules for Gmail, Google Calendar, GitHub

### OpenAI Agents SDK Patterns

**Basic Agent Creation:**
```python
from agents import Agent, Runner

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    model="o3-mini"
)
```

**Running Agents:**
```python
# Synchronous execution
result = Runner.run_sync(agent, "Write a haiku about recursion")
print(result.final_output)

# Asynchronous execution
result = await Runner.run(agent, "What's the weather like?")
print(result.final_output)
```

**Streaming Response Pattern:**
```python
result = Runner.run_streamed(agent, "Tell me jokes")
async for event in result.stream_events():
    if event.type == "raw_response_event":
        print(event.data.delta, end="", flush=True)
```

**Function Tool Pattern:**
```python
from agents import function_tool

@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny"

agent = Agent(
    name="Weather Assistant",
    instructions="Help with weather queries",
    tools=[get_weather]
)
```

**Multi-Agent Handoffs:**
```python
spanish_agent = Agent(
    name="Spanish Agent",
    instructions="You only speak Spanish"
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="Route to appropriate agent",
    handoffs=[spanish_agent, english_agent]
)
```

### Tool Integration Architecture

**Built-in Tools:**
- `WebSearchTool` - Web search capabilities
- `FileSearchTool` - Document retrieval and analysis
- `function_tool` decorator - Custom function integration

**MCP (Model Context Protocol) Integration:**
- `MCPServerStdio` - Standard I/O server connections
- `MCPServerSse` - Server-sent events connections
- `MCPServerStreamableHttp` - HTTP streaming connections

**Voice Capabilities:**
- `VoicePipeline` - Speech-to-text and text-to-speech
- `VoiceWorkflow` - Voice-enabled agent workflows

**Custom Function Calling:**
- Gmail API integration (read/send emails)
- Google Calendar API (CRUD operations)
- GitHub API integration
- Web scraping with BeautifulSoup4

### Environment Variables

Required for development:
```bash
OPENAI_API_KEY=your_openai_api_key

# Optional: Disable tracing globally
OPENAI_AGENTS_DISABLE_TRACING=1

# For Google integrations
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
GMAIL_REFRESH_TOKEN=your_gmail_refresh_token

# For Slack integration
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_SIGNING_SECRET=your_slack_signing_secret

# For custom model providers
EXAMPLE_BASE_URL=your_custom_llm_url
EXAMPLE_API_KEY=your_custom_llm_key
```

## Advanced Features

### Agent Orchestration

**Input/Output Guardrails:**
```python
from agents import InputGuardrail, OutputGuardrail

@input_guardrail
async def homework_check(ctx, agent, input_data):
    # Validate input before processing
    pass

agent = Agent(
    name="Tutoring Agent",
    input_guardrails=[homework_check],
    output_guardrails=[content_filter]
)
```

**Context Management:**
```python
from agents import RunContextWrapper

@function_tool
async def fetch_user_data(ctx: RunContextWrapper[UserInfo]):
    user_info = ctx.context
    return f"User {user_info.name} is {user_info.age} years old"
```

**Tracing and Monitoring:**
```python
from agents import trace, set_tracing_disabled

# Group multiple agent runs
with trace("Multi-agent Workflow"):
    result1 = await Runner.run(agent1, query)
    result2 = await Runner.run(agent2, result1.final_output)
```

### Model Configuration

**OpenAI Models:**
```python
from agents import ModelSettings

agent = Agent(
    name="Assistant",
    model="gpt-4o",
    model_settings=ModelSettings(
        temperature=0.7,
        max_tokens=1000,
        extra_args={"user": "user_123"}
    )
)
```

**Custom Model Providers:**
```python
from agents import set_default_openai_api
from agents.extensions.models.litellm_model import LitellmModel

# Use LiteLLM for non-OpenAI models
agent = Agent(
    name="Claude Agent",
    model=LitellmModel(
        model="anthropic/claude-3-sonnet-20240229",
        api_key="your_key"
    )
)
```

## Code Conventions

- **Python 3.11** with conda environment management
- **Type hints** used where appropriate
- **Docstrings** for all functions
- **Error handling** with try-catch blocks around API calls
- **Async/await patterns** for agent execution
- **Pydantic models** for structured outputs
- **4-space indentation** standard

## Testing Approach

- **pytest** framework for automated testing
- **Integration tests** for external APIs (Gmail, Calendar)
- **Unit tests** for individual agent components
- **Snapshot testing** for consistent outputs
- **Coverage reporting** with `make coverage`
- Tests are run with: `make tests` or `uv run pytest`

## Development Notes

- Uses `uv` for faster dependency management
- Jupyter notebooks are the primary development interface
- Each notebook demonstrates progressive SDK concepts
- Setup instructions provided for MCP servers and integrations
- Automated linting and type checking with `make format` and `make mypy`
- Project structure optimized for educational progression
- Examples include voice pipelines, multi-agent workflows, and custom tools

## Example Applications

**Financial Research Agent:**
```bash
python -m examples.financial_research_agent.main
```

**Research Bot:**
```bash
uv run python -m examples.research_bot.main
```

**MCP Integration Examples:**
```bash
# Filesystem server
uv run python examples/mcp/filesystem_example/main.py

# Git integration
uv run python examples/mcp/git_example/main.py

# Voice pipeline
uv run python examples/voice/main.py
```