"""
Content Production Pipeline Agent
==================================

An agent that:
- Takes a long transcript, notes, or ideas as input
- Generates multiple content formats:
  - YouTube description
  - Short-form script (TikTok/Reels/Shorts)
  - Newsletter summary
  - Title variations
- Saves outputs to disk

Demonstrates:
- Multi-output content generation
- Structured outputs with Pydantic
- Template-based content creation
- File saving workflows

Perfect for content creators who want to repurpose one piece
of content across multiple platforms.
"""

import os
import json
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

import nest_asyncio
nest_asyncio.apply()

from agents import Agent, Runner, function_tool


# ============================================
# Structured Output Models
# ============================================

class TitleVariation(BaseModel):
    """A title variation with its style."""
    title: str = Field(description="The title text")
    style: str = Field(description="Style: curiosity, benefit, how-to, listicle, controversial")


class YouTubeDescription(BaseModel):
    """YouTube video description content."""
    hook: str = Field(description="Attention-grabbing first line")
    summary: str = Field(description="2-3 paragraph summary of the content")
    timestamps: List[str] = Field(description="Key timestamps (e.g., '0:00 - Introduction')")
    call_to_action: str = Field(description="Subscribe/like/comment CTA")
    hashtags: List[str] = Field(description="Relevant hashtags")


class ShortFormScript(BaseModel):
    """Script for short-form content (60 seconds)."""
    hook: str = Field(description="First 3 seconds - attention grabber")
    body: str = Field(description="Main content (40-50 seconds)")
    call_to_action: str = Field(description="End with CTA (5-10 seconds)")
    visual_notes: List[str] = Field(description="Suggested visuals/b-roll")
    estimated_duration: str = Field(description="Estimated duration in seconds")


class NewsletterSummary(BaseModel):
    """Newsletter/email summary content."""
    subject_line: str = Field(description="Email subject line")
    preview_text: str = Field(description="Email preview text (40-90 chars)")
    introduction: str = Field(description="Opening paragraph")
    key_takeaways: List[str] = Field(description="3-5 bullet point takeaways")
    conclusion: str = Field(description="Closing paragraph with CTA")


class ContentPackage(BaseModel):
    """Complete content package from source material."""
    source_summary: str = Field(description="Brief summary of the original content")
    title_variations: List[TitleVariation] = Field(description="5 title options")
    youtube_description: YouTubeDescription = Field(description="YouTube description")
    short_form_script: ShortFormScript = Field(description="TikTok/Reels script")
    newsletter: NewsletterSummary = Field(description="Newsletter summary")
    content_themes: List[str] = Field(description="Main themes/topics covered")


# ============================================
# Tools
# ============================================

@function_tool
def read_source_content(file_path: str) -> str:
    """
    Read source content from a file (transcript, notes, etc.).

    Args:
        file_path: Path to the source file (.txt, .md)

    Returns:
        The content of the file
    """
    try:
        file_path = os.path.expanduser(file_path)

        if not os.path.exists(file_path):
            return json.dumps({"error": f"File not found: {file_path}"})

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        word_count = len(content.split())

        return json.dumps({
            "file_path": file_path,
            "word_count": word_count,
            "content": content,
            "preview": content[:500] + "..." if len(content) > 500 else content
        })

    except Exception as e:
        return json.dumps({"error": f"Error reading file: {str(e)}"})


@function_tool
def save_content_package(
    output_dir: str,
    package_name: str,
    youtube_description: str,
    short_form_script: str,
    newsletter_content: str,
    titles: list
) -> str:
    """
    Save all generated content to organized files.

    Args:
        output_dir: Directory to save the content package
        package_name: Name for this content package (used in filenames)
        youtube_description: The YouTube description text
        short_form_script: The short-form video script
        newsletter_content: The newsletter/email content
        titles: List of title variations

    Returns:
        Summary of saved files
    """
    try:
        output_dir = os.path.expanduser(output_dir)
        os.makedirs(output_dir, exist_ok=True)

        # Sanitize package name for filenames
        safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in package_name)
        safe_name = safe_name.replace(" ", "_")[:30]

        timestamp = datetime.now().strftime("%Y%m%d")
        base_name = f"{safe_name}_{timestamp}"

        saved_files = []

        # Save YouTube description
        yt_path = os.path.join(output_dir, f"{base_name}_youtube.txt")
        with open(yt_path, 'w', encoding='utf-8') as f:
            f.write(youtube_description)
        saved_files.append(yt_path)

        # Save short-form script
        short_path = os.path.join(output_dir, f"{base_name}_shortform.txt")
        with open(short_path, 'w', encoding='utf-8') as f:
            f.write(short_form_script)
        saved_files.append(short_path)

        # Save newsletter
        news_path = os.path.join(output_dir, f"{base_name}_newsletter.txt")
        with open(news_path, 'w', encoding='utf-8') as f:
            f.write(newsletter_content)
        saved_files.append(news_path)

        # Save titles
        titles_path = os.path.join(output_dir, f"{base_name}_titles.txt")
        with open(titles_path, 'w', encoding='utf-8') as f:
            f.write("TITLE VARIATIONS\n")
            f.write("=" * 40 + "\n\n")
            for i, title in enumerate(titles, 1):
                if isinstance(title, dict):
                    f.write(f"{i}. [{title.get('style', 'general')}] {title.get('title', str(title))}\n")
                else:
                    f.write(f"{i}. {title}\n")
        saved_files.append(titles_path)

        # Create master file with everything
        master_path = os.path.join(output_dir, f"{base_name}_COMPLETE.md")
        with open(master_path, 'w', encoding='utf-8') as f:
            f.write(f"# Content Package: {package_name}\n\n")
            f.write(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write("---\n\n")

            f.write("## Title Variations\n\n")
            for i, title in enumerate(titles, 1):
                if isinstance(title, dict):
                    f.write(f"{i}. **[{title.get('style', 'general')}]** {title.get('title', str(title))}\n")
                else:
                    f.write(f"{i}. {title}\n")

            f.write("\n---\n\n")
            f.write("## YouTube Description\n\n")
            f.write(youtube_description)

            f.write("\n\n---\n\n")
            f.write("## Short-Form Script (TikTok/Reels/Shorts)\n\n")
            f.write(short_form_script)

            f.write("\n\n---\n\n")
            f.write("## Newsletter/Email\n\n")
            f.write(newsletter_content)

        saved_files.append(master_path)

        return json.dumps({
            "success": True,
            "output_dir": output_dir,
            "files_created": len(saved_files),
            "files": saved_files,
            "master_file": master_path
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error saving content: {str(e)}"})


@function_tool
def extract_key_points(content: str, max_points: int = 5) -> str:
    """
    Extract key points from content for quick reference.

    Args:
        content: The content to analyze
        max_points: Maximum number of key points to extract

    Returns:
        JSON with extracted key points
    """
    # This is a simple extraction - the LLM will enhance it
    words = content.split()
    word_count = len(words)

    # Find sentences (rough approximation)
    sentences = content.replace('\n', ' ').split('.')
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    return json.dumps({
        "word_count": word_count,
        "sentence_count": len(sentences),
        "estimated_read_time_minutes": round(word_count / 200, 1),
        "sample_sentences": sentences[:max_points] if sentences else [],
        "note": "Use these as starting points to identify key themes"
    }, indent=2)


# ============================================
# Agent Definition
# ============================================

content_pipeline_agent = Agent(
    name="Content Pipeline Producer",
    instructions="""You are an expert content repurposing specialist who
    transforms long-form content into multiple formats for different platforms.

    Your job is to take source content (transcripts, notes, articles) and create:

    1. **Title Variations** (5 options):
       - Curiosity-driven (makes people want to know more)
       - Benefit-focused (what will they learn/gain)
       - How-to style (practical/actionable)
       - Listicle format (numbers/lists)
       - Controversial/contrarian (challenges assumptions)

    2. **YouTube Description**:
       - Strong hook in first line (this shows in search)
       - 2-3 paragraph summary with keywords
       - Timestamps for key sections
       - Call to action for engagement
       - 5-10 relevant hashtags

    3. **Short-Form Script** (60 seconds):
       - Hook in first 3 seconds (pattern interrupt)
       - Deliver ONE main point in the body
       - Clear CTA at the end
       - Include visual/b-roll suggestions
       - Write for speaking, not reading

    4. **Newsletter Summary**:
       - Compelling subject line (under 50 chars)
       - Preview text that creates curiosity
       - Personal, conversational intro
       - 3-5 key takeaways as bullets
       - CTA to engage further

    Guidelines:
    - Maintain the original message and tone
    - Adapt language for each platform's audience
    - Keep short-form punchy and fast-paced
    - Make newsletter feel personal and valuable
    - Use keywords naturally for SEO
    - Focus on transformation and value

    When content is provided directly (not via file), analyze it and create
    the full content package.
    """,
    model="gpt-4o-mini",
    tools=[read_source_content, save_content_package, extract_key_points],
    output_type=ContentPackage
)


# ============================================
# Main Function
# ============================================

def run_content_pipeline_agent(
    content: str,
    content_name: str = "Content",
    save_to_disk: bool = True,
    output_dir: str = "./content_output"
) -> ContentPackage:
    """
    Run the content pipeline agent on source content.

    Args:
        content: The source content (transcript, notes, article) OR file path
        content_name: Name for this content (used in saved files)
        save_to_disk: Whether to save outputs to files
        output_dir: Directory for saved files

    Returns:
        ContentPackage with all generated content

    Example:
        >>> transcript = '''Today we're going to talk about...'''
        >>> result = run_content_pipeline_agent(transcript, "AI Tutorial")
        >>> print(result.youtube_description.hook)
        >>> for title in result.title_variations:
        ...     print(f"[{title.style}] {title.title}")
    """
    # Check if content is a file path
    if os.path.exists(os.path.expanduser(content)):
        query = f"Read the content from '{content}' and create a complete content package."
    else:
        query = f"""Create a complete content package from the following source content.

Content Name: {content_name}

SOURCE CONTENT:
{content}

Generate all content variations (titles, YouTube description, short-form script, newsletter).
"""

    if save_to_disk:
        query += f"\n\nAfter generating all content, save it to '{output_dir}' with package name '{content_name}'."

    result = Runner.run_sync(content_pipeline_agent, query)
    return result.final_output


# ============================================
# Demo
# ============================================

SAMPLE_TRANSCRIPT = """
Welcome back to the channel. Today I want to share the three biggest mistakes
I see people make when they're learning to code, and more importantly, how to
avoid them.

Mistake number one is tutorial hell. You know what I'm talking about - watching
tutorial after tutorial, course after course, but never actually building
anything yourself. The solution? After every tutorial, build something small
on your own. Even if it's just modifying what you learned, that's real learning.

Mistake number two is trying to learn everything at once. When I started, I was
trying to learn Python, JavaScript, SQL, and machine learning all at the same
time. Bad idea. Pick one thing, get good at it, then expand. Focus beats
scattered effort every time.

The third mistake is not reading error messages. I know they look scary, but
error messages are literally telling you what's wrong. Start from the bottom,
read the actual error, Google it if you need to. This one skill will save you
hours of frustration.

So to recap: avoid tutorial hell by building stuff, focus on one thing at a
time, and actually read your error messages. If you found this helpful, make
sure to subscribe and hit that notification bell. Drop a comment below telling
me which mistake you've made - I know I've made all three!
"""


if __name__ == "__main__":
    print("=" * 60)
    print("Content Production Pipeline Agent")
    print("=" * 60)

    print("\n📝 Processing sample transcript...")
    print("-" * 40)

    result = run_content_pipeline_agent(
        content=SAMPLE_TRANSCRIPT,
        content_name="Coding Mistakes Tutorial",
        save_to_disk=True,
        output_dir="./content_output"
    )

    # Display results
    print(f"\n📋 Source Summary:\n{result.source_summary}")

    print(f"\n🏷️ Title Variations:")
    for i, title in enumerate(result.title_variations, 1):
        print(f"   {i}. [{title.style}] {title.title}")

    print(f"\n📺 YouTube Description Preview:")
    print(f"   Hook: {result.youtube_description.hook}")
    print(f"   Hashtags: {', '.join(result.youtube_description.hashtags[:5])}")

    print(f"\n🎬 Short-Form Script Preview:")
    print(f"   Hook: {result.short_form_script.hook}")
    print(f"   Duration: {result.short_form_script.estimated_duration}")

    print(f"\n📧 Newsletter Preview:")
    print(f"   Subject: {result.newsletter.subject_line}")
    print(f"   Preview: {result.newsletter.preview_text}")

    print(f"\n🎯 Content Themes:")
    for theme in result.content_themes:
        print(f"   • {theme}")

    print("\n" + "=" * 60)
    print("Content package generated!")
    print("Check ./content_output for saved files.")
