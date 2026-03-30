---
name: notion-py
description: Unofficial Python API client for Notion.so. Use when writing Python code to interact with Notion - reading/writing pages, managing databases, creating content blocks, querying collections, or building Notion integrations.
metadata:
  author: jamalex
  version: "0.1.0"
  source: https://github.com/jamalex/notion-py
---

# notion-py

Unofficial Python 3 client for the Notion.so internal API (v3). Provides an object-oriented interface for reading and writing Notion pages, databases, and blocks. Automatically converts between Notion's internal format and Python objects, supports Markdown in text fields, and offers local caching and callback-based change detection.

**Important:** This library uses Notion's **private internal API**, not the official public API. It authenticates via the `token_v2` browser cookie. The API surface is reverse-engineered and may break if Notion changes their internals.

## Setup & Installation

### Install the package

```bash
pip install notion
```

### Obtain `token_v2`

1. Log in to [notion.so](https://www.notion.so) in your browser (must be a full member, not a guest)
2. Open browser DevTools (F12) > Application > Cookies > `www.notion.so`
3. Copy the value of the `token_v2` cookie

### Initialize the client

```python
from notion.client import NotionClient

client = NotionClient(token_v2="<your_token_v2>")
```

### Constructor options

```python
client = NotionClient(
    token_v2="<token>",        # Required: auth cookie from browser
    monitor=False,             # Enable real-time change monitoring (currently broken)
    enable_caching=False,      # Enable disk cache in ~/.notion-py/cache/
    cache_key=None,            # Custom cache key (defaults to token hash)
)
```

**Alternative: email/password login** (if token_v2 is unavailable):

```python
client = NotionClient(email="you@example.com", password="your_password")
```

### Environment variable

Set `NOTION_DATA_DIR` to override the default data directory (`~/.notion-py/`).

## Core Workflow

The typical pattern when working with notion-py:

1. **Initialize client** with `token_v2`
2. **Retrieve blocks/pages** by URL or UUID using `client.get_block()`
3. **Read/modify properties** directly on the Python object (e.g., `page.title = "New Title"`)
4. **Navigate the block tree** via `.children` and `.parent`
5. **Add new blocks** via `page.children.add_new(BlockType, title="...")`
6. **Work with databases** via `client.get_collection_view()`, then query/add rows
7. **Batch operations** inside `client.as_atomic_transaction()` for performance

### Retrieving blocks

```python
# By page URL
page = client.get_block("https://www.notion.so/myorg/My-Page-c0d20a71c0944985ae96e661ccc99821")

# By block UUID
block = client.get_block("c0d20a71-c094-4985-ae96-e661ccc99821")

# By block URL (right-click > Copy Link on any block in Notion)
block = client.get_block("https://www.notion.so/myorg/My-Page-c0d20a71c0944985ae96e661ccc99821#a1b2c3d4")
```

### Reading and writing properties

```python
print(page.title)                 # Read title
page.title = "Updated Title"      # Write title (supports Markdown)
page.title = "**Bold** title"     # Markdown is converted automatically

print(page.icon)                  # Read page icon
page.icon = "https://..."         # Set icon URL or emoji
page.cover = "https://..."        # Set cover image
page.locked = True                # Lock the page
```

### Navigating the block tree

```python
for child in page.children:
    print(child.type, child.title)

parent = page.parent
print(f"Parent: {parent.id}")

# Filter children by type
from notion.block import TodoBlock
todos = page.children.filter(type=TodoBlock)
```

### Adding blocks

```python
from notion.block import (
    TextBlock, TodoBlock, HeaderBlock, SubheaderBlock,
    CodeBlock, QuoteBlock, BulletedListBlock, CalloutBlock,
    ImageBlock, BookmarkBlock, DividerBlock
)

# Add a text block
text = page.children.add_new(TextBlock, title="Hello, world!")

# Add a to-do item
todo = page.children.add_new(TodoBlock, title="Buy groceries")
todo.checked = True

# Add a code block
code = page.children.add_new(CodeBlock, title="print('hello')", language="Python")

# Add a header
header = page.children.add_new(HeaderBlock, title="Section Title")

# Add a callout
callout = page.children.add_new(CalloutBlock, title="Important note", icon="!")
```

### Moving and deleting blocks

```python
# Move block relative to another
my_block.move_to(target_block, "after")      # after, before, first-child, last-child

# Soft-delete (move to trash)
block.remove()

# Hard-delete (permanent)
block.remove(permanently=True)
```

### Working with databases

```python
# Get a collection view by its URL
cv = client.get_collection_view("https://www.notion.so/myorg/8511b9fc522249f79b90768b832599cc?v=8dee2a54f6b64cb296c83328adba78e1")

# List all rows
for row in cv.collection.get_rows():
    print(row.name, row.status, row.estimated_value)

# Add a new row
row = cv.collection.add_row()
row.name = "New item"
row.is_confirmed = True
row.estimated_value = 100
row.tags = ["A", "B"]
row.person = client.current_user

# Filtered query
filter_params = {
    "filters": [{
        "filter": {
            "value": {"type": "exact", "value": "Done"},
            "operator": "enum_is"
        },
        "property": "status"
    }],
    "operator": "and"
}
result = cv.build_query(filter=filter_params).execute()

# Sorted query
sort_params = [{"direction": "descending", "property": "estimated_value"}]
result = cv.build_query(sort=sort_params).execute()

# Aggregation
agg_params = [{"property": "estimated_value", "aggregator": "sum", "id": "total"}]
result = cv.build_query(aggregate=agg_params).execute()
print("Total:", result.get_aggregate("total"))
```

### Batch operations

```python
# All operations inside the context manager are sent as a single transaction
with client.as_atomic_transaction():
    page.title = "Batch update"
    page.children.add_new(TextBlock, title="Added in batch")
    page.children.add_new(TodoBlock, title="Also batched")
```

### Search

```python
# Search across the workspace
results = client.search("meeting notes")
for block in results:
    print(block.title, block.get_browseable_url())

# Search with limit
results = client.search("project", limit=10)
```

### File uploads

```python
from notion.block import ImageBlock, FileBlock

# Upload an image
img = page.children.add_new(ImageBlock)
img.upload_file("/path/to/image.png")

# Upload a file
file_block = page.children.add_new(FileBlock)
file_block.upload_file("/path/to/document.pdf")
```

### Multi-account user management

```python
# Check current user
print(client.current_user.email)

# Switch to a different user (multi-account scenarios)
client.set_user_by_email("other@example.com")
# or by UID
client.set_user_by_uid("<uid>")
```

## Important Notes & Gotchas

- **`token_v2` expiration**: The cookie expires periodically. You must re-obtain it from the browser when it does. There is no refresh mechanism.
- **Monitor is broken**: The real-time Notion-to-Python auto-updating system (`monitor=True`) is currently non-functional. Call `block.refresh()` manually to get fresh data from the server.
- **Property slugs**: Database column names are converted to Python-friendly slugs. "Estimated Value" becomes `row.estimated_value`. Use `collection.get_schema_properties()` to see all available slugs.
- **Markdown interface**: All text properties (titles, descriptions) accept and return CommonMark Markdown. Bold, italic, strikethrough, code, links, and LaTeX are supported.
- **Read-only properties**: `formula` and `rollup` database properties are computed server-side and cannot be set via the API.
- **Weak validation**: The API does not strongly validate data structures. Writing malformed data can corrupt blocks. Use `record.get()` (no args) to inspect the full internal structure.
- **Rate limiting**: Notion may rate-limit requests. The client uses a `requests.Session` with automatic retry (10 retries with backoff on 429/502/503/504 errors).
- **All API calls are POSTs**: Every endpoint (including reads) uses HTTP POST to `https://www.notion.so/api/v3/{endpoint}`.
- **Workspace pages**: Use `client.get_top_level_pages()` or `client.current_space.pages` to list all top-level pages.

## Deep-dive Documentation

| Reference | Description |
|-----------|-------------|
| [references/client.md](references/client.md) | `NotionClient` constructor, methods, transactions, search, session |
| [references/blocks.md](references/blocks.md) | Complete block type hierarchy, 35 block types, methods, properties |
| [references/collections.md](references/collections.md) | Databases, rows, views, queries, filters, sorts, aggregations, property types |
| [references/utilities.md](references/utilities.md) | Markdown conversion, RecordStore, Monitor, utility functions, settings |

## Templates

| Template | Description |
|----------|-------------|
| [templates/basic-page-operations.py](templates/basic-page-operations.py) | Connect to Notion, read/write pages, navigate block tree, add/move/delete blocks |
| [templates/database-operations.py](templates/database-operations.py) | Query databases, add rows, filter, sort, aggregate, work with property types |
| [templates/content-builder.py](templates/content-builder.py) | Build structured pages with headers, text, code, embeds, file uploads, callouts |
