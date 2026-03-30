# Utilities, Markdown, and Supporting Modules

## Markdown Conversion

notion-py automatically converts between CommonMark Markdown and Notion's internal annotated-span format. The conversion module is at `notion.markdown`.

### Supported Formatting

| Markdown | Notion Format | Example |
|----------|--------------|---------|
| `**bold**` | Bold | `**important**` |
| `*italic*` / `_italic_` | Italic | `*emphasis*` |
| `` `code` `` | Inline code | `` `variable` `` |
| `~~strike~~` | Strikethrough | `~~deleted~~` |
| `[text](url)` | Link | `[click here](https://...)` |
| `$latex$` | Inline equation | `$E = mc^2$` |

### Programmatic Conversion

```python
from notion.markdown import markdown_to_notion, notion_to_markdown, notion_to_plaintext

# Markdown -> Notion internal format
notion_fmt = markdown_to_notion("**Hello** *world*")
# Returns: [["Hello", [["b"]]], [" "], ["world", [["i"]]]]

# Notion internal format -> Markdown
md = notion_to_markdown([["Hello", [["b"]]], [" "], ["world", [["i"]]]])
# Returns: "**Hello** *world*"

# Notion internal format -> plain text (strip all formatting)
plain = notion_to_plaintext([["Hello", [["b"]]], [" "], ["world", [["i"]]]])
# Returns: "Hello world"
```

### Notion Internal Text Format

Notion stores formatted text as a list of spans:

```
[[text, [[format_type, format_arg], ...]], ...]
```

Each span is `[text_string]` or `[text_string, [[formatting_annotations]]]`.

Format types:
| Type | Meaning | Arg |
|------|---------|-----|
| `"b"` | Bold | None |
| `"i"` | Italic | None |
| `"s"` | Strikethrough | None |
| `"c"` | Inline code | None |
| `"a"` | Link | URL string |
| `"e"` | Inline equation | LaTeX string |
| `"u"` | User mention | User UUID |
| `"p"` | Page link | Page UUID |

Example: `[["Click ", [["b"]]], ["here", [["a", "https://example.com"]]]]` = **Click** [here](https://example.com)

## Record Base Class

All data objects (blocks, collections, users, spaces) extend `Record` from `notion.records`.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | UUID of the record |
| `role` | `str` | User's permission role for this record |
| `alive` | `bool` | Whether the record has not been deleted |

### Methods

#### `get(path=None, default=None, force_refresh=False)`

Read data from the local cache by dotted path.

```python
full_data = record.get()                   # Entire record dict
title = record.get("properties.title")     # Dotted path
color = record.get("format.block_color", "default")  # With default
fresh = record.get("properties.title", force_refresh=True)  # Force server fetch
```

#### `set(path, value)`

Write data to the server. Generates an operation and submits it.

```python
record.set("format.block_color", "blue_background")
record.set("properties.title", [["New Title"]])  # Raw Notion format
```

#### `refresh()`

Force-refresh the record's data from the server.

```python
record.refresh()
# record.get() now returns fresh server data
```

#### `add_callback(callback, callback_id=None, extra_kwargs=None)`

Register a function to be called when this record changes.

```python
def on_change(record, difference):
    print(f"Record {record.id} changed")
    for change_type, path, values in difference:
        print(f"  {change_type}: {path} = {values}")

record.add_callback(on_change, callback_id="my_watcher")
```

Callback signature: `callback(record, difference, **extra_kwargs)`
- `record`: The `Record` instance that changed
- `difference`: Output of `dictdiffer.diff()` -- list of `(change_type, path, values)` tuples
- Change types: `"add"`, `"change"`, `"remove"`

#### `remove_callbacks(callback_or_id=None)`

Remove callbacks. Pass a callback function, a callback_id string, or `None` to remove all.

```python
record.remove_callbacks("my_watcher")
record.remove_callbacks()  # Remove all
```

## RecordStore

The `RecordStore` (in `notion.store`) is the central local cache for all records.

### Key Behaviors

- **Thread-safe**: All cache reads/writes are thread-safe
- **Automatic population**: API responses contain many related records; all are stored
- **Change detection**: Uses `dictdiffer.diff()` to detect and report changes
- **Local operation simulation**: `run_local_operations()` applies operations to the local cache before server confirmation, keeping the UI responsive
- **Optional disk persistence**: When `enable_caching=True`, the cache is saved to `~/.notion-py/cache/`

### Internal API Methods

These are called by `NotionClient` internally:

| Method | Description |
|--------|-------------|
| `call_get_record_values(**kwargs)` | Fetch raw record data from server |
| `call_load_page_chunk(page_id, ...)` | Load a page's block tree |
| `call_query_collection(collection_id, view_id, ...)` | Query a database |
| `store_recordmap(recordmap)` | Store a batch of records and fire callbacks |
| `run_local_operations(operations)` | Apply operations locally before server round-trip |

## Monitor

The `Monitor` class (in `notion.monitor`) provides real-time change notifications via WebSocket long-polling.

**Current Status: BROKEN** -- The monitoring system is currently non-functional. Use `record.refresh()` for manual updates.

### How It Works (When Functional)

- Connects to `msgstore.www.notion.so/primus/` via WebSocket
- Subscribes to `versions/{id}:{table}` channels for each instantiated record
- Subscribes to `collection/{id}` channels for database rows
- When server-side versions change, auto-refreshes affected records
- Runs in a background daemon thread via `poll_async()`
- Reconnects automatically with re-subscription on failures

### Configuration

```python
# Enable monitoring (currently broken, not recommended)
client = NotionClient(token_v2="...", monitor=True)

# Disable monitoring (default)
client = NotionClient(token_v2="...", monitor=False)
```

### Workaround

Until monitoring is fixed, manually refresh records:

```python
block.refresh()        # Refresh a single block
collection.refresh()   # Refresh a collection
```

## Utility Functions

From `notion.utils`:

### `extract_id(url_or_id)`

Parse a Notion URL or UUID string to a canonical UUID.

```python
from notion.utils import extract_id

# From a URL
uuid = extract_id("https://www.notion.so/myorg/My-Page-c0d20a71c0944985ae96e661ccc99821")
# Returns: "c0d20a71-c094-4985-ae96-e661ccc99821"

# From a raw UUID (with or without dashes)
uuid = extract_id("c0d20a71c0944985ae96e661ccc99821")
# Returns: "c0d20a71-c094-4985-ae96-e661ccc99821"

# Already canonical
uuid = extract_id("c0d20a71-c094-4985-ae96-e661ccc99821")
# Returns: "c0d20a71-c094-4985-ae96-e661ccc99821"
```

### `slugify(original)`

Convert a string to an underscore-delimited slug (used for property name mapping).

```python
from notion.utils import slugify

slugify("Estimated Value")  # "estimated_value"
slugify("Due Date")         # "due_date"
slugify("Is Confirmed?")    # "is_confirmed"
```

### `get_embed_link(source_url)`

Resolve a URL to its Embedly embed URL.

```python
from notion.utils import get_embed_link

embed_url = get_embed_link("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
```

### `now()`

Current timestamp in milliseconds (used internally for operations).

```python
from notion.utils import now
ts = now()  # e.g., 1719849600000
```

### `get_by_path(path, obj, default=None)`

Traverse nested dicts/lists by dotted path.

```python
from notion.utils import get_by_path

data = {"format": {"block_color": "blue"}}
color = get_by_path("format.block_color", data)  # "blue"
missing = get_by_path("format.font_size", data, default=14)  # 14
```

### `add_signed_prefix_as_needed(url)` / `remove_signed_prefix_as_needed(url)`

Handle Notion's S3 signed URL prefixes.

```python
from notion.utils import add_signed_prefix_as_needed, remove_signed_prefix_as_needed

# Add signed prefix for S3 URLs
signed = add_signed_prefix_as_needed("https://s3-us-west-2.amazonaws.com/secure.notion-static.com/...")
# "https://www.notion.so/signed/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2F..."

# Remove signed prefix
raw = remove_signed_prefix_as_needed(signed)
```

## Operations

From `notion.operations`:

### `build_operation(id, path, args, command, table="block")`

Construct a single mutation operation for the Notion API.

```python
from notion.operations import build_operation

op = build_operation(
    id="block-uuid",
    path=["properties", "title"],
    args=[["New Title"]],
    command="set",
    table="block"
)
```

**Commands:**

| Command | Description |
|---------|-------------|
| `"set"` | Set a value at the path |
| `"update"` | Update/merge a value at the path |
| `"listAfter"` | Insert into a list after a reference |
| `"listBefore"` | Insert into a list before a reference |
| `"listRemove"` | Remove from a list |

### `operation_update_last_edited(user_id, block_id)`

Create an operation to update the "last edited" metadata on a block.

## Field Mapping (maps.py)

Descriptor protocol for mapping Python attributes to Notion record fields.

### `field_map(path, python_to_api=None, api_to_python=None)`

Map a Python attribute to a dotted path in the record JSON.

```python
# Inside a Block subclass definition:
icon = field_map("format.page_icon")
locked = field_map("format.block_locked")
color = field_map(
    "format.block_color",
    python_to_api=lambda x: x,
    api_to_python=lambda x: x
)
```

### `property_map(name, python_to_api=None, api_to_python=None, markdown=True)`

Like `field_map` but operates under `properties.{name}` with automatic Markdown conversion.

```python
title = property_map("title")  # Auto Markdown <-> Notion format
```

## Settings and Constants

From `notion.settings`:

| Constant | Value |
|----------|-------|
| `BASE_URL` | `https://www.notion.so/` |
| `API_BASE_URL` | `https://www.notion.so/api/v3/` |
| `SIGNED_URL_PREFIX` | `https://www.notion.so/signed/` |
| `S3_URL_PREFIX` | `https://s3-us-west-2.amazonaws.com/secure.notion-static.com/` |
| `DATA_DIR` | `~/.notion-py/` (override with `$NOTION_DATA_DIR`) |
| `CACHE_DIR` | `~/.notion-py/cache/` |

## Space Class

From `notion.space`:

| Property/Method | Type | Description |
|-----------------|------|-------------|
| `name` | `str` | Workspace name |
| `domain` | `str` | Workspace domain |
| `icon` | `str` | Workspace icon |
| `pages` | `list[Block]` | All top-level pages |
| `users` | `list[User]` | All workspace members |
| `add_page(title, type="page", shared=False)` | `Block` | Create a top-level page |

```python
space = client.current_space
print(space.name, space.domain)

# List all pages
for page in space.pages:
    print(page.title)

# List all users
for user in space.users:
    print(user.full_name, user.email)

# Add a new top-level page
new_page = space.add_page("My New Page")
```

## User Class

From `notion.user`:

| Property | Type | Description |
|----------|------|-------------|
| `given_name` | `str` | First name |
| `family_name` | `str` | Last name |
| `email` | `str` | Email address |
| `locale` | `str` | Locale setting |
| `time_zone` | `str` | Timezone |
| `full_name` | `str` | Computed full name (`given_name + family_name`) |

```python
user = client.current_user
print(user.full_name)    # "Jamie Alexandre"
print(user.email)        # "jamie@example.com"
print(user.time_zone)    # "America/New_York"
```
