"""
Content Builder with notion-py

Demonstrates:
- Building structured pages with various block types
- Headers, text, lists, code blocks, quotes, callouts
- Embedding content (video, bookmark, image)
- Uploading files
- Multi-column layouts
- Using atomic transactions for batch operations

Usage:
    1. Run extract-token.py first to save your token_v2
    2. Replace <YOUR_PAGE_URL> with the URL of a Notion page to build content in
    3. Run: python content-builder.py
"""

import os
from pathlib import Path

from notion.client import NotionClient
from notion.block import (
    TextBlock,
    TodoBlock,
    HeaderBlock,
    SubheaderBlock,
    SubsubheaderBlock,
    BulletedListBlock,
    NumberedListBlock,
    ToggleBlock,
    QuoteBlock,
    CodeBlock,
    EquationBlock,
    CalloutBlock,
    DividerBlock,
    BookmarkBlock,
    ImageBlock,
    VideoBlock,
    FileBlock,
    ColumnListBlock,
    ColumnBlock,
    PageBlock,
)

# ── Load token & connect to Notion ────────────────────────────────────────────

TOKEN_FILE = Path(os.environ.get("NOTION_DATA_DIR", Path.home() / ".notion-py")) / "token"

if not TOKEN_FILE.exists():
    raise FileNotFoundError(
        f"No saved token found at {TOKEN_FILE}. "
        "Run extract-token.py first to log in and save your token_v2."
    )

TOKEN = TOKEN_FILE.read_text().strip()
PAGE_URL = "<YOUR_PAGE_URL>"

client = NotionClient(token_v2=TOKEN)
page = client.get_block(PAGE_URL)

print(f"Building content in: {page.title}")


# ── Build a structured document ───────────────────────────────────────────────

with client.as_atomic_transaction():

    # ── Title section ─────────────────────────────────────────────────────

    page.title = "Project Documentation"
    page.icon = "📖"

    # ── Introduction ──────────────────────────────────────────────────────

    page.children.add_new(HeaderBlock, title="Introduction")

    page.children.add_new(
        TextBlock,
        title="This document describes the project architecture, "
              "setup instructions, and key decisions."
    )

    page.children.add_new(
        CalloutBlock,
        title="**Note:** This page was generated programmatically using notion-py.",
        icon="💡"
    )

    page.children.add_new(DividerBlock)

    # ── Requirements section ──────────────────────────────────────────────

    page.children.add_new(HeaderBlock, title="Requirements")

    page.children.add_new(SubheaderBlock, title="Prerequisites")

    page.children.add_new(BulletedListBlock, title="Python 3.8 or higher")
    page.children.add_new(BulletedListBlock, title="pip package manager")
    page.children.add_new(BulletedListBlock, title="A Notion account with API access")

    page.children.add_new(SubheaderBlock, title="Installation Steps")

    page.children.add_new(NumberedListBlock, title="Clone the repository")
    page.children.add_new(NumberedListBlock, title="Create a virtual environment")
    page.children.add_new(NumberedListBlock, title="Install dependencies")
    page.children.add_new(NumberedListBlock, title="Configure environment variables")

    page.children.add_new(DividerBlock)

    # ── Code examples ─────────────────────────────────────────────────────

    page.children.add_new(HeaderBlock, title="Code Examples")

    page.children.add_new(SubheaderBlock, title="Python Setup")

    page.children.add_new(
        CodeBlock,
        title=(
            "# Install dependencies\n"
            "pip install notion\n"
            "\n"
            "# Initialize client\n"
            "from notion.client import NotionClient\n"
            "client = NotionClient(token_v2='your_token')"
        ),
        language="Python"
    )

    page.children.add_new(SubheaderBlock, title="Shell Commands")

    page.children.add_new(
        CodeBlock,
        title=(
            "# Clone and setup\n"
            "git clone https://github.com/example/project.git\n"
            "cd project\n"
            "python -m venv venv\n"
            "source venv/bin/activate\n"
            "pip install -r requirements.txt"
        ),
        language="Shell"
    )

    page.children.add_new(SubheaderBlock, title="JSON Configuration")

    page.children.add_new(
        CodeBlock,
        title=(
            '{\n'
            '  "notion": {\n'
            '    "token": "your_token_v2",\n'
            '    "workspace": "your_workspace"\n'
            '  },\n'
            '  "settings": {\n'
            '    "cache_enabled": true,\n'
            '    "monitor": false\n'
            '  }\n'
            '}'
        ),
        language="JSON"
    )

    page.children.add_new(DividerBlock)

    # ── Equations ─────────────────────────────────────────────────────────

    page.children.add_new(HeaderBlock, title="Mathematical Formulas")

    page.children.add_new(
        EquationBlock,
        latex=r"E = mc^2"
    )

    page.children.add_new(
        EquationBlock,
        latex=r"\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}"
    )

    page.children.add_new(DividerBlock)

    # ── Quote ─────────────────────────────────────────────────────────────

    page.children.add_new(HeaderBlock, title="Inspiration")

    page.children.add_new(
        QuoteBlock,
        title="The best way to predict the future is to invent it. -- Alan Kay"
    )

    page.children.add_new(DividerBlock)

    # ── Task list ─────────────────────────────────────────────────────────

    page.children.add_new(HeaderBlock, title="Task List")

    tasks = [
        ("Set up development environment", True),
        ("Write initial documentation", True),
        ("Implement core features", False),
        ("Add test coverage", False),
        ("Deploy to production", False),
    ]

    for task_title, is_done in tasks:
        todo = page.children.add_new(TodoBlock, title=task_title)
        todo.checked = is_done

    page.children.add_new(DividerBlock)

    # ── Callouts with different icons ─────────────────────────────────────

    page.children.add_new(HeaderBlock, title="Status Indicators")

    page.children.add_new(
        CalloutBlock,
        title="**Success:** All tests are passing.",
        icon="✅"
    )

    page.children.add_new(
        CalloutBlock,
        title="**Warning:** Token expires in 24 hours.",
        icon="⚠️"
    )

    page.children.add_new(
        CalloutBlock,
        title="**Error:** Database connection failed.",
        icon="❌"
    )

    page.children.add_new(
        CalloutBlock,
        title="**Info:** See the README for more details.",
        icon="ℹ️"
    )

print("Structured document created!")


# ── Toggle blocks (collapsible sections) ──────────────────────────────────────

toggle = page.children.add_new(ToggleBlock, title="Click to expand: FAQ")
toggle.children.add_new(
    TextBlock,
    title="**Q: How do I get my token_v2?**"
)
toggle.children.add_new(
    TextBlock,
    title="A: Open browser DevTools > Application > Cookies > www.notion.so > token_v2"
)

print("Toggle section created!")


# ── Multi-column layout ──────────────────────────────────────────────────────

page.children.add_new(HeaderBlock, title="Side-by-Side Comparison")

col_list = page.children.add_new(ColumnListBlock)
col_left = col_list.children.add_new(ColumnBlock)
col_right = col_list.children.add_new(ColumnBlock)

# Left column
col_left.children.add_new(SubheaderBlock, title="Pros")
col_left.children.add_new(BulletedListBlock, title="Easy to use")
col_left.children.add_new(BulletedListBlock, title="Pythonic API")
col_left.children.add_new(BulletedListBlock, title="Markdown support")

# Right column
col_right.children.add_new(SubheaderBlock, title="Cons")
col_right.children.add_new(BulletedListBlock, title="Unofficial API")
col_right.children.add_new(BulletedListBlock, title="Token expires")
col_right.children.add_new(BulletedListBlock, title="Monitor broken")

print("Multi-column layout created!")


# ── Embedded content ──────────────────────────────────────────────────────────

page.children.add_new(HeaderBlock, title="Resources")

# Add a bookmark
bm = page.children.add_new(BookmarkBlock)
bm.set_new_link("https://github.com/jamalex/notion-py")

# Add a video by URL
# video = page.children.add_new(VideoBlock, width=640)
# video.set_source_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

print("Embedded content added!")


# ── File uploads ──────────────────────────────────────────────────────────────

# Upload an image from local disk
# img = page.children.add_new(ImageBlock)
# img.upload_file("/path/to/screenshot.png")

# Upload a document
# doc = page.children.add_new(FileBlock)
# doc.upload_file("/path/to/report.pdf")

# print("Files uploaded!")


# ── Sub-pages ─────────────────────────────────────────────────────────────────

page.children.add_new(HeaderBlock, title="Related Pages")

subpage1 = page.children.add_new(PageBlock, title="Architecture Decisions")
subpage1.icon = "🏗️"
subpage1.children.add_new(
    TextBlock,
    title="This page documents key architecture decisions for the project."
)

subpage2 = page.children.add_new(PageBlock, title="Meeting Notes")
subpage2.icon = "📝"
subpage2.children.add_new(
    TextBlock,
    title="Ongoing meeting notes and action items."
)

print("Sub-pages created!")


# ── Color and formatting ─────────────────────────────────────────────────────

# Text with Markdown formatting
page.children.add_new(
    TextBlock,
    title="This has **bold**, *italic*, ~~strikethrough~~, and `inline code`."
)

# Text with a link
page.children.add_new(
    TextBlock,
    title="Visit [notion-py on GitHub](https://github.com/jamalex/notion-py) for more info."
)

# Colored text (set via the raw format property)
colored_text = page.children.add_new(TextBlock, title="This text has a colored background.")
colored_text.color = "blue_background"

# Available colors:
# Text: gray, brown, orange, yellow, green, blue, purple, pink, red
# Background: gray_background, brown_background, orange_background, etc.

print("Formatted text added!")


# ── Convert block types ──────────────────────────────────────────────────────

# Convert a text block to a header
text_to_convert = page.children.add_new(TextBlock, title="I will become a header")
text_to_convert.convert_to_type(HeaderBlock)

print("Block type converted!")


# ── Export page as Markdown ──────────────────────────────────────────────────

# Export the entire page content as Markdown
# md_content = page.extract_markdown()
# print(f"\nExported Markdown ({len(md_content)} chars):")
# print(md_content[:500])


print("\nContent building complete!")
