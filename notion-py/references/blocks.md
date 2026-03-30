# Block Types and Operations Reference

## Block Type Hierarchy

All block types extend the base `Block` class from `notion.block`. Each has a `_type` string matching Notion's internal type identifier.

```
Record (notion.records)
  |
  +-- Block (base)
  |     |
  |     +-- DividerBlock              _type = "divider"
  |     +-- ColumnListBlock           _type = "column_list"
  |     +-- ColumnBlock               _type = "column"
  |     |
  |     +-- BasicBlock (adds: title, title_plaintext, color, convert_to_type())
  |     |     +-- TextBlock           _type = "text"
  |     |     +-- TodoBlock           _type = "to_do"         (+ checked)
  |     |     +-- HeaderBlock         _type = "header"
  |     |     +-- SubheaderBlock      _type = "sub_header"
  |     |     +-- SubsubheaderBlock   _type = "sub_sub_header"
  |     |     +-- BulletedListBlock   _type = "bulleted_list"
  |     |     +-- NumberedListBlock   _type = "numbered_list"
  |     |     +-- ToggleBlock         _type = "toggle"
  |     |     +-- QuoteBlock          _type = "quote"
  |     |     +-- CodeBlock           _type = "code"          (+ language, wrap)
  |     |     +-- EquationBlock       _type = "equation"      (+ latex)
  |     |     +-- FactoryBlock        _type = "factory"       (template button)
  |     |     +-- CalloutBlock        _type = "callout"       (+ icon)
  |     |     +-- PageBlock           _type = "page"          (+ icon, cover, locked)
  |     |           +-- CollectionRowBlock                    (database row)
  |     |                 +-- TemplateBlock                   (template row)
  |     |
  |     +-- MediaBlock (adds: caption)
  |     |     +-- BreadcrumbBlock     _type = "breadcrumb"
  |     |     +-- LinkToCollectionBlock _type = "link_to_collection"
  |     |     +-- EmbedBlock          _type = "embed"         (+ source, display_source, height, width, full_width, page_width)
  |     |     |     +-- BookmarkBlock _type = "bookmark"      (+ bookmark_cover, bookmark_icon, description, link, title)
  |     |     |     +-- FramerBlock   _type = "framer"
  |     |     |     +-- TweetBlock    _type = "tweet"
  |     |     |     +-- GistBlock     _type = "gist"
  |     |     |     +-- DriveBlock    _type = "drive"
  |     |     |     +-- FigmaBlock    _type = "figma"
  |     |     |     +-- LoomBlock     _type = "loom"
  |     |     |     +-- TypeformBlock _type = "typeform"
  |     |     |     +-- CodepenBlock  _type = "codepen"
  |     |     |     +-- MapsBlock     _type = "maps"
  |     |     |     +-- InvisionBlock _type = "invision"
  |     |     |     |
  |     |     |     +-- EmbedOrUploadBlock (adds: file_id, upload_file(path))
  |     |     |           +-- VideoBlock  _type = "video"
  |     |     |           +-- FileBlock   _type = "file"      (+ size, title)
  |     |     |           +-- AudioBlock  _type = "audio"
  |     |     |           +-- PDFBlock    _type = "pdf"
  |     |     |           +-- ImageBlock  _type = "image"
  |     |     |
  |     |     +-- CollectionViewBlock _type = "collection_view"  (+ collection, views, title, description, locked)
  |     |           +-- CollectionViewPageBlock _type = "collection_view_page" (+ icon, cover)
```

**Total: 35 block types** registered in the `BLOCK_TYPES` dict.

## Import Cheat Sheet

```python
from notion.block import (
    # Content blocks
    TextBlock, TodoBlock, HeaderBlock, SubheaderBlock, SubsubheaderBlock,
    BulletedListBlock, NumberedListBlock, ToggleBlock, QuoteBlock,
    CodeBlock, EquationBlock, CalloutBlock, DividerBlock,

    # Page blocks
    PageBlock,

    # Layout blocks
    ColumnListBlock, ColumnBlock,

    # Media / Embed blocks
    EmbedBlock, BookmarkBlock, ImageBlock, VideoBlock, AudioBlock,
    FileBlock, PDFBlock, GistBlock, TweetBlock, FigmaBlock, DriveBlock,
    LoomBlock, TypeformBlock, CodepenBlock, MapsBlock, InvisionBlock,
    FramerBlock,

    # Database blocks
    CollectionViewBlock, CollectionViewPageBlock,

    # Misc
    BreadcrumbBlock, LinkToCollectionBlock, FactoryBlock,
)

from notion.collection import CollectionRowBlock, TemplateBlock
```

## Block Base Class (`Block`)

All blocks inherit these methods and properties.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | UUID of the block |
| `type` | `str` | Block type string (e.g., `"text"`, `"page"`) |
| `parent` | `Block`/`Collection`/`Space` | Parent of this block |
| `children` | `Children` | List-like object of child blocks |
| `is_alias` | `bool` | Whether this block is an alias (reference) |
| `space_info` | `dict` | Public page data (if applicable) |
| `alive` | `bool` | Whether the block has not been deleted |

### Methods

#### `children.add_new(block_class, **kwargs)`

Create and append a new child block.

```python
from notion.block import TextBlock, TodoBlock

text = page.children.add_new(TextBlock, title="Hello world")
todo = page.children.add_new(TodoBlock, title="Task", checked=False)
```

**kwargs** are set as properties on the new block after creation.

#### `children.add_alias(block)`

Add a reference (alias) to an existing block without changing its parent.

```python
page.children.add_alias(some_other_block)
```

#### `children.filter(type=None)`

Filter children by block type.

```python
from notion.block import TodoBlock
todos = page.children.filter(type=TodoBlock)
```

#### `children.shuffle()`

Randomize the order of child blocks.

#### `move_to(target_block, position)`

Move this block relative to another block.

| Position | Description |
|----------|-------------|
| `"before"` | Insert before target_block |
| `"after"` | Insert after target_block |
| `"first-child"` | Insert as first child of target_block |
| `"last-child"` | Insert as last child of target_block |

```python
my_block.move_to(target_block, "after")
my_block.move_to(parent_block, "first-child")
```

#### `remove(permanently=False)`

Delete the block.

```python
block.remove()                 # Soft-delete (move to trash)
block.remove(permanently=True) # Hard-delete (permanent)
```

#### `get_browseable_url()`

Returns the notion.so URL for this block.

```python
url = block.get_browseable_url()
print(url)  # "https://www.notion.so/myorg/Page-Title-abc123..."
```

#### `refresh()`

Force-refresh block data from the server.

```python
block.refresh()
print(block.title)  # Now shows latest server data
```

#### `get(path=None, default=None, force_refresh=False)`

Read raw data from the block's record. With no path, returns the full record dict.

```python
full_record = block.get()                    # Entire record
title_raw = block.get("properties.title")    # Specific path
```

#### `set(path, value)`

Write raw data to the block's record. Use with caution -- must match Notion's internal structure.

```python
block.set("format.block_color", "blue_background")
```

### Callback Methods

#### `add_callback(callback, callback_id=None, extra_kwargs=None)`

Register a change listener.

```python
def on_change(record, difference):
    print(f"Block {record.id} changed:", difference)

block.add_callback(on_change)
```

#### `remove_callbacks(callback_or_id=None)`

Remove change listeners. Pass `None` to remove all.

## BasicBlock Properties

All `BasicBlock` subclasses (text, headers, lists, etc.) have:

| Property | Type | Description |
|----------|------|-------------|
| `title` | `str` | Block text content (Markdown-aware) |
| `title_plaintext` | `str` | Plain text version (no formatting) |
| `color` | `str` | Text/background color |

### `convert_to_type(block_class)`

Convert a block to a different type in-place.

```python
from notion.block import HeaderBlock
text_block.convert_to_type(HeaderBlock)
# text_block is now a header
```

### Color Values

Text colors: `"gray"`, `"brown"`, `"orange"`, `"yellow"`, `"green"`, `"blue"`, `"purple"`, `"pink"`, `"red"`

Background colors: `"gray_background"`, `"brown_background"`, `"orange_background"`, `"yellow_background"`, `"green_background"`, `"blue_background"`, `"purple_background"`, `"pink_background"`, `"red_background"`

## Block Type Details

### TodoBlock

```python
todo = page.children.add_new(TodoBlock, title="Buy groceries")
todo.checked = True
print(todo.checked)  # True
```

| Property | Type | Description |
|----------|------|-------------|
| `checked` | `bool` | Whether the todo is checked off |

### CodeBlock

```python
code = page.children.add_new(CodeBlock, title="print('hello')", language="Python")
code.wrap = True
```

| Property | Type | Description |
|----------|------|-------------|
| `language` | `str` | Programming language for syntax highlighting |
| `wrap` | `bool` | Whether to wrap long lines |

### EquationBlock

```python
eq = page.children.add_new(EquationBlock, latex="E = mc^2")
```

| Property | Type | Description |
|----------|------|-------------|
| `latex` | `str` | LaTeX equation string |

### CalloutBlock

```python
callout = page.children.add_new(CalloutBlock, title="Important!", icon="!")
```

| Property | Type | Description |
|----------|------|-------------|
| `icon` | `str` | Icon emoji or URL |

### PageBlock

```python
subpage = page.children.add_new(PageBlock, title="Sub Page")
subpage.icon = "https://example.com/icon.png"
subpage.cover = "https://example.com/cover.jpg"
subpage.locked = True
```

| Property | Type | Description |
|----------|------|-------------|
| `icon` | `str` | Page icon (emoji or URL) |
| `cover` | `str` | Cover image URL |
| `locked` | `bool` | Whether the page is locked |

#### `get_backlinks()`

Returns list of blocks that reference this page.

```python
backlinks = page.get_backlinks()
for bl in backlinks:
    print(bl.title)
```

#### `extract_markdown()`

Export the page content as Markdown via Notion's export API.

```python
md_content = page.extract_markdown()
print(md_content)
```

### MediaBlock Properties

All media blocks (embeds, images, etc.) have:

| Property | Type | Description |
|----------|------|-------------|
| `caption` | `str` | Block caption text |

### EmbedBlock

```python
embed = page.children.add_new(EmbedBlock, width=600)
embed.set_source_url("https://www.youtube.com/watch?v=...")
```

| Property | Type | Description |
|----------|------|-------------|
| `source` | `str` | Source URL |
| `display_source` | `str` | Embedly-resolved display URL |
| `height` | `int` | Display height in pixels |
| `width` | `int` | Display width in pixels |
| `full_width` | `bool` | Full-width display |
| `page_width` | `bool` | Page-width display |

#### `set_source_url(url)`

Set the embed source URL and auto-resolve the display URL via Embedly.

### BookmarkBlock

```python
bm = page.children.add_new(BookmarkBlock)
bm.set_new_link("https://example.com")
```

| Property | Type | Description |
|----------|------|-------------|
| `bookmark_cover` | `str` | Cover image URL |
| `bookmark_icon` | `str` | Favicon URL |
| `description` | `str` | Page description |
| `link` | `str` | Bookmark URL |
| `title` | `str` | Page title |

#### `set_new_link(url)`

Update the bookmark URL and refresh metadata from the page.

### EmbedOrUploadBlock (Video, File, Audio, PDF, Image)

These blocks support file uploads in addition to URL sources.

| Property | Type | Description |
|----------|------|-------------|
| `file_id` | `str` | ID of the uploaded file |

#### `upload_file(path)`

Upload a local file to Notion's S3 storage and attach it to the block.

```python
from notion.block import ImageBlock, FileBlock, VideoBlock, AudioBlock, PDFBlock

img = page.children.add_new(ImageBlock)
img.upload_file("/path/to/photo.png")

file_block = page.children.add_new(FileBlock)
file_block.upload_file("/path/to/document.pdf")

video = page.children.add_new(VideoBlock)
video.upload_file("/path/to/video.mp4")
```

**FileBlock** additional properties:

| Property | Type | Description |
|----------|------|-------------|
| `size` | `int` | File size |
| `title` | `str` | File title |

### CollectionViewBlock

Inline database block. See [collections.md](collections.md) for full database documentation.

| Property | Type | Description |
|----------|------|-------------|
| `collection` | `Collection` | The database object |
| `views` | `Views` | List-like of `CollectionView` objects |
| `title` | `str` | Database title |
| `description` | `str` | Database description |
| `locked` | `bool` | Whether the database is locked |

### CollectionViewPageBlock

Full-page database block. Same as `CollectionViewBlock` plus:

| Property | Type | Description |
|----------|------|-------------|
| `icon` | `str` | Page icon |
| `cover` | `str` | Cover image URL |

### ColumnListBlock and ColumnBlock

Used for multi-column layouts.

```python
from notion.block import ColumnListBlock, ColumnBlock, TextBlock

col_list = page.children.add_new(ColumnListBlock)
col1 = col_list.children.add_new(ColumnBlock)
col2 = col_list.children.add_new(ColumnBlock)

col1.children.add_new(TextBlock, title="Left column content")
col2.children.add_new(TextBlock, title="Right column content")
```

### DividerBlock

A horizontal divider line. Has no additional properties.

```python
from notion.block import DividerBlock
page.children.add_new(DividerBlock)
```

### FactoryBlock

A template button that creates blocks when clicked.

```python
from notion.block import FactoryBlock
factory = page.children.add_new(FactoryBlock, title="Add new item")
# Configure the template blocks as children of the factory
```

## Block Type Registry

The `BLOCK_TYPES` dict maps type strings to classes. Used internally by `get_block()` to instantiate the correct class.

```python
from notion.block import BLOCK_TYPES

# Lookup class by type string
block_class = BLOCK_TYPES.get("to_do")  # TodoBlock
```

| Type String | Class |
|-------------|-------|
| `"text"` | `TextBlock` |
| `"to_do"` | `TodoBlock` |
| `"header"` | `HeaderBlock` |
| `"sub_header"` | `SubheaderBlock` |
| `"sub_sub_header"` | `SubsubheaderBlock` |
| `"bulleted_list"` | `BulletedListBlock` |
| `"numbered_list"` | `NumberedListBlock` |
| `"toggle"` | `ToggleBlock` |
| `"quote"` | `QuoteBlock` |
| `"code"` | `CodeBlock` |
| `"equation"` | `EquationBlock` |
| `"callout"` | `CalloutBlock` |
| `"divider"` | `DividerBlock` |
| `"column_list"` | `ColumnListBlock` |
| `"column"` | `ColumnBlock` |
| `"factory"` | `FactoryBlock` |
| `"page"` | `PageBlock` |
| `"bookmark"` | `BookmarkBlock` |
| `"embed"` | `EmbedBlock` |
| `"image"` | `ImageBlock` |
| `"video"` | `VideoBlock` |
| `"audio"` | `AudioBlock` |
| `"file"` | `FileBlock` |
| `"pdf"` | `PDFBlock` |
| `"gist"` | `GistBlock` |
| `"tweet"` | `TweetBlock` |
| `"drive"` | `DriveBlock` |
| `"figma"` | `FigmaBlock` |
| `"loom"` | `LoomBlock` |
| `"typeform"` | `TypeformBlock` |
| `"codepen"` | `CodepenBlock` |
| `"maps"` | `MapsBlock` |
| `"invision"` | `InvisionBlock` |
| `"framer"` | `FramerBlock` |
| `"breadcrumb"` | `BreadcrumbBlock` |
| `"link_to_collection"` | `LinkToCollectionBlock` |
| `"collection_view"` | `CollectionViewBlock` |
| `"collection_view_page"` | `CollectionViewPageBlock` |
