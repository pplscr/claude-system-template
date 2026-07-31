#!/usr/bin/env python3
"""Trading 212 API Connector — REST client with pagination + caching.

Auth: HTTP Basic Auth (API_KEY:API_SECRET from ~/.claude/credentials.env).
Docs: https://t212public-api-docs.redoc.ly/
"""

import os
import re
import json
import time
import logging
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from base64 import b64encode

log = logging.getLogger("t212.connector")

# --- Credentials ---
CREDENTIALS_PATH = Path(os.environ.get(
    "CREDENTIALS_PATH",
    os.path.expanduser("~/.claude/credentials.env")
))


def _parse_creds() -> dict[str, str]:
    """Parse credentials.env shell-style file into a dict."""
    result = {}
    if not CREDENTIALS_PATH.exists():
        return result
    with open(CREDENTIALS_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:]
            # Match KEY="value", KEY='value', or KEY=value (no quotes)
            m = re.match(r'^(\w+)=["\'](.*)["\']$', line)
            if m:
                result[m.group(1)] = m.group(2)
            else:
                m = re.match(r'^(\w+)=(.+)$', line)
                if m:
                    val = m.group(2).strip().strip('"').strip("'")
                    result[m.group(1)] = val
    return result


# --- API Client ---
BASE_URL = "https://live.trading212.com/api/v0/equity"
REQUEST_TIMEOUT = 15  # seconds

# Rate limiting
RATE_LIMITS = {
    "account/summary": 5.0,
    "account/cash": 5.0,
    "positions": 1.0,
    "history/transactions": 1.5,
    "history/dividends": 1.5,
    "history/orders": 1.5,
    "history/exports": 30.0,
    "orders": 5.0,
}
_last_request: dict[str, float] = {}


class T212Client:
    """Trading 212 REST API client."""

    def __init__(self, base_url: str = BASE_URL, demo: bool = False):
        creds = _parse_creds()
        self.api_key = creds.get("TRADING212_API_KEY", "")
        self.api_secret = creds.get("TRADING212_API_SECRET", "")

        if demo:
            base_url = "https://demo.trading212.com/api/v0/equity"
        self.base_url = base_url.rstrip("/")

        if not self.api_key or not self.api_secret:
            log.warning("Trading 212 credentials not found in %s", CREDENTIALS_PATH)

        # Build auth header once
        auth_str = f"{self.api_key}:{self.api_secret}"
        self._auth_header = f"Basic {b64encode(auth_str.encode()).decode()}"

    # --- Low-level HTTP ---

    def _request(self, path: str, method: str = "GET", _retry: int = 0) -> dict | list:
        """Make an API request with rate limiting and bounded retries."""
        MAX_RETRIES = 3
        url = f"{self.base_url}/{path.lstrip('/')}"

        # Rate limit: wait if needed (with jitter)
        for prefix, min_interval in RATE_LIMITS.items():
            if path.lstrip("/").startswith(prefix):
                last = _last_request.get(prefix, 0)
                elapsed = time.monotonic() - last
                if elapsed < min_interval:
                    jitter = (hash(path) % 100) / 200  # 0..0.5s jitter
                    time.sleep(min_interval - elapsed + jitter)
                _last_request[prefix] = time.monotonic()
                break

        req = Request(url, headers={
            "Authorization": self._auth_header,
            "Accept": "application/json",
        })

        try:
            with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                data = resp.read()
                if not data:
                    return {}
                return json.loads(data)
        except HTTPError as e:
            if e.code == 429:
                if _retry >= MAX_RETRIES:
                    log.error("Rate limited %d times — giving up on %s", MAX_RETRIES, path)
                    raise RuntimeError(f"Trading 212 API rate limit exceeded after {MAX_RETRIES} retries")
                wait = 60 * (2 ** _retry)  # 60s, 120s, 240s
                log.warning("Rate limited (attempt %d/%d), sleeping %ds...", _retry + 1, MAX_RETRIES, wait)
                time.sleep(wait)
                return self._request(path, method, _retry + 1)
            log.error("HTTP %s on %s: %s", e.code, path, e.read()[:200])
            raise
        except URLError as e:
            log.error("Connection error on %s: %s", path, e)
            raise

    # --- Pagination helper ---

    def _paginate(self, path: str, limit: int = 50) -> list[dict]:
        """Fetch all pages from a cursor-paginated endpoint.

        Trading 212 returns nextPagePath in two formats:
        1. Full path: /api/v0/equity/history/...?cursor=...
        2. Query string only: limit=50&cursor=...&time=...
        """
        all_items = []
        current_path = f"{path}?limit={limit}"
        base_prefix = "/api/v0/equity/"

        while current_path:
            # Strip full API prefix if present
            if current_path.startswith(base_prefix):
                current_path = current_path[len(base_prefix):]

            log.debug("Paginating: %s", current_path[:80])
            resp = self._request(current_path)

            # Extract items
            items = resp.get("items", [])
            if not items and isinstance(resp, list):
                items = resp

            all_items.extend(items)
            log.debug("Got %d items (total: %d)", len(items), len(all_items))

            # Check for next page
            next_page = resp.get("nextPagePath") if isinstance(resp, dict) else None
            if next_page:
                # If nextPagePath is just a query string (no leading /), prepend the base path
                if not next_page.startswith("/"):
                    next_page = f"{path}?{next_page}"
                current_path = next_page
            else:
                break

        return all_items

    # --- Account ---

    def account_cash(self) -> dict:
        """Get cash balance: free, total, ppl, invested, blocked."""
        return self._request("account/cash")

    def account_summary(self) -> dict:
        """Get full account summary."""
        return self._request("account/summary")

    # --- Positions ---

    def positions(self) -> list[dict]:
        """Get all open positions."""
        return self._request("positions")

    # --- Pending Orders ---

    def pending_orders(self) -> list[dict]:
        """Get unfilled orders."""
        return self._request("orders")

    # --- History (with optional pagination) ---

    def transactions(self, paginate: bool = True) -> list[dict]:
        """Get transaction history (DEPOSIT, WITHDRAW, FEE, TRANSFER, INTEREST)."""
        if paginate:
            return self._paginate("history/transactions")
        return self._request("history/transactions?limit=50").get("items", [])

    def dividends(self, paginate: bool = True) -> list[dict]:
        """Get dividend history."""
        if paginate:
            return self._paginate("history/dividends")
        return self._request("history/dividends?limit=50").get("items", [])

    def orders_history(self, paginate: bool = True) -> list[dict]:
        """Get completed/cancelled orders with fills."""
        if paginate:
            return self._paginate("history/orders")
        return self._request("history/orders?limit=50").get("items", [])

    # --- Full snapshot ---

    def full_snapshot(self) -> dict:
        """Fetch complete account state: cash, positions, transactions, orders, dividends.

        Respects rate limits by spacing requests appropriately.
        """
        log.info("Fetching full Trading 212 snapshot...")

        # Fast endpoints first (no pagination)
        cash = self.account_cash()
        time.sleep(5)  # account/cash is 1 req/5s

        positions = self.positions()
        time.sleep(1)  # positions is 1 req/1s

        pending = self.pending_orders()
        time.sleep(5)  # orders is 1 req/5s

        # History endpoints with built-in pagination + rate limiting
        log.info("Fetching transactions (paginated)...")
        transactions = self.transactions()

        log.info("Fetching dividends (paginated)...")
        dividends = self.dividends()

        log.info("Fetching order history (paginated)...")
        orders_history = self.orders_history()

        return {
            "cash": cash,
            "positions": positions,
            "orders_pending": pending,
            "transactions": transactions,
            "dividends": dividends,
            "orders_history": orders_history,
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
