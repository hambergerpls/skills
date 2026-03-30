"""
Database Operations with notion-py

Demonstrates:
- Accessing a database (collection) and its views
- Reading schema/column definitions
- Listing and iterating rows
- Adding new rows with various property types
- Querying with filters, sorts, and aggregations

Usage:
    1. Replace <YOUR_TOKEN_V2> with your token_v2 cookie value
    2. Replace <YOUR_DATABASE_VIEW_URL> with the URL of a Notion database view
       (must include the ?v= parameter)
    3. Run: python database-operations.py
"""

from datetime import date, datetime

from notion.client import NotionClient
from notion.collection import NotionDate

# ── Connect to Notion ─────────────────────────────────────────────────────────

TOKEN = "<YOUR_TOKEN_V2>"
DATABASE_VIEW_URL = "<YOUR_DATABASE_VIEW_URL>"

client = NotionClient(token_v2=TOKEN)

# Get the collection view (the URL must include ?v= for the specific view)
cv = client.get_collection_view(DATABASE_VIEW_URL)
collection = cv.collection

print(f"Database: {collection.name}")
print(f"View: {cv.name} (type: {cv.type})")


# ── Inspect the schema ────────────────────────────────────────────────────────

print("\nSchema (columns):")
for prop in collection.get_schema_properties():
    print(f"  {prop['name']:30s} slug={prop['slug']:30s} type={prop['type']}")
    if prop["type"] in ("select", "multi_select") and prop.get("options"):
        for opt in prop["options"]:
            print(f"    - {opt['value']} ({opt['color']})")


# ── List all rows ─────────────────────────────────────────────────────────────

print("\nAll rows:")
for row in collection.get_rows():
    print(f"  {row.name}")


# ── Read row properties ──────────────────────────────────────────────────────

rows = list(collection.get_rows())
if rows:
    row = rows[0]
    print(f"\nFirst row details:")

    # Dynamic attribute access (uses slugified column names)
    print(f"  Name: {row.name}")

    # Get all properties as a dict
    all_props = row.get_all_properties()
    for key, value in all_props.items():
        print(f"  {key}: {value}")

    # Get a specific property by name
    # value = row.get_property("Status")

    # Get a specific property by slug
    # value = row.get_property("estimated_value")


# ── Add a new row ─────────────────────────────────────────────────────────────

# Method 1: Create row then set properties
row = collection.add_row()
row.name = "New Item from API"

# Set various property types (adjust to match your schema):
# row.status = "In Progress"            # select
# row.tags = ["API", "Automated"]       # multi_select
# row.estimated_value = 250             # number
# row.is_confirmed = True               # checkbox
# row.website = "https://example.com"   # url
# row.contact = "hello@example.com"     # email
# row.phone = "+1-555-0100"             # phone_number
# row.person = client.current_user      # person (single)
# row.person = [client.current_user]    # person (list)
# row.files = ["https://example.com/doc.pdf"]  # file (list of URLs)

# Date property examples:
# row.due_date = NotionDate(date(2025, 12, 31))
# row.due_date = NotionDate(date(2025, 6, 1), end=date(2025, 6, 30))  # date range
# row.meeting = NotionDate(datetime(2025, 6, 15, 14, 30), timezone="America/New_York")

# Relation property (link to another page/row):
# other_page = client.get_block("other-page-uuid")
# row.related_items = [other_page]

# Method 2: Set properties inline during creation
# row = collection.add_row(
#     name="Inline Item",
#     status="Active",
#     estimated_value=100,
#     is_confirmed=True,
# )

print(f"\nCreated row: {row.name} (id: {row.id})")


# ── Query with the default view settings ──────────────────────────────────────

print("\nDefault query results (using view's saved filters/sorts):")
result = cv.default_query().execute()
for row in result:
    print(f"  {row.name}")
print(f"  Total: {result.total}")


# ── Text search ───────────────────────────────────────────────────────────────

search_term = "Item"
print(f"\nSearch for '{search_term}':")
for row in collection.get_rows(search=search_term):
    print(f"  {row.name}")


# ── Filtered query ────────────────────────────────────────────────────────────

# Filter by select property (exact match)
# Adjust "status" and "Active" to match your schema
filter_params = {
    "filters": [{
        "filter": {
            "value": {
                "type": "exact",
                "value": "Active"
            },
            "operator": "enum_is"
        },
        "property": "status"
    }],
    "operator": "and"
}

print("\nFiltered results (status = Active):")
result = cv.build_query(filter=filter_params).execute()
for row in result:
    print(f"  {row.name}")


# Filter by person property
filter_by_person = {
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

# print("\nFiltered results (assigned to me):")
# result = cv.build_query(filter=filter_by_person).execute()
# for row in result:
#     print(f"  {row.name}")


# Multiple filters combined with AND
filter_multiple = {
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

# print("\nFiltered results (Active AND value > 100):")
# result = cv.build_query(filter=filter_multiple).execute()
# for row in result:
#     print(f"  {row.name}: {row.estimated_value}")


# ── Sorted query ──────────────────────────────────────────────────────────────

sort_params = [{
    "direction": "descending",
    "property": "estimated_value"
}]

# print("\nSorted results (by value, descending):")
# result = cv.build_query(sort=sort_params).execute()
# for row in result:
#     print(f"  {row.name}: {row.estimated_value}")


# Multiple sort criteria
sort_multiple = [
    {"direction": "ascending", "property": "status"},
    {"direction": "descending", "property": "estimated_value"}
]


# ── Aggregation query ─────────────────────────────────────────────────────────

aggregate_params = [{
    "property": "estimated_value",
    "aggregator": "sum",
    "id": "total_value"
}]

# print("\nAggregation results:")
# result = cv.build_query(aggregate=aggregate_params).execute()
# print(f"  Total estimated value: {result.get_aggregate('total_value')}")


# Multiple aggregations
aggregate_multiple = [
    {"property": "estimated_value", "aggregator": "sum", "id": "total"},
    {"property": "estimated_value", "aggregator": "average", "id": "avg"},
    {"property": "estimated_value", "aggregator": "max", "id": "highest"},
    {"property": "name", "aggregator": "count", "id": "count"},
]

# print("\nMultiple aggregations:")
# result = cv.build_query(aggregate=aggregate_multiple).execute()
# print(f"  Count: {result.get_aggregate('count')}")
# print(f"  Total: {result.get_aggregate('total')}")
# print(f"  Average: {result.get_aggregate('avg')}")
# print(f"  Max: {result.get_aggregate('highest')}")


# ── Combined query (filter + sort + aggregate) ───────────────────────────────

# result = cv.build_query(
#     filter=filter_params,
#     sort=sort_params,
#     aggregate=aggregate_params,
#     limit=50
# ).execute()
# print(f"\nCombined query: {len(result)} results, total = {result.get_aggregate('total_value')}")


# ── Inspect view's saved query ────────────────────────────────────────────────

# See the full query configuration saved in the view
saved_query = cv.get("query2")
print(f"\nView's saved query: {saved_query}")


# ── Delete a row ──────────────────────────────────────────────────────────────

# row.remove()                # Soft-delete (move to trash)
# row.remove(permanently=True)  # Hard-delete (permanent)

print("\nDone!")
