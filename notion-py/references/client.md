# NotionClient API Reference

## Constructor

```python
from notion.client import NotionClient

client = NotionClient(
    token_v2=None,              # str: Auth cookie from browser (primary auth method)
    monitor=False,              # bool: Enable real-time WebSocket change monitoring
    start_monitoring=False,     # bool: Alias for monitor
    enable_caching=False,       # bool: Enable disk cache in ~/.notion-py/cache/
    cache_key=None,             # str: Custom cache key (defaults to token hash)
    email=None,                 # str: Email for email/password login
    password=None,              # str: Password for email/password login
    client_specified_retry=None # Retry: Custom urllib3 Retry strategy
)
```

**Authentication priority:** If `token_v2` is provided, it is used directly. Otherwise, if `email` and `password` are provided, the client logs in via Notion's `/loginWithEmail` endpoint to obtain a token.

**Session:** The client creates a `requests.Session` with:
- `token_v2` set as a cookie
- Automatic retry: 10 retries with backoff factor 0.5 on status codes 429, 502, 503, 504
- Custom retry can be overridden via `client_specified_retry`

## Core Retrieval Methods

### `get_block(url_or_id, force_refresh=False)`

Retrieve any block or page by URL or UUID. Returns the appropriate `Block` subclass based on the block's `type`.

```python
# By full page URL
page = client.get_block("https://www.notion.so/myorg/My-Page-c0d20a71c0944985ae96e661ccc99821")

# By block UUID
block = client.get_block("c0d20a71-c094-4985-ae96-e661ccc99821")

# By inline block URL (with fragment)
block = client.get_block("https://www.notion.so/myorg/Page-abc123#block-id-fragment")

# Force refresh from server
block = client.get_block("...", force_refresh=True)
```

**Returns:** `Block` subclass instance (e.g., `PageBlock`, `TextBlock`, `CollectionViewBlock`, etc.)

### `get_collection(collection_id, force_refresh=False)`

Retrieve a database (collection) by its UUID.

```python
collection = client.get_collection("a1b2c3d4-...")
print(collection.name)
print(collection.get_schema_properties())
```

**Returns:** `Collection` instance

### `get_collection_view(url_or_id, collection=None, force_refresh=False)`

Retrieve a specific view of a database. The URL must include the view parameter (`?v=...`).

```python
cv = client.get_collection_view(
    "https://www.notion.so/myorg/8511b9fc?v=8dee2a54f6b64cb2"
)
print(cv.name, cv.type)  # e.g., "My View", "table"
```

**Returns:** `CollectionView` subclass (`TableView`, `BoardView`, `ListView`, `CalendarView`, `GalleryView`)

### `get_user(user_id)`

Retrieve a user by UUID.

```python
user = client.get_user("user-uuid")
print(user.full_name, user.email)
```

**Returns:** `User` instance

### `get_space(space_id)`

Retrieve a workspace by UUID.

```python
space = client.get_space("space-uuid")
print(space.name, space.domain)
```

**Returns:** `Space` instance

### `get_top_level_pages()`

Get all top-level pages in the current workspace.

```python
pages = client.get_top_level_pages()
for page in pages:
    print(page.title)
```

**Returns:** List of `Block` instances

### `get_record_data(table, id, force_refresh=False)`

Low-level method to get raw record data from cache or server.

```python
data = client.get_record_data("block", "some-uuid")
# Returns the raw dict from Notion's API
```

**Returns:** `dict` (raw record data)

## Search Methods

### `search(query, search_type=None, limit=None, sort=None, source=None, ...)`

Full-featured search across the workspace.

```python
# Simple text search
results = client.search("meeting notes")

# With limit
results = client.search("project", limit=10)

# Advanced: search with type filter
results = client.search("design", search_type="BlocksInAncestor")
```

**Full parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | Search text |
| `search_type` | `str` | Search scope type |
| `limit` | `int` | Max results to return |
| `sort` | `dict` | Sort configuration |
| `source` | `str` | Search source |
| `isDeletedOnly` | `bool` | Only search deleted items |
| `excludeTemplates` | `bool` | Exclude template pages |
| `isNavigableOnly` | `bool` | Only navigable pages |
| `requireEditPermissions` | `bool` | Only editable pages |
| `ancestors` | `list` | Ancestor block IDs to search within |
| `createdBy` | `str` | Filter by creator |
| `editedBy` | `str` | Filter by last editor |
| `lastEditedTime` | `dict` | Filter by last edit time range |
| `createdTime` | `dict` | Filter by creation time range |

**Returns:** List of `Block` instances matching the search

### `search_blocks(search, limit=20)`

Shortcut for `search()` that searches blocks.

```python
results = client.search_blocks("api documentation", limit=5)
```

### `search_pages_with_parent(parent_id, search="", limit=10000)`

Search pages that are children of a specific parent block.

```python
results = client.search_pages_with_parent("parent-uuid", search="draft")
```

## Mutation Methods

### `create_record(table, parent, **kwargs)`

Create a new record (block, collection_view, etc.).

```python
# Usually you don't call this directly; use children.add_new() instead
record_id = client.create_record("block", parent=page, type="text")
```

**Returns:** UUID string of the created record

### `submit_transaction(operations, update_last_edited=True)`

Submit API operations to the server. If inside an `as_atomic_transaction()` context, operations are queued and sent when the context exits.

```python
from notion.operations import build_operation

op = build_operation(
    id="block-uuid",
    path=["properties", "title"],
    args=[["New title"]],
    command="set",
    table="block"
)
client.submit_transaction([op])
```

## Transaction Support

### `as_atomic_transaction()`

Context manager that batches all operations into a single API call. Supports nesting (inner contexts are no-ops).

```python
with client.as_atomic_transaction():
    page.title = "Updated"
    page.children.add_new(TextBlock, title="New block")
    page.children.add_new(TodoBlock, title="New todo")
    # All three operations sent as one transaction on context exit
```

### `in_transaction()`

Check if currently inside a transaction context.

```python
if client.in_transaction():
    print("Operations will be batched")
```

## Refresh / Sync Methods

### `refresh_records(**kwargs)`

Force-refresh records from the server. kwargs map table names to lists of UUIDs.

```python
client.refresh_records(
    block=["uuid1", "uuid2"],
    collection=["collection-uuid"]
)
```

### `refresh_collection_rows(collection_id)`

Refresh all rows for a given collection.

```python
client.refresh_collection_rows("collection-uuid")
```

### `query_collection(*args, **kwargs)`

Delegates to the store's `call_query_collection`. Used internally by `CollectionQuery.execute()`.

## User Management

### `current_user`

Property returning the `User` instance for the authenticated user.

```python
print(client.current_user.full_name)
print(client.current_user.email)
```

### `current_space`

Property returning the `Space` instance for the active workspace.

```python
print(client.current_space.name)
print(client.current_space.domain)
```

### `get_email_uid()`

Returns a dict mapping email addresses to user IDs for all users in the workspace.

```python
email_map = client.get_email_uid()
# {"alice@example.com": "uuid1", "bob@example.com": "uuid2"}
```

### `set_user_by_email(email)`

Switch the active user by email (for multi-account scenarios).

```python
client.set_user_by_email("other@example.com")
print(client.current_user.email)  # "other@example.com"
```

### `set_user_by_uid(user_id)`

Switch the active user by UUID.

```python
client.set_user_by_uid("user-uuid")
```

## Internal API

### `post(endpoint, data)`

All Notion API calls are POST requests to `https://www.notion.so/api/v3/{endpoint}`.

```python
# Low-level API call (rarely needed)
response = client.post("loadPageChunk", {
    "pageId": "page-uuid",
    "limit": 50,
    "cursor": {"stack": []},
    "chunkNumber": 0,
    "verticalColumns": False
})
```

## Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `current_user` | `User` | The authenticated user |
| `current_space` | `Space` | The active workspace |
| `session` | `requests.Session` | HTTP session with retry and auth cookies |
