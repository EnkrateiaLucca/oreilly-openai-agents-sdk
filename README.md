# O'Reilly Live Training: Building AI Agents with OpenAI's Agents SDK

A comprehensive educational repository for learning to build sophisticated AI agents using OpenAI's Agents SDK. This course progresses from basic agent creation to advanced multi-agent workflows, tool integration, and voice capabilities.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Conda package manager
- OpenAI API key

### Setup
```bash
# Complete setup from scratch
make all

# Or step by step:
make conda-create          # Create conda environment
make env-setup            # Setup pip-tools and ipykernel  
make repo-setup           # Initialize requirements
make notebook-setup       # Install Jupyter kernel
make env-update           # Update dependencies
```

### Manual Setup
```bash
conda activate openai-agents
pip install openai-agents
```

## 📚 Course Structure

### Learning Path (Sequential Notebooks)

The course is organized as a progressive series of Jupyter notebooks:

- **0.0-** to **9.0-** - Main curriculum progression
- **extra-** notebooks - Advanced topics and extensions

Each notebook focuses on specific OpenAI Agents SDK capabilities, building from fundamentals to complex implementations.

### Core Modules

| Module | Purpose |
|--------|---------|
| `agents.py` | Core agent functionality and workflow patterns |
| `tools.py` | Tool implementations for function calling |
| `app.py` | Application integration examples |
| MCP modules | Model Context Protocol integrations |
| Voice modules | Speech-to-text and text-to-speech capabilities |
| Integration modules | Gmail, Google Calendar, GitHub APIs |

## 🛠 Development Commands

### Environment Management
```bash
make env-update           # Update dependencies using uv
make freeze              # Freeze current dependencies
make sync               # Install dependencies
```

### Code Quality
```bash
make format             # Apply code formatting
make lint              # Run linting
make mypy              # Run type checking
make tests             # Run all tests
```

### Testing
```bash
# Run specific tests
uv run pytest -s -k <test_name>

# Coverage reporting
make coverage
```

## 🤖 OpenAI Agents SDK Patterns

### Basic Agent Creation
```python
from agents import Agent, Runner

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    model="o3-mini"
)
```

### Running Agents
```python
# Synchronous execution
result = Runner.run_sync(agent, "Write a haiku about recursion")
print(result.final_output)

# Asynchronous execution
result = await Runner.run(agent, "What's the weather like?")
print(result.final_output)

# Streaming responses
result = Runner.run_streamed(agent, "Tell me jokes")
async for event in result.stream_events():
    if event.type == "raw_response_event":
        print(event.data.delta, end="", flush=True)
```

### Function Tools
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

### Multi-Agent Handoffs
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

## 🔧 Advanced Features

### Tool Integration
- **Built-in Tools**: WebSearchTool, FileSearchTool
- **MCP Integration**: MCPServerStdio, MCPServerSse, MCPServerStreamableHttp
- **Voice Capabilities**: VoicePipeline, VoiceWorkflow
- **Custom APIs**: Gmail, Google Calendar, GitHub, Web scraping

### Agent Orchestration
```python
from agents import InputGuardrail, OutputGuardrail, trace

@input_guardrail
async def homework_check(ctx, agent, input_data):
    # Validate input before processing
    pass

# Group multiple agent runs
with trace("Multi-agent Workflow"):
    result1 = await Runner.run(agent1, query)
    result2 = await Runner.run(agent2, result1.final_output)
```

### Model Configuration
```python
from agents import ModelSettings, set_default_openai_api
from agents.extensions.models.litellm_model import LitellmModel

# OpenAI models
agent = Agent(
    name="Assistant",
    model="gpt-4o",
    model_settings=ModelSettings(
        temperature=0.7,
        max_tokens=1000
    )
)

# Custom model providers
agent = Agent(
    name="Claude Agent", 
    model=LitellmModel(
        model="anthropic/claude-3-sonnet-20240229",
        api_key="your_key"
    )
)
```

## 🔑 Environment Variables

### Required
```bash
OPENAI_API_KEY=your_openai_api_key
```

### Optional
```bash
# Disable tracing globally
OPENAI_AGENTS_DISABLE_TRACING=1

# Google integrations
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
GMAIL_REFRESH_TOKEN=your_gmail_refresh_token

# Slack integration
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_SIGNING_SECRET=your_slack_signing_secret

# Custom model providers
EXAMPLE_BASE_URL=your_custom_llm_url
EXAMPLE_API_KEY=your_custom_llm_key
```

## 📝 Example Applications

### Financial Research Agent
```bash
python -m examples.financial_research_agent.main
```

### Research Bot
```bash
uv run python -m examples.research_bot.main
```

### MCP Integration Examples
```bash
# Filesystem server
uv run python examples/mcp/filesystem_example/main.py

# Git integration  
uv run python examples/mcp/git_example/main.py

# Voice pipeline
uv run python examples/voice/main.py
```

## 🏗 Architecture Overview

### Design Principles
- **Progressive Learning**: Notebooks build complexity incrementally
- **Modular Components**: Reusable agent patterns and tools
- **Real-world Integration**: Gmail, Calendar, GitHub APIs
- **Voice-first Design**: Speech-to-text and text-to-speech support
- **Multi-agent Workflows**: Handoffs and orchestration patterns

### Technology Stack
- **Python 3.11** with conda environment management
- **OpenAI Agents SDK** for agent creation and execution
- **Jupyter Notebooks** for interactive development
- **uv** for fast dependency management
- **pytest** for testing framework
- **Pydantic** for structured outputs
- **MCP** for model context protocol

## 🧪 Testing Approach

- **Integration tests** for external APIs (Gmail, Calendar)
- **Unit tests** for individual agent components  
- **Snapshot testing** for consistent outputs
- **Coverage reporting** with automated quality checks

## 📋 Code Conventions

- **Type hints** used throughout
- **Docstrings** for all functions
- **Error handling** with try-catch blocks around API calls
- **Async/await patterns** for agent execution
- **4-space indentation** standard
- **Automated linting** and type checking

## 🤝 Contributing

1. Follow the established code conventions
2. Add tests for new functionality
3. Run quality checks: `make format lint mypy tests`
4. Update documentation as needed

## 📄 License

This project is part of O'Reilly Live Training educational content.

## 🆘 Support

For questions about the course content or technical issues, please refer to the O'Reilly Live Training platform or course materials.