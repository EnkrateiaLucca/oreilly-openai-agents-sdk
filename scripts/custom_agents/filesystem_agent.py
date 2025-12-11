"""
File System Automation Agent (Local Cleanup Assistant)
======================================================

An agent that:
- Scans a folder (e.g., Downloads)
- Classifies files by type, size, or last-modified timestamp
- Moves them into organized subfolders
- Reports what it did in a summary

Demonstrates:
- Local file system tooling with @function_tool
- Safe file operations with validation
- Structured reporting of actions taken
- How LLMs can orchestrate admin tasks

SAFETY NOTE: This agent uses a DRY_RUN mode by default.
Set dry_run=False only when you're ready to actually move files.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

import nest_asyncio
nest_asyncio.apply()

from agents import Agent, Runner, function_tool


# ============================================
# Structured Output Models
# ============================================

class FileInfo(BaseModel):
    """Information about a single file."""
    name: str = Field(description="File name")
    extension: str = Field(description="File extension (e.g., '.pdf')")
    size_mb: float = Field(description="File size in megabytes")
    modified_date: str = Field(description="Last modified date")
    category: str = Field(description="Suggested category for this file")


class CleanupAction(BaseModel):
    """A single cleanup action taken or proposed."""
    file_name: str = Field(description="Name of the file")
    action: str = Field(description="Action taken: 'moved', 'skipped', 'would_move'")
    source: str = Field(description="Original location")
    destination: str = Field(description="New location (if moved)")
    reason: str = Field(description="Reason for the action")


class CleanupReport(BaseModel):
    """Summary report of the cleanup operation."""
    source_folder: str = Field(description="Folder that was cleaned up")
    total_files_scanned: int = Field(description="Total number of files found")
    files_organized: int = Field(description="Number of files moved/would be moved")
    files_skipped: int = Field(description="Number of files skipped")
    actions: List[CleanupAction] = Field(description="List of all actions taken")
    summary: str = Field(description="Human-readable summary of what happened")


# ============================================
# File Category Mapping
# ============================================

FILE_CATEGORIES = {
    # Documents
    ".pdf": "Documents/PDFs",
    ".doc": "Documents/Word",
    ".docx": "Documents/Word",
    ".txt": "Documents/Text",
    ".rtf": "Documents/Text",
    ".md": "Documents/Markdown",

    # Spreadsheets
    ".xls": "Spreadsheets",
    ".xlsx": "Spreadsheets",
    ".csv": "Spreadsheets",

    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".svg": "Images",
    ".webp": "Images",
    ".heic": "Images",

    # Videos
    ".mp4": "Videos",
    ".mov": "Videos",
    ".avi": "Videos",
    ".mkv": "Videos",
    ".webm": "Videos",

    # Audio
    ".mp3": "Audio",
    ".wav": "Audio",
    ".flac": "Audio",
    ".m4a": "Audio",
    ".aac": "Audio",

    # Archives
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",

    # Code
    ".py": "Code/Python",
    ".js": "Code/JavaScript",
    ".ts": "Code/TypeScript",
    ".html": "Code/Web",
    ".css": "Code/Web",
    ".json": "Code/Data",
    ".yaml": "Code/Data",
    ".yml": "Code/Data",

    # Applications
    ".dmg": "Installers",
    ".pkg": "Installers",
    ".exe": "Installers",
    ".msi": "Installers",
    ".app": "Applications",
}


# ============================================
# Tools
# ============================================

@function_tool
def scan_folder(folder_path: str, include_hidden: bool = False) -> str:
    """
    Scan a folder and return information about all files.

    Args:
        folder_path: Path to the folder to scan
        include_hidden: Whether to include hidden files (starting with .)

    Returns:
        JSON-formatted string with file information
    """
    import json

    folder = Path(folder_path).expanduser()

    if not folder.exists():
        return json.dumps({"error": f"Folder does not exist: {folder_path}"})

    if not folder.is_dir():
        return json.dumps({"error": f"Path is not a folder: {folder_path}"})

    files_info = []

    for item in folder.iterdir():
        # Skip directories
        if item.is_dir():
            continue

        # Skip hidden files unless requested
        if not include_hidden and item.name.startswith("."):
            continue

        # Get file info
        try:
            stat = item.stat()
            extension = item.suffix.lower()
            category = FILE_CATEGORIES.get(extension, "Other")

            files_info.append({
                "name": item.name,
                "extension": extension,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified_date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                "category": category,
                "full_path": str(item)
            })
        except (OSError, PermissionError) as e:
            files_info.append({
                "name": item.name,
                "error": str(e)
            })

    return json.dumps({
        "folder": str(folder),
        "total_files": len(files_info),
        "files": files_info
    }, indent=2)


@function_tool
def organize_files(
    source_folder: str,
    dry_run: bool = True
) -> str:
    """
    Organize files in a folder by moving them to category subfolders.

    Args:
        source_folder: Path to the folder to organize
        dry_run: If True, only report what would happen without moving files

    Returns:
        JSON report of actions taken or proposed
    """
    import json

    folder = Path(source_folder).expanduser()

    if not folder.exists() or not folder.is_dir():
        return json.dumps({"error": f"Invalid folder: {source_folder}"})

    actions = []
    moved_count = 0
    skipped_count = 0

    for item in folder.iterdir():
        # Skip directories
        if item.is_dir():
            continue

        # Skip hidden files
        if item.name.startswith("."):
            actions.append({
                "file_name": item.name,
                "action": "skipped",
                "reason": "Hidden file"
            })
            skipped_count += 1
            continue

        # Determine category
        extension = item.suffix.lower()
        category = FILE_CATEGORIES.get(extension, "Other")

        # Create destination path
        dest_folder = folder / category
        dest_path = dest_folder / item.name

        # Handle name conflicts
        if dest_path.exists():
            # Add timestamp to avoid overwriting
            stem = item.stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"{stem}_{timestamp}{extension}"
            dest_path = dest_folder / new_name

        if dry_run:
            actions.append({
                "file_name": item.name,
                "action": "would_move",
                "source": str(item),
                "destination": str(dest_path),
                "reason": f"Categorized as {category}"
            })
            moved_count += 1
        else:
            try:
                # Create destination folder if needed
                dest_folder.mkdir(parents=True, exist_ok=True)

                # Move the file
                shutil.move(str(item), str(dest_path))

                actions.append({
                    "file_name": item.name,
                    "action": "moved",
                    "source": str(item),
                    "destination": str(dest_path),
                    "reason": f"Categorized as {category}"
                })
                moved_count += 1
            except Exception as e:
                actions.append({
                    "file_name": item.name,
                    "action": "error",
                    "source": str(item),
                    "reason": str(e)
                })
                skipped_count += 1

    mode = "DRY RUN" if dry_run else "EXECUTED"

    return json.dumps({
        "mode": mode,
        "source_folder": str(folder),
        "total_files_processed": moved_count + skipped_count,
        "files_organized": moved_count,
        "files_skipped": skipped_count,
        "actions": actions
    }, indent=2)


@function_tool
def get_folder_summary(folder_path: str) -> str:
    """
    Get a summary of file types and sizes in a folder.

    Args:
        folder_path: Path to the folder to analyze

    Returns:
        Summary statistics about the folder
    """
    import json
    from collections import defaultdict

    folder = Path(folder_path).expanduser()

    if not folder.exists() or not folder.is_dir():
        return json.dumps({"error": f"Invalid folder: {folder_path}"})

    category_stats = defaultdict(lambda: {"count": 0, "total_size_mb": 0})
    total_size = 0

    for item in folder.iterdir():
        if item.is_dir() or item.name.startswith("."):
            continue

        try:
            size_mb = item.stat().st_size / (1024 * 1024)
            extension = item.suffix.lower()
            category = FILE_CATEGORIES.get(extension, "Other")

            category_stats[category]["count"] += 1
            category_stats[category]["total_size_mb"] += size_mb
            total_size += size_mb
        except (OSError, PermissionError):
            pass

    # Round sizes
    for category in category_stats:
        category_stats[category]["total_size_mb"] = round(
            category_stats[category]["total_size_mb"], 2
        )

    return json.dumps({
        "folder": str(folder),
        "total_size_mb": round(total_size, 2),
        "categories": dict(category_stats)
    }, indent=2)


# ============================================
# Agent Definition
# ============================================

filesystem_agent = Agent(
    name="File Organizer",
    instructions="""You are a helpful file organization assistant. You help
    users clean up and organize their folders.

    Your workflow:
    1. First, scan the folder to understand what files are there
    2. Get a summary of file types and sizes
    3. Propose an organization plan
    4. Execute the organization (or show dry-run results)

    Important guidelines:
    - ALWAYS use dry_run=True first to show what would happen
    - Only set dry_run=False if the user explicitly confirms they want to proceed
    - Skip system and hidden files
    - Report clearly what was done or would be done
    - Warn about any large files or unusual situations

    File categories are based on extensions:
    - Documents: PDF, Word, Text files
    - Spreadsheets: Excel, CSV files
    - Images: JPG, PNG, GIF, etc.
    - Videos: MP4, MOV, etc.
    - Audio: MP3, WAV, etc.
    - Archives: ZIP, RAR, etc.
    - Code: Python, JavaScript, etc.
    - Installers: DMG, EXE, etc.
    """,
    model="gpt-4o-mini",
    tools=[scan_folder, organize_files, get_folder_summary],
    output_type=CleanupReport
)


# ============================================
# Main Function
# ============================================

def run_filesystem_agent(
    folder_path: str,
    execute: bool = False
) -> CleanupReport:
    """
    Run the file organization agent on a folder.

    Args:
        folder_path: Path to the folder to organize
        execute: If True, actually move files. If False (default), dry run only.

    Returns:
        CleanupReport with summary of actions

    Example:
        >>> # Preview what would happen (safe)
        >>> result = run_filesystem_agent("~/Downloads")
        >>> print(result.summary)

        >>> # Actually organize files (after reviewing)
        >>> result = run_filesystem_agent("~/Downloads", execute=True)
    """
    if execute:
        query = f"""Please organize the files in '{folder_path}'.

        1. First scan the folder and show me a summary
        2. Then organize the files with dry_run=False
        3. Report what was moved"""
    else:
        query = f"""Please analyze the files in '{folder_path}' and show me:

        1. A summary of what's in the folder
        2. What organization would look like (dry run only)

        Do NOT actually move any files - use dry_run=True."""

    result = Runner.run_sync(filesystem_agent, query)
    return result.final_output


# ============================================
# Interactive Demo
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("File System Automation Agent")
    print("=" * 60)

    # Default to current directory for demo
    # Change this to your Downloads folder for real use
    demo_folder = "."

    print(f"\n📁 Analyzing folder: {demo_folder}")
    print("-" * 40)
    print("(Running in DRY RUN mode - no files will be moved)")

    result = run_filesystem_agent(demo_folder, execute=False)

    # Display results
    print(f"\n📊 Cleanup Report")
    print(f"   Source: {result.source_folder}")
    print(f"   Files Scanned: {result.total_files_scanned}")
    print(f"   Would Organize: {result.files_organized}")
    print(f"   Skipped: {result.files_skipped}")

    print(f"\n📝 Summary:\n{result.summary}")

    if result.actions:
        print(f"\n📋 Proposed Actions:")
        for action in result.actions[:10]:  # Show first 10
            print(f"   • {action.file_name}")
            print(f"     {action.action} → {action.destination or 'N/A'}")

        if len(result.actions) > 10:
            print(f"   ... and {len(result.actions) - 10} more files")

    print("\n" + "=" * 60)
    print("To actually organize files, run:")
    print("  run_filesystem_agent('~/Downloads', execute=True)")
    print("=" * 60)
