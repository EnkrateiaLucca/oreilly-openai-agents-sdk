from agents import Agent, Runner, WebSearchTool, function_tool
import asyncio

@function_tool
def read_file(file_path: str) -> str:
    """Reads the content of a text file and returns it as a string."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

@function_tool
def write_file(file_path: str, content: str) -> str:
    """Writes the provided content into a text file."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return "File written successfully."
    except Exception as e:
        return f"Error writing file: {e}"

agent = Agent(
    name="Personal Assistant",
    instructions="You are a helpful assistant that can answer questions and help with tasks.",
    model="gpt-5.4-mini",
    tools=[read_file, write_file, WebSearchTool()]
)

async def main():
    result = await Runner.run(agent, """
                              Can you:
                              1) Search the web for a Reddit thread about a decision framework for choosing an agent framework (e.g., OpenAI Agents SDK, Claude Agents SDK, LangGraph, etc.).
                              2) Summarize the framework and key decision criteria.
                              3) Save the results locally as a `.md` file in this directory.
                              """)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())