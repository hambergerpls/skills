"""
Basic Page Operations with notion-py

Demonstrates:
- Connecting to Notion
- Reading and writing page properties
- Navigating the block tree (parent/children)
- Adding, moving, and deleting blocks

Usage:
    1. Run extract-token.py first to save your token_v2
    2. Replace <YOUR_PAGE_URL> with the URL of a Notion page you want to work with
    3. Run: python basic-page-operations.py
"""

import os
from pathlib import Path

from notion.client import NotionClient
from notion.block import (
    TextBlock,
    TodoBlock,
    HeaderBlock,
    SubheaderBlock,
    BulletedListBlock,
    NumberedListBlock,
    QuoteBlock,
    DividerBlock,
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

print(f"Connected! Page title: {page.title}")
print(f"Page URL: {page.get_browseable_url()}")


# ── Read page properties ──────────────────────────────────────────────────────

print(f"\nTitle: {page.title}")
print(f"Icon: {page.icon}")
print(f"Cover: {page.cover}")
print(f"Locked: {page.locked}")
print(f"Parent ID: {page.parent.id}")


# ── Update page properties ────────────────────────────────────────────────────

# Set title (supports Markdown)
page.title = "My Updated Page Title"

# Set icon (emoji or URL)
page.icon = "https://example.com/icon.png"  # or an emoji string like "📝"

# Set cover image
page.cover = "https://example.com/cover.jpg"

# Lock/unlock page
page.locked = True
page.locked = False


# ── Navigate the block tree ───────────────────────────────────────────────────

# List all children
print(f"\nChildren of '{page.title}':")
for child in page.children:
    print(f"  [{child.type}] {getattr(child, 'title', '(no title)')}")

# Access parent
parent = page.parent
print(f"\nParent: {parent.id}")

# Filter children by type
todos = page.children.filter(type=TodoBlock)
print(f"\nTodo items: {len(list(todos))}")

# Get all top-level pages in the workspace
top_pages = client.get_top_level_pages()
print(f"\nTop-level pages: {len(top_pages)}")
for p in top_pages[:5]:
    print(f"  - {p.title}")


# ── Add blocks ────────────────────────────────────────────────────────────────

# Add a header
header = page.children.add_new(HeaderBlock, title="New Section")

# Add body text
text = page.children.add_new(TextBlock, title="This is a paragraph of text.")

# Add a subheader
subheader = page.children.add_new(SubheaderBlock, title="Subsection")

# Add bullet points
bullet1 = page.children.add_new(BulletedListBlock, title="First point")
bullet2 = page.children.add_new(BulletedListBlock, title="Second point")
bullet3 = page.children.add_new(BulletedListBlock, title="Third point")

# Add numbered list
num1 = page.children.add_new(NumberedListBlock, title="Step one")
num2 = page.children.add_new(NumberedListBlock, title="Step two")

# Add a quote
quote = page.children.add_new(QuoteBlock, title="To be or not to be.")

# Add a divider
page.children.add_new(DividerBlock)

# Add todo items
todo1 = page.children.add_new(TodoBlock, title="Buy groceries")
todo2 = page.children.add_new(TodoBlock, title="Clean the house")
todo1.checked = True  # Mark as done

# Add a sub-page
subpage = page.children.add_new(PageBlock, title="My Sub Page")
subpage.icon = "📄"
subpage.children.add_new(TextBlock, title="Content inside the sub-page.")


# ── Move blocks ───────────────────────────────────────────────────────────────

# Move a block after another block
quote.move_to(header, "after")

# Move a block to be the first child of a parent
text.move_to(page, "first-child")

# Move a block to be the last child of a parent
todo2.move_to(page, "last-child")

# Move a block before another block
num1.move_to(num2, "before")


# ── Delete blocks ─────────────────────────────────────────────────────────────

# Soft-delete (moves to trash, can be restored)
bullet3.remove()

# Hard-delete (permanent, cannot be restored)
# bullet3.remove(permanently=True)


# ── Batch operations ──────────────────────────────────────────────────────────

# All operations inside the context manager are sent as a single API transaction
with client.as_atomic_transaction():
    page.children.add_new(TextBlock, title="Batch item 1")
    page.children.add_new(TextBlock, title="Batch item 2")
    page.children.add_new(TextBlock, title="Batch item 3")


# ── Refresh data from server ─────────────────────────────────────────────────

# Force refresh a block's data from the server
page.refresh()
print(f"\nRefreshed title: {page.title}")


# ── Search ────────────────────────────────────────────────────────────────────

# Search across the workspace
results = client.search("meeting notes", limit=5)
print(f"\nSearch results for 'meeting notes':")
for r in results:
    print(f"  - {r.title} ({r.get_browseable_url()})")

print("\nDone!")
