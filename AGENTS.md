# AGENTS.md

## Repository Overview

This is a **skills collection repository** -- a knowledge base of structured reference material designed for AI coding agents. It is **not** a traditional software application. Each "skill" is a self-contained package of documentation, API references, and runnable example templates for a specific library or tool.

### Directory Structure

```
skills/
  <skill-name>/
    SKILL.md              # Skill manifest and primary documentation
    references/           # Detailed API reference docs (Markdown)
      <topic>.md
    templates/            # Runnable example scripts
      <example-name>.py
devenv.nix                # Nix-based dev environment config
devenv.yaml               # Nix input sources
devenv.lock               # Pinned Nix inputs
.gitignore
```

## Development Environment

The dev environment uses [devenv](https://devenv.sh/) (Nix-based). It provisions **Python 3.13** with a virtual environment.

```bash
# Enter the development shell
devenv shell

# Install Python dependencies (inside devenv shell)
pip install <package>
```

## Build / Lint / Test Commands

**There are no build, lint, test, or format commands.** This repository contains only documentation and example scripts. There is no CI/CD pipeline, no test framework, and no linter configuration.

- Python files under `templates/` are **illustrative examples**, not application code or tests.
- Do not attempt to run templates without user-provided credentials (e.g., `token_v2`).
- There is no `package.json`, `Makefile`, `pyproject.toml`, or equivalent build config.

## Skill Authoring Guide

### Creating a New Skill

1. Create a directory: `skills/<skill-name>/`
2. Add `SKILL.md` with YAML frontmatter and comprehensive documentation
3. Add `references/` with detailed API reference Markdown files
4. Add `templates/` with runnable example scripts

### SKILL.md Format

Every `SKILL.md` must begin with YAML frontmatter:

```yaml
---
name: <skill-name>            # Lowercase, hyphenated identifier
description: >-               # One-line description of when to use this skill.
  Brief description of the library/tool and when an agent should use it.
metadata:
  author: <author>             # Original library/tool author
  version: "<version>"         # Skill version (semver, quoted)
  source: <url>                # Link to the upstream project
---
```

After frontmatter, the document follows this structure:

1. **H1 title** -- matches `name` from frontmatter
2. **Overview paragraph** -- what the library does, key capabilities, caveats
3. **Setup & Installation** -- install commands, auth, initialization
4. **Core Workflow** -- the typical usage pattern, numbered steps
5. **Code examples** -- grouped by topic with H3 headings
6. **Important Notes & Gotchas** -- bullet list of pitfalls and edge cases
7. **Deep-dive Documentation** -- table linking to `references/*.md`
8. **Templates** -- table linking to `templates/*.py` with descriptions

### References Directory

Each file in `references/` covers one API surface area (e.g., `client.md`, `blocks.md`, `collections.md`, `utilities.md`). Structure:

- **H1 title** -- e.g., `# NotionClient API Reference`
- **Constructor / class signature** in a code block
- **Methods grouped by category** under H2/H3 headings
- **Parameters documented inline** as code comments
- **Return types and behaviors** described in prose after code blocks

### Templates Directory

Each template is a self-contained, runnable script demonstrating a specific workflow. See the Python style conventions below.

## Code Style Guidelines

### Markdown Files

- Use **ATX-style headings** (`#`, `##`, `###`) -- not underline style.
- Use **fenced code blocks** with language tags (` ```python `, ` ```bash `, ` ```yaml `).
- Use **pipe tables** for structured links (references, templates). Align columns.
- Use **bullet lists** (`-`) for notes, gotchas, and unordered items. Use **numbered lists** (`1.`) for sequential steps.
- Keep lines at a reasonable length. No hard wrap requirement, but avoid extremely long lines.
- One blank line between all block-level elements (headings, paragraphs, code blocks, lists, tables).
- No trailing whitespace. Files end with a single newline.

### Python Templates

**Module docstring** -- every template starts with a triple-quoted docstring:

```python
"""
<Title>

Demonstrates:
- Feature 1
- Feature 2

Usage:
    1. Replace <PLACEHOLDER> with your value
    2. Run: python <script-name>.py
"""
```

**Imports:**
- Standard library imports first, then a blank line, then third-party imports.
- Group related imports from the same package using parenthesized multi-line imports.
- Sort imports logically by category, not strictly alphabetically.

```python
from datetime import date, datetime

from notion.client import NotionClient
from notion.block import (
    TextBlock,
    TodoBlock,
    HeaderBlock,
)
```

**Section comments** -- use box-drawing characters to visually separate sections:

```python
# -- Section Name -------------------------------------------------------
```

The existing codebase uses Unicode box-drawing (`──`). Either form is acceptable; be consistent within a file.

**Naming conventions:**
- `UPPER_CASE` for constants and placeholder values (e.g., `TOKEN`, `PAGE_URL`)
- `snake_case` for variables, functions, and method names
- Descriptive names -- `page`, `client`, `header`, `todo1` -- not abbreviations

**Formatting:**
- Use **f-strings** for string interpolation, not `.format()` or `%`.
- Use `getattr(obj, 'attr', default)` for safe attribute access.
- Inline comments for non-obvious operations.
- No type annotations in templates -- keep examples simple and approachable.
- Two blank lines before each section comment block.
- Prefer explicit over implicit: show each step rather than chaining.

**Error handling:**
- Templates are demonstrative; they do not need try/except blocks.
- Note dangerous operations with comments (e.g., `# Hard-delete (permanent)`).
- Clearly mark placeholders that users must replace: `<YOUR_TOKEN_V2>`, `<YOUR_PAGE_URL>`.

### General Conventions

- **Encoding:** UTF-8 everywhere.
- **Line endings:** LF (Unix-style), not CRLF.
- **Final newline:** All files end with exactly one newline.
- **No secrets:** Never commit real tokens, passwords, or API keys. Use placeholder strings.
- **Skill naming:** Lowercase, hyphenated (e.g., `notion-py`, `aws-s3-client`).
- **File naming:** Lowercase, hyphenated for Markdown (e.g., `client.md`). Lowercase, hyphenated for Python templates (e.g., `basic-page-operations.py`).

## Agent Instructions

- No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md` files exist in this repository.
- No existing CI checks need to pass before committing.
- The `master` branch is the primary branch.
- When adding a new skill, follow the exact directory structure and file conventions documented above.
- When modifying an existing skill, preserve the established formatting patterns within that skill's files.
