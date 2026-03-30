# Collections (Databases) Reference

## Architecture Overview

Notion databases ("collections") have the following structure:

```
CollectionViewBlock (inline) / CollectionViewPageBlock (full-page)
  +-- Collection (schema definition, parent of rows)
  |     +-- CollectionRowBlock (row 1)
  |     +-- CollectionRowBlock (row 2)
  |     +-- ...
  +-- CollectionView (filters/sort/display for each view)
  +-- CollectionView (another view)
  +-- ...
```

- **CollectionViewBlock / CollectionViewPageBlock**: The container block on a page
- **Collection**: Holds the database schema and is the parent of all rows
- **CollectionRowBlock**: A single row/record in the database
- **CollectionView**: A saved view (table, board, list, calendar, gallery) with filters, sorts, etc.

## Getting a Database

```python
# By the URL of the database page (must include ?v= parameter for the view)
cv = client.get_collection_view(
    "https://www.notion.so/myorg/8511b9fc522249f79b90768b832599cc?v=8dee2a54f6b64cb296c83328adba78e1"
)

# Access the collection (schema + rows) from the view
collection = cv.collection

# Or get a collection directly by ID
collection = client.get_collection("collection-uuid")
```

## Collection Class

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Database name (Markdown-aware) |
| `description` | `str` | Database description (Markdown-aware) |
| `cover` | `str` | Cover image URL |
| `parent` | `Block` | Parent block (the `CollectionViewBlock`) |
| `templates` | `Templates` | Children object for template pages |

### `get_schema_properties()`

Returns all column/property definitions as a list of dicts.

```python
props = collection.get_schema_properties()
for prop in props:
    print(prop["name"], prop["slug"], prop["type"])
    # e.g., "Estimated Value", "estimated_value", "number"
```

Each dict contains:

| Key | Description |
|-----|-------------|
| `id` | Internal 4-character property ID |
| `slug` | Python-friendly name (used for attribute access on rows) |
| `name` | Display name in Notion |
| `type` | Property type string |
| `options` | For select/multi_select: list of `{id, value, color}` |

### `get_schema_property(identifier)`

Look up a single property by ID, name, or slug.

```python
prop = collection.get_schema_property("estimated_value")
print(prop["type"])  # "number"
```

### `add_row(update_views=True, **kwargs)`

Create a new row in the database. Returns a `CollectionRowBlock`.

```python
row = collection.add_row()
row.name = "New Item"
row.status = "In Progress"

# Or set properties inline
row = collection.add_row(name="New Item", status="In Progress", priority=5)
```

**Parameters:**
- `update_views` (bool): If True (default), updates view filters to include the new row
- `**kwargs`: Property slug names mapped to values

### `get_rows(search="", **kwargs)`

Retrieve rows from the database. Alias for `query()`.

```python
# All rows
rows = collection.get_rows()

# With text search
rows = collection.get_rows(search="Bob")

for row in rows:
    print(row.name, row.estimated_value)
```

### `query(**kwargs)`

Execute a query against the collection. Same as `get_rows()`. Accepts all `CollectionQuery` parameters.

### `check_schema_select_options(prop, values)`

Automatically add new select/multi_select options to the schema if they don't exist.

```python
collection.check_schema_select_options(
    prop={"id": "abc1", "name": "Status", "type": "select"},
    values=["New Status Option"]
)
```

## CollectionRowBlock

A single row in a database. Extends `PageBlock`.

### Dynamic Property Access

Database columns are automatically mapped to Python attributes using slugified column names. "Estimated Value" becomes `row.estimated_value`.

```python
# Read properties
print(row.name)
print(row.estimated_value)
print(row.tags)
print(row.assigned_to)

# Write properties
row.name = "Updated Name"
row.estimated_value = 500
row.tags = ["Important", "Urgent"]
row.is_confirmed = True
```

### Explicit Property Methods

#### `get_property(identifier)`

Get a property value by name, slug, or ID.

```python
value = row.get_property("estimated_value")
value = row.get_property("Estimated Value")  # by display name
value = row.get_property("abc1")             # by internal ID
```

#### `set_property(identifier, val)`

Set a property value by name, slug, or ID.

```python
row.set_property("estimated_value", 100)
row.set_property("Status", "Done")
```

#### `get_all_properties()`

Returns a dict of all property values.

```python
props = row.get_all_properties()
# {"name": "Item 1", "status": "Active", "estimated_value": 100, ...}
```

### Supported Property Types

| Property Type | Python Read Type | Python Write Type | Example |
|---------------|-----------------|-------------------|---------|
| `title` | `str` | `str` | `row.name = "Title"` |
| `text` | `str` | `str` | `row.notes = "Some text"` |
| `number` | `int` / `float` | `int` / `float` | `row.price = 9.99` |
| `select` | `str` / `None` | `str` | `row.status = "Done"` |
| `multi_select` | `list[str]` | `list[str]` | `row.tags = ["A", "B"]` |
| `date` | `NotionDate` | `NotionDate` / `date` / `datetime` | See NotionDate below |
| `person` | `list[User]` | `list[User]` / `list[str]` | `row.person = client.current_user` |
| `file` | `list[str]` (URLs) | `list[str]` (URLs) | `row.files = ["https://..."]` |
| `checkbox` | `bool` | `bool` | `row.is_confirmed = True` |
| `url` | `str` | `str` | `row.website = "https://..."` |
| `email` | `str` | `str` | `row.contact = "a@b.com"` |
| `phone_number` | `str` | `str` | `row.phone = "+1234567890"` |
| `relation` | `list[Block]` | `list[Block]` / `list[str]` | `row.related = [other_page]` |
| `created_time` | `datetime` | Read-only | -- |
| `last_edited_time` | `datetime` | Read-only | -- |
| `created_by` | `User` | Read-only | -- |
| `last_edited_by` | `User` | Read-only | -- |
| `formula` | (varies) | **Read-only** (computed server-side) | -- |
| `rollup` | (varies) | **Read-only** (computed server-side) | -- |

### NotionDate

Helper class for date properties. Supports single dates, date ranges, timezones, and reminders.

```python
from notion.collection import NotionDate
from datetime import date, datetime

# Single date
row.due_date = NotionDate(date(2025, 6, 15))

# Date range
row.date_range = NotionDate(date(2025, 6, 15), end=date(2025, 6, 20))

# With time and timezone
row.meeting = NotionDate(
    datetime(2025, 6, 15, 14, 30),
    timezone="America/New_York"
)

# Reading a date
nd = row.due_date
print(nd.start)     # date or datetime
print(nd.end)       # date, datetime, or None
print(nd.timezone)  # str or None
```

### Row as a Page

Since `CollectionRowBlock` extends `PageBlock`, rows also support:
- `row.icon`, `row.cover` -- Page icon and cover
- `row.children` -- Child blocks within the row page
- `row.children.add_new(...)` -- Add content blocks to the row page
- `row.remove()` -- Delete the row

## CollectionView Types

| Class | `_type` | Description |
|-------|---------|-------------|
| `TableView` | `"table"` | Standard table view |
| `BoardView` | `"board"` | Kanban board view |
| `ListView` | `"list"` | Simple list view |
| `CalendarView` | `"calendar"` | Calendar view |
| `GalleryView` | `"gallery"` | Gallery/card view |

### CollectionView Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | View name |
| `type` | `str` | View type string |
| `parent` | `Block` | Parent block |

### `build_query(**kwargs)`

Build a query without executing it. Returns a `CollectionQuery`.

```python
query = cv.build_query(
    search="",
    filter=[],
    sort=[],
    aggregate=[],
    limit=100
)
result = query.execute()
```

### `default_query()`

Build a query using the view's saved query parameters (filters, sorts, etc.).

```python
result = cv.default_query().execute()
for row in result:
    print(row.name)
```

### BoardView Extra

| Property | Type | Description |
|----------|------|-------------|
| `group_by` | `str` | Property used for board columns |

## Querying Collections

### CollectionQuery

```python
query = cv.build_query(
    search="",           # Text search within rows
    type="table",        # Result type
    aggregate=[],        # Aggregation parameters
    aggregations=[],     # New-format aggregations
    filter=[],           # Filter conditions
    sort=[],             # Sort conditions
    calendar_by="",      # For calendar views
    group_by="",         # For board views
    limit=100            # Max results (-1 for all)
)
result = query.execute()
```

### Filter Syntax

Filters use Notion's internal format. Inspect the network tab in the browser for complex examples (look for `queryCollection` calls).

#### Basic filter

```python
filter_params = {
    "filters": [{
        "filter": {
            "value": {
                "type": "exact",
                "value": "Done"
            },
            "operator": "enum_is"
        },
        "property": "status"  # Use the property slug
    }],
    "operator": "and"
}
result = cv.build_query(filter=filter_params).execute()
```

#### Person filter

```python
filter_params = {
    "filters": [{
        "filter": {
            "value": {
                "type": "exact",
                "value": {
                    "table": "notion_user",
                    "id": client.current_user.id
                }
            },
            "operator": "person_contains"
        },
        "property": "assigned_to"
    }],
    "operator": "and"
}
```

#### Multiple filters (AND)

```python
filter_params = {
    "filters": [
        {
            "filter": {
                "value": {"type": "exact", "value": "Active"},
                "operator": "enum_is"
            },
            "property": "status"
        },
        {
            "filter": {
                "value": {"type": "exact", "value": 100},
                "operator": "number_greater_than"
            },
            "property": "estimated_value"
        }
    ],
    "operator": "and"
}
```

#### Multiple filters (OR)

```python
filter_params = {
    "filters": [
        {
            "filter": {
                "value": {"type": "exact", "value": "Active"},
                "operator": "enum_is"
            },
            "property": "status"
        },
        {
            "filter": {
                "value": {"type": "exact", "value": "Pending"},
                "operator": "enum_is"
            },
            "property": "status"
        }
    ],
    "operator": "or"
}
```

#### Common filter operators

| Operator | Applies To | Description |
|----------|-----------|-------------|
| `enum_is` | select | Exact match |
| `enum_is_not` | select | Not equal |
| `enum_contains` | multi_select | Contains option |
| `enum_does_not_contain` | multi_select | Does not contain |
| `string_is` | text/title | Exact string match |
| `string_is_not` | text/title | Not equal |
| `string_contains` | text/title | Contains substring |
| `string_starts_with` | text/title | Starts with |
| `number_equals` | number | Equal |
| `number_greater_than` | number | Greater than |
| `number_less_than` | number | Less than |
| `number_greater_than_or_equal_to` | number | >= |
| `number_less_than_or_equal_to` | number | <= |
| `date_is_before` | date | Before date |
| `date_is_after` | date | After date |
| `date_is_on_or_before` | date | On or before |
| `date_is_on_or_after` | date | On or after |
| `person_contains` | person | Contains user |
| `person_does_not_contain` | person | Does not contain user |
| `checkbox_is` | checkbox | Exact match |
| `is_empty` | any | Property is empty |
| `is_not_empty` | any | Property is not empty |

### Sort Syntax

```python
sort_params = [
    {
        "direction": "descending",  # or "ascending"
        "property": "estimated_value"  # property slug
    }
]
result = cv.build_query(sort=sort_params).execute()
```

#### Multiple sorts

```python
sort_params = [
    {"direction": "ascending", "property": "status"},
    {"direction": "descending", "property": "estimated_value"}
]
```

### Aggregation Syntax

```python
aggregate_params = [
    {
        "property": "estimated_value",
        "aggregator": "sum",
        "id": "total_value"  # custom ID to retrieve the result
    }
]
result = cv.build_query(aggregate=aggregate_params).execute()
print("Total:", result.get_aggregate("total_value"))
```

#### Common aggregators

| Aggregator | Applies To | Description |
|------------|-----------|-------------|
| `count` | any | Count of rows |
| `count_values` | any | Count of non-empty values |
| `unique` | any | Count of unique values |
| `empty` | any | Count of empty values |
| `not_empty` | any | Count of non-empty values |
| `sum` | number | Sum |
| `average` | number | Average |
| `median` | number | Median |
| `min` | number | Minimum |
| `max` | number | Maximum |
| `range` | number | Max - Min |
| `percent_empty` | any | Percentage empty |
| `percent_not_empty` | any | Percentage not empty |
| `percent_checked` | checkbox | Percentage checked |
| `percent_unchecked` | checkbox | Percentage unchecked |
| `earliest_date` | date | Earliest date |
| `latest_date` | date | Latest date |
| `date_range` | date | Date range span |

### Combining Query Parameters

```python
result = cv.build_query(
    filter=filter_params,
    sort=sort_params,
    aggregate=aggregate_params,
    limit=50
).execute()
```

### Inspecting View Queries

To see the full saved query from a view:

```python
query_data = cv.get("query2")
print(query_data)
```

## QueryResult

Query results are iterable, indexable, and have length.

```python
result = cv.default_query().execute()

# Iterate
for row in result:
    print(row.name)

# Index
first = result[0]

# Length
print(len(result))

# Contains
print(some_row in result)

# Total count (may differ from len if limit was applied)
print(result.total)

# Get aggregate value
total = result.get_aggregate("total_value")
```

### QueryResult Types

| Class | For View Type |
|-------|--------------|
| `TableQueryResult` | `"table"` |
| `BoardQueryResult` | `"board"` |
| `CalendarQueryResult` | `"calendar"` |
| `ListQueryResult` | `"list"` |
| `GalleryQueryResult` | `"gallery"` |

## Creating a New Database

```python
from notion.block import CollectionViewBlock

# Create a new inline database on a page
cvb = page.children.add_new(CollectionViewBlock, collection=collection)
view = cvb.views.add_new(view_type="table")

# Configure the view (required before it can be browsed in Notion)
# view.set("query", ...)
# view.set("format.board_groups", ...)
# view.set("format.board_properties", ...)
```

## Working with Templates

```python
# Access collection templates
templates = collection.templates
for tmpl in templates:
    print(tmpl.title)

# Create a new template
tmpl = collection.templates.add_new(title="My Template")
tmpl.children.add_new(TextBlock, title="Default content")
```
