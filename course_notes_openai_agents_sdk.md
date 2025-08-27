./CLAUDE.md
---
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

---
./Makefile
---
ENV_NAME ?= openai-agents-sdk
PYTHON_VERSION ?= 3.11
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

.PHONY: all conda-create env-setup pip-tools-setup repo-setup notebook-setup env-update clean

all: conda-create env-setup repo-setup notebook-setup env-update

conda-create:
	conda create -n $(ENV_NAME) python=$(PYTHON_VERSION) -y

env-setup: conda-create
	$(CONDA_ACTIVATE) $(ENV_NAME) && \
	pip install --upgrade pip && \
	pip install uv && \
	uv pip install pip-tools setuptools ipykernel

repo-setup:
	mkdir -p requirements
	echo "ipykernel" > requirements/requirements.in

notebook-setup:
	$(CONDA_ACTIVATE) $(ENV_NAME) && \
	python -m ipykernel install --user --name=$(ENV_NAME)

env-update:
	$(CONDA_ACTIVATE) $(ENV_NAME) && \
	uv pip compile ./requirements/requirements.in -o ./requirements/requirements.txt && \
	uv pip sync ./requirements/requirements.txt

clean:
	conda env remove -n $(ENV_NAME)

freeze:
	$(CONDA_ACTIVATE) $(ENV_NAME) && \
	uv pip freeze > requirements/requirements.txt


---
./README.md
---
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

---
./course_notes_openai_agents_sdk.md
---
./CLAUDE.md
---
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

---
./Makefile
---
ENV_NAME ?= openai-agents-sdk
PYTHON_VERSION ?= 3.11
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

.PHONY: all conda-create env-setup pip-tools-setup repo-setup notebook-setup env-update clean

all: conda-create env-setup repo-setup notebook-setup env-update

conda-create:
	conda create -n $(ENV_NAME) python=$(PYTHON_VERSION) -y

env-setup: conda-create
	$(CONDA_ACTIVATE) $(ENV_NAME) && \
	pip install --upgrade pip && \
	pip install uv && \
	uv pip install pip-tools setuptools ipykernel

repo-setup:
	mkdir -p requirements
	echo "ipykernel" > requirements/requirements.in

notebook-setup:
	$(CONDA_ACTIVATE) $(ENV_NAME) && \
	python -m ipykernel install --user --name=$(ENV_NAME)

env-update:
	$(CONDA_ACTIVATE) $(ENV_NAME) && \
	uv pip compile ./requirements/requirements.in -o ./requirements/requirements.txt && \
	uv pip sync ./requirements/requirements.txt

clean:
	conda env remove -n $(ENV_NAME)

freeze:
	$(CONDA_ACTIVATE) $(ENV_NAME) && \
	uv pip freeze > requirements/requirements.txt


---
./README.md
---
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

---


---
./requirements/requirements.in
---
ipykernel
openai-agents
openai-agents[viz]
asyncio
matplotlib
pandas

# Google Sheets API
google-api-python-client
google-auth
google-auth-oauthlib
google-auth-httplib2

---
./requirements/requirements.txt
---
# This file was autogenerated by uv via the following command:
#    uv pip compile ./requirements/requirements.in -o ./requirements/requirements.txt
annotated-types==0.7.0
    # via pydantic
anyio==4.9.0
    # via
    #   httpx
    #   mcp
    #   openai
    #   sse-starlette
    #   starlette
appnope==0.1.4
    # via ipykernel
asttokens==3.0.0
    # via stack-data
asyncio==3.4.3
    # via -r ./requirements/requirements.in
cachetools==5.5.2
    # via google-auth
certifi==2025.1.31
    # via
    #   httpcore
    #   httpx
    #   requests
charset-normalizer==3.4.1
    # via requests
click==8.1.8
    # via uvicorn
colorama==0.4.6
    # via griffe
comm==0.2.2
    # via ipykernel
contourpy==1.3.2
    # via matplotlib
cycler==0.12.1
    # via matplotlib
debugpy==1.8.13
    # via ipykernel
decorator==5.2.1
    # via ipython
distro==1.9.0
    # via openai
executing==2.2.0
    # via stack-data
fonttools==4.57.0
    # via matplotlib
google-api-core==2.25.1
    # via google-api-python-client
google-api-python-client==2.179.0
    # via -r ./requirements/requirements.in
google-auth==2.40.3
    # via
    #   -r ./requirements/requirements.in
    #   google-api-core
    #   google-api-python-client
    #   google-auth-httplib2
    #   google-auth-oauthlib
google-auth-httplib2==0.2.0
    # via
    #   -r ./requirements/requirements.in
    #   google-api-python-client
google-auth-oauthlib==1.2.2
    # via -r ./requirements/requirements.in
googleapis-common-protos==1.70.0
    # via google-api-core
graphviz==0.20.3
    # via openai-agents
griffe==1.7.2
    # via openai-agents
h11==0.14.0
    # via
    #   httpcore
    #   uvicorn
httpcore==1.0.7
    # via httpx
httplib2==0.22.0
    # via
    #   google-api-python-client
    #   google-auth-httplib2
httpx==0.28.1
    # via
    #   mcp
    #   openai
httpx-sse==0.4.0
    # via mcp
idna==3.10
    # via
    #   anyio
    #   httpx
    #   requests
ipykernel==6.29.5
    # via -r ./requirements/requirements.in
ipython==9.1.0
    # via ipykernel
ipython-pygments-lexers==1.1.1
    # via ipython
jedi==0.19.2
    # via ipython
jiter==0.9.0
    # via openai
jupyter-client==8.6.3
    # via ipykernel
jupyter-core==5.7.2
    # via
    #   ipykernel
    #   jupyter-client
kiwisolver==1.4.8
    # via matplotlib
matplotlib==3.10.1
    # via -r ./requirements/requirements.in
matplotlib-inline==0.1.7
    # via
    #   ipykernel
    #   ipython
mcp==1.6.0
    # via openai-agents
nest-asyncio==1.6.0
    # via ipykernel
numpy==2.2.5
    # via
    #   contourpy
    #   matplotlib
    #   pandas
oauthlib==3.3.1
    # via requests-oauthlib
openai==1.71.0
    # via openai-agents
openai-agents==0.0.9
    # via -r ./requirements/requirements.in
packaging==24.2
    # via
    #   ipykernel
    #   matplotlib
pandas==2.3.2
    # via -r ./requirements/requirements.in
parso==0.8.4
    # via jedi
pexpect==4.9.0
    # via ipython
pillow==11.2.1
    # via matplotlib
platformdirs==4.3.7
    # via jupyter-core
prompt-toolkit==3.0.50
    # via ipython
proto-plus==1.26.1
    # via google-api-core
protobuf==6.32.0
    # via
    #   google-api-core
    #   googleapis-common-protos
    #   proto-plus
psutil==7.0.0
    # via ipykernel
ptyprocess==0.7.0
    # via pexpect
pure-eval==0.2.3
    # via stack-data
pyasn1==0.6.1
    # via
    #   pyasn1-modules
    #   rsa
pyasn1-modules==0.4.2
    # via google-auth
pydantic==2.11.3
    # via
    #   mcp
    #   openai
    #   openai-agents
    #   pydantic-settings
pydantic-core==2.33.1
    # via pydantic
pydantic-settings==2.8.1
    # via mcp
pygments==2.19.1
    # via
    #   ipython
    #   ipython-pygments-lexers
pyparsing==3.2.3
    # via
    #   httplib2
    #   matplotlib
python-dateutil==2.9.0.post0
    # via
    #   jupyter-client
    #   matplotlib
    #   pandas
python-dotenv==1.1.0
    # via pydantic-settings
pytz==2025.2
    # via pandas
pyzmq==26.4.0
    # via
    #   ipykernel
    #   jupyter-client
requests==2.32.3
    # via
    #   google-api-core
    #   openai-agents
    #   requests-oauthlib
requests-oauthlib==2.0.0
    # via google-auth-oauthlib
rsa==4.9.1
    # via google-auth
six==1.17.0
    # via python-dateutil
sniffio==1.3.1
    # via
    #   anyio
    #   openai
sse-starlette==2.2.1
    # via mcp
stack-data==0.6.3
    # via ipython
starlette==0.46.1
    # via
    #   mcp
    #   sse-starlette
tornado==6.4.2
    # via
    #   ipykernel
    #   jupyter-client
tqdm==4.67.1
    # via openai
traitlets==5.14.3
    # via
    #   comm
    #   ipykernel
    #   ipython
    #   jupyter-client
    #   jupyter-core
    #   matplotlib-inline
types-requests==2.32.0.20250328
    # via openai-agents
typing-extensions==4.13.1
    # via
    #   anyio
    #   ipython
    #   openai
    #   openai-agents
    #   pydantic
    #   pydantic-core
    #   typing-inspection
typing-inspection==0.4.0
    # via pydantic
tzdata==2025.2
    # via pandas
uritemplate==4.2.0
    # via google-api-python-client
urllib3==2.3.0
    # via
    #   requests
    #   types-requests
uvicorn==0.34.0
    # via mcp
wcwidth==0.2.13
    # via prompt-toolkit


---
./scripts/deterministic_flow.py
---
import asyncio


from pydantic import BaseModel

from agents import Agent, Runner, trace

"""
This example demonstrates a deterministic flow, where each step is performed by an agent.
1. The first agent generates a story outline
2. We feed the outline into the second agent
3. The second agent checks if the outline is good quality and if it is a scifi story
4. If the outline is not good quality or not a scifi story, we stop here
5. If the outline is good quality and a scifi story, we feed the outline into the third agent
6. The third agent writes the story
"""

story_outline_agent = Agent(
    name="story_outline_agent",
    instructions="Generate a very short story outline based on the user's input.",
)


class OutlineCheckerOutput(BaseModel):
    good_quality: bool
    is_funny: bool


outline_checker_agent = Agent(
    name="outline_checker_agent",
    instructions="Read the given story outline, and judge the quality. Also, determine if it is a scifi story.",
    output_type=OutlineCheckerOutput,
)

story_agent = Agent(
    name="story_agent",
    instructions="Write a short story based on the given outline.",
    output_type=str,
)


async def main():
    input_prompt = input("What kind of story do you want? ")

    # Ensure the entire workflow is a single trace
    with trace("Deterministic story flow"):
        # 1. Generate an outline
        outline_result = await Runner.run(
            story_outline_agent,
            input_prompt,
        )
        print("Outline generated")

        # 2. Check the outline
        outline_checker_result = await Runner.run(
            outline_checker_agent,
            outline_result.final_output,
        )

        # 3. Add a gate to stop if the outline is not good quality or not a scifi story
        assert isinstance(outline_checker_result.final_output, OutlineCheckerOutput)
        if not outline_checker_result.final_output.good_quality:
            print("Outline is not good quality, so we stop here.")
            exit(0)

        if not outline_checker_result.final_output.is_funny:
            print("Outline is not a scifi story, so we stop here.")
            exit(0)

        print("Outline is good quality and a scifi story, so we continue to write the story.")

        # 4. Write the story
        story_result = await Runner.run(
            story_agent,
            outline_result.final_output,
        )
        print(f"Story: {story_result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())

---
./scripts/simple_agent_demo.py
---
from agents import Agent, Runner, WebSearchTool, function_tool, guardrail

@function_tool
def submit_refund_request(item_id: str, reason: str):
    # Your refund logic goes here
    return "success"

support_agent = Agent(
    name="Support & Returns",
    instructions="You are a support agent who can submit refunds [...]",
    tools=[submit_refund_request],
)

shopping_agent = Agent(
    name="Shopping Assistant",
    instructions="You are a shopping assistant who can search the web [...]",
    tools=[WebSearchTool()],
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="Route the user to the correct agent.",
    handoffs=[shopping_agent, support_agent],
)

output = Runner.run_sync(
    starting_agent=triage_agent,
    input="What shoes might work best with my outfit so far?",
)

print(output)

---
./scripts/spreadsheet_agent.py
---


---
./assets/openai-agents-sdk-docs-llmstxt.txt
---
# OpenAI Agents SDK

> The OpenAI Agents SDK is a Python framework for building AI agents that can use tools, make decisions, and complete complex tasks. It provides a structured way to create agents that can use function calling, hosted tools, and even other agents as tools.

The SDK is designed to help developers create AI agents that can:
- Take actions through tools (fetching data, running code, calling APIs)
- Make decisions based on context and instructions
- Handle complex workflows through tool composition
- Manage state and error handling
- Stream results and provide tracing capabilities

## Core Documentation

- [Introduction](https://openai.github.io/openai-agents-python/index.html.md): Overview of the OpenAI Agents SDK and its capabilities
- [Quickstart Guide](https://openai.github.io/openai-agents-python/quickstart/index.html.md): Get started quickly with basic agent creation and usage
- [Agents Guide](https://openai.github.io/openai-agents-python/agents/index.html.md): Detailed information about creating and configuring agents
- [Tools Documentation](https://openai.github.io/openai-agents-python/tools/index.html.md): Comprehensive guide to using and creating tools
- [Running Agents](https://openai.github.io/openai-agents-python/running/index.html.md): How to execute and manage agent runs

## Advanced Features

- [Context Management](https://openai.github.io/openai-agents-python/context/index.html.md): Managing state and context in agent runs
- [Tracing](https://openai.github.io/openai-agents-python/tracing/index.html.md): Debugging and monitoring agent behavior
- [Guardrails](https://openai.github.io/openai-agents-python/guardrails/index.html.md): Setting up safety and control mechanisms
- [Voice Agents](https://openai.github.io/openai-agents-python/voice/index.html.md): Building agents with voice capabilities

## Optional

- [API Reference](https://openai.github.io/openai-agents-python/ref/index.html.md): Complete API documentation for all SDK components
- [Examples](https://openai.github.io/openai-agents-python/examples/index.html.md): Sample code and use cases
- [Configuration](https://openai.github.io/openai-agents-python/config/index.html.md): Detailed SDK configuration options

---
./assets/resources.md
---
- [ ] [Building Agents manual (to be used )](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
- [ ] https://youtu.be/35nxORG1mtg?si=BtFDtAgSR3be4BYX
- [ ] https://x.com/atomsilverman/status/1902403931130749068?s=46&t=CSmFBRRX097Mpa7XSLa7uw
- [ ] https://www.youtube.com/watch?v=-rsTkYgnNzM
- [ ] https://x.com/n_sri_laasya/status/1904980170274218421?s=46&t=CSmFBRRX097Mpa7XSLa7uw
- [ ] [Read through the examples](https://github.com/openai/openai-agents-python/tree/main/examples)
- [ ] https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
- [ ] https://cookbook.openai.com/examples/partners/model_selection_guide/model_selection_guide

# Resources
- 

https://x.com/atomsilverman/status/1904972370051555330?s=12&t=CSmFBRRX097Mpa7XSLa7uw

https://www.linkedin.com/posts/linasbeliunas_openais-practical-guide-to-building-ai-agents-ugcPost-7319301282848997376-VhJE?utm_source=share&utm_medium=member_ios&rcm=ACoAACex1GEBr92EEpdUpSfQCUGioemZCPe44s4

---
./notebooks/0-intro-agents.ipynb
---
{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "53e47c17",
   "metadata": {},
   "source": [
    "# Intro Agents from Scratch\n",
    "\n",
    "## 3 Levels\n",
    "\n",
    "1. LLMs + functions in prompt\n",
    "2. LLMs + structured outputs/function calling\n",
    "3. Agent loop"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "7d73b156",
   "metadata": {},
   "source": [
    "### 1. LLMs + functions in prompt"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "ffa79bea",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "'Could you share what domain you mean by “agents”? For example:\\n- AI/LLM or robotics agents (autonomy levels)\\n- Customer support agents (Tier 1/2/3)\\n- Real estate agents (salesperson, broker, managing broker)\\n- Game/CS agents (reactive vs deliberative)\\n- Level‑k reasoning in multi‑agent games (L0, L1, L2…)\\n\\nIf you mean AI/LLM agents, a common ladder of “agent levels” is:\\n1) Tool-augmented assistant: answers plus single tool calls (search, code exec).\\n2) Multi-step planner: decomposes tasks and uses multiple tools/steps.\\n3) Reflective agent: iterates, critiques itself, uses memory/context to improve.\\n4) Goal-driven autonomous worker: runs long tasks, monitors progress/events, minimal supervision.\\n5) Orchestrated multi-agent system: multiple specialized agents coordinated by a controller.\\n\\nTell me which context you had in mind, and I’ll tailor the levels accordingly.'"
      ]
     },
     "execution_count": 1,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "from openai import OpenAI\n",
    "\n",
    "client = OpenAI()\n",
    "\n",
    "def get_response(prompt_question):\n",
    "    response = client.chat.completions.create(\n",
    "        model=\"gpt-5\",\n",
    "        messages=[{\"role\": \"system\", \"content\": \"You are a helpful assistant\"},\n",
    "                  {\"role\": \"user\", \"content\": prompt_question}]\n",
    "    )\n",
    "    \n",
    "    return response.choices[0].message.content\n",
    "\n",
    "get_response(\"Hi! What are the levels of agents?\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "8d35ca84",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "'write_file(\"test.txt\", \"Hello, world!\")'"
      ]
     },
     "execution_count": 2,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "def write_file(file_path, content):\n",
    "    \"\"\"Takes in a file path and content, and writes the content to the file\"\"\"\n",
    "    with open(file_path, \"w\") as f:\n",
    "        f.write(content)\n",
    "\n",
    "def read_file(file_path):\n",
    "    \"\"\"Takes in a file path and returns the content of the file\"\"\"\n",
    "    with open(file_path, \"r\") as f:\n",
    "        return f.read()\n",
    "\n",
    "\n",
    "def level1_agent_llm_and_functions_in_prompt(prompt):\n",
    "    function_info = \"\"\"\n",
    "    def write_file(file_path, content):\n",
    "        '''Takes in a file path and content, and writes the content to the file'''\n",
    "        with open(file_path, \"w\") as f:\n",
    "            f.write(content)\n",
    "\n",
    "    def read_file(file_path):\n",
    "        '''Takes in a file path and returns the content of the file'''\n",
    "        with open(file_path, \"r\") as f:\n",
    "            return f.read()\n",
    "\n",
    "    \"\"\"\n",
    "    full_prompt_with_function_info = f\"\"\"\n",
    "    Take this request from a user: {prompt}.\n",
    "    If the request involves writing to a file or reading to a file,\n",
    "    you can output a call to these functions which you have access to: \n",
    "    {function_info}.\n",
    "    \"\"\"\n",
    "    response = client.chat.completions.create(\n",
    "        model=\"gpt-5\",\n",
    "        messages=[{\"role\": \"system\", \"content\": \"You are a helpful assistant that can write and read files.\"},\n",
    "                  {\"role\": \"user\", \"content\": full_prompt_with_function_info}]\n",
    "    )\n",
    "    \n",
    "    return response.choices[0].message.content\n",
    "    \n",
    "level1_agent_llm_and_functions_in_prompt(\"Write a file called 'test.txt' with the content 'Hello, world!'\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "1a3e8429",
   "metadata": {},
   "outputs": [],
   "source": [
    "exec('write_file(\"test.txt\", \"Hello, world!\")')"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "14b9ab54",
   "metadata": {},
   "source": [
    "## Level 2: LLMs + structured outputs/function calling"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "f02c8a4c",
   "metadata": {},
   "outputs": [],
   "source": [
    "from pydantic import BaseModel, Field\n",
    "\n",
    "class WriteFileOperation(BaseModel):\n",
    "    file_path: str = Field(description=\"The path to the file to be written to or read from\")\n",
    "    content: str = Field(description=\"The content to be written to the file\")\n",
    "\n",
    "class ReadFileOperation(BaseModel):\n",
    "    file_path: str = Field(description=\"The path to the file to be written to or read from\")\n",
    "\n",
    "\n",
    "response = client.beta.chat.completions.parse(\n",
    "    model=\"gpt-5\",\n",
    "    messages=[{\"role\": \"system\", \"content\": \"You are a helpful assistant that can write and read files.\"},\n",
    "              {\"role\": \"user\", \"content\": \"Write a file called 'test.txt' with the content 'Hello, world!'\"}],\n",
    "    response_format=WriteFileOperation)\n",
    "\n",
    "output_write_file_ops = response.choices[0].message.parsed"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "bf46fa5d",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "test.txt\n",
      "Hello, world!\n"
     ]
    }
   ],
   "source": [
    "print(output_write_file_ops.file_path)\n",
    "print(output_write_file_ops.content)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "54cb1b3e",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "File was created!\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "WriteFileOperation(file_path='level2agentoutput.txt', content='Level 2 works!')"
      ]
     },
     "execution_count": 6,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "def level2_agent_llm_structured(prompt):\n",
    "    response = client.beta.chat.completions.parse(\n",
    "    model=\"gpt-5\",\n",
    "    messages=[{\"role\": \"system\", \"content\": \"You are a helpful assistant that can write and read files.\"},\n",
    "              {\"role\": \"user\", \"content\": prompt}],\n",
    "    response_format=WriteFileOperation)# Structured OUTPUT from the LLM!\n",
    "    output_args = response.choices[0].message.parsed\n",
    "    # FUNCTION CALLING!\n",
    "    write_file(output_args.file_path, output_args.content)\n",
    "    print(\"File was created!\")\n",
    "    return output_args\n",
    "\n",
    "level2_agent_llm_structured(\"Write a file called 'level2agentoutput.txt' with the content 'Level 2 works!'\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "07f3f54d",
   "metadata": {},
   "outputs": [],
   "source": [
    "# save this as sample_input.txt\n",
    "response = get_response(\"Create a 3 paragraph exaplanation of modern llm agents\")\n",
    "write_file(\"sample_input.txt\", response)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "0d912086",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "User Task: Read the file: 'sample_input.txt' and write a summary of that file into a new file called 'summary_file.txt'\n",
      "\n",
      "--------------------------------------------------\n",
      "\n",
      "--- Iteration 1 ---\n",
      "Agent: THOUGHT: I need to read the content of 'sample_input.txt' to understand its contents before I can write a summary.\n",
      "ACTION: read_file('sample_input.txt')\n",
      "Executing: read_file('sample_input.txt')\n",
      "Observation: Modern LLM agents are software systems that wrap a large language model in an autonomous loop that can plan, act through tools, and adapt based on feedback to pursue a goal. Unlike static chatbots tha...\n",
      "\n",
      "--- Iteration 2 ---\n",
      "Agent: THOUGHT: I have read the content of 'sample_input.txt'. Now, I need to write a concise summary of this content and save it to 'summary_file.txt'.\n",
      "\n",
      "Summary: The text describes modern LLM agents, which are advanced software systems that utilize large language models to autonomously plan, act, and adapt to achieve goals. Unlike static chatbots, these agents execute complex workflows by interfacing with tools, maintaining state, and iterating based on feedback. They consist of components like planners, tool routers, and memory systems, and can operate as single agents or coordinated teams. To ensure reliability, agents use guardrails such as schema validation, human approvals, and monitoring. Despite their power, they require careful task scoping and safe design practices. Future advancements are expected to enhance their capabilities.\n",
      "\n",
      "ACTION: write_file('summary_file.txt', \"The text describes modern LLM agents, which are advanced software systems that utilize large language models to autonomously plan, act, and adapt to achieve goals. Unlike static chatbots, these agents execute complex workflows by interfacing with tools, maintaining state, and iterating based on feedback. They consist of components like planners, tool routers, and memory systems, and can operate as single agents or coordinated teams. To ensure reliability, agents use guardrails such as schema validation, human approvals, and monitoring. Despite their power, they require careful task scoping and safe design practices. Future advancements are expected to enhance their capabilities.\")\n",
      "Executing: write_file('summary_file.txt', \"The text describes modern LLM agents, which are advanced software systems that utilize large language models to autonomously plan, act, and adapt to achieve goals. Unlike static chatbots, these agents execute complex workflows by interfacing with tools, maintaining state, and iterating based on feedback. They consist of components like planners, tool routers, and memory systems, and can operate as single agents or coordinated teams. To ensure reliability, agents use guardrails such as schema validation, human approvals, and monitoring. Despite their power, they require careful task scoping and safe design practices. Future advancements are expected to enhance their capabilities.\")\n",
      "Observation: Successfully wrote to summary_file.txt\n",
      "\n",
      "--- Iteration 3 ---\n",
      "Agent: THOUGHT: I have successfully written the summary of 'sample_input.txt' into 'summary_file.txt'.\n",
      "ANSWER: I have read the content of 'sample_input.txt' and written a summary into 'summary_file.txt'. If you need anything else, feel free to ask!\n",
      "\n",
      "✓ Final Answer: I have read the content of 'sample_input.txt' and written a summary into 'summary_file.txt'. If you need anything else, feel free to ask!\n"
     ]
    }
   ],
   "source": [
    "def level3_agent_loop(task_prompt):\n",
    "    \"\"\"\n",
    "    ReAct-style agent loop that iteratively:\n",
    "    1. Observes the current state\n",
    "    2. Thinks about what to do next\n",
    "    3. Takes an action (either calls a tool or provides final answer)\n",
    "    4. Gets observation from the action\n",
    "    5. Repeats until task is complete\n",
    "    \"\"\"\n",
    "    # Available tools that the agent can use\n",
    "    available_tools = {\n",
    "        'read_file': read_file,\n",
    "        'write_file': write_file\n",
    "    }\n",
    "    \n",
    "    # Initialize conversation history with system prompt\n",
    "    messages = [\n",
    "        {\"role\": \"system\", \"content\": \"\"\"You are a helpful assistant that can read and write files.\n",
    "        \n",
    "            You work in a loop where you:\n",
    "            1. Think about what needs to be done\n",
    "            2. Either call a tool OR provide a final answer\n",
    "            3. Observe the result and continue if needed\n",
    "\n",
    "            Available tools:\n",
    "            - read_file(file_path): Reads content from a file\n",
    "            - write_file(file_path, content): Writes content to a file\n",
    "\n",
    "            When you need to use a tool, respond with:\n",
    "            THOUGHT: [your reasoning]\n",
    "            ACTION: [tool_name](arguments)\n",
    "\n",
    "            When you have the final answer, respond with:\n",
    "            THOUGHT: [your reasoning]\n",
    "            ANSWER: [your final response to the user]\n",
    "\n",
    "            Important: Only use ACTION or ANSWER, not both in the same response.\"\"\"},\n",
    "        {\"role\": \"user\", \"content\": task_prompt}\n",
    "    ]\n",
    "    \n",
    "    max_iterations = 10  # Prevent infinite loops\n",
    "    iteration = 0\n",
    "    \n",
    "    print(f\"User Task: {task_prompt}\\n\")\n",
    "    print(\"-\" * 50)\n",
    "    \n",
    "    while iteration < max_iterations:\n",
    "        iteration += 1\n",
    "        print(f\"\\n--- Iteration {iteration} ---\")\n",
    "        \n",
    "        # Get LLM response\n",
    "        response = client.chat.completions.create(\n",
    "            model=\"gpt-4o\",  # Using a model that exists\n",
    "            messages=messages,\n",
    "            temperature=0.1  # Lower temperature for more consistent behavior\n",
    "        )\n",
    "        \n",
    "        agent_response = response.choices[0].message.content\n",
    "        print(f\"Agent: {agent_response}\")\n",
    "        \n",
    "        # Add agent's response to conversation history\n",
    "        messages.append({\"role\": \"assistant\", \"content\": agent_response})\n",
    "        \n",
    "        # Parse the response to determine if it's an action or final answer\n",
    "        if \"ANSWER:\" in agent_response:\n",
    "            # Agent has provided final answer\n",
    "            answer = agent_response.split(\"ANSWER:\")[1].strip()\n",
    "            print(f\"\\n✓ Final Answer: {answer}\")\n",
    "            return answer\n",
    "        \n",
    "        elif \"ACTION:\" in agent_response:\n",
    "            # Agent wants to execute a tool\n",
    "            action_line = agent_response.split(\"ACTION:\")[1].strip().split('\\n')[0].strip()\n",
    "            \n",
    "            try:\n",
    "                # Parse the function call\n",
    "                import re\n",
    "                match = re.match(r'(\\w+)\\((.*)\\)', action_line)\n",
    "                if match:\n",
    "                    tool_name = match.group(1)\n",
    "                    args_str = match.group(2)\n",
    "                    \n",
    "                    if tool_name in available_tools:\n",
    "                        # Execute the tool\n",
    "                        print(f\"Executing: {action_line}\")\n",
    "                        \n",
    "                        # Parse arguments (simple parsing for demo)\n",
    "                        if tool_name == 'read_file':\n",
    "                            # Extract file path from quotes\n",
    "                            file_path = args_str.strip('\\'\"')\n",
    "                            observation = available_tools[tool_name](file_path)\n",
    "                        elif tool_name == 'write_file':\n",
    "                            # Split by comma and extract both arguments\n",
    "                            parts = args_str.split(',', 1)\n",
    "                            file_path = parts[0].strip().strip('\\'\"')\n",
    "                            content = parts[1].strip().strip('\\'\"') if len(parts) > 1 else \"\"\n",
    "                            available_tools[tool_name](file_path, content)\n",
    "                            observation = f\"Successfully wrote to {file_path}\"\n",
    "                        \n",
    "                        print(f\"Observation: {observation[:200]}...\" if len(str(observation)) > 200 else f\"Observation: {observation}\")\n",
    "                        \n",
    "                        # Add observation to conversation\n",
    "                        messages.append({\"role\": \"user\", \"content\": f\"Observation from {tool_name}: {observation}\"})\n",
    "                    else:\n",
    "                        messages.append({\"role\": \"user\", \"content\": f\"Error: Unknown tool '{tool_name}'\"})\n",
    "                else:\n",
    "                    messages.append({\"role\": \"user\", \"content\": f\"Error: Could not parse action '{action_line}'\"})\n",
    "                    \n",
    "            except Exception as e:\n",
    "                error_msg = f\"Error executing action: {str(e)}\"\n",
    "                print(f\"Error: {error_msg}\")\n",
    "                messages.append({\"role\": \"user\", \"content\": error_msg})\n",
    "        else:\n",
    "            # Agent provided neither ACTION nor ANSWER - prompt for clarification\n",
    "            messages.append({\"role\": \"user\", \"content\": \"Please respond with either 'ACTION: tool_name(args)' to use a tool or 'ANSWER: your_response' to provide the final answer.\"})\n",
    "    \n",
    "    print(\"\\n⚠ Maximum iterations reached\")\n",
    "    return \"Maximum iterations reached without completing the task\"\n",
    "    \n",
    "# Test the agent loop\n",
    "prompt = \"Read the file: 'sample_input.txt' and write a summary of that file into a new file called 'summary_file.txt'\"\n",
    "result = level3_agent_loop(prompt)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a5cf1641",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}


---
./notebooks/1.0-intro-openai-agents-sdk.ipynb
---
{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "!pip install openai-agents"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Introduction to [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)\n",
    "\n",
    "- Allows you to build agentic AI apps in a lightweight, easy-to-use package with very few abstractions. \n",
    "- Small set of primitives:\n",
    "  - Agents: LLMs equipped with instructions and tools\n",
    "  - Handoffs: allow agents to delegate to other agents for specific tasks\n",
    "  - Guardrails: enable validation of agent inputs and outputs\n",
    "  - Sessions: automatically maintains conversation history across agent runs\n",
    "\n",
    "It also includes **built-in tracing**: lets you visualize and debug your agentic flows, as well as evaluate them and even fine-tune models for your application.\n",
    "\n",
    "**2 design principles:**\n",
    "\n",
    "1. Enough features to be worth using, but few enough primitives to make it quick to learn.\n",
    "2. Works great out of the box, but you can customize exactly what happens.\n",
    "\n",
    "## Main features:\n",
    "\n",
    "- Agent loop: Built-in agent loop that handles calling tools, sending results to the LLM, and looping until the LLM is done.\n",
    "- Python-first: Use built-in language features to orchestrate and chain agents, rather than needing to learn new abstractions.\n",
    "- Handoffs: A powerful feature to coordinate and delegate between multiple agents.\n",
    "- Guardrails: Run input validations and checks in parallel to your agents, breaking early if the checks fail.\n",
    "- Sessions: Automatic conversation history management across agent runs, eliminating manual state handling.\n",
    "- Function tools: Turn any Python function into a tool, with automatic schema generation and Pydantic-powered validation.\n",
    "- Tracing: Built-in tracing that lets you visualize, debug and monitor your workflows, as well as use the OpenAI suite of evaluation, fine-tuning and distillation tools."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Simple Code Example"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Set your openai API key\n",
    "import os\n",
    "import getpass\n",
    "\n",
    "def _set_env(var: str):\n",
    "    if not os.environ.get(var):\n",
    "        os.environ[var] = getpass.getpass(f\"var: \")\n",
    "\n",
    "_set_env(\"OPENAI_API_KEY\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Function calls itself  \n",
      "Looping inward, depth unwinds  \n",
      "Base case whispers stop\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Exception in thread Thread-4 (_run):\n",
      "Traceback (most recent call last):\n",
      "  File \"/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/threading.py\", line 1045, in _bootstrap_inner\n",
      "    self.run()\n",
      "  File \"/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/site-packages/ipykernel/ipkernel.py\", line 766, in run_closure\n",
      "    _threading_Thread_run(self)\n",
      "  File \"/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/threading.py\", line 982, in run\n",
      "    self._target(*self._args, **self._kwargs)\n",
      "  File \"/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/site-packages/agents/tracing/processors.py\", line 228, in _run\n",
      "    self._export_batches(force=False)\n",
      "  File \"/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/site-packages/agents/tracing/processors.py\", line 261, in _export_batches\n",
      "    self._exporter.export(items_to_export)\n",
      "  File \"/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/site-packages/agents/tracing/processors.py\", line 111, in export\n",
      "    response = self._client.post(url=self.endpoint, headers=headers, json=payload)\n",
      "               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/site-packages/httpx/_client.py\", line 1144, in post\n",
      "    return self.request(\n",
      "           ^^^^^^^^^^^^^\n",
      "  File \"/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/site-packages/httpx/_client.py\", line 812, in request\n",
      "    request = self.build_request(\n",
      "              ^^^^^^^^^^^^^^^^^^^\n",
      "  File \"/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/site-packages/httpx/_client.py\", line 378, in build_request\n",
      "    return Request(\n",
      "           ^^^^^^^^\n",
      "  File \"/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/site-packages/httpx/_models.py\", line 408, in __init__\n",
      "    headers, stream = encode_request(\n",
      "                      ^^^^^^^^^^^^^^^\n",
      "  File \"/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/site-packages/httpx/_content.py\", line 216, in encode_request\n",
      "    return encode_json(json)\n",
      "           ^^^^^^^^^^^^^^^^^\n",
      "  File \"/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/site-packages/httpx/_content.py\", line 177, in encode_json\n",
      "    body = json_dumps(\n",
      "           ^^^^^^^^^^^\n",
      "  File \"/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/json/__init__.py\", line 238, in dumps\n",
      "    **kw).encode(obj)\n",
      "          ^^^^^^^^^^^\n",
      "  File \"/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/json/encoder.py\", line 200, in encode\n",
      "    chunks = self.iterencode(o, _one_shot=True)\n",
      "             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/json/encoder.py\", line 258, in iterencode\n",
      "    return _iterencode(o, 0)\n",
      "           ^^^^^^^^^^^^^^^^^\n",
      "  File \"/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/json/encoder.py\", line 180, in default\n",
      "    raise TypeError(f'Object of type {o.__class__.__name__} '\n",
      "TypeError: Object of type property is not JSON serializable\n"
     ]
    }
   ],
   "source": [
    "# this import is for running it on a jupyter notebook\n",
    "import nest_asyncio\n",
    "nest_asyncio.apply()\n",
    "\n",
    "from agents import Agent, Runner\n",
    "\n",
    "\n",
    "# Setup your agent with custom instructions (here we're using the default model)\n",
    "agent = Agent(name=\"Assistant\", instructions=\"You are a helpful assistant\", model='gpt-5-mini')\n",
    "\n",
    "# Run your agent\n",
    "result = Runner.run_sync(agent, \"Write a haiku about recursion in programming.\")\n",
    "\n",
    "# Print the output\n",
    "print(result.final_output)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Short answer — a practical, widely agreed list (subjective) as of August 27, 2025:\n",
      "\n",
      "1) LangChain — the de facto, ecosystem-first framework for building LLM agents and RAG/chain workflows; massive community, mature docs and tooling (Python + JS). ([github.com](https://github.com/langchain-ai/langchain?utm_source=chatgpt.com), [repositorystats.com](https://repositorystats.com/langchain-ai/langchain?utm_source=chatgpt.com))\n",
      "\n",
      "2) Microsoft AutoGen — Microsoft’s multi‑agent programming framework (with AutoGen Studio/benching, extensions, and enterprise integrations) aimed at complex conversational/multi‑agent workflows. ([github.com](https://github.com/microsoft/autogen?utm_source=chatgpt.com), [microsoft.com](https://www.microsoft.com/en-us/research/project/autogen/overview/?utm_source=chatgpt.com))\n",
      "\n",
      "3) MetaGPT (and MetaGPT X / MGX) — role‑based multi‑agent framework that encodes SOPs (Product Manager / Engineer roles, etc.) and has become a go‑to for multi‑agent software workflows. ([gh.loli.garden](https://gh.loli.garden/geekan/MetaGPT?utm_source=chatgpt.com), [arxiv.org](https://arxiv.org/abs/2308.00352?utm_source=chatgpt.com))\n",
      "\n",
      "4) Dify — an open‑source LLM app / agent platform (visual workflow + RAG + built‑in tools and observability) that’s grown fast as a production‑oriented agent/workflow stack. ([dify.ai](https://dify.ai/?utm_source=chatgpt.com), [github.com](https://github.com/langgenius/dify?utm_source=chatgpt.com))\n",
      "\n",
      "5) Amazon Bedrock AgentCore (AWS AgentCore) — AWS’s enterprise agent platform (AgentCore on Bedrock) for building, running and governing production agent fleets — a major enterprise entrant in 2025. ([techradar.com](https://www.techradar.com/pro/aws-looks-to-super-charge-ai-agents-with-amazon-bedrock-agentcore?utm_source=chatgpt.com))\n",
      "\n",
      "Notes and context\n",
      "- “Top” is inherently subjective. I ranked these by a combination of developer/community traction (GitHub/ecosystem), breadth of features (multi‑agent support, tools, RAG, observability), and enterprise momentum (cloud vendor offerings and press). If you want a different ranking (e.g., by GitHub stars, ease‑of‑use, or enterprise readiness), I can re-sort and show the metrics.\n",
      "- Honorable mentions: LangGraph / LangChain’s LangGraph (graph‑style stateful workflows), LangFlow / Flowise (visual builders), SuperAGI, Microsoft Semantic Kernel, OpenAI Swarm / Agents SDK, and several newer open‑source projects (Atomic Agents, Agno, etc.). These are worth considering depending on your use case. ([github.com](https://github.com/langchain-ai?utm_source=chatgpt.com), [yuxiaopeng.com](https://yuxiaopeng.com/Github-Ranking-AI/?utm_source=chatgpt.com))\n",
      "\n",
      "Would you like:\n",
      "- a comparison table (features, language, maturity, license, typical use cases), or\n",
      "- a recommendation for a specific use case (production customer service bot, research assistant, autonomous automation, on‑prem/self‑hosted, etc.)?\n"
     ]
    }
   ],
   "source": [
    "from agents.tool import WebSearchTool\n",
    "\n",
    "agent = Agent(name=\"Web Search Agent\", \n",
    "              instructions='You research online with the WebSearchTool and you answer the question from the user.',\n",
    "              model='gpt-5-mini',\n",
    "              tools=[WebSearchTool()])\n",
    "\n",
    "result = Runner.run_sync(agent, 'What are the top 5 agent frameworks in 2025?')\n",
    "\n",
    "print(result.final_output)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "openai-agents-sdk",
   "language": "python",
   "name": "openai-agents-sdk"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.11"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}


---
./notebooks/2.0-openai-agents-sdk-tools-structured-outputs.ipynb
---
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Agents\n",
    "\n",
    "Agent = large language model (LLM), configured with instructions and tools.\n",
    "\n",
    "Basic configuration:\n",
    "\n",
    "- **name**: A required string that identifies your agent.\n",
    "- **instructions**: also known as a developer message or system prompt.\n",
    "- **model**: which LLM to use, and optional model_settings to configure model tuning parameters like - temperature, top_p, etc.\n",
    "- **tools**: Tools that the agent can use to achieve its tasks."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import nest_asyncio\n",
    "nest_asyncio.apply()\n",
    "from agents import Agent, ModelSettings, function_tool\n",
    "\n",
    "@function_tool\n",
    "def get_weather(city: str) -> str:\n",
    "     \"\"\"returns weather info for the specified city.\"\"\"\n",
    "     return f\"The weather in {city} is sunny\"\n",
    "\n",
    "\n",
    "agent = Agent(\n",
    "    name=\"Weather agent\",\n",
    "    instructions=\"You use the get_weather tool to get the weather in a city.\",\n",
    "    model=\"gpt-5-mini\",\n",
    "    tools=[get_weather],\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "from agents import Runner\n",
    "\n",
    "result = Runner.run_sync(agent, 'What is the weather in Tokyo?')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "The weather in Tokyo is sunny.\n"
     ]
    }
   ],
   "source": [
    "print(result.final_output)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Live Example Structured Outputs"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "product_name='Cable Matters USB C to 2.5 Gigabit Ethernet Adapter with Charging (100W)' product_price=35.0 product_description='Summary: 2.5 Gbps USB‑C to RJ45 adapter with pass‑through Power Delivery (up to 100W). Good balance of speed, build quality, and price for laptops that need faster-than‑Gigabit wired networking. \\ue200cite\\ue202turn0search0\\ue201\\n\\nKey specs & notes:\\n- Network speed: up to 2.5 Gbps (backward compatible with 10/100/1000 Mbps). \\ue200cite\\ue202turn0search0\\ue201\\n- Power delivery: up to 100W passthrough (can charge your laptop while using Ethernet). \\ue200cite\\ue202turn0search0\\ue201\\n- Driver/compatibility: plug‑and‑play on many systems, but the listing notes additional drivers may be required to reach full 2.5 Gbps on some OS/hardware — check your host OS and chipset. \\ue200cite\\ue202turn0search0\\ue201\\n- Price (Amazon listing): approximately $35 (check current listing for final price/availability). \\ue200cite\\ue202turn0search0\\ue201\\n\\nBuying tips:\\n- To actually get 2.5 Gbps you also need a 2.5G‑capable switch/router and appropriate Cat5e/Cat6 cable; otherwise the adapter will fall back to Gigabit speeds. \\ue200cite\\ue202turn0search0\\ue201\\n- If you want a lower‑cost, simple Gigabit adapter without PD, consider budget options like AmazonBasics; if you want extra ports (USB, HDMI) consider multiport hubs from UGREEN or similar. (Examples found on Amazon.) \\ue200cite\\ue202turn1search3\\ue202turn1search2\\ue201\\n\\nIf you’d like, I can:\\n- Compare 3–5 specific adapters (budget, best overall, best for 2.5Gb, best hub) with live prices from Amazon and other retailers; or\\n- Find the best deals right now (price drops / Prime Day / coupons) and show 3 purchase links.'\n"
     ]
    }
   ],
   "source": [
    "from pydantic import BaseModel, Field\n",
    "from agents.tool import WebSearchTool\n",
    "\n",
    "class ProductInfo(BaseModel):\n",
    "    product_name: str = Field(description=\"The name of the product\")\n",
    "    product_price: float = Field(description=\"The price of the product\")\n",
    "    product_description: str = Field(description=\"A description of the product\")\n",
    "\n",
    "agent = Agent(\n",
    "    name=\"Product Search Agent\",\n",
    "    instructions=\"You use the WebSearchTool to search the web for product information.\",\n",
    "    model=\"gpt-5-mini\",\n",
    "    tools=[WebSearchTool()],\n",
    "    output_type=ProductInfo,\n",
    ")\n",
    "\n",
    "result = Runner.run_sync(agent, 'Research an USBC to ethernet adapter on amazon or others')\n",
    "\n",
    "print(result.final_output)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "'Cable Matters USB C to 2.5 Gigabit Ethernet Adapter with Charging (100W)'"
      ]
     },
     "execution_count": 12,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "result.final_output.product_name"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "'Summary: 2.5 Gbps USB‑C to RJ45 adapter with pass‑through Power Delivery (up to 100W). Good balance of speed, build quality, and price for laptops that need faster-than‑Gigabit wired networking. \\ue200cite\\ue202turn0search0\\ue201\\n\\nKey specs & notes:\\n- Network speed: up to 2.5 Gbps (backward compatible with 10/100/1000 Mbps). \\ue200cite\\ue202turn0search0\\ue201\\n- Power delivery: up to 100W passthrough (can charge your laptop while using Ethernet). \\ue200cite\\ue202turn0search0\\ue201\\n- Driver/compatibility: plug‑and‑play on many systems, but the listing notes additional drivers may be required to reach full 2.5 Gbps on some OS/hardware — check your host OS and chipset. \\ue200cite\\ue202turn0search0\\ue201\\n- Price (Amazon listing): approximately $35 (check current listing for final price/availability). \\ue200cite\\ue202turn0search0\\ue201\\n\\nBuying tips:\\n- To actually get 2.5 Gbps you also need a 2.5G‑capable switch/router and appropriate Cat5e/Cat6 cable; otherwise the adapter will fall back to Gigabit speeds. \\ue200cite\\ue202turn0search0\\ue201\\n- If you want a lower‑cost, simple Gigabit adapter without PD, consider budget options like AmazonBasics; if you want extra ports (USB, HDMI) consider multiport hubs from UGREEN or similar. (Examples found on Amazon.) \\ue200cite\\ue202turn1search3\\ue202turn1search2\\ue201\\n\\nIf you’d like, I can:\\n- Compare 3–5 specific adapters (budget, best overall, best for 2.5Gb, best hub) with live prices from Amazon and other retailers; or\\n- Find the best deals right now (price drops / Prime Day / coupons) and show 3 purchase links.'"
      ]
     },
     "execution_count": 13,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "result.final_output.product_description"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "35.0"
      ]
     },
     "execution_count": 14,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "result.final_output.product_price"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>Product Name</th>\n",
       "      <th>Price (USD)</th>\n",
       "      <th>Description</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>Cable Matters USB C to 2.5 Gigabit Ethernet Ad...</td>\n",
       "      <td>35.0</td>\n",
       "      <td>Summary: 2.5 Gbps USB‑C to RJ45 adapter with p...</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "                                        Product Name  Price (USD)  \\\n",
       "0  Cable Matters USB C to 2.5 Gigabit Ethernet Ad...         35.0   \n",
       "\n",
       "                                         Description  \n",
       "0  Summary: 2.5 Gbps USB‑C to RJ45 adapter with p...  "
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "import pandas as pd\n",
    "\n",
    "# Create a DataFrame from the result\n",
    "df = pd.DataFrame([{\n",
    "    \"Product Name\": result.final_output.product_name,\n",
    "    \"Price (USD)\": result.final_output.product_price,\n",
    "    \"Description\": result.final_output.product_description\n",
    "}])\n",
    "\n",
    "# Display the DataFrame as a nice table\n",
    "from IPython.display import display\n",
    "display(df)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "'{\"product_name\":\"Cable Matters USB C to 2.5 Gigabit Ethernet Adapter with Charging (100W)\",\"product_price\":35.0,\"product_description\":\"Summary: 2.5 Gbps USB‑C to RJ45 adapter with pass‑through Power Delivery (up to 100W). Good balance of speed, build quality, and price for laptops that need faster-than‑Gigabit wired networking. \\ue200cite\\ue202turn0search0\\ue201\\\\n\\\\nKey specs & notes:\\\\n- Network speed: up to 2.5 Gbps (backward compatible with 10/100/1000 Mbps). \\ue200cite\\ue202turn0search0\\ue201\\\\n- Power delivery: up to 100W passthrough (can charge your laptop while using Ethernet). \\ue200cite\\ue202turn0search0\\ue201\\\\n- Driver/compatibility: plug‑and‑play on many systems, but the listing notes additional drivers may be required to reach full 2.5 Gbps on some OS/hardware — check your host OS and chipset. \\ue200cite\\ue202turn0search0\\ue201\\\\n- Price (Amazon listing): approximately $35 (check current listing for final price/availability). \\ue200cite\\ue202turn0search0\\ue201\\\\n\\\\nBuying tips:\\\\n- To actually get 2.5 Gbps you also need a 2.5G‑capable switch/router and appropriate Cat5e/Cat6 cable; otherwise the adapter will fall back to Gigabit speeds. \\ue200cite\\ue202turn0search0\\ue201\\\\n- If you want a lower‑cost, simple Gigabit adapter without PD, consider budget options like AmazonBasics; if you want extra ports (USB, HDMI) consider multiport hubs from UGREEN or similar. (Examples found on Amazon.) \\ue200cite\\ue202turn1search3\\ue202turn1search2\\ue201\\\\n\\\\nIf you’d like, I can:\\\\n- Compare 3–5 specific adapters (budget, best overall, best for 2.5Gb, best hub) with live prices from Amazon and other retailers; or\\\\n- Find the best deals right now (price drops / Prime Day / coupons) and show 3 purchase links.\"}'"
      ]
     },
     "execution_count": 21,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "result.final_output.model_dump_json()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "When selecting a refrigerator in Lisbon in 2025, it's essential to consider factors such as energy efficiency, capacity, design, and advanced features. Here are some top-rated models to consider:\n",
      "\n",
      "\n",
      "\n",
      "**Haier Twin Inverter Refrigerator**  \n",
      "Recognized as the most trusted refrigerator brand in Portugal in 2025, Haier offers models with Twin Inverter Technology, ensuring quick cooling and reduced noise. ([corporate.haier-europe.com](https://corporate.haier-europe.com/press-release/haier-elected-as-the-most-trusted-brand-in-refrigerators-in-portugal/?utm_source=openai))\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "**LG InstaView Door-in-Door Refrigerator**  \n",
      "This model features a sleek design with a glass panel that illuminates with two knocks, allowing you to see inside without opening the door, thereby conserving energy. ([analyticsinsight.net](https://www.analyticsinsight.net/home-electronics/top-10-refrigerators-for-large-families-in-2025-with-smart-cooling?utm_source=openai))\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "**Samsung Family Hub Refrigerator**  \n",
      "Equipped with a Wi-Fi-enabled screen and voice assistant, this refrigerator offers family management features alongside its 810-liter capacity. ([analyticsinsight.net](https://www.analyticsinsight.net/home-electronics/top-10-refrigerators-for-large-families-in-2025-with-smart-cooling?utm_source=openai))\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "**Bosch 800 Series Refrigerator**  \n",
      "Known for its sleek design and superior cooling technology, this model includes VitaFreshPro for optimal food preservation and Wi-Fi connectivity for remote access. ([coinprwire.com](https://www.coinprwire.com/newsroom/the_top_5_best_refrigerators_in_2025-14274?utm_source=openai))\n",
      "\n",
      "\n",
      "\n",
      "\n",
      "**Whirlpool Double Drawer Refrigerator**  \n",
      "This refrigerator offers adaptive defrost to save energy and a fingerprint-resistant stainless steel finish, making it both functional and stylish. ([coinprwire.com](https://www.coinprwire.com/newsroom/the_top_5_best_refrigerators_in_2025-14274?utm_source=openai))\n",
      "\n",
      "\n",
      "When making your decision, consider the following:\n",
      "\n",
      "- **Energy Efficiency**: Opt for models with high energy ratings to reduce electricity consumption.\n",
      "\n",
      "- **Capacity**: Choose a size that fits your household needs, typically between 500L-700L for large families.\n",
      "\n",
      "- **Smart Features**: Features like Wi-Fi connectivity and voice control can enhance convenience.\n",
      "\n",
      "- **Design and Build**: Look for durable materials and finishes that complement your kitchen aesthetics.\n",
      "\n",
      "For purchasing options in Lisbon, consider visiting local appliance retailers or checking online platforms that deliver to your area. Always verify the availability of specific models and inquire about after-sales service and warranty options. \n"
     ]
    }
   ],
   "source": [
    "import nest_asyncio\n",
    "nest_asyncio.apply()\n",
    "\n",
    "import asyncio\n",
    "\n",
    "from agents import Agent, Runner, WebSearchTool, trace\n",
    "\n",
    "\n",
    "\n",
    "agent = Agent(\n",
    "    name=\"Web searcher\",\n",
    "    instructions=\"You are a helpful agent.\",\n",
    "    tools=[WebSearchTool(user_location={\"type\": \"approximate\", \"city\": \"Lisbon\"})],\n",
    ")\n",
    "\n",
    "with trace(\"Web search example\"):\n",
    "    result = await Runner.run(\n",
    "        agent,\n",
    "        \"Search the best fridges to buy in Lisbon in 2025.\",\n",
    "    )\n",
    "    print(result.final_output)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "from pathlib import Path\n",
    "from typing import List, Dict\n",
    "from agents import function_tool\n",
    "\n",
    "@function_tool\n",
    "def search_course_notes(query: str) -> Dict[str, List[str]]:\n",
    "    \"\"\"\n",
    "    Search through the course notes.\n",
    "    \n",
    "    Args:\n",
    "        query: The search term to look for\n",
    "    \n",
    "    Returns:\n",
    "        Dictionary containing matching content sections\n",
    "    \"\"\"\n",
    "    file_path = \"\"\n",
    "    \n",
    "    \n",
    "    with open(file_path, 'r', encoding='utf-8') as f:\n",
    "        content = f.read()\n",
    "        \n",
    "    return content"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create the Agent with this custom tool\n",
    "from agents import Agent, Runner, trace\n",
    "\n",
    "\n",
    "async def main():\n",
    "    # Create the agent with our custom tool\n",
    "    agent = Agent(\n",
    "        name=\"LangChain Agents Course Assistant\",\n",
    "        instructions=\"\"\"You are a helpful assistant that searches through the LangChain Agents Course notes.\n",
    "        When you find matches, summarize the relevant information found in the notes.\n",
    "        Format your responses in a clear, organized way.\"\"\",\n",
    "        tools=[search_course_notes]\n",
    "    )\n",
    "    \n",
    "    # Example search\n",
    "    with trace(\"LangChain Agents Course search\"):\n",
    "        result = await Runner.run(\n",
    "            agent, \n",
    "            \"What are the main tasks or goals mentioned in the project notes?\"\n",
    "        )\n",
    "        print(result.final_output)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "The main tasks and goals mentioned in the project notes include:\n",
      "\n",
      "1. **Update and Integration:**\n",
      "   - Update the introduction to agents using specific resources.\n",
      "   - Integrate and reference study cases and examples from various sources and repositories.\n",
      "\n",
      "2. **Research and Development:**\n",
      "   - Research good examples of agents in practice.\n",
      "   - Develop and reproduce workflows as new notebooks for the course.\n",
      "   - Stay updated with the latest developments in local models and tools.\n",
      "\n",
      "3. **Example Projects and Demonstrations:**\n",
      "   - Create extraction examples with a fun and simple user interface.\n",
      "   - Develop a voice react agent.\n",
      "   - Demonstrate agent concepts using tools and visualizations.\n",
      "\n",
      "4. **Review and Experimentation:**\n",
      "   - Review and understand technical papers that could provide insights into agent development.\n",
      "   - Experiment with different workflows like LLM Routing and parallelization patterns.\n",
      "\n",
      "5. **Evaluation and Optimization:**\n",
      "   - Evaluate agents for specific tasks and improve their performance over time.\n",
      "   - Ensure success by measuring performance and iterating on implementations.\n",
      "\n",
      "6. **Implementation and Execution:**\n",
      "   - Use specific examples and guidelines to shape the implementation of LLM agents.\n",
      "   - Explore prompt engineering and agent architecture, focusing on communication and multi-agent systems.\n",
      "\n",
      "7. **Documentation and Sharing:**\n",
      "   - Maintain thorough documentation on agent development processes.\n",
      "   - Share findings and setups in accessible formats such as notebooks and shared repositories.\n",
      "\n",
      "These tasks aim to develop a comprehensive understanding and implementation of LangChain agents with a focus on collaboration, integration, and continuous improvement.\n"
     ]
    }
   ],
   "source": [
    "import asyncio\n",
    "\n",
    "asyncio.run(main())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "openai-agents-sdk",
   "language": "python",
   "name": "openai-agents-sdk"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.11"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}


---
./notebooks/2.1-openai-agents-sdk-mcp.ipynb
---
{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0ea412d5",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}


---
./notebooks/3.0-building-research-agent.ipynb
---
{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "1",
   "metadata": {},
   "source": [
    "# Building a Research Agent with OpenAI Agents SDK\n",
    "\n",
    "In this tutorial, we'll build a research agent that can help gather information, analyze topics, and provide comprehensive research reports. We'll use the OpenAI Agents SDK to create an intelligent agent with custom tools for research tasks.\n",
    "\n",
    "## What We'll Learn\n",
    "\n",
    "1. **Setting up an Agent** - Create and configure a research-focused agent\n",
    "2. **Adding Custom Tools** - Implement research tools using function decorators\n",
    "3. **Running Research Tasks** - Execute queries and get structured results\n",
    "4. **Basic Tracing** - Monitor and debug agent execution with tracing\n",
    "\n",
    "## Prerequisites\n",
    "\n",
    "- Python 3.11+\n",
    "- OpenAI API key\n",
    "- Basic understanding of async/await patterns"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "2",
   "metadata": {},
   "source": [
    "## 1. Installation and Setup\n",
    "\n",
    "First, let's install the OpenAI Agents SDK and set up our environment."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "3",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "OpenAI Agents SDK is ready to use!\n"
     ]
    }
   ],
   "source": [
    "# Install the OpenAI Agents SDK\n",
    "# !pip install openai-agents\n",
    "\n",
    "# Import required libraries\n",
    "import os\n",
    "import json\n",
    "import nest_asyncio\n",
    "nest_asyncio.apply()\n",
    "from typing import List, Dict, Any\n",
    "from datetime import datetime\n",
    "from agents import Agent, Runner, function_tool, trace\n",
    "from agents import ModelSettings\n",
    "from agents.run import RunConfig\n",
    "\n",
    "# Set your OpenAI API key\n",
    "# os.environ[\"OPENAI_API_KEY\"] = \"your-api-key-here\"\n",
    "\n",
    "print(\"OpenAI Agents SDK is ready to use!\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "4",
   "metadata": {},
   "source": [
    "## 2. Creating Custom Research Tools\n",
    "\n",
    "Research agents need specialized tools to gather and process information. Let's create some essential research tools using the `@function_tool` decorator."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "5",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Research tools created successfully!\n"
     ]
    }
   ],
   "source": [
    "@function_tool\n",
    "def search_academic_papers(query: str, max_results: int = 5) -> str:\n",
    "    \"\"\"\n",
    "    Search for academic papers on a given topic.\n",
    "    \n",
    "    Args:\n",
    "        query: The research query or topic\n",
    "        max_results: Maximum number of results to return\n",
    "    \n",
    "    Returns:\n",
    "        A formatted string with paper titles and abstracts\n",
    "    \"\"\"\n",
    "    # Simulated academic paper search\n",
    "    # In a real implementation, you would connect to APIs like arXiv, PubMed, or Google Scholar\n",
    "    papers = [\n",
    "        {\n",
    "            \"title\": f\"Advanced Studies in {query}: A Comprehensive Review\",\n",
    "            \"authors\": \"Smith et al.\",\n",
    "            \"year\": 2024,\n",
    "            \"abstract\": f\"This paper provides a comprehensive review of recent advances in {query}...\"\n",
    "        },\n",
    "        {\n",
    "            \"title\": f\"Machine Learning Applications for {query}\",\n",
    "            \"authors\": \"Johnson & Lee\",\n",
    "            \"year\": 2024,\n",
    "            \"abstract\": f\"We explore how machine learning can be applied to {query} problems...\"\n",
    "        },\n",
    "        {\n",
    "            \"title\": f\"Future Directions in {query} Research\",\n",
    "            \"authors\": \"Chen et al.\",\n",
    "            \"year\": 2023,\n",
    "            \"abstract\": f\"This paper outlines promising future research directions in {query}...\"\n",
    "        }\n",
    "    ]\n",
    "    \n",
    "    results = []\n",
    "    for paper in papers[:max_results]:\n",
    "        results.append(\n",
    "            f\"**{paper['title']}**\\n\"\n",
    "            f\"Authors: {paper['authors']} ({paper['year']})\\n\"\n",
    "            f\"Abstract: {paper['abstract']}\\n\"\n",
    "        )\n",
    "    \n",
    "    return \"\\n\".join(results) if results else \"No papers found for the given query.\"\n",
    "\n",
    "@function_tool\n",
    "def analyze_data_trends(topic: str, timeframe: str = \"last 5 years\") -> str:\n",
    "    \"\"\"\n",
    "    Analyze data trends related to a research topic.\n",
    "    \n",
    "    Args:\n",
    "        topic: The topic to analyze\n",
    "        timeframe: The timeframe for trend analysis\n",
    "    \n",
    "    Returns:\n",
    "        Analysis of trends and patterns\n",
    "    \"\"\"\n",
    "    analysis = f\"\"\"\n",
    "**Trend Analysis for {topic}**\n",
    "\n",
    "Timeframe: {timeframe}\n",
    "\n",
    "Key Findings:\n",
    "1. **Growing Interest**: Research publications on {topic} have increased by 150% over the {timeframe}\n",
    "2. **Emerging Subtopics**: New focus areas include sustainable approaches and AI integration\n",
    "3. **Geographic Distribution**: Major research centers in North America (40%), Europe (35%), and Asia (25%)\n",
    "4. **Industry Adoption**: Commercial applications have grown significantly in healthcare and finance sectors\n",
    "5. **Future Outlook**: Experts predict continued growth with emphasis on ethical considerations\n",
    "\n",
    "Data Sources: Academic databases, industry reports, patent filings\n",
    "    \"\"\"\n",
    "    return analysis\n",
    "\n",
    "@function_tool\n",
    "def get_expert_opinions(topic: str, num_experts: int = 3) -> str:\n",
    "    \"\"\"\n",
    "    Get expert opinions on a research topic.\n",
    "    \n",
    "    Args:\n",
    "        topic: The topic to get expert opinions on\n",
    "        num_experts: Number of expert opinions to include\n",
    "    \n",
    "    Returns:\n",
    "        Compiled expert opinions and insights\n",
    "    \"\"\"\n",
    "    experts = [\n",
    "        {\n",
    "            \"name\": \"Dr. Sarah Mitchell\",\n",
    "            \"affiliation\": \"MIT\",\n",
    "            \"opinion\": f\"{topic} represents one of the most promising areas of research today. The potential applications are vast.\"\n",
    "        },\n",
    "        {\n",
    "            \"name\": \"Prof. James Chen\",\n",
    "            \"affiliation\": \"Stanford University\",\n",
    "            \"opinion\": f\"We're seeing breakthrough developments in {topic}. The next decade will be transformative.\"\n",
    "        },\n",
    "        {\n",
    "            \"name\": \"Dr. Maria Rodriguez\",\n",
    "            \"affiliation\": \"Oxford University\",\n",
    "            \"opinion\": f\"The interdisciplinary nature of {topic} is what makes it so exciting. Collaboration is key.\"\n",
    "        }\n",
    "    ]\n",
    "    \n",
    "    opinions = []\n",
    "    for expert in experts[:num_experts]:\n",
    "        opinions.append(\n",
    "            f\"**{expert['name']}** ({expert['affiliation']}):\\n\"\n",
    "            f\"\\\"{expert['opinion']}\\\"\"\n",
    "        )\n",
    "    \n",
    "    return \"\\n\\n\".join(opinions)\n",
    "\n",
    "print(\"Research tools created successfully!\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "6",
   "metadata": {},
   "source": [
    "## 3. Building the Research Agent\n",
    "\n",
    "Now let's create our research agent with custom instructions and attach our research tools."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "7",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Research Agent 'Research Assistant' created with 3 tools\n"
     ]
    }
   ],
   "source": [
    "# Create the research agent with specialized instructions\n",
    "research_agent = Agent(\n",
    "    name=\"Research Assistant\",\n",
    "    instructions=\"\"\"\n",
    "    You are an expert research assistant specializing in comprehensive analysis and information gathering.\n",
    "    \n",
    "    Your approach to research:\n",
    "    1. Start by understanding the research question thoroughly\n",
    "    2. Search for relevant academic papers and studies\n",
    "    3. Analyze trends and patterns in the data\n",
    "    4. Gather expert opinions when available\n",
    "    5. Synthesize findings into clear, actionable insights\n",
    "    \n",
    "    Always provide:\n",
    "    - Evidence-based conclusions\n",
    "    - Multiple perspectives on the topic\n",
    "    - Clear citations and sources\n",
    "    - Practical recommendations\n",
    "    \n",
    "    Be thorough, objective, and critical in your analysis.\n",
    "    \"\"\",\n",
    "    model=\"gpt-4o-mini\",  # You can also use \"gpt-4o\" for more advanced capabilities\n",
    "    tools=[\n",
    "        search_academic_papers,\n",
    "        analyze_data_trends,\n",
    "        get_expert_opinions\n",
    "    ],\n",
    "    model_settings=ModelSettings(\n",
    "        temperature=0.7,  # Balance between creativity and consistency\n",
    "        max_tokens=2000   # Allow for comprehensive responses\n",
    "    )\n",
    ")\n",
    "\n",
    "print(f\"Research Agent '{research_agent.name}' created with {len(research_agent.tools)} tools\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "8",
   "metadata": {},
   "source": [
    "## 4. Running Simple Research Tasks\n",
    "\n",
    "Let's test our research agent with some basic queries using the correct `Runner.run_sync` method."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "9",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "==================================================\n",
      "Example 1: Basic Research Query\n",
      "==================================================\n",
      "\n",
      "Query: What are the latest developments in quantum computing?\n",
      "\n",
      "Research Agent Response:\n",
      "------------------------------\n",
      "### Latest Developments in Quantum Computing\n",
      "\n",
      "#### Recent Academic Research\n",
      "1. **Advanced Studies in Quantum Computing**  \n",
      "   - **Authors**: Smith et al. (2024)  \n",
      "   - **Summary**: This paper reviews significant advances in quantum computing, focusing on new algorithms and hardware improvements.\n",
      "\n",
      "2. **Machine Learning Applications**  \n",
      "   - **Authors**: Johnson & Lee (2024)  \n",
      "   - **Summary**: Exploration of how machine learning techniques can optimize quantum computing processes, potentially enhancing performance and efficiency.\n",
      "\n",
      "3. **Future Directions in Research**  \n",
      "   - **Authors**: Chen et al. (2023)  \n",
      "   - **Summary**: This paper outlines promising future research directions, emphasizing the need for sustainable and ethical approaches in quantum computing.\n",
      "\n",
      "#### Data Trends (Last 5 Years)\n",
      "- **Publication Growth**: Research papers on quantum computing have surged by **150%**.\n",
      "- **Emerging Focus Areas**: Increasing interest in sustainable quantum computing and the integration of AI.\n",
      "- **Geographic Distribution**:\n",
      "  - North America: **40%**\n",
      "  - Europe: **35%**\n",
      "  - Asia: **25%**\n",
      "- **Industry Adoption**: Notable growth in applications within healthcare and finance sectors.\n",
      "- **Future Outlook**: Experts anticipate ongoing growth, highlighting the importance of ethical considerations in future research.\n",
      "\n",
      "#### Expert Opinions\n",
      "- **Dr. Sarah Mitchell (MIT)**: Emphasizes the vast potential applications of quantum computing, marking it as a promising research area.\n",
      "- **Prof. James Chen (Stanford)**: Highlights breakthrough developments and predicts transformative changes in the next decade.\n",
      "- **Dr. Maria Rodriguez (Oxford)**: Notes the interdisciplinary nature of quantum computing, stressing the importance of collaboration in advancing the field.\n",
      "\n",
      "### Conclusions and Recommendations\n",
      "1. **Interdisciplinary Collaboration**: Foster partnerships between quantum computing, machine learning, and sustainability sectors to drive innovation.\n",
      "2. **Ethical Frameworks**: Develop ethical guidelines to govern research and applications in quantum computing to address societal impacts.\n",
      "3. **Investment in Education**: Encourage academic institutions to enhance educational offerings in quantum computing to prepare the workforce for the emerging industry.\n",
      "\n",
      "### Sources\n",
      "- Academic papers and studies from various journals.\n",
      "- Data from academic databases and industry reports.\n",
      "- Insights from leading experts in the field.\n"
     ]
    }
   ],
   "source": [
    "# Example 1: Basic research query\n",
    "print(\"=\" * 50)\n",
    "print(\"Example 1: Basic Research Query\")\n",
    "print(\"=\" * 50)\n",
    "\n",
    "query = \"What are the latest developments in quantum computing?\"\n",
    "result = Runner.run_sync(research_agent, query)\n",
    "\n",
    "print(f\"\\nQuery: {query}\\n\")\n",
    "print(\"Research Agent Response:\")\n",
    "print(\"-\" * 30)\n",
    "print(result.final_output)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "10",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "==================================================\n",
      "Example 2: Research with Workflow Naming\n",
      "==================================================\n",
      "\n",
      "Query: Compare renewable energy sources: solar, wind, and hydroelectric power\n",
      "\n",
      "Research Agent Response:\n",
      "------------------------------\n",
      "### Comparison of Renewable Energy Sources: Solar, Wind, and Hydroelectric Power\n",
      "\n",
      "Renewable energy sources play a critical role in reducing carbon emissions and promoting sustainable development. This analysis compares three major renewable energy sources: solar, wind, and hydroelectric power, focusing on academic research, trends, and expert opinions.\n",
      "\n",
      "#### 1. **Solar Energy**\n",
      "\n",
      "- **Research Overview**: \n",
      "  - **Key Studies**:\n",
      "    - *Advanced Studies in Solar Energy: A Comprehensive Review* (Smith et al., 2024) provides an extensive review of recent advances.\n",
      "    - *Machine Learning Applications for Solar Energy* (Johnson & Lee, 2024) discusses innovative technologies in solar energy.\n",
      "    - *Future Directions in Solar Energy Research* (Chen et al., 2023) outlines promising areas for future studies.\n",
      "  \n",
      "- **Trends (Last 5 Years)**:\n",
      "  - Research publications have increased by **150%**.\n",
      "  - Emerging subtopics include **sustainable approaches** and **AI integration**.\n",
      "  - Major research centers are located in **North America (40%)**, **Europe (35%)**, and **Asia (25%)**.\n",
      "  - Industry adoption has notably expanded in sectors like **healthcare** and **finance**.\n",
      "  \n",
      "- **Future Outlook**: Continued growth is expected, with an emphasis on ethical considerations.\n",
      "\n",
      "#### 2. **Wind Energy**\n",
      "\n",
      "- **Research Overview**: \n",
      "  - **Key Studies**:\n",
      "    - *Advanced Studies in Wind Energy: A Comprehensive Review* (Smith et al., 2024) offers insights into the latest advancements.\n",
      "    - *Machine Learning Applications for Wind Energy* (Johnson & Lee, 2024) highlights technology applications in wind energy.\n",
      "    - *Future Directions in Wind Energy Research* (Chen et al., 2023) identifies potential future research domains.\n",
      "  \n",
      "- **Trends (Last 5 Years)**:\n",
      "  - Similar to solar, research publications have increased by **150%**.\n",
      "  - Key areas of focus include **sustainable practices** and **AI integration**.\n",
      "  - Research centers are predominantly in **North America (40%)**, **Europe (35%)**, and **Asia (25%)**.\n",
      "  - Significant growth in commercial applications is noted.\n",
      "  \n",
      "- **Future Outlook**: Anticipation of continuous advancements and ethical considerations.\n",
      "\n",
      "#### 3. **Hydroelectric Power**\n",
      "\n",
      "- **Research Overview**: \n",
      "  - **Key Studies**:\n",
      "    - *Advanced Studies in Hydroelectric Power: A Comprehensive Review* (Smith et al., 2024) surveys recent developments.\n",
      "    - *Machine Learning Applications for Hydroelectric Power* (Johnson & Lee, 2024) examines tech applications.\n",
      "    - *Future Directions in Hydroelectric Power Research* (Chen et al., 2023) discusses future research trajectories.\n",
      "  \n",
      "- **Trends (Last 5 Years)**:\n",
      "  - Also shows a **150%** increase in research publications.\n",
      "  - Focus areas similar to solar and wind, including **sustainability** and **AI**.\n",
      "  - Research distribution mirrors other sources (North America 40%, Europe 35%, Asia 25%).\n",
      "  - Increased adoption in commercial sectors.\n",
      "  \n",
      "- **Future Outlook**: Expected growth with a strong focus on ethical considerations.\n",
      "\n",
      "#### Expert Opinions\n",
      "\n",
      "1. **Dr. Sarah Mitchell (MIT)**: \"Renewable energy sources represent one of the most promising areas of research today. The potential applications are vast.\"\n",
      "2. **Prof. James Chen (Stanford University)**: \"We're seeing breakthrough developments in renewable energy sources. The next decade will be transformative.\"\n",
      "3. **Dr. Maria Rodriguez (Oxford University)**: \"The interdisciplinary nature of renewable energy sources is what makes it so exciting. Collaboration is key.\"\n",
      "\n",
      "### Conclusion\n",
      "\n",
      "- **Commonalities**: All three renewable energy sources exhibit significant research growth and are key areas of technological innovation. The integration of AI and sustainable practices is a common theme across all fields.\n",
      "- **Future Directions**: Ethical considerations and interdisciplinary collaboration will be crucial for advancing research and practical applications in all three areas.\n",
      "\n",
      "### Recommendations\n",
      "\n",
      "1. **Invest in Research and Development**: Stakeholders should prioritize funding for research in solar, wind, and hydroelectric technologies.\n",
      "2. **Foster Collaboration**: Encourage partnerships between academia and industry to promote innovation.\n",
      "3. **Focus on Ethics**: Address ethical implications related to technology deployment and environmental sustainability.\n",
      "\n",
      "This comprehensive analysis underscores the importance of renewable energy sources in achieving a sustainable future.\n"
     ]
    }
   ],
   "source": [
    "# Example 2: Research with RunConfig for workflow naming\n",
    "print(\"\\n\" + \"=\" * 50)\n",
    "print(\"Example 2: Research with Workflow Naming\")\n",
    "print(\"=\" * 50)\n",
    "\n",
    "research_query = \"Compare renewable energy sources: solar, wind, and hydroelectric power\"\n",
    "\n",
    "# Use RunConfig to set workflow name for better tracing\n",
    "run_config = RunConfig(\n",
    "    workflow_name=\"Renewable Energy Research\",\n",
    "    trace_include_sensitive_data=False  # Don't include sensitive data in traces\n",
    ")\n",
    "\n",
    "result = Runner.run_sync(research_agent, research_query, run_config=run_config)\n",
    "\n",
    "print(f\"\\nQuery: {research_query}\\n\")\n",
    "print(\"Research Agent Response:\")\n",
    "print(\"-\" * 30)\n",
    "print(result.final_output)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "11",
   "metadata": {},
   "source": [
    "## 5. Basic Tracing with OpenAI Agents SDK\n",
    "\n",
    "Tracing helps us monitor and debug our agent's execution. Let's see how to use basic tracing features."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "12",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Example: Using trace context manager to group operations\n",
    "print(\"=\" * 50)\n",
    "print(\"Example: Multi-step Research with Tracing\")\n",
    "print(\"=\" * 50)\n",
    "\n",
    "async def traced_research_workflow():\n",
    "    \"\"\"Demonstrate tracing with multiple agent calls\"\"\"\n",
    "    \n",
    "    with trace(\"Multi-step Research Workflow\") as research_trace:\n",
    "        print(f\"Started trace: {research_trace.id}\")\n",
    "        \n",
    "        # Step 1: Initial research\n",
    "        print(\"\\n📚 Step 1: Initial Research...\")\n",
    "        result1 = await Runner.run(\n",
    "            research_agent, \n",
    "            \"What are the key challenges in artificial intelligence research?\",\n",
    "            run_config=RunConfig(workflow_name=\"AI Research - Initial\")\n",
    "        )\n",
    "        \n",
    "        # Step 2: Follow-up analysis\n",
    "        print(\"\\n🔍 Step 2: Follow-up Analysis...\")\n",
    "        result2 = await Runner.run(\n",
    "            research_agent,\n",
    "            f\"Based on these challenges: {result1.final_output[:200]}..., what are the most promising solutions?\",\n",
    "            run_config=RunConfig(workflow_name=\"AI Research - Solutions\")\n",
    "        )\n",
    "        \n",
    "        print(\"\\n\" + \"=\" * 60)\n",
    "        print(\"📋 RESEARCH WORKFLOW RESULTS\")\n",
    "        print(\"=\" * 60)\n",
    "        print(\"\\n🔍 Initial Research Findings:\")\n",
    "        print(result1.final_output[:500] + \"...\")\n",
    "        print(\"\\n💡 Promising Solutions:\")\n",
    "        print(result2.final_output[:500] + \"...\")\n",
    "        \n",
    "        return result1, result2\n",
    "\n",
    "# Run the traced workflow\n",
    "# Uncomment to run async version:\n",
    "# import asyncio\n",
    "# results = await traced_research_workflow()\n",
    "\n",
    "print(\"Traced research workflow example prepared (uncomment to run async version)\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "13",
   "metadata": {},
   "source": [
    "## 6. Synchronous Tracing Example\n",
    "\n",
    "For simpler use cases, here's how to do basic tracing with synchronous calls."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "14",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Synchronous tracing example\n",
    "print(\"=\" * 50)\n",
    "print(\"Synchronous Research with Tracing\")\n",
    "print(\"=\" * 50)\n",
    "\n",
    "def sync_research_workflow():\n",
    "    \"\"\"Simple synchronous research with tracing configuration\"\"\"\n",
    "    \n",
    "    # Configure tracing for the research session\n",
    "    research_config = RunConfig(\n",
    "        workflow_name=\"Synchronous Research Session\",\n",
    "        trace_include_sensitive_data=False,\n",
    "        group_id=\"research_session_001\"  # Group related traces together\n",
    "    )\n",
    "    \n",
    "    topics = [\n",
    "        \"machine learning trends\",\n",
    "        \"climate change solutions\",\n",
    "        \"space exploration advances\"\n",
    "    ]\n",
    "    \n",
    "    results = []\n",
    "    \n",
    "    for i, topic in enumerate(topics, 1):\n",
    "        print(f\"\\n🔍 Researching topic {i}/3: {topic}\")\n",
    "        \n",
    "        # Each research call will be traced under the same workflow\n",
    "        result = Runner.run_sync(\n",
    "            research_agent,\n",
    "            f\"Provide a brief overview of recent developments in {topic}\",\n",
    "            run_config=research_config\n",
    "        )\n",
    "        \n",
    "        results.append({\n",
    "            \"topic\": topic,\n",
    "            \"summary\": result.final_output[:200] + \"...\"\n",
    "        })\n",
    "        \n",
    "        print(f\"✅ Completed research on {topic}\")\n",
    "    \n",
    "    return results\n",
    "\n",
    "# Run the synchronous research\n",
    "research_results = sync_research_workflow()\n",
    "\n",
    "print(\"\\n\" + \"=\" * 60)\n",
    "print(\"📊 RESEARCH SESSION SUMMARY\")\n",
    "print(\"=\" * 60)\n",
    "\n",
    "for i, result in enumerate(research_results, 1):\n",
    "    print(f\"\\n{i}. **{result['topic'].title()}**\")\n",
    "    print(f\"   {result['summary']}\")\n",
    "\n",
    "print(f\"\\n✅ Completed research on {len(research_results)} topics\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "15",
   "metadata": {},
   "source": [
    "## 7. Tracing Configuration and Management\n",
    "\n",
    "Learn how to configure tracing behavior for different scenarios."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "16",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Tracing configuration examples\n",
    "from agents import set_tracing_disabled, set_tracing_export_api_key\n",
    "\n",
    "print(\"Tracing Configuration Examples:\")\n",
    "print(\"=\" * 40)\n",
    "\n",
    "# Example 1: Disable tracing globally (useful for production)\n",
    "print(\"\\n1. Disable Tracing Globally:\")\n",
    "print(\"   set_tracing_disabled(True)\")\n",
    "print(\"   # All subsequent agent runs will not be traced\")\n",
    "\n",
    "# Example 2: Set a dedicated API key for tracing\n",
    "print(\"\\n2. Set Dedicated Tracing API Key:\")\n",
    "print(\"   set_tracing_export_api_key('your-tracing-api-key')\")\n",
    "print(\"   # Use a separate API key for trace uploads\")\n",
    "\n",
    "# Example 3: Disable tracing for a specific run\n",
    "print(\"\\n3. Disable Tracing for Specific Run:\")\n",
    "print(\"   run_config = RunConfig(tracing_disabled=True)\")\n",
    "print(\"   result = Runner.run_sync(agent, query, run_config=run_config)\")\n",
    "\n",
    "# Example 4: Advanced tracing configuration\n",
    "print(\"\\n4. Advanced Tracing Configuration:\")\n",
    "advanced_config = RunConfig(\n",
    "    workflow_name=\"Advanced Research Pipeline\",\n",
    "    trace_include_sensitive_data=False,\n",
    "    group_id=\"research_batch_001\",\n",
    "    trace_metadata={\n",
    "        \"user_id\": \"researcher_123\",\n",
    "        \"session_type\": \"batch_research\",\n",
    "        \"version\": \"1.0\"\n",
    "    }\n",
    ")\n",
    "\n",
    "print(f\"   Advanced config created with metadata: {advanced_config.trace_metadata}\")\n",
    "\n",
    "# Demonstrate a research call with advanced tracing\n",
    "print(\"\\n🔬 Running research with advanced tracing...\")\n",
    "result = Runner.run_sync(\n",
    "    research_agent,\n",
    "    \"What are the ethical implications of AI in healthcare?\",\n",
    "    run_config=advanced_config\n",
    ")\n",
    "\n",
    "print(f\"✅ Research completed. Preview: {result.final_output[:150]}...\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "17",
   "metadata": {},
   "source": [
    "## 8. Streaming Research with Tracing\n",
    "\n",
    "For longer research tasks, we can stream the response while maintaining tracing capabilities."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "18",
   "metadata": {},
   "outputs": [],
   "source": [
    "import asyncio\n",
    "\n",
    "async def stream_research_with_tracing(agent, query, workflow_name=\"Streaming Research\"):\n",
    "    \"\"\"Stream research responses with tracing\"\"\"\n",
    "    print(f\"Research Query: {query}\")\n",
    "    print(\"\\nStreaming Response with Tracing:\")\n",
    "    print(\"-\" * 50)\n",
    "    \n",
    "    # Configure streaming with tracing\n",
    "    stream_config = RunConfig(\n",
    "        workflow_name=workflow_name,\n",
    "        trace_include_sensitive_data=False\n",
    "    )\n",
    "    \n",
    "    # Run the agent with streaming\n",
    "    result = Runner.run_streamed(agent, query, run_config=stream_config)\n",
    "    \n",
    "    # Stream the events as they come\n",
    "    full_response = \"\"\n",
    "    async for event in result.stream_events():\n",
    "        if event.type == \"raw_response_event\":\n",
    "            # Print each chunk as it arrives\n",
    "            chunk = event.data.delta\n",
    "            print(chunk, end=\"\", flush=True)\n",
    "            full_response += chunk\n",
    "    \n",
    "    print(\"\\n\" + \"-\" * 50)\n",
    "    print(f\"\\n✅ Streaming complete! Workflow: {workflow_name}\")\n",
    "    return full_response\n",
    "\n",
    "# Example streaming research query\n",
    "streaming_query = \"\"\"\n",
    "Conduct research on the future of renewable energy:\n",
    "1. Current state of technology\n",
    "2. Major challenges\n",
    "3. Breakthrough innovations expected\n",
    "4. Timeline for widespread adoption\n",
    "\"\"\"\n",
    "\n",
    "print(\"Streaming research example prepared.\")\n",
    "print(\"To run: await stream_research_with_tracing(research_agent, streaming_query)\")\n",
    "\n",
    "# Uncomment to run the streaming example:\n",
    "# response = await stream_research_with_tracing(research_agent, streaming_query)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "19",
   "metadata": {},
   "source": [
    "## 9. Best Practices for Research Agents\n",
    "\n",
    "Here are key best practices when building research agents with the OpenAI Agents SDK."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "20",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Best Practices Examples\n",
    "\n",
    "# 1. Error Handling in Tools\n",
    "@function_tool\n",
    "def safe_research_tool(query: str) -> str:\n",
    "    \"\"\"\n",
    "    A research tool with proper error handling.\n",
    "    \"\"\"\n",
    "    try:\n",
    "        # Validate input\n",
    "        if not query or len(query.strip()) < 3:\n",
    "            return \"Error: Query must be at least 3 characters long\"\n",
    "        \n",
    "        # Your research logic here\n",
    "        result = f\"Research results for: {query}\"\n",
    "        return result\n",
    "        \n",
    "    except Exception as e:\n",
    "        return f\"Error during research: {str(e)}\"\n",
    "\n",
    "# 2. Structured Configuration Management\n",
    "def create_research_config(workflow_name: str, include_sensitive: bool = False) -> RunConfig:\n",
    "    \"\"\"Create standardized research configuration\"\"\"\n",
    "    return RunConfig(\n",
    "        workflow_name=workflow_name,\n",
    "        trace_include_sensitive_data=include_sensitive,\n",
    "        trace_metadata={\n",
    "            \"created_at\": datetime.now().isoformat(),\n",
    "            \"agent_type\": \"research_agent\",\n",
    "            \"version\": \"1.0\"\n",
    "        }\n",
    "    )\n",
    "\n",
    "# 3. Research Session Manager\n",
    "class ResearchSession:\n",
    "    \"\"\"Manage research sessions with consistent tracing\"\"\"\n",
    "    \n",
    "    def __init__(self, session_id: str, agent: Agent):\n",
    "        self.session_id = session_id\n",
    "        self.agent = agent\n",
    "        self.results = []\n",
    "    \n",
    "    def research(self, query: str, workflow_suffix: str = \"\") -> str:\n",
    "        \"\"\"Conduct research with consistent configuration\"\"\"\n",
    "        workflow_name = f\"Research Session {self.session_id}\"\n",
    "        if workflow_suffix:\n",
    "            workflow_name += f\" - {workflow_suffix}\"\n",
    "        \n",
    "        config = create_research_config(workflow_name)\n",
    "        result = Runner.run_sync(self.agent, query, run_config=config)\n",
    "        \n",
    "        # Store result\n",
    "        self.results.append({\n",
    "            \"timestamp\": datetime.now().isoformat(),\n",
    "            \"query\": query,\n",
    "            \"response\": result.final_output\n",
    "        })\n",
    "        \n",
    "        return result.final_output\n",
    "    \n",
    "    def get_session_summary(self) -> Dict[str, Any]:\n",
    "        \"\"\"Get summary of the research session\"\"\"\n",
    "        return {\n",
    "            \"session_id\": self.session_id,\n",
    "            \"total_queries\": len(self.results),\n",
    "            \"results\": self.results\n",
    "        }\n",
    "\n",
    "# Example usage of best practices\n",
    "print(\"Best Practices Implementation:\")\n",
    "print(\"=\" * 40)\n",
    "\n",
    "# Create a research session\n",
    "session = ResearchSession(\"demo_001\", research_agent)\n",
    "\n",
    "# Conduct research\n",
    "print(\"\\n🔬 Conducting research with best practices...\")\n",
    "result = session.research(\n",
    "    \"What are the latest trends in quantum computing applications?\", \n",
    "    \"Quantum Trends\"\n",
    ")\n",
    "\n",
    "print(f\"✅ Research completed: {result[:100]}...\")\n",
    "print(f\"📊 Session has {len(session.results)} completed research queries\")\n",
    "\n",
    "print(\"\\n✅ Best practices examples loaded!\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "21",
   "metadata": {},
   "source": [
    "## 10. Summary and Next Steps\n",
    "\n",
    "### What We've Learned\n",
    "\n",
    "In this tutorial, we've built a research agent using the OpenAI Agents SDK with proper configuration:\n",
    "\n",
    "1. **Agent Creation** - Setting up agents with custom instructions and tools\n",
    "2. **Correct Runner Usage** - Using `Runner.run_sync()` and `Runner.run()` with `RunConfig`\n",
    "3. **Basic Tracing** - Monitoring agent execution with workflow names and trace management\n",
    "4. **Configuration Management** - Using `RunConfig` for tracing and workflow organization\n",
    "5. **Best Practices** - Error handling, structured configuration, and session management\n",
    "\n",
    "### Key Takeaways\n",
    "\n",
    "- Use `RunConfig` to configure tracing, not direct parameters\n",
    "- Always use workflow names for better trace organization\n",
    "- The `trace()` context manager groups multiple operations\n",
    "- Disable sensitive data in traces for production use\n",
    "- Structure your code with proper error handling and configuration management\n",
    "\n",
    "### Next Steps\n",
    "\n",
    "1. **Real API Integration** - Connect to actual academic databases and search APIs\n",
    "2. **Advanced Tracing** - Explore custom spans and trace processors\n",
    "3. **Agent Handoffs** - Build multi-agent research workflows\n",
    "4. **Production Deployment** - Configure tracing for production environments\n",
    "\n",
    "### Quick Research Function\n",
    "\n",
    "Here's a simple function using the correct SDK patterns:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "22",
   "metadata": {},
   "outputs": [],
   "source": [
    "def quick_research(topic: str, depth: str = \"basic\") -> str:\n",
    "    \"\"\"\n",
    "    Quick research function using correct OpenAI Agents SDK patterns.\n",
    "    \n",
    "    Args:\n",
    "        topic: The topic to research\n",
    "        depth: Research depth ('basic', 'detailed')\n",
    "    \n",
    "    Returns:\n",
    "        Research findings as a string\n",
    "    \"\"\"\n",
    "    instructions = {\n",
    "        \"basic\": \"Provide a brief overview with key points\",\n",
    "        \"detailed\": \"Conduct thorough research using all available tools\"\n",
    "    }\n",
    "    \n",
    "    query = f\"Research topic: {topic}. {instructions.get(depth, instructions['basic'])}\"\n",
    "    \n",
    "    # Use RunConfig for proper tracing\n",
    "    config = RunConfig(\n",
    "        workflow_name=f\"Quick Research - {topic[:30]}\",\n",
    "        trace_include_sensitive_data=False\n",
    "    )\n",
    "    \n",
    "    result = Runner.run_sync(research_agent, query, run_config=config)\n",
    "    return result.final_output\n",
    "\n",
    "# Example usage\n",
    "print(\"Quick Research Example:\")\n",
    "print(\"=\" * 50)\n",
    "findings = quick_research(\"Future of space exploration\", depth=\"basic\")\n",
    "print(findings[:300] + \"...\")\n",
    "\n",
    "print(\"\\n\" + \"=\" * 60)\n",
    "print(\"🎉 Congratulations! You've successfully built a research agent!\")\n",
    "print(\"=\" * 60)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}


---
./notebooks/4.0-handoffs.ipynb
---
{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "59d9a259",
   "metadata": {},
   "outputs": [],
   "source": [
    "import nest_asyncio\n",
    "nest_asyncio.apply()\n",
    "from agents import Agent, Runner"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4fc4e229",
   "metadata": {},
   "outputs": [],
   "source": [
    "g_sheets_agent = Agent(name=\"Google-Sheets-Agent\", instructions=\"You help with Google Sheets information.\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2f1a607e",
   "metadata": {},
   "outputs": [],
   "source": [
    "bash_cmds_agent = Agent(name=\"Bash-Commands-Agent\", instructions=\"You help with information about Bash commands. Your output is always a bash cmd and a simple justification.\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e7c30285",
   "metadata": {},
   "outputs": [],
   "source": [
    "from agents import InputGuardrail, GuardrailFunctionOutput, Agent, Runner\n",
    "from pydantic import BaseModel\n",
    "\n",
    "class GoogleSheetsOrBashOutput(BaseModel):\n",
    "    is_google_sheets_or_bash: bool\n",
    "    reasoning: str\n",
    "\n",
    "guardrail_agent = Agent(\n",
    "    name=\"Guardrail check\",\n",
    "    instructions=\"Check if the user is asking about google sheets stuff or bash commands.\",\n",
    "    output_type=GoogleSheetsOrBashOutput,\n",
    ")\n",
    "\n",
    "async def gsheets_or_bash_guardrail(ctx, agent, input_data):\n",
    "    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)\n",
    "    final_output = result.final_output_as(GoogleSheetsOrBashOutput)\n",
    "    return GuardrailFunctionOutput(\n",
    "        output_info=final_output,\n",
    "        tripwire_triggered=not final_output.is_google_sheets_or_bash,\n",
    "    )"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "99d31091",
   "metadata": {},
   "outputs": [],
   "source": [
    "triage_agent = Agent(\n",
    "    name=\"Triage Agent\",\n",
    "    instructions=\"You determine which agent to use based on the user's homework question\",\n",
    "    handoffs=[g_sheets_agent, bash_cmds_agent],\n",
    "    input_guardrails=[\n",
    "        InputGuardrail(guardrail_function=gsheets_or_bash_guardrail),\n",
    "    ]\n",
    ")\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cac2b3e2",
   "metadata": {},
   "outputs": [],
   "source": [
    "from agents import Runner\n",
    "\n",
    "async def main():\n",
    "    result = await Runner.run(triage_agent, \"What is the right command to list the files in the current directory?\")\n",
    "    print(result.final_output)\n",
    "    \n",
    "    result = await Runner.run(triage_agent, \"In google sheets, how do I sort data from one column according to the values in another column?\")\n",
    "    print(result.final_output)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e6b34e15",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "```bash\n",
      "ls\n",
      "```\n",
      "\n",
      "This command lists the files and directories in the current directory.\n",
      "To sort data in Google Sheets based on the values in another column, you can follow these steps:\n",
      "\n",
      "1. **Select the Range:**\n",
      "   - Highlight the range of cells you want to sort, including both the data column and the column whose values you'll base the sort on.\n",
      "\n",
      "2. **Open the Sort Options:**\n",
      "   - Click on \"Data\" in the menu at the top.\n",
      "\n",
      "3. **Sort Data:**\n",
      "   - Choose \"Sort range\" from the dropdown menu.\n",
      "   - In the dialog box that appears, you can select which column you want to sort by.\n",
      "   - You can choose to sort in ascending or descending order.\n",
      "\n",
      "4. **Confirm the Sort:**\n",
      "   - Click \"Sort\" to apply the changes.\n",
      "\n",
      "This will rearrange your data based on the values in the selected column.\n"
     ]
    }
   ],
   "source": [
    "import asyncio\n",
    "\n",
    "asyncio.run(main())"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "5d33c578",
   "metadata": {},
   "source": [
    "**View your traces**\n",
    "\n",
    "To review what happened during your agent run, navigate to the [Trace viewer](https://platform.openai.com/traces) in the OpenAI Dashboard to view traces of your agent runs."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "bd72235e",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/svg+xml": [
       "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n",
       "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\"\n",
       " \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n",
       "<!-- Generated by graphviz version 12.2.0 (20241103.1931)\n",
       " -->\n",
       "<!-- Title: G Pages: 1 -->\n",
       "<svg width=\"334pt\" height=\"298pt\"\n",
       " viewBox=\"0.00 0.00 334.00 298.38\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">\n",
       "<g id=\"graph0\" class=\"graph\" transform=\"scale(1 1) rotate(0) translate(4 294.38)\">\n",
       "<title>G</title>\n",
       "<polygon fill=\"white\" stroke=\"none\" points=\"-4,4 -4,-294.38 330,-294.38 330,4 -4,4\"/>\n",
       "<!-- __start__ -->\n",
       "<g id=\"node1\" class=\"node\">\n",
       "<title>__start__</title>\n",
       "<ellipse fill=\"lightblue\" stroke=\"black\" cx=\"159.25\" cy=\"-273.58\" rx=\"51.09\" ry=\"16.79\"/>\n",
       "<text text-anchor=\"middle\" x=\"159.25\" y=\"-268.16\" font-family=\"Arial\" font-size=\"14.00\">__start__</text>\n",
       "</g>\n",
       "<!-- Triage Agent -->\n",
       "<g id=\"node3\" class=\"node\">\n",
       "<title>Triage Agent</title>\n",
       "<polygon fill=\"lightyellow\" stroke=\"black\" points=\"213.25,-220.79 105.25,-220.79 105.25,-163.19 213.25,-163.19 213.25,-220.79\"/>\n",
       "<text text-anchor=\"middle\" x=\"159.25\" y=\"-186.56\" font-family=\"Arial\" font-size=\"14.00\">Triage Agent</text>\n",
       "</g>\n",
       "<!-- __start__&#45;&gt;Triage Agent -->\n",
       "<g id=\"edge1\" class=\"edge\">\n",
       "<title>__start__&#45;&gt;Triage Agent</title>\n",
       "<path fill=\"none\" stroke=\"black\" stroke-width=\"1.5\" d=\"M159.25,-256.47C159.25,-249.64 159.25,-241.34 159.25,-233.02\"/>\n",
       "<polygon fill=\"black\" stroke=\"black\" stroke-width=\"1.5\" points=\"162.75,-233.26 159.25,-223.26 155.75,-233.26 162.75,-233.26\"/>\n",
       "</g>\n",
       "<!-- __end__ -->\n",
       "<g id=\"node2\" class=\"node\">\n",
       "<title>__end__</title>\n",
       "<ellipse fill=\"lightblue\" stroke=\"black\" cx=\"159.25\" cy=\"-16.79\" rx=\"48.44\" ry=\"16.79\"/>\n",
       "<text text-anchor=\"middle\" x=\"159.25\" y=\"-11.37\" font-family=\"Arial\" font-size=\"14.00\">__end__</text>\n",
       "</g>\n",
       "<!-- Google&#45;Sheets&#45;Agent -->\n",
       "<g id=\"node4\" class=\"node\">\n",
       "<title>Google&#45;Sheets&#45;Agent</title>\n",
       "<polygon fill=\"lightyellow\" stroke=\"black\" points=\"146.5,-127.19 0,-127.19 0,-69.59 146.5,-69.59 146.5,-127.19\"/>\n",
       "<text text-anchor=\"middle\" x=\"73.25\" y=\"-92.96\" font-family=\"Arial\" font-size=\"14.00\">Google&#45;Sheets&#45;Agent</text>\n",
       "</g>\n",
       "<!-- Triage Agent&#45;&gt;Google&#45;Sheets&#45;Agent -->\n",
       "<g id=\"edge2\" class=\"edge\">\n",
       "<title>Triage Agent&#45;&gt;Google&#45;Sheets&#45;Agent</title>\n",
       "<path fill=\"none\" stroke=\"black\" stroke-width=\"1.5\" d=\"M132.98,-163.01C125.05,-154.56 116.22,-145.16 107.84,-136.23\"/>\n",
       "<polygon fill=\"black\" stroke=\"black\" stroke-width=\"1.5\" points=\"110.61,-134.06 101.21,-129.17 105.5,-138.85 110.61,-134.06\"/>\n",
       "</g>\n",
       "<!-- Bash&#45;Commands&#45;Agent -->\n",
       "<g id=\"node5\" class=\"node\">\n",
       "<title>Bash&#45;Commands&#45;Agent</title>\n",
       "<polygon fill=\"lightyellow\" stroke=\"black\" points=\"326,-127.19 164.5,-127.19 164.5,-69.59 326,-69.59 326,-127.19\"/>\n",
       "<text text-anchor=\"middle\" x=\"245.25\" y=\"-92.96\" font-family=\"Arial\" font-size=\"14.00\">Bash&#45;Commands&#45;Agent</text>\n",
       "</g>\n",
       "<!-- Triage Agent&#45;&gt;Bash&#45;Commands&#45;Agent -->\n",
       "<g id=\"edge4\" class=\"edge\">\n",
       "<title>Triage Agent&#45;&gt;Bash&#45;Commands&#45;Agent</title>\n",
       "<path fill=\"none\" stroke=\"black\" stroke-width=\"1.5\" d=\"M185.52,-163.01C193.45,-154.56 202.28,-145.16 210.66,-136.23\"/>\n",
       "<polygon fill=\"black\" stroke=\"black\" stroke-width=\"1.5\" points=\"213,-138.85 217.29,-129.17 207.89,-134.06 213,-138.85\"/>\n",
       "</g>\n",
       "<!-- Google&#45;Sheets&#45;Agent&#45;&gt;__end__ -->\n",
       "<g id=\"edge3\" class=\"edge\">\n",
       "<title>Google&#45;Sheets&#45;Agent&#45;&gt;__end__</title>\n",
       "<path fill=\"none\" stroke=\"black\" stroke-width=\"1.5\" d=\"M103.81,-69.1C113.66,-59.99 124.46,-49.99 133.89,-41.26\"/>\n",
       "<polygon fill=\"black\" stroke=\"black\" stroke-width=\"1.5\" points=\"136.15,-43.94 141.12,-34.58 131.4,-38.8 136.15,-43.94\"/>\n",
       "</g>\n",
       "<!-- Bash&#45;Commands&#45;Agent&#45;&gt;__end__ -->\n",
       "<g id=\"edge5\" class=\"edge\">\n",
       "<title>Bash&#45;Commands&#45;Agent&#45;&gt;__end__</title>\n",
       "<path fill=\"none\" stroke=\"black\" stroke-width=\"1.5\" d=\"M214.69,-69.1C204.84,-59.99 194.04,-49.99 184.61,-41.26\"/>\n",
       "<polygon fill=\"black\" stroke=\"black\" stroke-width=\"1.5\" points=\"187.1,-38.8 177.38,-34.58 182.35,-43.94 187.1,-38.8\"/>\n",
       "</g>\n",
       "</g>\n",
       "</svg>\n"
      ],
      "text/plain": [
       "<graphviz.sources.Source at 0x1214a2f10>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "from agents.extensions.visualization import draw_graph\n",
    "\n",
    "draw_graph(triage_agent)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9effc849",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "plot_data\n",
      "Plot data on a graph\n",
      "{\n",
      "  \"$defs\": {\n",
      "    \"PlotData\": {\n",
      "      \"properties\": {\n",
      "        \"x_values\": {\n",
      "          \"description\": \"The x-values to plot\",\n",
      "          \"items\": {\n",
      "            \"type\": \"number\"\n",
      "          },\n",
      "          \"title\": \"X Values\",\n",
      "          \"type\": \"array\"\n",
      "        },\n",
      "        \"y_values\": {\n",
      "          \"description\": \"The y-values to plot\",\n",
      "          \"items\": {\n",
      "            \"type\": \"number\"\n",
      "          },\n",
      "          \"title\": \"Y Values\",\n",
      "          \"type\": \"array\"\n",
      "        },\n",
      "        \"title\": {\n",
      "          \"description\": \"The title of the graph\",\n",
      "          \"title\": \"Title\",\n",
      "          \"type\": \"string\"\n",
      "        },\n",
      "        \"x_label\": {\n",
      "          \"description\": \"The label of the x-axis\",\n",
      "          \"title\": \"X Label\",\n",
      "          \"type\": \"string\"\n",
      "        },\n",
      "        \"y_label\": {\n",
      "          \"description\": \"The label of the y-axis\",\n",
      "          \"title\": \"Y Label\",\n",
      "          \"type\": \"string\"\n",
      "        },\n",
      "        \"plot_color\": {\n",
      "          \"description\": \"The color of the plot\",\n",
      "          \"title\": \"Plot Color\",\n",
      "          \"type\": \"string\"\n",
      "        }\n",
      "      },\n",
      "      \"required\": [\n",
      "        \"x_values\",\n",
      "        \"y_values\",\n",
      "        \"title\",\n",
      "        \"x_label\",\n",
      "        \"y_label\",\n",
      "        \"plot_color\"\n",
      "      ],\n",
      "      \"title\": \"PlotData\",\n",
      "      \"type\": \"object\",\n",
      "      \"additionalProperties\": false\n",
      "    }\n",
      "  },\n",
      "  \"properties\": {\n",
      "    \"data\": {\n",
      "      \"$ref\": \"#/$defs/PlotData\"\n",
      "    }\n",
      "  },\n",
      "  \"required\": [\n",
      "    \"data\"\n",
      "  ],\n",
      "  \"title\": \"plot_data_args\",\n",
      "  \"type\": \"object\",\n",
      "  \"additionalProperties\": false\n",
      "}\n",
      "\n"
     ]
    }
   ],
   "source": [
    "from agents import Agent, FunctionTool, RunContextWrapper, function_tool\n",
    "from pydantic import BaseModel, Field\n",
    "import matplotlib.pyplot as plt\n",
    "import json\n",
    "\n",
    "class PlotData(BaseModel):\n",
    "    x_values: list[float] = Field(description=\"The x-values to plot\")\n",
    "    y_values: list[float] = Field(description=\"The y-values to plot\")\n",
    "    title: str = Field(description=\"The title of the graph\")\n",
    "    x_label: str = Field(description=\"The label of the x-axis\")\n",
    "    y_label: str = Field(description=\"The label of the y-axis\")\n",
    "    plot_color: str = Field(description=\"The color of the plot\")\n",
    "\n",
    "@function_tool\n",
    "def plot_data(data: PlotData):\n",
    "    \"\"\"Plot data on a graph\"\"\"\n",
    "    plt.plot(data.x_values, data.y_values, color=data.plot_color)\n",
    "    plt.title(data.title)\n",
    "    plt.xlabel(data.x_label)\n",
    "    plt.ylabel(data.y_label)\n",
    "    plt.show()\n",
    "    return \"Graph plotted successfully\"\n",
    "\n",
    "\n",
    "\n",
    "\n",
    "agent = Agent(name=\"Test Agent\", instructions=\"You are a helpful assistant with the ability to plot data in graphs.\",\n",
    "              tools=[plot_data],\n",
    "              )\n",
    "for tool in agent.tools:\n",
    "    if isinstance(tool, FunctionTool):\n",
    "        print(tool.name)\n",
    "        print(tool.description)\n",
    "        print(json.dumps(tool.params_json_schema, indent=2))\n",
    "        print()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cf23b8c7",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "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",
      "text/plain": [
       "<Figure size 640x480 with 1 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "The graph of the data has been plotted with a dark green line. The title is \"Exponential Growth\" with \"Index\" as the x-axis label and \"Value\" as the y-axis label.\n"
     ]
    }
   ],
   "source": [
    "task = \"Plot this data for me: [1, 3, 9, 27, 81] make it dark green with a nice title and labels\"\n",
    "\n",
    "result = Runner.run_sync(agent, task)\n",
    "print(result.final_output)"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}


---
./notebooks/5.0-tracing.ipynb
---
{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "introduction",
   "metadata": {},
   "source": [
    "# Tracing with Research Agents\n",
    "\n",
    "This notebook demonstrates the built-in tracing capabilities of the OpenAI Agents SDK using a real research agent with built-in tools. We'll explore how tracing automatically captures agent runs, tool calls, and create structured research reports.\n",
    "\n",
    "## Key Concepts\n",
    "\n",
    "- **Default Tracing**: Automatic tracking of agent runs and tool usage\n",
    "- **Built-in Tools**: WebSearchTool for real web searches\n",
    "- **Structured Outputs**: Using Pydantic models for formatted responses\n",
    "- **Trace Organization**: Grouping related operations\n",
    "\n",
    "View your traces at: [OpenAI Traces Dashboard](https://platform.openai.com/traces)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "setup-header",
   "metadata": {},
   "source": [
    "## Setup"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "id": "setup-imports",
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "from pydantic import BaseModel\n",
    "from typing import List\n",
    "from agents import (\n",
    "    Agent, \n",
    "    Runner, \n",
    "    RunConfig, \n",
    "    WebSearchTool, \n",
    "    trace, \n",
    "    custom_span\n",
    ")\n",
    "\n",
    "# Ensure OpenAI API key is set\n",
    "if not os.getenv(\"OPENAI_API_KEY\"):\n",
    "    raise ValueError(\"Please set OPENAI_API_KEY environment variable\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "part1-header",
   "metadata": {},
   "source": [
    "## Part 1: Simple Research Agent with Tracing\n",
    "\n",
    "Let's create a research agent using OpenAI's built-in WebSearchTool. Every tool call will be automatically traced."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "id": "simple-research-agent",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Research Results:\n",
      "In 2024, artificial intelligence (AI) experienced significant advancements across various domains, including technological innovations, regulatory frameworks, and industry applications.\n",
      "\n",
      "**Technological Innovations**\n",
      "\n",
      "- **Multimodal AI Systems**: The development of multimodal AI systems, capable of processing and generating content across multiple formats such as text, audio, video, and images, marked a significant breakthrough. OpenAI's GPT-4o exemplified this trend, enabling tasks like generating written narratives from visual data and converting complex datasets into comprehensible visual representations. ([linkedin.com](https://www.linkedin.com/pulse/artificial-intelligence-2024-year-review-bob-cristello-gcx0e?utm_source=openai))\n",
      "\n",
      "- **Advancements in Large Language Models (LLMs)**: Models like OpenAI's GPT-4 and Google's PaLM 2, with trillions of parameters, pushed the boundaries of natural language processing. These models demonstrated enhanced understanding, generation, and translation of human language, expanding applications in industries such as healthcare, legal, and customer service. ([medium.com](https://medium.com/%40subraash1/artificial-intelligence-technology-key-developments-in-2024-and-expectations-for-2025-ff74d55d69c5?utm_source=openai))\n",
      "\n",
      "- **Generative AI in Creative Fields**: Generative AI tools leveraging technologies like generative adversarial networks (GANs) and diffusion models gained momentum. Companies like Adobe and NVIDIA introduced AI-powered creative tools that allowed users to produce high-quality visual content with minimal effort, impacting industries such as gaming, media, and entertainment. ([medium.com](https://medium.com/%40subraash1/artificial-intelligence-technology-key-developments-in-2024-and-expectations-for-2025-ff74d55d69c5?utm_source=openai))\n",
      "\n",
      "**Regulatory Developments**\n",
      "\n",
      "- **European Union's Artificial Intelligence Act**: The EU's Artificial Intelligence Act, a comprehensive regulation establishing a common legal framework for AI, came into force on August 1, 2024. The Act classifies AI applications by risk levels—unacceptable, high, limited, and minimal—and imposes corresponding obligations to ensure safety and compliance. ([en.wikipedia.org](https://en.wikipedia.org/wiki/Artificial_Intelligence_Act?utm_source=openai))\n",
      "\n",
      "- **Framework Convention on Artificial Intelligence**: Adopted under the Council of Europe, this international treaty aims to align AI development and use with fundamental human rights, democratic values, and the rule of law. Signed by over 50 countries, including EU member states, the treaty addresses risks such as misinformation and algorithmic discrimination. ([en.wikipedia.org](https://en.wikipedia.org/wiki/Framework_Convention_on_Artificial_Intelligence?utm_source=openai))\n",
      "\n",
      "**Industry Applications**\n",
      "\n",
      "- **AI-Driven Automation and Robotics**: Industries like manufacturing, logistics, and supply chain management increasingly adopted AI-driven automation and robotics to optimize operations and reduce human intervention. Companies such as Boston Dynamics and ABB Robotics introduced AI-powered robots capable of performing complex tasks with high precision and adaptability. ([medium.com](https://medium.com/%40subraash1/artificial-intelligence-technology-key-developments-in-2024-and-expectations-for-2025-ff74d55d69c5?utm_source=openai))\n",
      "\n",
      "- **AI in Healthcare**: AI significantly impacted healthcare through advancements in medical imaging analysis, predictive analytics for disease outbreaks, and virtual health assistants. AI-driven platforms like IBM Watson Health and Google Health processed vast datasets to uncover new insights in genomics, medical research, and personalized treatment plans. ([medium.com](https://medium.com/%40subraash1/artificial-intelligence-technology-key-developments-in-2024-and-expectations-for-2025-ff74d55d69c5?utm_source=openai))\n",
      "\n",
      "**International Collaboration**\n",
      "\n",
      "- **AI Seoul Summit**: Co-hosted by South Korea and the United Kingdom in May 2024, the summit resulted in the Seoul Declaration, emphasizing international cooperation to develop AI governance frameworks that are interoperable between countries. The declaration advocates for human-centric AI development in collaboration with the private sector, academia, and civil society. ([en.wikipedia.org](https://en.wikipedia.org/wiki/AI_Seoul_Summit?utm_source=openai))\n",
      "\n",
      "These developments underscore AI's transformative role in technology, regulation, and industry, highlighting the importance of balancing innovation with ethical considerations and regulatory oversight.\n",
      "\n",
      "\n",
      "## Key AI Developments in 2024:\n",
      "- [Early adoption of AI will boost US growth](https://www.ft.com/content/339a7e8c-d7ba-499c-b02d-40a514d6bd8a?utm_source=openai)\n",
      "- [Microsoft pitches AI 'agents' that can perform tasks on their own at Ignite 2024](https://apnews.com/article/782119423e28a7d88e4a27c12ce4e11f?utm_source=openai)\n",
      "- [Google puts AI agents at the center of Gemini update](https://www.reuters.com/technology/artificial-intelligence/google-puts-ai-agents-center-gemini-update-2024-12-11/?utm_source=openai) \n"
     ]
    }
   ],
   "source": [
    "# Create research agent with built-in web search tool\n",
    "research_agent = Agent(\n",
    "    name=\"Research Assistant\",\n",
    "    instructions=\"\"\"You are a research assistant. Use web search to find current, \n",
    "    accurate information and provide well-researched answers with sources.\"\"\",\n",
    "    model=\"gpt-4o\",\n",
    "    tools=[WebSearchTool()]\n",
    ")\n",
    "\n",
    "# This will automatically create a trace named \"Agent workflow\"\n",
    "result = await Runner.run(\n",
    "    research_agent,\n",
    "    \"What are the latest developments in artificial intelligence in 2024?\"\n",
    ")\n",
    "\n",
    "print(\"Research Results:\")\n",
    "print(result.final_output)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "part2-header",
   "metadata": {},
   "source": [
    "## Part 2: Custom Workflow Names and Metadata"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "custom-metadata",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Renewable Energy Research:\n",
      "As of August 2025, the renewable energy sector is experiencing significant advancements across various technologies, driven by innovation, policy shifts, and increasing global energy demands. Key trends include:\n",
      "\n",
      "**1. Solar Energy Innovations**\n",
      "\n",
      "- **Perovskite Solar Cells**: These next-generation cells have achieved efficiencies exceeding 25%, surpassing traditional silicon-based panels. Their flexibility and lightweight nature enable integration into diverse applications, from building materials to portable devices. ([ratedpower.com](https://ratedpower.com/blog/renewable-industry-developments-innovations-2025/?utm_source=openai))\n",
      "\n",
      "- **Bifacial Solar Panels**: Designed to capture sunlight from both sides, bifacial panels can generate up to 30% more electricity than conventional panels, especially in environments with reflective surfaces like snow or sand. ([ratedpower.com](https://ratedpower.com/blog/renewable-industry-developments-innovations-2025/?utm_source=openai))\n",
      "\n",
      "- **Floating Solar Farms**: Also known as \"floatovoltaics,\" these systems are deployed on water bodies, addressing land scarcity and benefiting from the cooling effect of water, which enhances efficiency by up to 15%. ([ratedpower.com](https://ratedpower.com/blog/renewable-industry-developments-innovations-2025/?utm_source=openai))\n",
      "\n",
      "**2. Wind Energy Developments**\n",
      "\n",
      "- **Offshore Wind Expansion**: Advancements in floating turbine technology have enabled installations in deeper waters, tapping into high-capacity wind resources. The UK, for instance, approved a record 16.1 gigawatts of new renewable energy capacity in the second quarter of 2025, including major offshore wind projects. ([ft.com](https://www.ft.com/content/926a29ae-ffb0-49ec-b548-c98182a307b8?utm_source=openai))\n",
      "\n",
      "- **Larger Turbines**: Modern turbines now exceed 18 MW capacity, significantly reducing installation costs per megawatt and increasing energy capture. ([ffisolutions.com](https://www.ffisolutions.com/new-energy-outlook-what-2025-holds-for-solar-wind-storage-and-grid-infrastructure/?utm_source=openai))\n",
      "\n",
      "**3. Advanced Energy Storage Solutions**\n",
      "\n",
      "- **Solid-State and Flow Batteries**: These technologies offer higher energy density, longer lifespans, and improved safety compared to traditional lithium-ion batteries, addressing the intermittency challenges of renewable energy sources. ([ratedpower.com](https://ratedpower.com/blog/renewable-industry-developments-innovations-2025/?utm_source=openai))\n",
      "\n",
      "- **Battery Energy Storage Systems (BESS)**: The global BESS market is projected to grow at a compound annual rate of 26.8%, driven by the need to balance supply and demand in renewable energy grids. ([ratedpower.com](https://ratedpower.com/blog/renewable-industry-developments-innovations-2025/?utm_source=openai))\n",
      "\n",
      "**4. Green Hydrogen Production**\n",
      "\n",
      "Green hydrogen, produced through water electrolysis powered by renewable energy, is emerging as a zero-carbon fuel for sectors that are difficult to electrify, such as heavy industry and long-haul transportation. Investments in green hydrogen projects have grown from $10 billion in 2020 to $75 billion in 2024, with China leading the push, accounting for 60% of global electrolyzer manufacturing. ([ratedpower.com](https://ratedpower.com/blog/renewable-industry-developments-innovations-2025/?utm_source=openai))\n",
      "\n",
      "**5. Artificial Intelligence (AI) and Digitalization**\n",
      "\n",
      "- **AI-Driven Energy Management**: AI enhances grid stability by accurately predicting energy demand and supply, optimizing operations, and reducing costs. ([ratedpower.com](https://ratedpower.com/blog/renewable-industry-developments-innovations-2025/?utm_source=openai))\n",
      "\n",
      "- **Digital Twins**: Virtual replicas of physical energy assets allow for precise simulations and performance analysis, improving planning and efficiency. ([ratedpower.com](https://ratedpower.com/blog/renewable-industry-developments-innovations-2025/?utm_source=openai))\n",
      "\n",
      "**6. Decentralized Energy Systems**\n",
      "\n",
      "The rise of microgrids and community-based renewable power systems is reducing reliance on centralized grids, enhancing energy resilience, and enabling localized energy production. ([powerinfotoday.com](https://www.powerinfotoday.com/articles/eight-energy-trends-2025-redefining-global-energy-landscape/?utm_source=openai))\n",
      "\n",
      "**7. Policy and Investment Shifts**\n",
      "\n",
      "- **UK's Offshore Wind Initiatives**: The UK government has extended the contract duration for Contracts for Difference (CfDs) from 15 to 20 years, aiming to revive offshore wind development and meet its 2030 target of 43–50 GW. ([reuters.com](https://www.reuters.com/business/energy/uk-subsidy-shift-could-put-offshore-wind-back-track-2025-08-27/?utm_source=openai))\n",
      "\n",
      "- **U.S. Renewable Energy Investment Decline**: In the first half of 2025, U.S. investment in renewable energy declined by 36%, attributed to policy shifts under the Trump administration, including reduced federal support and increased regulatory constraints. ([axios.com](https://www.axios.com/newsletters/axios-generate-c4304600-81bf-11f0-abeb-7d735356e3b7?utm_source=openai))\n",
      "\n",
      "These trends underscore a dynamic and rapidly evolving renewable energy landscape, characterized by technological breakthroughs, strategic policy decisions, and shifting investment patterns.\n",
      "\n",
      "\n",
      "## Recent Developments in Renewable Energy:\n",
      "- [UK subsidy shift could put offshore wind back on track](https://www.reuters.com/business/energy/uk-subsidy-shift-could-put-offshore-wind-back-track-2025-08-27/?utm_source=openai)\n",
      "- [Solar may account for half of new US electricity added this year, EIA says](https://www.reuters.com/sustainability/climate-energy/solar-may-account-half-new-us-electricity-added-this-year-eia-says-2025-08-20/?utm_source=openai)\n",
      "- [UK green power surges with record approvals for new renewable energy capacity](https://www.ft.com/content/926a29ae-ffb0-49ec-b548-c98182a307b8?utm_source=openai) \n"
     ]
    }
   ],
   "source": [
    "# Research with custom trace metadata using OpenAI Agents SDK\n",
    "from agents import trace\n",
    "\n",
    "with trace(\"Renewable Energy Research\", metadata={\n",
    "    \"topic\": \"renewable_energy\",\n",
    "    \"research_type\": \"trend_analysis\",\n",
    "    \"date\": \"2024-01-27\"\n",
    "}):\n",
    "    result = await Runner.run(\n",
    "        research_agent,\n",
    "        \"What are the current trends in renewable energy technology?\"\n",
    "    )\n",
    "\n",
    "print(\"Renewable Energy Research:\")\n",
    "print(result.final_output)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "part3-header",
   "metadata": {},
   "source": [
    "## Part 3: Multi-Step Research with Higher-Level Traces\n",
    "\n",
    "Group multiple research queries under a single trace for comprehensive analysis."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "id": "multi-step-research",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "=== AI Market Overview ===\n",
      "The artificial intelligence (AI) market experienced significant growth in 2024, with various analyses highlighting its expansion:\n",
      "\n",
      "- **Global Market Size**: The AI market was valued at approximately USD 638.23 billion in 2024, with projections indicating growth to USD 757.58 billion in 2025 and reac...\n",
      "\n",
      "=== Key Players ===\n",
      "As of August 27, 2025, several companies are at the forefront of artificial intelligence (AI) development, each holding significant positions in the market:\n",
      "\n",
      "**1. NVIDIA Corporation**\n",
      "\n",
      "NVIDIA has emerged as a dominant force in AI hardware, particularly with its graphics processing units (GPUs) that ...\n",
      "\n",
      "=== Future Predictions ===\n",
      "The artificial intelligence (AI) market is projected to experience substantial growth over the next five years, driven by advancements in technology and increasing adoption across various industries. According to MarketsandMarkets™, the global AI market size is expected to grow from USD 150.2 billio...\n",
      "\n"
     ]
    }
   ],
   "source": [
    "async def comprehensive_research():\n",
    "    \"\"\"Conduct multi-step research on a topic\"\"\"\n",
    "    \n",
    "    # Group all research under one trace\n",
    "    with trace(\"Comprehensive AI Market Research\"):\n",
    "        \n",
    "        # Step 1: Current market overview\n",
    "        market_result = await Runner.run(\n",
    "            research_agent,\n",
    "            \"What is the current size and growth of the AI market in 2024?\"\n",
    "        )\n",
    "        \n",
    "        # Step 2: Key players analysis\n",
    "        players_result = await Runner.run(\n",
    "            research_agent,\n",
    "            \"Who are the leading companies in AI development and what are their market positions?\"\n",
    "        )\n",
    "        \n",
    "        # Step 3: Future predictions\n",
    "        future_result = await Runner.run(\n",
    "            research_agent,\n",
    "            \"What are the predictions for AI market growth over the next 5 years?\"\n",
    "        )\n",
    "        \n",
    "        print(\"=== AI Market Overview ===\")\n",
    "        print(market_result.final_output[:300] + \"...\\n\")\n",
    "        \n",
    "        print(\"=== Key Players ===\")\n",
    "        print(players_result.final_output[:300] + \"...\\n\")\n",
    "        \n",
    "        print(\"=== Future Predictions ===\")\n",
    "        print(future_result.final_output[:300] + \"...\\n\")\n",
    "        \n",
    "        return {\n",
    "            \"market_overview\": market_result.final_output,\n",
    "            \"key_players\": players_result.final_output,\n",
    "            \"future_predictions\": future_result.final_output\n",
    "        }\n",
    "\n",
    "research_data = await comprehensive_research()"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "part4-header",
   "metadata": {},
   "source": [
    "## Part 4: Structured Research Reports with Tracing\n",
    "\n",
    "Create agents that output structured data using Pydantic models. This shows how tracing works with structured outputs."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 27,
   "id": "structured-reports",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "=== STRUCTURED RESEARCH REPORT ===\n",
      "Title: Impact of Quantum Computing on Cybersecurity\n",
      "\n",
      "Summary: Quantum computing poses a significant threat to current cybersecurity practices by potentially rendering existing encryption methods obsolete. Organizations must proactively transition to post-quantum cryptography to safeguard sensitive data against future quantum attacks.\n",
      "\n",
      "Key Findings:\n",
      "1. Quantum computers can break widely used encryption algorithms like RSA and ECC, compromising data security.\n",
      "2. 'Harvest now, decrypt later' attacks involve collecting encrypted data now to decrypt once quantum capabilities are available.\n",
      "3. Post-quantum cryptography (PQC) is being developed to create algorithms resistant to quantum attacks.\n",
      "4. Many organizations are unprepared for quantum threats, with only 4% having a defined quantum strategy.\n",
      "5. Transitioning to quantum-safe systems is complex and time-consuming, necessitating immediate action.\n",
      "\n",
      "Confidence Level: High\n",
      "Research Date: 2025-08-27\n",
      "\n",
      "Sources:\n",
      "- https://www.techradar.com/pro/quantum-computing-explained-what-it-means-for-cybersecurity-and-why-its-coming-faster-than-you-think\n",
      "- https://www.techradar.com/pro/cyber-resilience-in-the-post-quantum-era-the-time-of-crypto-agility\n",
      "- https://www.ft.com/content/96e14cb0-f49f-4632-b94f-2d1cdc625f8b\n",
      "- https://www.itpro.com/security/nearly-half-of-enterprises-arent-prepared-for-quantum-cybersecurity-threats\n",
      "- https://www.pwc.com/us/en/services/consulting/cybersecurity-risk-regulatory/library/quantum-computing-cybersecurity-risk.html\n"
     ]
    }
   ],
   "source": [
    "# --- OpenAI Agents SDK version ---\n",
    "from agents import Agent, Runner, function_tool, RunConfig\n",
    "from pydantic import BaseModel\n",
    "from typing import List\n",
    "\n",
    "# Define structured report format using Pydantic\n",
    "class ResearchReport(BaseModel):\n",
    "    title: str\n",
    "    summary: str\n",
    "    key_findings: List[str]\n",
    "    sources: List[str]\n",
    "    confidence_level: str  # \"high\", \"medium\", \"low\"\n",
    "    date_researched: str\n",
    "\n",
    "# Define a web search tool as a function tool for the agent\n",
    "\n",
    "# Create agent with structured output using OpenAI Agents SDK\n",
    "structured_research_agent = Agent(\n",
    "    name=\"Structured Research Agent\",\n",
    "    instructions=(\n",
    "        \"Conduct thorough research using web search and create a structured report.\\n\\n\"\n",
    "        \"Guidelines:\\n\"\n",
    "        \"- Use web search to find current, reliable information\\n\"\n",
    "        \"- Summarize findings clearly\\n\"\n",
    "        \"- List 3-5 key findings\\n\"\n",
    "        \"- Include actual source URLs when possible\\n\"\n",
    "        \"- Assess confidence level based on source quality and consistency\"\n",
    "    ),\n",
    "    model=\"gpt-4o\",\n",
    "    tools=[WebSearchTool()],  # Use the function_tool-decorated function\n",
    "    output_type=ResearchReport\n",
    ")\n",
    "\n",
    "# Generate structured report - this will be traced with structured output\n",
    "structured_result = await Runner.run(\n",
    "    structured_research_agent,\n",
    "    \"Research the impact of quantum computing on cybersecurity\",\n",
    "    run_config=RunConfig(  # <-- FIX: use run_config (not config)\n",
    "        workflow_name=\"Quantum Computing Cybersecurity Report\",\n",
    "        trace_metadata={  # <-- FIX: use trace_metadata (not metadata)\n",
    "            \"report_type\": \"structured\",\n",
    "            \"domain\": \"quantum_computing_cybersecurity\"\n",
    "        }\n",
    "    )\n",
    ")\n",
    "\n",
    "# Access structured output\n",
    "report = structured_result.final_output\n",
    "print(\"=== STRUCTURED RESEARCH REPORT ===\")\n",
    "print(f\"Title: {report.title}\")\n",
    "print(f\"\\nSummary: {report.summary}\")\n",
    "print(\"\\nKey Findings:\")\n",
    "for i, finding in enumerate(report.key_findings, 1):\n",
    "    print(f\"{i}. {finding}\")\n",
    "print(f\"\\nConfidence Level: {report.confidence_level}\")\n",
    "print(f\"Research Date: {report.date_researched}\")\n",
    "print(\"\\nSources:\")\n",
    "for source in report.sources:\n",
    "    print(f\"- {source}\")\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "part5-header",
   "metadata": {},
   "source": [
    "## Part 5: Research Pipeline with Custom Spans\n",
    "\n",
    "Add custom instrumentation to track different phases of the research process."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "id": "research-pipeline",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "🔍 Starting initial research on: electric vehicle battery technology\n",
      "✅ Initial research complete\n",
      "🔬 Conducting detailed analysis...\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "/Users/greatmaster/miniconda3/envs/openai-agents-sdk/lib/python3.11/typing.py:409: RuntimeWarning: coroutine 'Runner.run' was never awaited\n",
      "  ev_args = tuple(_eval_type(a, globalns, localns, recursive_guard) for a in t.__args__)\n",
      "RuntimeWarning: Enable tracemalloc to get the object allocation traceback\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "✅ Detailed analysis complete\n",
      "📄 Generating structured report...\n",
      "✅ Report generation complete\n",
      "\n",
      "============================================================\n",
      "FINAL RESEARCH REPORT\n",
      "============================================================\n",
      "Title: Electric Vehicle Battery Technology: Current Advancements and Challenges\n",
      "\n",
      "Summary: The electric vehicle (EV) battery technology landscape is evolving rapidly with significant advancements across several domains, focusing on enhanced performance, safety, and sustainability. Despite impressive progress, the industry continues to confront challenges related to materials, manufacturing, safety, and environmental impact.\n",
      "\n",
      "Key Findings:\n",
      "1. Lithium-Ion Dominance: Lithium-ion batteries, including variants like NMC and LFP, remain the primary choice for EVs due to their balance of energy density and cost-effectiveness.\n",
      "2. Emerging Technologies: Solid-state, sodium-ion, and lithium-sulfur batteries are emerging technologies offering higher energy densities and reduced reliance on critical minerals.\n",
      "3. Innovative Development: Structural battery composites and ultra-fast charging technologies are advancing, enhancing efficiency and reducing vehicle weight.\n",
      "4. Industry Strategies: Companies like CATL and GM are spearheading innovations and diversifying their battery solutions to reduce costs and improve performance.\n",
      "5. Challenges: The EV battery industry faces challenges in material supply, manufacturing scalability, safety, performance in extreme conditions, and sustainability.\n"
     ]
    }
   ],
   "source": [
    "from agents import Runner, trace\n",
    "from agents.tracing import custom_span\n",
    "\n",
    "async def research_pipeline(topic: str):\n",
    "    \"\"\"Complete research pipeline with custom spans\"\"\"\n",
    "    \n",
    "    with trace(\"Complete Research Pipeline\"):\n",
    "        \n",
    "        # Phase 1: Initial research\n",
    "        with custom_span(\"initial_research\", data={\"topic\": topic}):  # FIX: use data= (not metadata=)\n",
    "            print(f\"🔍 Starting initial research on: {topic}\")\n",
    "            initial_result = await Runner.run(\n",
    "                research_agent,\n",
    "                f\"Provide an overview of {topic} with current information\"\n",
    "            )\n",
    "            print(\"✅ Initial research complete\")\n",
    "        \n",
    "        # Phase 2: Deep dive analysis\n",
    "        with custom_span(\"deep_analysis\", data={\"phase\": \"detailed_research\"}):  # FIX\n",
    "            print(\"🔬 Conducting detailed analysis...\")\n",
    "            detailed_result = await Runner.run(\n",
    "                research_agent,\n",
    "                f\"What are the latest technical developments and challenges in {topic}?\"\n",
    "            )\n",
    "            print(\"✅ Detailed analysis complete\")\n",
    "        \n",
    "        # Phase 3: Generate structured report\n",
    "        with custom_span(\"report_generation\", data={\"output_type\": \"structured\"}):  # FIX\n",
    "            print(\"📄 Generating structured report...\")\n",
    "            \n",
    "            # Combine findings for final report\n",
    "            combined_research = f\"\"\"\n",
    "            Based on the following research findings, create a comprehensive report:\n",
    "            \n",
    "            Initial Overview:\n",
    "            {initial_result.final_output}\n",
    "            \n",
    "            Detailed Analysis:\n",
    "            {detailed_result.final_output}\n",
    "            \n",
    "            Topic: {topic}\n",
    "            \"\"\"\n",
    "            \n",
    "            final_report = await Runner.run(\n",
    "                structured_research_agent,\n",
    "                combined_research\n",
    "            )\n",
    "            print(\"✅ Report generation complete\")\n",
    "        \n",
    "        return final_report.final_output\n",
    "\n",
    "# Run the complete research pipeline\n",
    "topic = \"electric vehicle battery technology\"\n",
    "final_report = await research_pipeline(topic)\n",
    "\n",
    "print(\"\\n\" + \"=\"*60)\n",
    "print(\"FINAL RESEARCH REPORT\")\n",
    "print(\"=\"*60)\n",
    "print(f\"Title: {final_report.title}\")\n",
    "print(f\"\\nSummary: {final_report.summary}\")\n",
    "print(\"\\nKey Findings:\")\n",
    "for i, finding in enumerate(final_report.key_findings, 1):\n",
    "    print(f\"{i}. {finding}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "part6-header",
   "metadata": {},
   "source": [
    "## Part 6: Tracing Controls\n",
    "\n",
    "Control tracing behavior and sensitive data handling."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "id": "tracing-controls",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Research without tracing completed\n",
      "Data privacy regulations are laws designed to protect individuals' personal data and ensure its proper management by organizations. Some key regulations include:\n",
      "\n",
      "1. **General Data Protection Regulati...\n",
      "\n",
      "--------------------------------------------------\n",
      "\n",
      "Secure research completed\n",
      "Ensuring the security of APIs is crucial given the increasing reliance on them for connecting applications and services. Here are some best practices for API security:\n",
      "\n",
      "1. **Authentication and Authori...\n"
     ]
    }
   ],
   "source": [
    "# Example 1: Research without tracing (for sensitive topics)\n",
    "sensitive_result = await Runner.run(\n",
    "    research_agent,\n",
    "    \"General information about data privacy regulations\",\n",
    "    run_config=RunConfig(\n",
    "        tracing_disabled=True,  # No trace will be created\n",
    "        workflow_name=\"Sensitive Research\"\n",
    "    )\n",
    ")\n",
    "\n",
    "print(\"Research without tracing completed\")\n",
    "print(sensitive_result.final_output[:200] + \"...\")\n",
    "\n",
    "print(\"\\n\" + \"-\"*50 + \"\\n\")\n",
    "\n",
    "# Example 2: Research with metadata but no sensitive data in traces\n",
    "result_no_sensitive = await Runner.run(\n",
    "    research_agent,\n",
    "    \"What are best practices for API security?\",\n",
    "    run_config=RunConfig(\n",
    "        workflow_name=\"API Security Research\",\n",
    "        trace_include_sensitive_data=False,  # Exclude sensitive data from traces\n",
    "        trace_metadata={\n",
    "            \"security_research\": True,\n",
    "            \"classification\": \"standard\"\n",
    "        }\n",
    "    )\n",
    ")\n",
    "\n",
    "print(\"Secure research completed\")\n",
    "print(result_no_sensitive.final_output[:200] + \"...\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "summary",
   "metadata": {},
   "source": [
    "## Summary\n",
    "\n",
    "### What We Demonstrated\n",
    "\n",
    "1. **Real Research Agent**: Used OpenAI's WebSearchTool for actual web searches\n",
    "2. **Automatic Tracing**: All tool calls and agent runs were automatically traced\n",
    "3. **Structured Outputs**: Created formatted reports using Pydantic models\n",
    "4. **Trace Organization**: Grouped related operations with `trace()` context managers\n",
    "5. **Custom Spans**: Added instrumentation for different research phases\n",
    "6. **Tracing Controls**: Demonstrated disabling tracing and sensitive data handling\n",
    "\n",
    "### Key Benefits of Tracing\n",
    "\n",
    "- **Debugging**: See exactly what searches were performed and their results\n",
    "- **Performance**: Monitor how long each research phase takes\n",
    "- **Audit Trail**: Track all research activities for compliance\n",
    "- **Optimization**: Identify bottlenecks in your research workflows\n",
    "\n",
    "### Best Practices\n",
    "\n",
    "- Use descriptive workflow names for easy identification\n",
    "- Add relevant metadata for filtering and analysis\n",
    "- Group related operations with `trace()` contexts\n",
    "- Use `trace_include_sensitive_data=False` for production\n",
    "- Add custom spans for important business logic phases\n",
    "\n",
    "### Viewing Your Traces\n",
    "\n",
    "Visit [OpenAI Traces Dashboard](https://platform.openai.com/traces) to:\n",
    "- Visualize your research workflows\n",
    "- Debug tool call issues\n",
    "- Monitor performance metrics\n",
    "- Analyze usage patterns"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}


---
./notebooks/6.0-context-management.ipynb
---
{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "2db0e960",
   "metadata": {},
   "source": [
    "source: https://openai.github.io/openai-agents-python/context/\n",
    "# Context management\n",
    "\n",
    "1. Context available locally to your code: this is data and dependencies you might need when tool functions run, during callbacks like on_handoff, in lifecycle hooks, etc.\n",
    "2. Context available to LLMs: this is data the LLM sees when generating a response.\n",
    "\n",
    "## Local context\n",
    "Represented via the RunContextWrapper class and the context property within it. The way this works is:\n",
    "\n",
    "- You create any Python object you want. A common pattern is to use a dataclass or a Pydantic object.\n",
    "- You pass that object to the various run methods (e.g. Runner.run(..., **context=whatever**)).\n",
    "- All your tool calls, lifecycle hooks etc will be passed a wrapper object, RunContextWrapper[T], where T = context object type accessible via wrapper.context.\n",
    "\n",
    "The most important thing to be aware of: every agent, tool function, lifecycle etc for a given agent run **must use the same type of context.**\n",
    "\n",
    "You can use it for:\n",
    "\n",
    "- Contextual data for your run (e.g. things like a username/uid or other information about the user)\n",
    "- Dependencies (e.g. logger objects, data fetchers, etc)\n",
    "- Helper functions\n",
    "\n",
    "Note\n",
    "The context object is not sent to the LLM. It is purely a local object that you can read from, write to and call methods on it.\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "f710361f",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "The product SuperWidget costs $99.99.\n"
     ]
    }
   ],
   "source": [
    "import nest_asyncio\n",
    "nest_asyncio.apply()\n",
    "from dataclasses import dataclass\n",
    "from agents import Agent, RunContextWrapper, Runner, function_tool\n",
    "\n",
    "@dataclass\n",
    "class ProductInfo:  \n",
    "    product_name: str\n",
    "    product_id: int\n",
    "\n",
    "@function_tool\n",
    "async def fetch_product_price(wrapper: RunContextWrapper[ProductInfo]) -> str:  \n",
    "    \"\"\"Fetch the price of the product. Call this function to get product's price information.\"\"\"\n",
    "    return f\"The product {wrapper.context.product_name} costs $99.99\"\n",
    "\n",
    "\n",
    "product_info = ProductInfo(product_name=\"SuperWidget\", product_id=456)\n",
    "\n",
    "agent = Agent[ProductInfo](  \n",
    "    name=\"ProductAssistant\",\n",
    "    tools=[fetch_product_price],\n",
    ")\n",
    "\n",
    "# In a Jupyter notebook, you need to use 'await' for async functions,\n",
    "# unless you use an event loop runner like asyncio.run (not recommended in notebooks),\n",
    "# or use IPython's built-in 'await' support (which is available in modern Jupyter).\n",
    "# So, you should keep 'await' here:\n",
    "result = await Runner.run(  \n",
    "    starting_agent=agent,\n",
    "    input=\"What is the price of the product?\",\n",
    "    context=product_info,\n",
    ")\n",
    "\n",
    "print(result.final_output)  \n",
    "# The product SuperWidget costs $99.99."
   ]
  },
  {
   "cell_type": "markdown",
   "id": "118cb0ef",
   "metadata": {},
   "source": [
    "# Agent/LLM context\n",
    "\n",
    "To make new data available to an LLM, you must add it to the conversation history. Main ways to do this:\n",
    "\n",
    "- Add it to Agent instructions (system prompt), either as a static string or a dynamic function.\n",
    "- Include it in the input when calling Runner.run.\n",
    "- Expose it via function tools for on-demand access.\n",
    "- Use retrieval or web search tools to fetch relevant data as needed."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7cca4bad",
   "metadata": {},
   "outputs": [],
   "source": [
    "# You can experiment with different ways to expose data to the LLM here:"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}


---
./notebooks/7.0-spreadsheet-agent.ipynb
---
{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "1",
   "metadata": {},
   "source": [
    "# Building a Google Sheets Agent with OpenAI Agents SDK\n",
    "\n",
    "In this tutorial, we'll build a powerful spreadsheet agent that can interact with Google Sheets to read, write, and manipulate data. This agent will use the OpenAI Agents SDK with custom tools for Google Sheets integration.\n",
    "\n",
    "## What We'll Learn\n",
    "\n",
    "1. **Google Sheets Setup** - Configure Google Sheets API credentials\n",
    "2. **Custom Sheets Tools** - Create function tools for Google Sheets operations\n",
    "3. **Spreadsheet Agent** - Build an intelligent agent for data analysis and manipulation\n",
    "4. **Practical Examples** - Real-world use cases and workflows\n",
    "\n",
    "## Prerequisites\n",
    "\n",
    "- Python 3.11+\n",
    "- OpenAI API key\n",
    "- Google Cloud Platform account\n",
    "- Google Sheets API enabled\n",
    "- Service account credentials (credentials.json)\n",
    "\n",
    "## Google Sheets API Setup\n",
    "\n",
    "**Important: Before running this notebook, you need to:**\n",
    "\n",
    "1. **Create a Google Cloud Project**:\n",
    "   - Go to [Google Cloud Console](https://console.cloud.google.com/)\n",
    "   - Create a new project or select an existing one\n",
    "\n",
    "2. **Enable Google Sheets API**:\n",
    "   - Navigate to \"APIs & Services\" > \"Library\"\n",
    "   - Search for \"Google Sheets API\" and enable it\n",
    "\n",
    "3. **Create Service Account Credentials**:\n",
    "   - Go to \"APIs & Services\" > \"Credentials\"\n",
    "   - Click \"Create Credentials\" > \"Service Account\"\n",
    "   - Fill in the details and create the service account\n",
    "   - Click on the service account, go to \"Keys\" tab\n",
    "   - Click \"Add Key\" > \"Create new key\" > \"JSON\"\n",
    "   - Save the downloaded file as `credentials.json` in your project directory\n",
    "\n",
    "4. **Share Your Spreadsheet**:\n",
    "   - Open your Google Sheet\n",
    "   - Share it with the service account email (found in credentials.json)\n",
    "   - Give \"Editor\" permissions"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "2",
   "metadata": {},
   "source": [
    "## 1. Installation and Setup\n",
    "\n",
    "First, let's install the required packages and set up our environment."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "3",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "All packages imported successfully!\n"
     ]
    }
   ],
   "source": [
    "# Install required packages\n",
    "# !pip install openai-agents google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2\n",
    "\n",
    "# Import required libraries\n",
    "import os\n",
    "import json\n",
    "from typing import List, Dict, Any, Optional\n",
    "from datetime import datetime\n",
    "import pandas as pd\n",
    "\n",
    "# OpenAI Agents SDK\n",
    "from agents import Agent, Runner, function_tool, trace\n",
    "from agents import ModelSettings\n",
    "from agents.run import RunConfig\n",
    "\n",
    "# Google Sheets API\n",
    "import googleapiclient.discovery\n",
    "from google.oauth2 import service_account\n",
    "from googleapiclient.errors import HttpError\n",
    "\n",
    "# Set your OpenAI API key\n",
    "# os.environ[\"OPENAI_API_KEY\"] = \"your-api-key-here\"\n",
    "\n",
    "print(\"All packages imported successfully!\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "4",
   "metadata": {},
   "source": [
    "## 2. Google Sheets Service Setup\n",
    "\n",
    "Let's set up the Google Sheets API connection using service account credentials."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "❌ Error setting up Google Sheets service: Service account info was not in the expected format, missing fields token_uri, client_email.\n",
      "⚠️ Google Sheets service not available. Please check your credentials.\n"
     ]
    }
   ],
   "source": [
    "# Google Sheets setup\n",
    "SCOPES = ['https://www.googleapis.com/auth/spreadsheets']\n",
    "CREDENTIALS_FILE = '../credentials.json'  # Path to your service account credentials\n",
    "\n",
    "def setup_sheets_service():\n",
    "    \"\"\"Initialize Google Sheets service with service account credentials.\"\"\"\n",
    "    try:\n",
    "        credentials = service_account.Credentials.from_service_account_file(\n",
    "            CREDENTIALS_FILE, scopes=SCOPES\n",
    "        )\n",
    "        service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)\n",
    "        return service\n",
    "    except FileNotFoundError:\n",
    "        print(\"❌ Error: credentials.json not found!\")\n",
    "        print(\"Please download your service account credentials from Google Cloud Console\")\n",
    "        print(\"and save them as 'credentials.json' in this directory.\")\n",
    "        return None\n",
    "    except Exception as e:\n",
    "        print(f\"❌ Error setting up Google Sheets service: {e}\")\n",
    "        return None\n",
    "\n",
    "# Initialize the service\n",
    "sheets_service = setup_sheets_service()\n",
    "\n",
    "if sheets_service:\n",
    "    print(\"✅ Google Sheets service initialized successfully!\")\n",
    "else:\n",
    "    print(\"⚠️ Google Sheets service not available. Please check your credentials.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "6",
   "metadata": {},
   "source": [
    "## 3. Custom Google Sheets Tools\n",
    "\n",
    "Now let's create custom tools for Google Sheets operations using the `@function_tool` decorator."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7",
   "metadata": {},
   "outputs": [],
   "source": [
    "@function_tool\n",
    "def read_sheet_data(spreadsheet_id: str, range_name: str = \"A:Z\") -> str:\n",
    "    \"\"\"\n",
    "    Read data from a Google Sheet.\n",
    "    \n",
    "    Args:\n",
    "        spreadsheet_id: The ID of the Google Spreadsheet (from the URL)\n",
    "        range_name: The range to read (e.g., 'Sheet1!A1:C10' or 'A:Z')\n",
    "    \n",
    "    Returns:\n",
    "        String representation of the sheet data\n",
    "    \"\"\"\n",
    "    if not sheets_service:\n",
    "        return \"Error: Google Sheets service not available. Please check your credentials.\"\n",
    "    \n",
    "    try:\n",
    "        # Call the Sheets API\n",
    "        result = sheets_service.spreadsheets().values().get(\n",
    "            spreadsheetId=spreadsheet_id,\n",
    "            range=range_name\n",
    "        ).execute()\n",
    "        \n",
    "        values = result.get('values', [])\n",
    "        \n",
    "        if not values:\n",
    "            return \"No data found in the specified range.\"\n",
    "        \n",
    "        # Convert to a more readable format\n",
    "        data_summary = f\"Retrieved {len(values)} rows of data:\\n\\n\"\n",
    "        \n",
    "        # Add headers if available\n",
    "        if values:\n",
    "            headers = values[0]\n",
    "            data_summary += f\"Columns: {', '.join(headers)}\\n\\n\"\n",
    "            \n",
    "            # Add sample data (first few rows)\n",
    "            sample_rows = min(5, len(values))\n",
    "            data_summary += \"Sample data:\\n\"\n",
    "            for i, row in enumerate(values[:sample_rows]):\n",
    "                # Ensure all rows have the same number of columns\n",
    "                padded_row = row + [''] * (len(headers) - len(row))\n",
    "                row_data = ' | '.join(padded_row[:len(headers)])\n",
    "                data_summary += f\"Row {i+1}: {row_data}\\n\"\n",
    "            \n",
    "            if len(values) > sample_rows:\n",
    "                data_summary += f\"... and {len(values) - sample_rows} more rows\"\n",
    "        \n",
    "        return data_summary\n",
    "        \n",
    "    except HttpError as error:\n",
    "        return f\"Error reading sheet: {error}\"\n",
    "    except Exception as e:\n",
    "        return f\"Unexpected error: {e}\"\n",
    "\n",
    "@function_tool\n",
    "def write_sheet_data(spreadsheet_id: str, range_name: str, values: List[List[str]]) -> str:\n",
    "    \"\"\"\n",
    "    Write data to a Google Sheet.\n",
    "    \n",
    "    Args:\n",
    "        spreadsheet_id: The ID of the Google Spreadsheet\n",
    "        range_name: The range to write to (e.g., 'Sheet1!A1:C3')\n",
    "        values: 2D array of values to write\n",
    "    \n",
    "    Returns:\n",
    "        Success or error message\n",
    "    \"\"\"\n",
    "    if not sheets_service:\n",
    "        return \"Error: Google Sheets service not available. Please check your credentials.\"\n",
    "    \n",
    "    try:\n",
    "        body = {\n",
    "            'values': values\n",
    "        }\n",
    "        \n",
    "        result = sheets_service.spreadsheets().values().update(\n",
    "            spreadsheetId=spreadsheet_id,\n",
    "            range=range_name,\n",
    "            valueInputOption='USER_ENTERED',  # Parse formulas and format data\n",
    "            body=body\n",
    "        ).execute()\n",
    "        \n",
    "        updated_cells = result.get('updatedCells', 0)\n",
    "        return f\"Successfully updated {updated_cells} cells in range {range_name}\"\n",
    "        \n",
    "    except HttpError as error:\n",
    "        return f\"Error writing to sheet: {error}\"\n",
    "    except Exception as e:\n",
    "        return f\"Unexpected error: {e}\"\n",
    "\n",
    "@function_tool\n",
    "def append_sheet_data(spreadsheet_id: str, range_name: str, values: List[List[str]]) -> str:\n",
    "    \"\"\"\n",
    "    Append data to a Google Sheet.\n",
    "    \n",
    "    Args:\n",
    "        spreadsheet_id: The ID of the Google Spreadsheet\n",
    "        range_name: The range to append to (e.g., 'Sheet1!A:C')\n",
    "        values: 2D array of values to append\n",
    "    \n",
    "    Returns:\n",
    "        Success or error message\n",
    "    \"\"\"\n",
    "    if not sheets_service:\n",
    "        return \"Error: Google Sheets service not available. Please check your credentials.\"\n",
    "    \n",
    "    try:\n",
    "        body = {\n",
    "            'values': values\n",
    "        }\n",
    "        \n",
    "        result = sheets_service.spreadsheets().values().append(\n",
    "            spreadsheetId=spreadsheet_id,\n",
    "            range=range_name,\n",
    "            valueInputOption='USER_ENTERED',\n",
    "            body=body\n",
    "        ).execute()\n",
    "        \n",
    "        updated_cells = result.get('updates', {}).get('updatedCells', 0)\n",
    "        return f\"Successfully appended {len(values)} rows ({updated_cells} cells) to {range_name}\"\n",
    "        \n",
    "    except HttpError as error:\n",
    "        return f\"Error appending to sheet: {error}\"\n",
    "    except Exception as e:\n",
    "        return f\"Unexpected error: {e}\"\n",
    "\n",
    "@function_tool\n",
    "def clear_sheet_range(spreadsheet_id: str, range_name: str) -> str:\n",
    "    \"\"\"\n",
    "    Clear data from a specific range in a Google Sheet.\n",
    "    \n",
    "    Args:\n",
    "        spreadsheet_id: The ID of the Google Spreadsheet\n",
    "        range_name: The range to clear (e.g., 'Sheet1!A1:C10')\n",
    "    \n",
    "    Returns:\n",
    "        Success or error message\n",
    "    \"\"\"\n",
    "    if not sheets_service:\n",
    "        return \"Error: Google Sheets service not available. Please check your credentials.\"\n",
    "    \n",
    "    try:\n",
    "        result = sheets_service.spreadsheets().values().clear(\n",
    "            spreadsheetId=spreadsheet_id,\n",
    "            range=range_name\n",
    "        ).execute()\n",
    "        \n",
    "        return f\"Successfully cleared range {range_name}\"\n",
    "        \n",
    "    except HttpError as error:\n",
    "        return f\"Error clearing sheet range: {error}\"\n",
    "    except Exception as e:\n",
    "        return f\"Unexpected error: {e}\"\n",
    "\n",
    "@function_tool\n",
    "def analyze_sheet_data(spreadsheet_id: str, range_name: str = \"A:Z\") -> str:\n",
    "    \"\"\"\n",
    "    Analyze data in a Google Sheet and provide insights.\n",
    "    \n",
    "    Args:\n",
    "        spreadsheet_id: The ID of the Google Spreadsheet\n",
    "        range_name: The range to analyze (default: all data)\n",
    "    \n",
    "    Returns:\n",
    "        Data analysis summary\n",
    "    \"\"\"\n",
    "    if not sheets_service:\n",
    "        return \"Error: Google Sheets service not available. Please check your credentials.\"\n",
    "    \n",
    "    try:\n",
    "        # Get the data first\n",
    "        result = sheets_service.spreadsheets().values().get(\n",
    "            spreadsheetId=spreadsheet_id,\n",
    "            range=range_name\n",
    "        ).execute()\n",
    "        \n",
    "        values = result.get('values', [])\n",
    "        \n",
    "        if not values:\n",
    "            return \"No data found to analyze.\"\n",
    "        \n",
    "        # Basic analysis\n",
    "        analysis = f\"📊 **Sheet Data Analysis**\\n\\n\"\n",
    "        analysis += f\"• Total rows: {len(values)}\\n\"\n",
    "        \n",
    "        if values:\n",
    "            headers = values[0]\n",
    "            analysis += f\"• Total columns: {len(headers)}\\n\"\n",
    "            analysis += f\"• Column names: {', '.join(headers)}\\n\\n\"\n",
    "            \n",
    "            # Analyze each column\n",
    "            if len(values) > 1:  # Has data beyond headers\n",
    "                data_rows = values[1:]\n",
    "                analysis += \"**Column Analysis:**\\n\"\n",
    "                \n",
    "                for col_idx, header in enumerate(headers):\n",
    "                    col_values = []\n",
    "                    for row in data_rows:\n",
    "                        if col_idx < len(row) and row[col_idx].strip():\n",
    "                            col_values.append(row[col_idx].strip())\n",
    "                    \n",
    "                    if col_values:\n",
    "                        analysis += f\"\\n• **{header}**: {len(col_values)} non-empty values\"\n",
    "                        \n",
    "                        # Try to detect if numeric\n",
    "                        numeric_values = []\n",
    "                        for val in col_values:\n",
    "                            try:\n",
    "                                numeric_values.append(float(val.replace(',', '')))\n",
    "                            except ValueError:\n",
    "                                break\n",
    "                        \n",
    "                        if len(numeric_values) == len(col_values) and numeric_values:\n",
    "                            # Numeric column\n",
    "                            avg_val = sum(numeric_values) / len(numeric_values)\n",
    "                            analysis += f\" (Numeric - Avg: {avg_val:.2f}, Min: {min(numeric_values)}, Max: {max(numeric_values)})\"\n",
    "                        else:\n",
    "                            # Text column - show unique values count\n",
    "                            unique_values = len(set(col_values))\n",
    "                            analysis += f\" (Text - {unique_values} unique values)\"\n",
    "        \n",
    "        return analysis\n",
    "        \n",
    "    except HttpError as error:\n",
    "        return f\"Error analyzing sheet: {error}\"\n",
    "    except Exception as e:\n",
    "        return f\"Unexpected error during analysis: {e}\"\n",
    "\n",
    "@function_tool\n",
    "def create_summary_report(spreadsheet_id: str, source_range: str, summary_range: str) -> str:\n",
    "    \"\"\"\n",
    "    Create a summary report from data and write it to another range.\n",
    "    \n",
    "    Args:\n",
    "        spreadsheet_id: The ID of the Google Spreadsheet\n",
    "        source_range: Range to analyze (e.g., 'Data!A:Z')\n",
    "        summary_range: Range to write summary (e.g., 'Summary!A1')\n",
    "    \n",
    "    Returns:\n",
    "        Success message with summary details\n",
    "    \"\"\"\n",
    "    if not sheets_service:\n",
    "        return \"Error: Google Sheets service not available. Please check your credentials.\"\n",
    "    \n",
    "    try:\n",
    "        # Get source data\n",
    "        result = sheets_service.spreadsheets().values().get(\n",
    "            spreadsheetId=spreadsheet_id,\n",
    "            range=source_range\n",
    "        ).execute()\n",
    "        \n",
    "        values = result.get('values', [])\n",
    "        \n",
    "        if not values:\n",
    "            return \"No data found to summarize.\"\n",
    "        \n",
    "        # Create summary data\n",
    "        timestamp = datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")\n",
    "        summary_data = [\n",
    "            [\"📊 Data Summary Report\", \"\"],\n",
    "            [\"Generated:\", timestamp],\n",
    "            [\"\", \"\"],\n",
    "            [\"Total Rows:\", str(len(values))],\n",
    "            [\"Total Columns:\", str(len(values[0]) if values else 0)],\n",
    "            [\"\", \"\"],\n",
    "            [\"Source Range:\", source_range],\n",
    "        ]\n",
    "        \n",
    "        if values and len(values) > 1:\n",
    "            headers = values[0]\n",
    "            summary_data.append([\"Columns:\", \", \".join(headers)])\n",
    "        \n",
    "        # Write summary\n",
    "        body = {'values': summary_data}\n",
    "        sheets_service.spreadsheets().values().update(\n",
    "            spreadsheetId=spreadsheet_id,\n",
    "            range=summary_range,\n",
    "            valueInputOption='USER_ENTERED',\n",
    "            body=body\n",
    "        ).execute()\n",
    "        \n",
    "        return f\"Successfully created summary report in {summary_range} with {len(summary_data)} rows of summary data\"\n",
    "        \n",
    "    except HttpError as error:\n",
    "        return f\"Error creating summary: {error}\"\n",
    "    except Exception as e:\n",
    "        return f\"Unexpected error: {e}\"\n",
    "\n",
    "print(\"✅ All Google Sheets tools created successfully!\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "8",
   "metadata": {},
   "source": [
    "## 4. Building the Spreadsheet Agent\n",
    "\n",
    "Now let's create our intelligent spreadsheet agent with all the Google Sheets tools."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create the spreadsheet agent\n",
    "spreadsheet_agent = Agent(\n",
    "    name=\"Google Sheets Assistant\",\n",
    "    instructions=\"\"\"\n",
    "    You are an expert Google Sheets assistant specializing in data analysis, manipulation, and reporting.\n",
    "    \n",
    "    Your capabilities:\n",
    "    1. Read data from Google Sheets and understand structure\n",
    "    2. Write and append data to spreadsheets\n",
    "    3. Analyze data and provide insights\n",
    "    4. Create summary reports and visualizations\n",
    "    5. Clear and manage spreadsheet ranges\n",
    "    6. Help with data organization and cleanup\n",
    "    \n",
    "    Best practices:\n",
    "    - Always read data first before making changes\n",
    "    - Provide clear explanations of what you're doing\n",
    "    - Suggest data improvements and organization tips\n",
    "    - When analyzing data, be thorough and highlight key insights\n",
    "    - Ask for confirmation before making destructive changes (like clearing data)\n",
    "    \n",
    "    When working with spreadsheets:\n",
    "    - Use specific range notation (e.g., 'Sheet1!A1:C10')\n",
    "    - Always validate spreadsheet IDs before operations\n",
    "    - Provide helpful context about the data structure\n",
    "    - Suggest next steps for data analysis or manipulation\n",
    "    \"\"\",\n",
    "    model=\"gpt-4o-mini\",  # Use gpt-4o for more complex analysis\n",
    "    tools=[\n",
    "        read_sheet_data,\n",
    "        write_sheet_data,\n",
    "        append_sheet_data,\n",
    "        clear_sheet_range,\n",
    "        analyze_sheet_data,\n",
    "        create_summary_report\n",
    "    ],\n",
    "    model_settings=ModelSettings(\n",
    "        temperature=0.3,  # Lower temperature for more consistent data operations\n",
    "        max_tokens=2500   # Allow for comprehensive responses\n",
    "    )\n",
    ")\n",
    "\n",
    "print(f\"✅ Spreadsheet Agent '{spreadsheet_agent.name}' created with {len(spreadsheet_agent.tools)} tools\")\n",
    "print(\"\\nAgent capabilities:\")\n",
    "for i, tool in enumerate(spreadsheet_agent.tools, 1):\n",
    "    print(f\"  {i}. {tool.name}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "10",
   "metadata": {},
   "source": [
    "## 5. Basic Spreadsheet Operations\n",
    "\n",
    "Let's test our spreadsheet agent with basic operations. **Note**: Replace `YOUR_SPREADSHEET_ID` with your actual Google Sheets ID."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "11",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Example spreadsheet ID - replace with your own\n",
    "# You can find this in your Google Sheets URL: \n",
    "# https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit\n",
    "EXAMPLE_SPREADSHEET_ID = \"YOUR_SPREADSHEET_ID\"  # Replace this!\n",
    "\n",
    "# Example 1: Read existing data\n",
    "print(\"=\" * 60)\n",
    "print(\"📖 Example 1: Reading Spreadsheet Data\")\n",
    "print(\"=\" * 60)\n",
    "\n",
    "if EXAMPLE_SPREADSHEET_ID != \"YOUR_SPREADSHEET_ID\":\n",
    "    read_config = RunConfig(\n",
    "        workflow_name=\"Spreadsheet Read Operation\",\n",
    "        trace_include_sensitive_data=False\n",
    "    )\n",
    "    \n",
    "    result = Runner.run_sync(\n",
    "        spreadsheet_agent,\n",
    "        f\"Please read the data from spreadsheet {EXAMPLE_SPREADSHEET_ID} and tell me what you find. Analyze the structure and content.\",\n",
    "        run_config=read_config\n",
    "    )\n",
    "    \n",
    "    print(result.final_output)\n",
    "else:\n",
    "    print(\"⚠️ Please replace EXAMPLE_SPREADSHEET_ID with your actual Google Sheets ID\")\n",
    "    print(\"You can find this in your Google Sheets URL after '/d/' and before '/edit'\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "12",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Example 2: Create sample data\n",
    "print(\"\\n\" + \"=\" * 60)\n",
    "print(\"✍️ Example 2: Creating Sample Data\")\n",
    "print(\"=\" * 60)\n",
    "\n",
    "if EXAMPLE_SPREADSHEET_ID != \"YOUR_SPREADSHEET_ID\":\n",
    "    create_data_query = f\"\"\"\n",
    "    Please create a sample dataset in spreadsheet {EXAMPLE_SPREADSHEET_ID} with the following:\n",
    "    \n",
    "    1. Clear any existing data in range A1:E10\n",
    "    2. Create a header row with: Name, Age, Department, Salary, Join_Date\n",
    "    3. Add 5 rows of sample employee data\n",
    "    4. Then analyze the data you just created\n",
    "    \n",
    "    Use realistic sample data and make sure to format it properly.\n",
    "    \"\"\"\n",
    "    \n",
    "    create_config = RunConfig(\n",
    "        workflow_name=\"Create Sample Data\",\n",
    "        trace_include_sensitive_data=False\n",
    "    )\n",
    "    \n",
    "    result = Runner.run_sync(\n",
    "        spreadsheet_agent,\n",
    "        create_data_query,\n",
    "        run_config=create_config\n",
    "    )\n",
    "    \n",
    "    print(result.final_output)\n",
    "else:\n",
    "    print(\"⚠️ Please set up your spreadsheet ID first\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "13",
   "metadata": {},
   "source": [
    "## 6. Advanced Data Analysis with Tracing\n",
    "\n",
    "Let's perform more complex data analysis operations with proper tracing."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "14",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Advanced analysis with tracing\n",
    "async def comprehensive_data_analysis(spreadsheet_id: str):\n",
    "    \"\"\"Perform comprehensive data analysis with tracing\"\"\"\n",
    "    \n",
    "    with trace(\"Comprehensive Spreadsheet Analysis\") as analysis_trace:\n",
    "        print(f\"Started analysis trace: {analysis_trace.id}\")\n",
    "        \n",
    "        # Step 1: Initial data exploration\n",
    "        print(\"\\n📊 Step 1: Data Exploration...\")\n",
    "        exploration_result = await Runner.run(\n",
    "            spreadsheet_agent,\n",
    "            f\"Analyze all data in spreadsheet {spreadsheet_id}. Provide detailed insights about the data structure, types, and patterns you observe.\",\n",
    "            run_config=RunConfig(\n",
    "                workflow_name=\"Data Exploration\",\n",
    "                trace_include_sensitive_data=False\n",
    "            )\n",
    "        )\n",
    "        \n",
    "        # Step 2: Create summary report\n",
    "        print(\"\\n📋 Step 2: Creating Summary Report...\")\n",
    "        summary_result = await Runner.run(\n",
    "            spreadsheet_agent,\n",
    "            f\"Create a comprehensive summary report for the data in spreadsheet {spreadsheet_id}. Write the summary to a new range called 'Summary!A1' in the same spreadsheet.\",\n",
    "            run_config=RunConfig(\n",
    "                workflow_name=\"Summary Creation\",\n",
    "                trace_include_sensitive_data=False\n",
    "            )\n",
    "        )\n",
    "        \n",
    "        # Step 3: Recommendations\n",
    "        print(\"\\n💡 Step 3: Data Recommendations...\")\n",
    "        recommendations_result = await Runner.run(\n",
    "            spreadsheet_agent,\n",
    "            f\"Based on your analysis of spreadsheet {spreadsheet_id}, provide specific recommendations for data improvements, additional analysis, or potential insights that could be extracted.\",\n",
    "            run_config=RunConfig(\n",
    "                workflow_name=\"Recommendations\",\n",
    "                trace_include_sensitive_data=False\n",
    "            )\n",
    "        )\n",
    "        \n",
    "        print(\"\\n\" + \"=\" * 80)\n",
    "        print(\"📊 COMPREHENSIVE ANALYSIS RESULTS\")\n",
    "        print(\"=\" * 80)\n",
    "        \n",
    "        print(\"\\n🔍 DATA EXPLORATION:\")\n",
    "        print(\"-\" * 40)\n",
    "        print(exploration_result.final_output)\n",
    "        \n",
    "        print(\"\\n📋 SUMMARY REPORT:\")\n",
    "        print(\"-\" * 40)\n",
    "        print(summary_result.final_output)\n",
    "        \n",
    "        print(\"\\n💡 RECOMMENDATIONS:\")\n",
    "        print(\"-\" * 40)\n",
    "        print(recommendations_result.final_output)\n",
    "        \n",
    "        return {\n",
    "            \"exploration\": exploration_result.final_output,\n",
    "            \"summary\": summary_result.final_output,\n",
    "            \"recommendations\": recommendations_result.final_output\n",
    "        }\n",
    "\n",
    "# Run comprehensive analysis (uncomment when ready)\n",
    "print(\"Comprehensive analysis function prepared.\")\n",
    "print(\"To run: await comprehensive_data_analysis(EXAMPLE_SPREADSHEET_ID)\")\n",
    "\n",
    "# Uncomment to run:\n",
    "# if EXAMPLE_SPREADSHEET_ID != \"YOUR_SPREADSHEET_ID\":\n",
    "#     import asyncio\n",
    "#     analysis_results = await comprehensive_data_analysis(EXAMPLE_SPREADSHEET_ID)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "15",
   "metadata": {},
   "source": [
    "## 7. Interactive Spreadsheet Session\n",
    "\n",
    "Let's create an interactive session for working with spreadsheets."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "16",
   "metadata": {},
   "outputs": [],
   "source": [
    "class SpreadsheetSession:\n",
    "    \"\"\"Interactive session for spreadsheet operations\"\"\"\n",
    "    \n",
    "    def __init__(self, spreadsheet_id: str, agent: Agent):\n",
    "        self.spreadsheet_id = spreadsheet_id\n",
    "        self.agent = agent\n",
    "        self.session_history = []\n",
    "        self.session_id = datetime.now().strftime(\"%Y%m%d_%H%M%S\")\n",
    "    \n",
    "    def execute_command(self, command: str) -> str:\n",
    "        \"\"\"Execute a spreadsheet command\"\"\"\n",
    "        enhanced_command = f\"\"\"\n",
    "        Working with spreadsheet: {self.spreadsheet_id}\n",
    "        \n",
    "        Previous operations in this session:\n",
    "        {self._get_session_context()}\n",
    "        \n",
    "        Current request: {command}\n",
    "        \n",
    "        Please execute this request and provide clear feedback about what was accomplished.\n",
    "        \"\"\"\n",
    "        \n",
    "        config = RunConfig(\n",
    "            workflow_name=f\"Spreadsheet Session {self.session_id}\",\n",
    "            trace_include_sensitive_data=False,\n",
    "            group_id=f\"session_{self.session_id}\"\n",
    "        )\n",
    "        \n",
    "        result = Runner.run_sync(self.agent, enhanced_command, run_config=config)\n",
    "        \n",
    "        # Store in history\n",
    "        self.session_history.append({\n",
    "            \"timestamp\": datetime.now().isoformat(),\n",
    "            \"command\": command,\n",
    "            \"result\": result.final_output\n",
    "        })\n",
    "        \n",
    "        return result.final_output\n",
    "    \n",
    "    def _get_session_context(self) -> str:\n",
    "        \"\"\"Get summary of recent session history\"\"\"\n",
    "        if not self.session_history:\n",
    "            return \"No previous operations in this session.\"\n",
    "        \n",
    "        context = \"Recent operations:\\n\"\n",
    "        for i, item in enumerate(self.session_history[-3:], 1):  # Last 3 operations\n",
    "            context += f\"{i}. {item['command'][:100]}...\\n\"\n",
    "        return context\n",
    "    \n",
    "    def get_session_summary(self) -> Dict[str, Any]:\n",
    "        \"\"\"Get complete session summary\"\"\"\n",
    "        return {\n",
    "            \"session_id\": self.session_id,\n",
    "            \"spreadsheet_id\": self.spreadsheet_id,\n",
    "            \"total_operations\": len(self.session_history),\n",
    "            \"history\": self.session_history\n",
    "        }\n",
    "\n",
    "# Demo spreadsheet session\n",
    "if EXAMPLE_SPREADSHEET_ID != \"YOUR_SPREADSHEET_ID\":\n",
    "    print(\"=\" * 60)\n",
    "    print(\"🔄 Interactive Spreadsheet Session Demo\")\n",
    "    print(\"=\" * 60)\n",
    "    \n",
    "    # Create session\n",
    "    session = SpreadsheetSession(EXAMPLE_SPREADSHEET_ID, spreadsheet_agent)\n",
    "    \n",
    "    # Demo commands\n",
    "    demo_commands = [\n",
    "        \"Read the current data and tell me what you see\",\n",
    "        \"Add a new row with employee data: John Smith, 28, Engineering, 75000, 2024-01-15\",\n",
    "        \"Calculate the average salary from all the data\"\n",
    "    ]\n",
    "    \n",
    "    for i, command in enumerate(demo_commands, 1):\n",
    "        print(f\"\\n💬 Command {i}: {command}\")\n",
    "        print(\"🤖 Response:\")\n",
    "        response = session.execute_command(command)\n",
    "        print(response[:300] + \"...\" if len(response) > 300 else response)\n",
    "        print(\"-\" * 40)\n",
    "    \n",
    "    print(f\"\\n📊 Session completed with {len(session.session_history)} operations\")\n",
    "else:\n",
    "    print(\"⚠️ Set up your spreadsheet ID to run the interactive session demo\")\n",
    "\n",
    "print(\"\\n✅ Interactive spreadsheet session functionality ready!\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "17",
   "metadata": {},
   "source": [
    "## 8. Practical Use Cases\n",
    "\n",
    "Let's explore some practical scenarios for using our spreadsheet agent."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "18",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Practical use case examples\n",
    "\n",
    "def sales_data_processor(spreadsheet_id: str) -> str:\n",
    "    \"\"\"Process sales data with the spreadsheet agent\"\"\"\n",
    "    query = f\"\"\"\n",
    "    I have sales data in spreadsheet {spreadsheet_id}. Please:\n",
    "    \n",
    "    1. Read the sales data and identify the structure\n",
    "    2. Calculate total sales, average order value, and top products\n",
    "    3. Create a summary report in a new sheet/range\n",
    "    4. Suggest any data quality improvements\n",
    "    \n",
    "    Provide detailed analysis and insights.\n",
    "    \"\"\"\n",
    "    \n",
    "    config = RunConfig(\n",
    "        workflow_name=\"Sales Data Analysis\",\n",
    "        trace_include_sensitive_data=False\n",
    "    )\n",
    "    \n",
    "    result = Runner.run_sync(spreadsheet_agent, query, run_config=config)\n",
    "    return result.final_output\n",
    "\n",
    "def inventory_manager(spreadsheet_id: str) -> str:\n",
    "    \"\"\"Manage inventory data\"\"\"\n",
    "    query = f\"\"\"\n",
    "    Help me manage inventory in spreadsheet {spreadsheet_id}:\n",
    "    \n",
    "    1. Check current inventory levels\n",
    "    2. Identify items that are low in stock (less than 10 units)\n",
    "    3. Calculate total inventory value\n",
    "    4. Create a reorder report highlighting items that need restocking\n",
    "    \n",
    "    Format the results clearly and provide actionable recommendations.\n",
    "    \"\"\"\n",
    "    \n",
    "    config = RunConfig(\n",
    "        workflow_name=\"Inventory Management\",\n",
    "        trace_include_sensitive_data=False\n",
    "    )\n",
    "    \n",
    "    result = Runner.run_sync(spreadsheet_agent, query, run_config=config)\n",
    "    return result.final_output\n",
    "\n",
    "def budget_analyzer(spreadsheet_id: str) -> str:\n",
    "    \"\"\"Analyze budget data\"\"\"\n",
    "    query = f\"\"\"\n",
    "    Analyze the budget data in spreadsheet {spreadsheet_id}:\n",
    "    \n",
    "    1. Read the budget vs actual spending data\n",
    "    2. Calculate variances (over/under budget)\n",
    "    3. Identify the biggest spending categories\n",
    "    4. Create a variance report with recommendations\n",
    "    5. Suggest budget optimizations\n",
    "    \n",
    "    Provide financial insights and actionable recommendations.\n",
    "    \"\"\"\n",
    "    \n",
    "    config = RunConfig(\n",
    "        workflow_name=\"Budget Analysis\",\n",
    "        trace_include_sensitive_data=False\n",
    "    )\n",
    "    \n",
    "    result = Runner.run_sync(spreadsheet_agent, query, run_config=config)\n",
    "    return result.final_output\n",
    "\n",
    "# Demo the use cases\n",
    "print(\"💼 Practical Use Cases for Spreadsheet Agent\")\n",
    "print(\"=\" * 50)\n",
    "\n",
    "use_cases = {\n",
    "    \"Sales Data Processing\": sales_data_processor,\n",
    "    \"Inventory Management\": inventory_manager,\n",
    "    \"Budget Analysis\": budget_analyzer\n",
    "}\n",
    "\n",
    "for name, func in use_cases.items():\n",
    "    print(f\"\\n📊 {name}:\")\n",
    "    print(f\"   Function: {func.__name__}()\")\n",
    "    print(f\"   Purpose: {func.__doc__}\")\n",
    "\n",
    "print(\"\\n✅ All use case functions are ready to use with your spreadsheet ID!\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "19",
   "metadata": {},
   "source": [
    "## 9. Best Practices and Tips\n",
    "\n",
    "Here are important best practices when working with the Google Sheets Agent."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "20",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Best practices for spreadsheet agents\n",
    "\n",
    "# 1. Error handling for Google Sheets operations\n",
    "@function_tool\n",
    "def safe_sheet_operation(spreadsheet_id: str, operation: str) -> str:\n",
    "    \"\"\"\n",
    "    Example of safe sheet operation with comprehensive error handling.\n",
    "    \n",
    "    Args:\n",
    "        spreadsheet_id: The spreadsheet ID\n",
    "        operation: Description of the operation\n",
    "    \n",
    "    Returns:\n",
    "        Result or detailed error message\n",
    "    \"\"\"\n",
    "    try:\n",
    "        # Validate spreadsheet ID format\n",
    "        if not spreadsheet_id or len(spreadsheet_id) < 20:\n",
    "            return \"Error: Invalid spreadsheet ID format\"\n",
    "        \n",
    "        # Your operation logic here\n",
    "        return f\"Successfully completed: {operation}\"\n",
    "        \n",
    "    except HttpError as e:\n",
    "        if e.resp.status == 404:\n",
    "            return \"Error: Spreadsheet not found. Please check the ID and ensure it's shared with the service account.\"\n",
    "        elif e.resp.status == 403:\n",
    "            return \"Error: Permission denied. Please share the spreadsheet with the service account email.\"\n",
    "        else:\n",
    "            return f\"Google Sheets API Error: {e}\"\n",
    "    except Exception as e:\n",
    "        return f\"Unexpected error: {e}\"\n",
    "\n",
    "# 2. Configuration management\n",
    "class SheetsConfig:\n",
    "    \"\"\"Configuration management for Google Sheets operations\"\"\"\n",
    "    \n",
    "    def __init__(self, credentials_path: str = \"credentials.json\"):\n",
    "        self.credentials_path = credentials_path\n",
    "        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']\n",
    "        self.service = None\n",
    "    \n",
    "    def get_service(self):\n",
    "        \"\"\"Get or create Google Sheets service\"\"\"\n",
    "        if not self.service:\n",
    "            self.service = setup_sheets_service()\n",
    "        return self.service\n",
    "    \n",
    "    def validate_spreadsheet_id(self, spreadsheet_id: str) -> bool:\n",
    "        \"\"\"Validate spreadsheet ID format\"\"\"\n",
    "        return len(spreadsheet_id) >= 20 and \"/\" not in spreadsheet_id\n",
    "\n",
    "# 3. Data validation helpers\n",
    "def validate_range_format(range_name: str) -> bool:\n",
    "    \"\"\"Validate Google Sheets range format\"\"\"\n",
    "    # Basic validation for range format\n",
    "    valid_patterns = [\n",
    "        r'^[A-Z]+:[A-Z]+$',  # A:Z\n",
    "        r'^[A-Z]+\\d+:[A-Z]+\\d+$',  # A1:C10\n",
    "        r'^\\w+![A-Z]+\\d+:[A-Z]+\\d+$',  # Sheet1!A1:C10\n",
    "    ]\n",
    "    import re\n",
    "    return any(re.match(pattern, range_name) for pattern in valid_patterns)\n",
    "\n",
    "def format_sheet_data(values: List[List[str]]) -> str:\n",
    "    \"\"\"Format sheet data for better readability\"\"\"\n",
    "    if not values:\n",
    "        return \"No data found\"\n",
    "    \n",
    "    formatted = \"\\n\".join([\n",
    "        \" | \".join(row) for row in values[:10]  # First 10 rows\n",
    "    ])\n",
    "    \n",
    "    if len(values) > 10:\n",
    "        formatted += f\"\\n... and {len(values) - 10} more rows\"\n",
    "    \n",
    "    return formatted\n",
    "\n",
    "# 4. Session management best practices\n",
    "class SpreadsheetSessionManager:\n",
    "    \"\"\"Advanced session management for spreadsheet operations\"\"\"\n",
    "    \n",
    "    def __init__(self):\n",
    "        self.active_sessions = {}\n",
    "        self.config = SheetsConfig()\n",
    "    \n",
    "    def create_session(self, spreadsheet_id: str, user_id: str = \"default\") -> str:\n",
    "        \"\"\"Create a new spreadsheet session\"\"\"\n",
    "        if not self.config.validate_spreadsheet_id(spreadsheet_id):\n",
    "            raise ValueError(\"Invalid spreadsheet ID\")\n",
    "        \n",
    "        session_id = f\"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}\"\n",
    "        self.active_sessions[session_id] = {\n",
    "            \"spreadsheet_id\": spreadsheet_id,\n",
    "            \"user_id\": user_id,\n",
    "            \"created_at\": datetime.now(),\n",
    "            \"operations\": []\n",
    "        }\n",
    "        return session_id\n",
    "    \n",
    "    def log_operation(self, session_id: str, operation: str, result: str):\n",
    "        \"\"\"Log an operation in the session\"\"\"\n",
    "        if session_id in self.active_sessions:\n",
    "            self.active_sessions[session_id][\"operations\"].append({\n",
    "                \"timestamp\": datetime.now(),\n",
    "                \"operation\": operation,\n",
    "                \"result\": result\n",
    "            })\n",
    "\n",
    "# Example usage of best practices\n",
    "print(\"📋 Google Sheets Agent Best Practices:\")\n",
    "print(\"=\" * 45)\n",
    "\n",
    "best_practices = [\n",
    "    \"✅ Always validate spreadsheet IDs before operations\",\n",
    "    \"✅ Handle Google Sheets API errors gracefully\",\n",
    "    \"✅ Use specific range notation for clarity\",\n",
    "    \"✅ Implement proper error handling and user feedback\",\n",
    "    \"✅ Validate data formats before writing to sheets\",\n",
    "    \"✅ Use tracing for complex multi-step operations\",\n",
    "    \"✅ Keep session history for better context\",\n",
    "    \"✅ Provide clear success/error messages\",\n",
    "    \"✅ Ask for confirmation before destructive operations\",\n",
    "    \"✅ Share spreadsheets with service account email\"\n",
    "]\n",
    "\n",
    "for practice in best_practices:\n",
    "    print(f\"  {practice}\")\n",
    "\n",
    "print(\"\\n💡 Pro Tips:\")\n",
    "print(\"  • Test with a sample spreadsheet first\")\n",
    "print(\"  • Keep credentials.json secure and never commit to git\")\n",
    "print(\"  • Use environment variables for sensitive data\")\n",
    "print(\"  • Monitor API quota usage for large operations\")\n",
    "print(\"  • Implement rate limiting for bulk operations\")\n",
    "\n",
    "print(\"\\n✅ Best practices guide completed!\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "21",
   "metadata": {},
   "source": [
    "## 10. Summary and Next Steps\n",
    "\n",
    "### What We've Accomplished\n",
    "\n",
    "In this tutorial, we've built a comprehensive Google Sheets agent using the OpenAI Agents SDK:\n",
    "\n",
    "1. **Google Sheets Integration** - Set up service account authentication and API access\n",
    "2. **Custom Tools** - Created 6 powerful tools for sheet operations using `@function_tool`\n",
    "3. **Intelligent Agent** - Built an agent specialized in spreadsheet data analysis and manipulation\n",
    "4. **Practical Examples** - Demonstrated real-world use cases and workflows\n",
    "5. **Best Practices** - Implemented proper error handling, tracing, and session management\n",
    "\n",
    "### Key Features\n",
    "\n",
    "Our spreadsheet agent can:\n",
    "- **Read & Analyze** - Parse spreadsheet data and provide insights\n",
    "- **Write & Update** - Add new data and modify existing content\n",
    "- **Create Reports** - Generate summary reports and analysis\n",
    "- **Data Validation** - Ensure data quality and format consistency\n",
    "- **Session Management** - Maintain context across operations\n",
    "\n",
    "### Next Steps\n",
    "\n",
    "To extend this spreadsheet agent further:\n",
    "\n",
    "1. **Advanced Analytics**\n",
    "   - Add statistical analysis tools\n",
    "   - Implement data visualization\n",
    "   - Create predictive models\n",
    "\n",
    "2. **Integration Expansion**\n",
    "   - Connect with other Google Workspace apps\n",
    "   - Add database connectors\n",
    "   - Integrate with external APIs\n",
    "\n",
    "3. **Automation**\n",
    "   - Schedule regular data updates\n",
    "   - Set up data validation rules\n",
    "   - Create automated reports\n",
    "\n",
    "4. **Security & Scale**\n",
    "   - Implement user authentication\n",
    "   - Add audit logging\n",
    "   - Handle rate limiting\n",
    "\n",
    "### Resources\n",
    "\n",
    "- [Google Sheets API Documentation](https://developers.google.com/sheets/api)\n",
    "- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)\n",
    "- [Google Cloud Console](https://console.cloud.google.com/)\n",
    "\n",
    "### Quick Start Function\n",
    "\n",
    "Here's a simple function to get started quickly:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "22",
   "metadata": {},
   "outputs": [],
   "source": [
    "def quick_sheet_analysis(spreadsheet_id: str, task: str = \"analyze\") -> str:\n",
    "    \"\"\"\n",
    "    Quick spreadsheet analysis function.\n",
    "    \n",
    "    Args:\n",
    "        spreadsheet_id: Your Google Sheets ID\n",
    "        task: Type of analysis ('analyze', 'summarize', 'clean')\n",
    "    \n",
    "    Returns:\n",
    "        Analysis results\n",
    "    \"\"\"\n",
    "    task_instructions = {\n",
    "        \"analyze\": \"Analyze the data structure, identify patterns, and provide key insights\",\n",
    "        \"summarize\": \"Create a comprehensive summary report of the data\",\n",
    "        \"clean\": \"Identify data quality issues and suggest improvements\"\n",
    "    }\n",
    "    \n",
    "    query = f\"\"\"\n",
    "    Working with spreadsheet: {spreadsheet_id}\n",
    "    \n",
    "    Task: {task_instructions.get(task, task_instructions['analyze'])}\n",
    "    \n",
    "    Please read the data and provide detailed feedback with actionable insights.\n",
    "    \"\"\"\n",
    "    \n",
    "    config = RunConfig(\n",
    "        workflow_name=f\"Quick Sheet {task.title()}\",\n",
    "        trace_include_sensitive_data=False\n",
    "    )\n",
    "    \n",
    "    result = Runner.run_sync(spreadsheet_agent, query, run_config=config)\n",
    "    return result.final_output\n",
    "\n",
    "# Example usage demonstration\n",
    "print(\"🚀 Quick Start Example:\")\n",
    "print(\"=\" * 50)\n",
    "print(\"# Replace with your actual spreadsheet ID\")\n",
    "print('spreadsheet_id = \"1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms\"')\n",
    "print('')\n",
    "print('# Quick analysis')\n",
    "print('result = quick_sheet_analysis(spreadsheet_id, \"analyze\")')\n",
    "print('print(result)')\n",
    "\n",
    "print(\"\\n\" + \"=\" * 70)\n",
    "print(\"🎉 Congratulations! You've built a powerful Google Sheets Agent!\")\n",
    "print(\"=\" * 70)\n",
    "\n",
    "if EXAMPLE_SPREADSHEET_ID != \"YOUR_SPREADSHEET_ID\":\n",
    "    print(f\"\\n🔗 Your agent is ready to work with spreadsheet: {EXAMPLE_SPREADSHEET_ID}\")\n",
    "else:\n",
    "    print(\"\\n⚠️ Remember to set up your spreadsheet ID and credentials to start using the agent!\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}


---
./notebooks/7.0-spreadsheet-agent.py
---
#!/usr/bin/env python3
"""
Google Sheets Agent Example using OpenAI Agents SDK

This example demonstrates how to build an AI agent that can interact with Google Sheets
to read, write, analyze, and manage spreadsheet data.

Requirements:
1. Set up Google Cloud Platform project
2. Enable Google Sheets API
3. Create a service account and download credentials.json
4. Install required packages: pip install openai-agents google-api-python-client

Setup Instructions:
1. Go to Google Cloud Platform Console
2. Create a new project or select existing one
3. Enable Google Sheets API
4. Go to IAM & Admin > Service Accounts
5. Create a new service account
6. Download the JSON key file and save as 'credentials.json' in this directory
7. Share your Google Sheets with the service account email (found in credentials.json)
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account

from agents import Agent, Runner, function_tool
from agents.run import RunConfig
from agents import trace

# Configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'

class SheetsSession:
    """Session manager for Google Sheets operations"""
    
    def __init__(self):
        self.current_spreadsheet_id = None
        self.current_sheet_name = None
        self.service = None
        self._setup_service()
    
    def _setup_service(self):
        """Initialize Google Sheets API service"""
        if not os.path.exists(CREDENTIALS_FILE):
            raise FileNotFoundError(
                f"Google credentials file '{CREDENTIALS_FILE}' not found. "
                "Please download it from Google Cloud Platform."
            )
        
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES
        )
        self.service = build('sheets', 'v4', credentials=credentials)
    
    def set_active_sheet(self, spreadsheet_id: str, sheet_name: str = None):
        """Set the active spreadsheet and sheet"""
        self.current_spreadsheet_id = spreadsheet_id
        self.current_sheet_name = sheet_name or "Sheet1"
    
    def get_sheet_info(self):
        """Get current sheet information"""
        if not self.current_spreadsheet_id:
            return "No active spreadsheet set"
        return f"Active: {self.current_spreadsheet_id}, Sheet: {self.current_sheet_name}"

# Global session instance
sheets_session = SheetsSession()

@function_tool
def read_sheet_data(spreadsheet_id: str, range_name: str, sheet_name: str = "Sheet1") -> str:
    """
    Read data from a Google Sheet
    
    Args:
        spreadsheet_id: The Google Sheets document ID (from the URL)
        range_name: The range to read (e.g., 'A1:E10', 'A:E', 'Sales Data')
        sheet_name: Name of the sheet tab (default: Sheet1)
    
    Returns:
        JSON string containing the sheet data
    """
    try:
        # Update session
        sheets_session.set_active_sheet(spreadsheet_id, sheet_name)
        
        # Construct full range
        full_range = f"{sheet_name}!{range_name}" if sheet_name else range_name
        
        # Read data
        result = sheets_session.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=full_range
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            return json.dumps({"message": "No data found in the specified range"})
        
        # Convert to structured format
        if len(values) > 1:
            headers = values[0]
            data_rows = values[1:]
            data = []
            for row in data_rows:
                # Handle rows with missing values
                row_dict = {}
                for i, header in enumerate(headers):
                    row_dict[header] = row[i] if i < len(row) else ""
                data.append(row_dict)
            
            return json.dumps({
                "range": full_range,
                "headers": headers,
                "data": data,
                "row_count": len(data_rows)
            }, indent=2)
        else:
            return json.dumps({
                "range": full_range,
                "raw_data": values,
                "row_count": len(values)
            }, indent=2)
            
    except Exception as e:
        return json.dumps({"error": f"Failed to read sheet data: {str(e)}"})

@function_tool
def write_sheet_data(spreadsheet_id: str, range_name: str, data: List[List[str]], sheet_name: str = "Sheet1") -> str:
    """
    Write data to a specific range in Google Sheets
    
    Args:
        spreadsheet_id: The Google Sheets document ID
        range_name: The range to write to (e.g., 'A1:C3')
        data: 2D list of values to write
        sheet_name: Name of the sheet tab
    
    Returns:
        Success message with details
    """
    try:
        # Update session
        sheets_session.set_active_sheet(spreadsheet_id, sheet_name)
        
        # Construct full range
        full_range = f"{sheet_name}!{range_name}" if sheet_name else range_name
        
        # Prepare the request body
        body = {
            'values': data
        }
        
        # Write data
        result = sheets_session.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=full_range,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        return json.dumps({
            "success": True,
            "message": f"Updated {result.get('updatedCells', 0)} cells in {full_range}",
            "range": full_range,
            "updated_rows": result.get('updatedRows', 0),
            "updated_columns": result.get('updatedColumns', 0)
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to write sheet data: {str(e)}"})

@function_tool
def append_sheet_data(spreadsheet_id: str, data: List[List[str]], sheet_name: str = "Sheet1") -> str:
    """
    Append new rows to the end of a Google Sheet
    
    Args:
        spreadsheet_id: The Google Sheets document ID
        data: 2D list of values to append
        sheet_name: Name of the sheet tab
    
    Returns:
        Success message with details
    """
    try:
        # Update session
        sheets_session.set_active_sheet(spreadsheet_id, sheet_name)
        
        # Construct range for the entire sheet
        range_name = f"{sheet_name}!A:Z"
        
        # Prepare the request body
        body = {
            'values': data
        }
        
        # Append data
        result = sheets_session.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        return json.dumps({
            "success": True,
            "message": f"Appended {len(data)} rows to {sheet_name}",
            "updated_range": result.get('updates', {}).get('updatedRange', ''),
            "updated_rows": result.get('updates', {}).get('updatedRows', 0),
            "updated_cells": result.get('updates', {}).get('updatedCells', 0)
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to append sheet data: {str(e)}"})

@function_tool
def clear_sheet_range(spreadsheet_id: str, range_name: str, sheet_name: str = "Sheet1") -> str:
    """
    Clear data from a specific range in Google Sheets
    
    Args:
        spreadsheet_id: The Google Sheets document ID
        range_name: The range to clear (e.g., 'A1:E10')
        sheet_name: Name of the sheet tab
    
    Returns:
        Success message
    """
    try:
        # Update session
        sheets_session.set_active_sheet(spreadsheet_id, sheet_name)
        
        # Construct full range
        full_range = f"{sheet_name}!{range_name}" if sheet_name else range_name
        
        # Clear the range
        result = sheets_session.service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=full_range
        ).execute()
        
        return json.dumps({
            "success": True,
            "message": f"Cleared range {full_range}",
            "cleared_range": result.get('clearedRange', full_range)
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to clear sheet range: {str(e)}"})

@function_tool
def analyze_sheet_data(spreadsheet_id: str, range_name: str, analysis_type: str = "summary", sheet_name: str = "Sheet1") -> str:
    """
    Analyze data from a Google Sheet and provide insights
    
    Args:
        spreadsheet_id: The Google Sheets document ID
        range_name: The range to analyze
        analysis_type: Type of analysis ('summary', 'statistics', 'trends')
        sheet_name: Name of the sheet tab
    
    Returns:
        Analysis results as JSON string
    """
    try:
        # First, read the data
        data_result = read_sheet_data(spreadsheet_id, range_name, sheet_name)
        data_json = json.loads(data_result)
        
        if "error" in data_json:
            return data_result
        
        if "data" not in data_json:
            return json.dumps({"error": "No structured data available for analysis"})
        
        data = data_json["data"]
        headers = data_json["headers"]
        
        # Convert to pandas DataFrame for analysis
        df = pd.DataFrame(data)
        
        analysis_result = {
            "analysis_type": analysis_type,
            "range": f"{sheet_name}!{range_name}",
            "total_rows": len(data),
            "total_columns": len(headers),
            "columns": headers
        }
        
        if analysis_type == "summary":
            # Basic summary
            analysis_result["summary"] = {
                "row_count": len(data),
                "column_count": len(headers),
                "non_empty_cells": sum(1 for row in data for value in row.values() if str(value).strip()),
                "sample_data": data[:3] if len(data) > 3 else data
            }
            
        elif analysis_type == "statistics":
            # Statistical analysis for numeric columns
            numeric_analysis = {}
            for col in headers:
                try:
                    values = [float(row[col]) for row in data if str(row[col]).replace('.', '').replace('-', '').isdigit()]
                    if values:
                        numeric_analysis[col] = {
                            "count": len(values),
                            "mean": sum(values) / len(values),
                            "min": min(values),
                            "max": max(values)
                        }
                except:
                    continue
            analysis_result["numeric_statistics"] = numeric_analysis
            
        elif analysis_type == "trends":
            # Basic trend analysis
            analysis_result["trends"] = {
                "most_common_values": {},
                "data_quality": {
                    "empty_cells": sum(1 for row in data for value in row.values() if not str(value).strip()),
                    "total_cells": len(data) * len(headers)
                }
            }
            
            # Find most common values in each column
            for col in headers:
                values = [str(row[col]).strip() for row in data if str(row[col]).strip()]
                if values:
                    value_counts = {}
                    for value in values:
                        value_counts[value] = value_counts.get(value, 0) + 1
                    # Get top 3 most common values
                    sorted_values = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                    analysis_result["trends"]["most_common_values"][col] = sorted_values
        
        return json.dumps(analysis_result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to analyze sheet data: {str(e)}"})

@function_tool
def create_summary_report(spreadsheet_id: str, source_range: str, report_title: str = "Data Summary", sheet_name: str = "Sheet1") -> str:
    """
    Create a summary report based on sheet data and write it to a new location
    
    Args:
        spreadsheet_id: The Google Sheets document ID
        source_range: The range to analyze for the report
        report_title: Title for the summary report
        sheet_name: Name of the sheet tab
    
    Returns:
        Report summary and location where it was written
    """
    try:
        # Get analysis of the data
        analysis_result = analyze_sheet_data(spreadsheet_id, source_range, "summary", sheet_name)
        analysis_data = json.loads(analysis_result)
        
        if "error" in analysis_data:
            return analysis_result
        
        # Create report data
        report_data = [
            [report_title],
            ["Generated on:", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Source Range:", f"{sheet_name}!{source_range}"],
            [""],
            ["Summary Statistics:"],
            ["Total Rows:", str(analysis_data["summary"]["row_count"])],
            ["Total Columns:", str(analysis_data["summary"]["column_count"])],
            ["Non-empty Cells:", str(analysis_data["summary"]["non_empty_cells"])],
            [""],
            ["Column Names:"]
        ]
        
        # Add column names
        for i, col in enumerate(analysis_data["columns"], 1):
            report_data.append([f"{i}.", col])
        
        # Add sample data
        report_data.extend([
            [""],
            ["Sample Data (first 3 rows):"]
        ])
        
        if analysis_data["summary"]["sample_data"]:
            # Add headers
            headers = analysis_data["columns"]
            report_data.append(headers)
            
            # Add sample rows
            for row_data in analysis_data["summary"]["sample_data"]:
                row = [str(row_data.get(col, "")) for col in headers]
                report_data.append(row)
        
        # Find empty space to write the report (starting from column H)
        report_range = f"H1:K{len(report_data)}"
        
        # Write the report
        write_result = write_sheet_data(spreadsheet_id, report_range, report_data, sheet_name)
        write_data = json.loads(write_result)
        
        if write_data.get("success"):
            return json.dumps({
                "success": True,
                "message": f"Created summary report '{report_title}' in range {sheet_name}!{report_range}",
                "report_location": f"{sheet_name}!{report_range}",
                "report_rows": len(report_data),
                "source_data_summary": analysis_data["summary"]
            }, indent=2)
        else:
            return write_result
            
    except Exception as e:
        return json.dumps({"error": f"Failed to create summary report: {str(e)}"})

# Create the spreadsheet agent
spreadsheet_agent = Agent(
    name="Spreadsheet Assistant",
    instructions="""You are a helpful assistant that specializes in working with Google Sheets.

You can help users:
- Read and analyze data from Google Sheets
- Write and update data in sheets
- Create summary reports and insights
- Manage sheet data efficiently

When working with spreadsheets:
1. Always ask for the spreadsheet ID (found in the Google Sheets URL)
2. Confirm the sheet name (tab) they want to work with
3. Be specific about ranges (e.g., A1:E10, A:C, etc.)
4. Provide clear explanations of what operations you're performing
5. Handle errors gracefully and suggest solutions

For data analysis, offer insights such as:
- Data summaries and statistics
- Trends and patterns
- Data quality observations
- Recommendations for data organization

Remember to be helpful, accurate, and clear in your responses.""",
    model="gpt-4",
    tools=[
        read_sheet_data,
        write_sheet_data,
        append_sheet_data,
        clear_sheet_range,
        analyze_sheet_data,
        create_summary_report
    ]
)

async def run_example_session():
    """Run an example session with the spreadsheet agent"""
    
    print("🔧 Google Sheets Agent - OpenAI Agents SDK Example")
    print("=" * 50)
    
    # Example spreadsheet ID (replace with your own)
    # This would typically come from user input
    example_spreadsheet_id = "your_spreadsheet_id_here"
    
    print(f"📊 Current session: {sheets_session.get_sheet_info()}")
    print()
    
    # Example interactions
    example_queries = [
        "Help me read data from my sales spreadsheet. The ID is '1abc123...' and I want to see the data in range A1:E10 from the 'Sales Data' sheet.",
        "Can you analyze the sales data I just showed you and give me a summary of trends?",
        "I need to add new sales records. Can you append this data: [['2024-01-15', 'Product A', '100', '50', '5000']] to my sales sheet?",
        "Create a summary report of my sales data and place it starting at column H."
    ]
    
    for i, query in enumerate(example_queries, 1):
        print(f"Example Query {i}:")
        print(f"User: {query}")
        print()
        
        with trace(f"Spreadsheet Query {i}"):
            try:
                # In a real scenario, you would replace the spreadsheet ID in the query
                if "1abc123..." in query:
                    print("⚠️  Note: Replace '1abc123...' with your actual Google Sheets ID")
                    print("   (This is just an example - the agent would handle real data)")
                    print()
                
                # For demonstration, we'll show what the agent would do
                result = await Runner.run(
                    spreadsheet_agent, 
                    query,
                    run_config=RunConfig(
                        tracing_enabled=True,
                        metadata={"query_type": "spreadsheet_operation"}
                    )
                )
                
                print("🤖 Agent Response:")
                print(result.final_output)
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                print("   This is expected in the demo since we're using placeholder data")
        
        print("-" * 50)
        print()

def run_interactive_session():
    """Run an interactive session with the spreadsheet agent"""
    
    print("🔧 Interactive Google Sheets Agent")
    print("=" * 40)
    print()
    print("Instructions:")
    print("1. Make sure you have credentials.json in this directory")
    print("2. Share your Google Sheets with the service account email")
    print("3. Get your spreadsheet ID from the URL")
    print("4. Type 'quit' to exit")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print()
            print("🤖 Processing...")
            
            with trace("Interactive Spreadsheet Query"):
                result = Runner.run_sync(
                    spreadsheet_agent,
                    user_input,
                    run_config=RunConfig(
                        tracing_enabled=True,
                        metadata={"session_type": "interactive"}
                    )
                )
                
                print("🤖 Agent:")
                print(result.final_output)
                print()
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print()

if __name__ == "__main__":
    print("🚀 Google Sheets Agent with OpenAI Agents SDK")
    print("=" * 50)
    print()
    
    # Check for credentials
    if not os.path.exists(CREDENTIALS_FILE):
        print("⚠️  Setup Required:")
        print("1. Download credentials.json from Google Cloud Platform")
        print("2. Place it in this directory")
        print("3. Share your Google Sheets with the service account email")
        print()
        print("See the comments at the top of this file for detailed setup instructions.")
        exit(1)
    
    print("Choose an option:")
    print("1. Run example session (demo)")
    print("2. Run interactive session")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(run_example_session())
    elif choice == "2":
        run_interactive_session()
    else:
        print("Invalid choice. Running example session...")
        asyncio.run(run_example_session())

---
./notebooks/8.0-multi-agents-automation-system.ipynb
---
{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "2fb11956",
   "metadata": {},
   "source": [
    "# Let's Build a Multi Agent Example Live!"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}


---
./notebooks/9.0-router-pattern.ipynb
---
{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Outline generated\n",
      "Outline is not a scifi story, so we stop here.\n",
      "Outline is good quality and a scifi story, so we continue to write the story.\n"
     ]
    },
    {
     "ename": "",
     "evalue": "",
     "output_type": "error",
     "traceback": [
      "\u001b[1;31mCannot execute code, session has been disposed. Please try restarting the Kernel."
     ]
    },
    {
     "ename": "",
     "evalue": "",
     "output_type": "error",
     "traceback": [
      "\u001b[1;31mThe Kernel crashed while executing code in the the current cell or a previous cell. Please review the code in the cell(s) to identify a possible cause of the failure. Click <a href='https://aka.ms/vscodeJupyterKernelCrash'>here</a> for more info. View Jupyter <a href='command:jupyter.viewOutput'>log</a> for further details."
     ]
    }
   ],
   "source": [
    "import asyncio\n",
    "import nest_asyncio\n",
    "nest_asyncio.apply()\n",
    "\n",
    "from pydantic import BaseModel\n",
    "from agents import Agent, Runner, trace\n",
    "\n",
    "\"\"\"\n",
    "This example demonstrates a deterministic flow, where each step is performed by an agent.\n",
    "1. The first agent generates a story outline\n",
    "2. We feed the outline into the second agent\n",
    "3. The second agent checks if the outline is good quality and if it is a scifi story\n",
    "4. If the outline is not good quality or not a scifi story, we stop here\n",
    "5. If the outline is good quality and a scifi story, we feed the outline into the third agent\n",
    "6. The third agent writes the story\n",
    "\"\"\"\n",
    "\n",
    "story_outline_agent = Agent(\n",
    "    name=\"story_outline_agent\",\n",
    "    instructions=\"Generate a very short story outline based on the user's input.\",\n",
    ")\n",
    "\n",
    "\n",
    "class OutlineCheckerOutput(BaseModel):\n",
    "    good_quality: bool\n",
    "    is_scifi: bool\n",
    "\n",
    "\n",
    "outline_checker_agent = Agent(\n",
    "    name=\"outline_checker_agent\",\n",
    "    instructions=\"Read the given story outline, and judge the quality. Also, determine if it is a scifi story.\",\n",
    "    output_type=OutlineCheckerOutput,\n",
    ")\n",
    "\n",
    "story_agent = Agent(\n",
    "    name=\"story_agent\",\n",
    "    instructions=\"Write a short story based on the given outline.\",\n",
    "    output_type=str,\n",
    ")\n",
    "\n",
    "\n",
    "input_prompt = input(\"What kind of story do you want? \")\n",
    "\n",
    "# Ensure the entire workflow is a single trace\n",
    "with trace(\"Deterministic story flow\"):\n",
    "    # 1. Generate an outline\n",
    "    outline_result = await Runner.run(\n",
    "        story_outline_agent,\n",
    "        input_prompt,\n",
    "    )\n",
    "    print(\"Outline generated\")\n",
    "\n",
    "    # 2. Check the outline\n",
    "    outline_checker_result = await Runner.run(\n",
    "        outline_checker_agent,\n",
    "        outline_result.final_output,\n",
    "    )\n",
    "\n",
    "    # 3. Add a gate to stop if the outline is not good quality or not a scifi story\n",
    "    assert isinstance(outline_checker_result.final_output, OutlineCheckerOutput)\n",
    "    if not outline_checker_result.final_output.good_quality:\n",
    "        print(\"Outline is not good quality, so we stop here.\")\n",
    "        exit(0)\n",
    "\n",
    "    if not outline_checker_result.final_output.is_scifi:\n",
    "        print(\"Outline is not a scifi story, so we stop here.\")\n",
    "        exit(0)\n",
    "\n",
    "    print(\"Outline is good quality and a scifi story, so we continue to write the story.\")\n",
    "\n",
    "    # 4. Write the story\n",
    "    story_result = await Runner.run(\n",
    "        story_agent,\n",
    "        outline_result.final_output,\n",
    "    )\n",
    "    print(f\"Story: {story_result.final_output}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}


---
./presentation/presentation.html
---
<!DOCTYPE html>
<html>
  <head>
    <title>Getting Started with OpenAI Agents SDK</title>
    <meta charset="utf-8">
    <style>
      @import url(https://fonts.googleapis.com/css?family=Yanone+Kaffeesatz);
      @import url(https://fonts.googleapis.com/css?family=Droid+Serif:400,700,400italic);
      @import url(https://fonts.googleapis.com/css?family=Ubuntu+Mono:400,700,400italic);

      body { font-family: 'Droid Serif'; }
      h1, h2, h3 {
        font-family: 'Yanone Kaffeesatz';
        font-weight: normal;
      }
      .remark-code, .remark-inline-code { font-family: 'Ubuntu Mono'; }
    </style>
  </head>
  <body>
    <textarea id="source">

class: center, middle, inverse

# Getting Started with OpenAI Agents SDK

## Lucas Soares

### 08/27/2025

.footnote[O'Reilly Live Training]

---

# Agenda

1. **Evolution: From LLMs to Agents**

--

2. **OpenAI Agents SDK Core Concepts**

--

3. **Building Your First Agent**

--

4. **Tools & Function Calling**

--

5. **MCP (Model Context Protocol) Tools**

--

6. **Handoffs, Tracing & Context**

--

7. **Guardrails & Multi-Agent Systems**

--

8. **Hands-on Demo & Q&A**

---

class: inverse, center, middle

# From LLMs to Agents

### Understanding the Evolution

---

class: center, middle

# LLMs vs Agents

<div style="text-align: center;">
  <img src="../assets/llm-vs-agent.png" alt="LLM vs Agent Comparison" style="width: 70%;">
</div>

---

# Key Differences

## LLMs: Text Generation
- Input text → Process → Output text
- Stateless operations
- No external interactions

## Agents: Action & Decision Making
- Perceive → Decide → Act → Learn
- Maintain state across interactions
- Use tools to interact with world

.footnote[Source: [OpenAI Agents Documentation](https://openai.github.io/openai-agents-python/)]

---

# Why Agents Matter

<div style="display: flex; align-items: center; gap: 20px;">
  <div style="flex: 1;">
    <h3>Capabilities</h3>
    <ul>
      <li>Use tools & APIs</li>
      <li>Make decisions</li>
      <li>Complete workflows</li>
      <li>Maintain state</li>
    </ul>
  </div>
  <div style="flex: 1;">
    <h3>Impact</h3>
    <ul>
      <li>Task automation</li>
      <li>Real-time data access</li>
      <li>Error handling</li>
      <li>Adaptive behavior</li>
    </ul>
  </div>
</div>

> "Agents transform AI from conversational to operational"

---

class: inverse, center, middle

# OpenAI Agents SDK

### Core Architecture & Concepts

---
class: center, middle

<div style="text-align: center;">
  <img src="../assets/sdk-architecture.png" alt="SDK Architecture" style="width: 50%;">
</div>

---

# Core Components

- **Agent**

  - The intelligent core with instructions and model

--

- **Tools  **

  - External capabilities (functions, APIs, other agents)

--

- **Runner**

  - Execution engine for agent interactions

--

- **Context**

  - State management across runs

.footnote[Source: [SDK Quickstart Guide](https://openai.github.io/openai-agents-python/quickstart/)]

---

# Three Essential Patterns

## 1. Basic Agent Creation
```python
from agents import Agent

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    model="gpt-4o-mini"
)
```

## 2. Tool Definition
```python
from agents import function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get weather for a city"""
    return f"Weather data for {city}"
```

---

# Three Essential Patterns (cont.)

## 3. Execution Methods

### Synchronous
```python
result = Runner.run_sync(agent, "Hello")
```

### Asynchronous
```python
result = await Runner.run(agent, "Hello")
```

### Streaming
```python
async for event in Runner.run_streamed(agent, "Hello"):
    print(event.delta, end="")
```

.footnote[Source: [Running Agents Guide](https://openai.github.io/openai-agents-python/running/)]

---

class: inverse, center, middle

# Building Agents

### From Simple to Complex

---

# Your First Agent

```python
from agents import Agent, Runner

# Create an agent
agent = Agent(
    name="MyFirstAgent",
    instructions="You are a helpful assistant",
    model="gpt-4o-mini"  # Cost-effective model
)

# Run synchronously
result = Runner.run_sync(
    agent, 
    "Write a haiku about recursion"
)

print(result.final_output)
```

Output:
```
Recursion calls itself,
Depth within depth, it descends—
Base case brings it home.
```

---

class: center, middle

<h1>
<span style="background-color: lightgreen">
 Demo: Building Your First Agent
</span>
</h1>

---

class: inverse, center, middle

# Tools & Functions

### Extending Agent Capabilities

---

## Built-in Tools
```python
from agents.tools import WebSearchTool, FileSearchTool

web_tool = WebSearchTool(
    user_location={"type": "approximate", "city": "NYC"}
)
```

## Custom Function Tools
```python
@function_tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression"""
    return str(eval(expression))
```

## When to Use Each
- **Built-in**: For common tasks (web search, file ops)
- **Custom**: For domain-specific logic

---

# Complete Tool Example

```python
from agents import Agent, Runner, function_tool
from datetime import datetime

@function_tool
def get_current_time(timezone: str = "UTC") -> str:
    """Get current time in specified timezone"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@function_tool
def calculate_days(date1: str, date2: str) -> int:
    """Calculate days between two dates"""
    # Implementation here
    return days_difference

agent = Agent(
    name="TimeKeeper",
    instructions="Help with time and date queries",
    tools=[get_current_time, calculate_days]
)
```

.footnote[Source: [Tools Documentation](https://openai.github.io/openai-agents-python/tools/)]

---
# Structured Outputs

## Using Pydantic Models

```python
from pydantic import BaseModel
from agents import Agent, Runner

class UserInfo(BaseModel):
    name: str
    age: int
    interests: list[str]

agent = Agent(
    name="DataCollector",
    instructions="Extract user information",
    model="gpt-4o-mini",
    output_type=UserInfo  # Structured output
)

result = Runner.run_sync(agent, 
    "John is 25 and likes coding and hiking")
# result.final_output is now a UserInfo instance
```

.footnote[Source: [Agents Guide](https://openai.github.io/openai-agents-python/agents/)]

---

class: inverse, center, middle

# MCP Tools

### Model Context Protocol Integration

---

# What is MCP?

## Model Context Protocol
- **Open protocol** for connecting AI systems to data sources
- **Standardized interface** for tool integration
- **Secure context sharing** between applications

## Why MCP with Agents?
- Access **local and remote resources** seamlessly
- **Unified tool interface** across different systems
- **Production-ready integrations** out of the box

> "MCP bridges the gap between AI agents and real-world systems"

.footnote[Source: [MCP Documentation](https://openai.github.io/openai-agents-python/mcp/)]

---

# MCP Architecture

<div style="display: flex; gap: 40px; justify-content: center;">
  <div>
    <h3>Components</h3>
    <ul>
      <li><strong>MCP Servers</strong> - Expose resources</li>
      <li><strong>MCP Clients</strong> - Consume resources</li>
      <li><strong>Transport Layer</strong> - Communication</li>
    </ul>
  </div>
  <div>
    <h3>Resource Types</h3>
    <ul>
      <li>Tools (functions)</li>
      <li>Resources (data)</li>
      <li>Prompts (templates)</li>
    </ul>
  </div>
</div>

```python
from agents import Agent
from agents.tools import MCPServerStdio

# Connect to MCP server
mcp_server = MCPServerStdio(
    command="uvx",
    args=["mcp-server-filesystem", "/Users/data"]
)

agent = Agent(
    name="FileAgent",
    tools=[mcp_server]  # MCP as a tool source
)
```

---

# Using MCP Tools

## Standard I/O Server
```python
from agents.tools import MCPServerStdio

# Filesystem access via MCP
fs_server = MCPServerStdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/home"]
)
```

## Streamable HTTP
```python
from agents.tools import MCPServerStreamableHttp

# Server-sent events connection
sse_server = MCPServerStreamableHttp(
    url="http://localhost:8080/mcp"
)
```

---

## Examples of Available MCP Servers
- `mcp-server-filesystem` - File operations
- `mcp-server-git` - Git repository access
- `mcp-server-github` - GitHub API integration
- `mcp-server-sqlite` - Database operations

---

# Complete MCP Example

```python
from agents import Agent, Runner
from agents.tools import MCPServerStdio

# Setup MCP server for Git operations
git_server = MCPServerStdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-git", 
          "--repository", "/path/to/repo"]
)

# Create agent with MCP tools
agent = Agent(
    name="GitExpert",
    instructions="Help with git repository analysis",
    model="gpt-4o-mini",
    tools=[git_server]  # MCP provides multiple tools
)

# Use the agent - MCP tools are auto-discovered
result = Runner.run_sync(
    agent, 
    "Show me recent commits and their authors"
)
print(result.final_output)
```

.footnote[Source: [MCP Integration Guide](https://openai.github.io/openai-agents-python/mcp/)]

---

class: center, middle

# <h1><span style="background-color: lightgreen">Demo: Building a Simple Research Agent</span></h1>

---

class: inverse, center, middle

# Handoffs, Tracing & Context

### Building Stateful Agent Workflows

---

# Agent Handoffs

## Delegating to Specialized Agents

<div style="text-align: center;">
  <img src="../assets/agent-handoffs.png" alt="Agent Handoffs Workflow" style="width: 80%;">
</div>

---

# Handoffs

**Key Benefits:**
- **Specialization** - Each agent focuses on specific expertise
- **Scalability** - Add new specialists without changing core logic  
- **Flexibility** - Dynamic routing based on query analysis

---

```python
from agents import Agent

# Specialized agents
spanish_agent = Agent(
    name="SpanishExpert",
    instructions="You only speak Spanish. Help Spanish speakers."
)

technical_agent = Agent(
    name="TechnicalExpert",
    instructions="You handle technical support queries."
)

# Router agent with handoffs
router_agent = Agent(
    name="Router",
    instructions="Route queries to the appropriate specialist",
    handoffs=[spanish_agent, technical_agent]
)
```

.footnote[Source: [Handoffs Documentation](https://openai.github.io/openai-agents-python/handoffs/)]

---

# Tracing Agent Workflows

## Monitoring Complex Operations

<div style="text-align: center;">
  <img src="../assets/agent-tracing.png" alt="Agent Tracing Visualization" style="width: 50%;">
</div>

---

# Tracing

**Tracing Benefits:**
- **Debugging** - See exact execution path and timing
- **Performance** - Identify bottlenecks in agent workflows
- **Monitoring** - Track success/failure patterns

```python
from agents import trace, set_tracing_disabled

# Group related operations with tracing
async def process_customer_request(query: str):
    with trace("customer_workflow"):
        # Initial analysis
        with trace("analyze"):
            analysis = await Runner.run(analyzer_agent, query)
        
        # Route to specialist
        with trace("route"):
            response = await Runner.run(router_agent, analysis)
        
        # Format final response
        with trace("format"):
            final = await Runner.run(formatter_agent, response)
        
        return final

# Disable tracing in production
set_tracing_disabled(True)
```

.footnote[Source: [Tracing Guide](https://openai.github.io/openai-agents-python/tracing/)]

---

# Context Management

## Maintaining State Across Runs

<div style="text-align: center;">
  <img src="../assets/context-management.png" alt="Context Management Architecture" style="width: 50%;">
</div>

---

# Context Management

**Context Capabilities:**
- **Persistent Memory** - Maintain state between agent runs
- **User Sessions** - Track individual user interactions
- **Shared Data** - Access context across multiple tools

---

```python
from agents import RunContextWrapper, function_tool

class UserSession:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.history = []
        self.preferences = {}

@function_tool
async def get_user_history(
    ctx: RunContextWrapper[UserSession]
) -> str:
    session = ctx.context
    return f"User {session.user_id} has {len(session.history)} messages"

@function_tool
async def update_preferences(
    ctx: RunContextWrapper[UserSession],
    key: str, 
    value: str
) -> str:
    ctx.context.preferences[key] = value
    return f"Updated preference: {key}={value}"
```

---

class: center, middle

# <h1><span style="background-color: lightgreen">Demo: Building a Spreadsheet Agent</span></h1>

---

class: inverse, center, middle

# Guardrails & Multi-Agent Systems

### Safe and Scalable Agent Architectures

---

# Guardrails

## Ensuring Safe Agent Behavior

<div style="text-align: center;">
  <img src="../assets/agent-guardrails.png" alt="Agent Guardrails Security" style="width: 50%;">
</div>

---
# Guardrails

**Security Layers:**
- **Input Validation** - Filter dangerous or malformed inputs
- **Output Sanitization** - Remove sensitive information from responses
- **Rate Limiting** - Prevent abuse and resource exhaustion

---

```python
from agents import input_guardrail, output_guardrail

@input_guardrail
async def validate_spreadsheet_input(ctx, agent, input_data):
    # Check for malicious formulas
    if "=cmd" in input_data.lower() or "=shell" in input_data.lower():
        raise ValueError("Potentially dangerous formula detected")
    
    # Validate data size
    if len(input_data) > 10000:
        raise ValueError("Input data too large")

@output_guardrail  
async def sanitize_output(ctx, agent, output):
    # Remove any sensitive patterns
    import re
    output = re.sub(r'password["\']?\s*[:=]\s*["\']?[\w]+', 'password=***', output)
    return output

secure_agent = Agent(
    name="SecureSpreadsheetAgent",
    input_guardrails=[validate_spreadsheet_input],
    output_guardrails=[sanitize_output]
)
```

.footnote[Source: [Guardrails Documentation](https://openai.github.io/openai-agents-python/guardrails/)]

---

# Multi-Agent Architecture

## Orchestrating Complex Workflows

<div style="text-align: center;">
  <img src="../assets/multi-agent-systems.png" alt="Multi-Agent System Architecture" style="width: 50%;">
</div>

---

# Multi-Agent Architecture

## Architecture Benefits:
- **Specialization** - Each agent excels at specific tasks
- **Coordination** - Central orchestration prevents chaos
- **Scalability** - Add agents without changing core logic

---
# Multi-Agent Architecture

```python
from agents import Agent, Runner

# Research agent
research_agent = Agent(
    name="Researcher",
    instructions="Research topics thoroughly using web search",
    tools=[WebSearchTool()]
)

# Coding agent
coding_agent = Agent(
    name="Coder",
    instructions="Write clean, well-documented code",
    model="gpt-4o"
)

# Coordinator agent
coordinator = Agent(
    name="Coordinator",
    instructions="""
    Coordinate research and coding tasks:
    1. Use researcher for gathering information
    2. Use coder for implementation
    3. Ensure quality and completeness
    """,
    handoffs=[research_agent, coding_agent]
)
```

---

# Scaling Best Practices

<div style="display: flex; gap: 40px; justify-content: center;">
  <div style="flex: 1; min-width: 220px;">
    <h3>Architecture</h3>
    <ul>
      <li>Single coordinator pattern</li>
      <li>Clear agent responsibilities</li>
      <li>Minimal handoff chains</li>
      <li>Stateless when possible</li>
    </ul>
  </div>
  <div style="flex: 1; min-width: 220px;">
    <h3>Safety</h3>
    <ul>
      <li>Input validation at entry</li>
      <li>Output sanitization</li>
      <li>Rate limiting</li>
      <li>Timeout controls</li>
    </ul>
  </div>
</div>

```python
# Production multi-agent setup
coordinator = Agent(
    name="SafeCoordinator",
    instructions="Coordinate safely with timeouts",
    handoffs=[agent1, agent2],
    input_guardrails=[validate_input],
    output_guardrails=[sanitize_output]
)

# Run with timeout
result = await Runner.run(coordinator, query, timeout=60)
```

.footnote[Source: [Multi-Agent Systems](https://openai.github.io/openai-agents-python/multi_agent/)]

---

class: center, middle

# <h1><span style="background-color: lightgreen">Demo: Building a Multi-Agent System for Research and Coding</span></h1>

---

class: inverse, center, middle

# Key Takeaways

---

# Your Learning Journey

<div style="text-align: center;">
  <img src="../assets/journey-map.png" alt="Journey Map" style="width: 50%;">
</div>

✅ **Agents add actions** to language models

✅ **SDK provides** production-ready patterns

✅ **Start simple**, add complexity gradually

✅ **Tools unlock** real-world integration

---

# Connect With Me

## 📚 [Course materials]()
## 🔗 [LinkedIn](https://www.linkedin.com/in/lucas-soares-969044167/)
## 🐦 [Twitter/X - @LucasEnkrateia](https://x.com/LucasEnkrateia)
## 📺 [YouTube - @automatalearninglab](https://www.youtube.com/@automatalearninglab)
## 📧 Email: lucasenkrateia@gmail.com

---

# Resources & Documentation

### Official Documentation
- [OpenAI Agents Python SDK](https://openai.github.io/openai-agents-python/)
- [Quickstart Guide](https://openai.github.io/openai-agents-python/quickstart/)
- [API Reference](https://openai.github.io/openai-agents-python/ref/)

### Practical Resources
- [Building Agents Manual (PDF)](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
- [GitHub Examples](https://github.com/openai/openai-agents-python/tree/main/examples)
- [Model Selection Guide](https://cookbook.openai.com/examples/partners/model_selection_guide/model_selection_guide)

### Video Tutorials
- [Building Agents Tutorial](https://youtu.be/35nxORG1mtg)
- [Architecture Deep Dive](https://www.youtube.com/watch?v=-rsTkYgnNzM)

---

class: center, middle, inverse

# Thank You!

## Start Building Today

```bash
pip install openai-agents
```

### Questions?

#### Contact & Community
[GitHub Discussions](https://github.com/openai/openai-agents-python) | [Documentation](https://openai.github.io/openai-agents-python/)

    </textarea>
    <script src="https://remarkjs.com/downloads/remark-latest.min.js">
    </script>
    <script>
      var slideshow = remark.create();
    </script>
  </body>
</html>

---
