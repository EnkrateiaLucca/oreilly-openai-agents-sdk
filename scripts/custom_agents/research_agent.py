"""
Personal Research & Summarization Agent
========================================

An agent that:
- Accepts a topic (e.g., "LLM context windows", "productivity apps")
- Uses web search to gather information
- Produces a structured summary: key points, citations, open questions
- Optionally saves results to a notes file

Demonstrates:
- WebSearchTool for real-time information retrieval
- Structured output with Pydantic models
- File saving with @function_tool
- Clear, source-aware research summaries
"""

import os
import json
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# Apply nest_asyncio for Jupyter notebook compatibility
import nest_asyncio
nest_asyncio.apply()

from agents import Agent, Runner, function_tool, WebSearchTool


# ============================================
# Structured Output Models
# ============================================

class Citation(BaseModel):
    """A source citation from the research."""
    title: str = Field(description="Title of the source")
    url: str = Field(description="URL of the source")
    snippet: str = Field(description="Relevant snippet from the source")


class ResearchSummary(BaseModel):
    """Structured research output with key findings and citations."""
    topic: str = Field(description="The research topic")
    key_points: List[str] = Field(
        description="3-5 main findings or key points from the research"
    )
    citations: List[Citation] = Field(
        description="List of sources used in the research"
    )
    open_questions: List[str] = Field(
        description="Unanswered questions or areas needing more research"
    )
    summary: str = Field(
        description="A 2-3 sentence executive summary of the findings"
    )


# ============================================
# Tools
# ============================================

@function_tool
def save_research_notes(
    topic: str,
    content: str,
    output_dir: str = "./research_notes"
) -> str:
    """
    Save research notes to a markdown file.

    Args:
        topic: The research topic (used for filename)
        content: The formatted research content to save
        output_dir: Directory to save notes (default: ./research_notes)

    Returns:
        Path to the saved file or error message
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Create a safe filename from the topic
        safe_topic = "".join(c if c.isalnum() or c in " -_" else "_" for c in topic)
        safe_topic = safe_topic.replace(" ", "_")[:50]

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_topic}_{timestamp}.md"
        filepath = os.path.join(output_dir, filename)

        # Write the content
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Research Notes: {topic}\n\n")
            f.write(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write("---\n\n")
            f.write(content)

        return f"Successfully saved research notes to: {filepath}"

    except Exception as e:
        return f"Error saving notes: {str(e)}"


@function_tool
def format_research_for_saving(
    topic: str,
    key_points_json: str,
    citations_json: str,
    open_questions_json: str,
    summary: str
) -> str:
    """
    Format research findings into a markdown document.

    Args:
        topic: The research topic
        key_points_json: JSON array of key findings (e.g., '["point 1", "point 2"]')
        citations_json: JSON array of citation objects with title, url, snippet
        open_questions_json: JSON array of unanswered questions
        summary: Executive summary

    Returns:
        Formatted markdown string
    """
    # Parse JSON inputs
    try:
        key_points = json.loads(key_points_json) if key_points_json else []
        citations = json.loads(citations_json) if citations_json else []
        open_questions = json.loads(open_questions_json) if open_questions_json else []
    except json.JSONDecodeError as e:
        return f"Error parsing JSON input: {str(e)}"

    md_content = []

    # Executive Summary
    md_content.append("## Executive Summary\n")
    md_content.append(f"{summary}\n")

    # Key Points
    md_content.append("\n## Key Findings\n")
    for i, point in enumerate(key_points, 1):
        md_content.append(f"{i}. {point}\n")

    # Citations
    md_content.append("\n## Sources\n")
    for citation in citations:
        if isinstance(citation, dict):
            title = citation.get("title", "Unknown")
            url = citation.get("url", "#")
            snippet = citation.get("snippet", "")
            md_content.append(f"- **[{title}]({url})**\n")
            if snippet:
                md_content.append(f"  > {snippet}\n")

    # Open Questions
    md_content.append("\n## Open Questions\n")
    for question in open_questions:
        md_content.append(f"- {question}\n")

    return "\n".join(md_content)


# ============================================
# Agent Definition
# ============================================

research_agent = Agent(
    name="Research Assistant",
    instructions="""You are a thorough research assistant that helps users
    gather information on any topic.

    Your research process:
    1. Use web search to find current, relevant information on the topic
    2. Identify 3-5 key findings or important points
    3. Note all sources with proper citations
    4. Identify gaps or questions that need further research
    5. Provide a concise executive summary

    Guidelines:
    - Focus on recent, credible sources
    - Be objective and balanced in your analysis
    - Clearly distinguish between facts and opinions
    - Always cite your sources
    - Highlight areas where information is uncertain or conflicting

    When asked to save notes, use the format_research_for_saving tool first,
    then use save_research_notes with the formatted content.
    """,
    model="gpt-4o-mini",
    tools=[
        WebSearchTool(),
        save_research_notes,
        format_research_for_saving
    ],
    output_type=ResearchSummary  # Enforce structured output
)


# ============================================
# Main Function
# ============================================

def run_research_agent(
    topic: str,
    save_notes: bool = False,
    output_dir: str = "./research_notes"
) -> ResearchSummary:
    """
    Run the research agent on a given topic.

    Args:
        topic: The topic to research
        save_notes: Whether to save the results to a file
        output_dir: Directory to save notes if save_notes is True

    Returns:
        ResearchSummary with structured findings

    Example:
        >>> result = run_research_agent("LLM context windows")
        >>> print(result.summary)
        >>> for point in result.key_points:
        ...     print(f"- {point}")
    """
    # Build the query
    query = f"Research the following topic and provide comprehensive findings: {topic}"

    if save_notes:
        query += f"\n\nAfter completing the research, save the notes to the '{output_dir}' directory."

    # Run the agent
    result = Runner.run_sync(research_agent, query)

    return result.final_output


# ============================================
# Interactive Demo
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Personal Research & Summarization Agent")
    print("=" * 60)

    # Example topics
    example_topics = [
        "LLM context windows and their limitations",
        "Best productivity apps for time blocking in 2024",
        "Latest developments in AI agents"
    ]

    # Run research on the first topic
    topic = example_topics[0]
    print(f"\nResearching: {topic}")
    print("-" * 40)

    result = run_research_agent(topic, save_notes=True)

    # Display results
    print(f"\n📋 Topic: {result.topic}")
    print(f"\n📝 Summary:\n{result.summary}")

    print(f"\n🔑 Key Points:")
    for i, point in enumerate(result.key_points, 1):
        print(f"  {i}. {point}")

    print(f"\n📚 Citations:")
    for citation in result.citations:
        print(f"  - {citation.title}")
        print(f"    URL: {citation.url}")

    print(f"\n❓ Open Questions:")
    for question in result.open_questions:
        print(f"  - {question}")

    print("\n" + "=" * 60)
    print("Research complete!")
