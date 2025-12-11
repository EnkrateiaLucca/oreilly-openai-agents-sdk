"""
Custom Agents Examples for OpenAI Agents SDK Course
====================================================

This package contains four practical agent examples demonstrating
real-world applications of the OpenAI Agents SDK:

1. research_agent.py - Personal Research & Summarization Agent
   - Web search with WebSearchTool
   - Structured outputs (ResearchSummary model)
   - Save notes to files

2. filesystem_agent.py - File System Automation Agent
   - Local file operations (safe, with dry-run)
   - File categorization and organization
   - Cleanup reports

3. data_dashboard_agent.py - Personal Data Dashboard Agent
   - CSV/Excel analysis with pandas
   - Anomaly detection (outliers, missing data)
   - Chart generation with matplotlib

4. content_pipeline_agent.py - Content Production Pipeline Agent
   - Multi-format content generation
   - YouTube, TikTok, Newsletter outputs
   - Title variations and SEO

Usage:
    from scripts.custom_agents import run_research_agent
    result = run_research_agent("LLM context windows")
    print(result.summary)

Run individual agents:
    python -m scripts.custom_agents.research_agent
    python -m scripts.custom_agents.filesystem_agent
    python -m scripts.custom_agents.data_dashboard_agent
    python -m scripts.custom_agents.content_pipeline_agent
"""

from .research_agent import run_research_agent, research_agent, ResearchSummary
from .filesystem_agent import run_filesystem_agent, filesystem_agent, CleanupReport
from .data_dashboard_agent import run_data_dashboard_agent, dashboard_agent, DataAnalysisReport
from .content_pipeline_agent import run_content_pipeline_agent, content_pipeline_agent, ContentPackage

__all__ = [
    # Main runner functions
    "run_research_agent",
    "run_filesystem_agent",
    "run_data_dashboard_agent",
    "run_content_pipeline_agent",
    # Agent objects (for advanced use)
    "research_agent",
    "filesystem_agent",
    "dashboard_agent",
    "content_pipeline_agent",
    # Output models (for type hints)
    "ResearchSummary",
    "CleanupReport",
    "DataAnalysisReport",
    "ContentPackage"
]
