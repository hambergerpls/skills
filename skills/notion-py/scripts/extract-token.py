"""
Extract token_v2 via Browser Login

Demonstrates:
- Launching a headed browser for interactive Notion login
- Polling browser cookies via Playwright
- Extracting and securely saving the token_v2 cookie

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    1. Run: python extract-token.py
    2. Log in to Notion in the browser window that opens
    3. The script automatically detects login and saves your token_v2
"""

import os
import stat
import time

from playwright.sync_api import sync_playwright

# ── Configuration ─────────────────────────────────────────────────────────────

NOTION_LOGIN_URL = "https://www.notion.so/login"
COOKIE_NAME = "token_v2"
POLL_INTERVAL = 1  # seconds between cookie checks
DATA_DIR = os.environ.get("NOTION_DATA_DIR", os.path.expanduser("~/.notion-py"))
TOKEN_FILE = os.path.join(DATA_DIR, "token")


# ── Browser login & cookie extraction ────────────────────────────────────────

def extract_token():
    """Launch a visible browser, wait for the user to log in, extract token_v2."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(NOTION_LOGIN_URL)
        print("Browser opened. Please log in to Notion...")
        print(f"Waiting for {COOKIE_NAME} cookie...\n")

        token = None
        while token is None:
            time.sleep(POLL_INTERVAL)
            cookies = context.cookies(["https://www.notion.so"])
            for cookie in cookies:
                if cookie["name"] == COOKIE_NAME:
                    token = cookie["value"]
                    break

        browser.close()

    return token


# ── Save token securely ──────────────────────────────────────────────────────

def save_token(token):
    """Write token to ~/.notion-py/token with restrictive permissions."""
    os.makedirs(DATA_DIR, mode=0o700, exist_ok=True)

    with open(TOKEN_FILE, "w") as f:
        f.write(token)

    # Owner read/write only (0o600)
    os.chmod(TOKEN_FILE, stat.S_IRUSR | stat.S_IWUSR)

    print(f"Token saved to {TOKEN_FILE}")


# ── Load token helper ────────────────────────────────────────────────────────

def load_token():
    """Read a previously saved token from ~/.notion-py/token."""
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(
            f"No saved token found at {TOKEN_FILE}. "
            "Run this script first to log in and extract your token_v2."
        )

    with open(TOKEN_FILE, "r") as f:
        return f.read().strip()


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    token = extract_token()
    save_token(token)

    print(f"\ntoken_v2: {token}")
    print("\nYou can now use this token with NotionClient:")
    print("  from notion.client import NotionClient")
    print(f'  client = NotionClient(token_v2="{token[:8]}...")')
    print("\nOr load it from the saved file:")
    print("  from pathlib import Path")
    print("  token = Path('~/.notion-py/token').expanduser().read_text().strip()")
    print("  client = NotionClient(token_v2=token)")
