import httpx
import asyncio
from typing import List, Dict
import feedparser

async def fetch_yahoo_rss(ticker: str) -> List[Dict]:
    rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
    feed = feedparser.parse(rss_url)
    return [
        {"source": "Yahoo Finance", "title": entry.title, "description": entry.summary, "url": entry.link}
        for entry in feed.entries
    ]

async def fetch_reddit(ticker: str) -> List[Dict]:
    url = f"https://www.reddit.com/r/stocks/search.json?q={ticker}&restrict_sr=1&limit=10"
    headers = {"User-Agent": "FinancialSentimentBot/1.0"}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, headers=headers)
        posts = resp.json().get("data", {}).get("children", [])
        return [
            {"source": "Reddit", "title": p["data"]["title"], "description": p["data"]["selftext"], "url": f"https://reddit.com{p['data']['permalink']}"}
            for p in posts
        ]

async def fetch_all_news(ticker: str) -> List[Dict]:
    results = await asyncio.gather(
        fetch_yahoo_rss(ticker),
        fetch_reddit(ticker),
        return_exceptions=True
    )

    articles = []
    for r in results:
        if isinstance(r, Exception):
            print("Error:", r)
        else:
            articles.extend(r)
    return articles
