#!/usr/bin/env python3
"""
Financial News Collector — multi-source with lazy loading and caching.

Sources (free, no API key needed):
  - Google News RSS
  - Yahoo Finance RSS

Sources (free, needs API key):
  - Finnhub: 60 req/min
  - Alpha Vantage: 25 req/day (NEWS_SENTIMENT)
  - Reddit: free API, no key needed for read

Usage:
  python3 collector.py                    # collect for top 15 positions
  python3 collector.py --ticker AAPL      # single ticker
  python3 collector.py --all              # all 60 positions (slow)
  python3 collector.py --force            # ignore cache
"""

import json
import sys
import time
import random
import logging
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timedelta, timezone

log = logging.getLogger("news.collector")

# ── Paths ──────────────────────────────────────────────
HOME = Path.home()
FINANCE = HOME / "spaces" / "finance"
DATA_DIR = FINANCE / "news"
CACHE_FILE = DATA_DIR / "news_cache.json"
POSITIONS_FILE = FINANCE / "trading212" / "positions.json"
CREDENTIALS_PATH = HOME / ".claude" / "credentials.env"

# ── Cache TTL ──────────────────────────────────────────
CACHE_TTL_HOURS = 2  # Refresh news every 2 hours
REQUEST_DELAY = 1.0   # Seconds between API calls (be polite)
MAX_TICKERS_DEFAULT = 15


def _parse_creds() -> dict:
    """Parse shell-style credentials.env."""
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
            if '="' in line:
                k, v = line.split('="', 1)
                result[k] = v.rstrip('"')
            elif "='" in line:
                k, v = line.split("='", 1)
                result[k] = v.rstrip("'")
            elif "=" in line:
                k, v = line.split("=", 1)
                result[k] = v.strip().strip('"').strip("'")
    return result


def get_positions(top_n: int = MAX_TICKERS_DEFAULT) -> list[dict]:
    """Get top positions by market value."""
    if not POSITIONS_FILE.exists():
        log.warning("Positions file not found: %s", POSITIONS_FILE)
        return []
    with open(POSITIONS_FILE) as f:
        positions = json.load(f)
    for p in positions:
        p["_value"] = p.get("quantity", 0) * p.get("currentPrice", 0)
    positions.sort(key=lambda p: abs(p["_value"]), reverse=True)
    return positions[:top_n]


def extract_ticker_symbol(full_ticker: str) -> str:
    """Extract base symbol from T212 ticker format.

    Examples:
        AAPL_US_EQ -> AAPL
        WGLDd_EQ -> WGLDd (WisdomTree Gold — keep full)
        SXR8d_EQ -> SXR8d (iShares S&P 500 — keep full)
        KMB_US_EQ -> KMB
    """
    # For US stocks: remove _US_EQ suffix
    if "_US_EQ" in full_ticker:
        return full_ticker.replace("_US_EQ", "")
    # For European ETFs: keep as-is but remove exchange suffix
    if "_EQ" in full_ticker:
        # Try to get just the base symbol
        parts = full_ticker.split("_")
        return parts[0] if parts else full_ticker
    return full_ticker


# ═══════════════════════════════════════════════════════════
# NEWS SOURCES
# ═══════════════════════════════════════════════════════════

def fetch_google_news(ticker: str, max_results: int = 5) -> list[dict]:
    """Google News RSS — free, no API key, global coverage."""
    try:
        # Google News uses the base symbol
        symbol = extract_ticker_symbol(ticker)
        query = urllib.parse.quote(f"{symbol} stock OR earnings OR dividend")
        url = f"https://news.google.com/rss/search?q={query}&hl=en&ceid=US:en"
        req = urllib.request.Request(url, headers={"User-Agent": "FinanceBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        root = ET.fromstring(data)
        items = []
        for item in root.findall(".//item")[:max_results]:
            items.append({
                "title": item.findtext("title", ""),
                "link": item.findtext("link", ""),
                "published": item.findtext("pubDate", ""),
                "source": "Google News",
                "ticker": ticker,
            })
        return items
    except Exception as e:
        log.debug("Google News [%s]: %s", ticker, str(e)[:80])
        return []


def fetch_yahoo_news(ticker: str) -> list[dict]:
    """Yahoo Finance RSS — free, no API key."""
    try:
        symbol = extract_ticker_symbol(ticker)
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
        req = urllib.request.Request(url, headers={"User-Agent": "FinanceBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        root = ET.fromstring(data)
        items = []
        for item in root.findall(".//item")[:5]:
            items.append({
                "title": item.findtext("title", ""),
                "link": item.findtext("link", ""),
                "published": item.findtext("pubDate", ""),
                "source": "Yahoo Finance",
                "ticker": ticker,
            })
        return items
    except Exception as e:
        log.debug("Yahoo [%s]: %s", ticker, str(e)[:80])
        return []


def fetch_reddit_sentiment(ticker: str) -> list[dict]:
    """Reddit API — free, no key needed. Searches investment subreddits."""
    try:
        symbol = extract_ticker_symbol(ticker)
        # Search r/wallstreetbets + r/stocks + r/investing
        subreddits = "wallstreetbets+stocks+investing"
        query = urllib.parse.quote(f"{symbol}")
        url = f"https://www.reddit.com/r/{subreddits}/search.json?q={query}&sort=new&limit=5&t=week"
        req = urllib.request.Request(url, headers={
            "User-Agent": "FinanceBot/1.0 (by /u/ruslanmaneliuk)"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        items = []
        for post in data.get("data", {}).get("children", []):
            d = post["data"]
            items.append({
                "title": d.get("title", ""),
                "link": f"https://reddit.com{d.get('permalink', '')}",
                "published": datetime.fromtimestamp(
                    d.get("created_utc", 0), tz=timezone.utc
                ).isoformat(),
                "source": f"r/{d.get('subreddit', '?')}",
                "ticker": ticker,
                "score": d.get("score", 0),
                "num_comments": d.get("num_comments", 0),
            })
        return items
    except Exception as e:
        log.debug("Reddit [%s]: %s", ticker, str(e)[:80])
        return []


def fetch_finnhub_news(ticker: str, api_key: str) -> list[dict]:
    """Finnhub company news — 60 req/min free."""
    try:
        symbol = extract_ticker_symbol(ticker)
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        url = (
            f"https://finnhub.io/api/v1/company-news"
            f"?symbol={symbol}&from={week_ago.strftime('%Y-%m-%d')}"
            f"&to={today.strftime('%Y-%m-%d')}&token={api_key}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "FinanceBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        items = []
        for article in data[:5]:
            items.append({
                "title": article.get("headline", ""),
                "link": article.get("url", ""),
                "published": article.get("datetime", ""),
                "source": article.get("source", "Finnhub"),
                "summary": article.get("summary", "")[:300],
                "category": article.get("category", ""),
                "ticker": ticker,
            })
        return items
    except Exception as e:
        log.debug("Finnhub [%s]: %s", ticker, str(e)[:80])
        return []


# ═══════════════════════════════════════════════════════════
# MAIN COLLECTOR
# ═══════════════════════════════════════════════════════════

def load_cache() -> dict:
    """Load existing news cache."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError):
            pass
    return {"news": {}, "collected_at": None}


def is_cache_fresh(cache: dict) -> bool:
    """Check if cache is still valid."""
    collected = cache.get("collected_at")
    if not collected:
        return False
    try:
        collected_time = datetime.fromisoformat(collected)
        age = datetime.now() - collected_time
        return age < timedelta(hours=CACHE_TTL_HOURS)
    except (ValueError, TypeError):
        return False


def collect_all(
    top_n: int = MAX_TICKERS_DEFAULT,
    force: bool = False,
    single_ticker: str = None,
    use_reddit: bool = True,
    use_finnhub: bool = False,
) -> dict:
    """Collect news for portfolio positions.

    Args:
        top_n: Number of top positions to scan (default 15)
        force: Ignore cache, re-fetch
        single_ticker: Only fetch this ticker
        use_reddit: Include Reddit search
        use_finnhub: Include Finnhub (needs API key)
    """
    # Check cache
    cache = load_cache()
    if not force and is_cache_fresh(cache):
        total = sum(len(v) for v in cache.get("news", {}).values())
        log.info("Cache fresh (%d items, %s). Use --force to refresh.",
                 total, cache["collected_at"][:19])
        return cache

    # Get tickers
    if single_ticker:
        positions = [{"instrument": {"ticker": single_ticker}, "ticker": single_ticker}]
    else:
        positions = get_positions(top_n)

    tickers = [p.get("instrument", {}).get("ticker", p.get("ticker", "?"))
               for p in positions]
    tickers = [t for t in tickers if t and t != "?"]

    # API keys
    creds = _parse_creds()
    finnhub_key = creds.get("FINNHUB_API_KEY", "")

    all_news = cache.get("news", {}) if not force else {}
    total_new = 0

    for i, ticker in enumerate(tickers):
        # Skip if in cache and not forced
        if ticker in all_news and not force:
            continue

        news = []

        # 1. Google News (always on, free)
        gnews = fetch_google_news(ticker)
        news.extend(gnews)

        # Polite delay
        if i < len(tickers) - 1:
            time.sleep(REQUEST_DELAY + random.uniform(0, 0.5))

        # 2. Yahoo Finance (always on, free)
        ynews = fetch_yahoo_news(ticker)
        news.extend(ynews)

        # 3. Reddit (free, rate-limited but generous)
        if use_reddit:
            time.sleep(0.5 + random.uniform(0, 0.5))
            rnews = fetch_reddit_sentiment(ticker)
            news.extend(rnews)

        # 4. Finnhub (needs API key)
        if use_finnhub and finnhub_key:
            time.sleep(1)
            fnews = fetch_finnhub_news(ticker, finnhub_key)
            news.extend(fnews)

        # Deduplicate
        seen = set()
        unique = []
        for n in news:
            key = n["title"][:100]
            if key not in seen:
                seen.add(key)
                unique.append(n)

        if unique:
            all_news[ticker] = unique
            total_new += len(unique)
            log.info("%s: %d news (G:%d Y:%d R:%d)",
                     ticker, len(unique),
                     len(gnews), len(ynews),
                     len(rnews) if use_reddit else 0)
        else:
            log.debug("%s: 0 news", ticker)

    # Save
    result = {
        "collected_at": datetime.now().isoformat(),
        "tickers_scanned": len(tickers),
        "tickers_with_news": len(all_news),
        "total_items": sum(len(v) for v in all_news.values()),
        "news": all_news,
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)

    return result


# ═══════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    args = sys.argv[1:]
    kwargs = {"force": "--force" in args}

    if "--all" in args:
        kwargs["top_n"] = 60
    if "--reddit" in args:
        kwargs["use_reddit"] = True
    if "--finnhub" in args:
        kwargs["use_finnhub"] = True

    # Single ticker
    for a in args:
        if a.startswith("--ticker="):
            kwargs["single_ticker"] = a.split("=", 1)[1]

    result = collect_all(**kwargs)

    print(f"\n📰 {result['total_items']} news items for "
          f"{result['tickers_with_news']}/{result['tickers_scanned']} tickers")
    print(f"💾 Cache: {CACHE_FILE}")
    print(f"🕐 Collected: {result['collected_at'][:19]}")
