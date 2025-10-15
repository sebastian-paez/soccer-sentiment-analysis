import httpx
import asyncio
import os
from typing import List, Dict

async def fetch_subreddit_posts_with_comments(subreddit: str, limit: int = 10) -> List[Dict]:
    """
    Fetch the most recent posts and all comments for each post from a subreddit.
    Returns a list of dicts, each with post info and a list of comments.
    """
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"
    headers = {
        "User-Agent": "python:SoccerSentimentBot:1.0 (by /u/soccer_sentiment_bot)",
        "Accept": "application/json"
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"Reddit fetch failed: status {resp.status_code}, url: {url}")
            return []
        try:
            posts = resp.json().get("data", {}).get("children", [])
        except Exception as e:
            print(f"Reddit JSON decode error: {e}")
            return []
        results = []
        for p in posts:
            post_data = p["data"]
            post_url = f"https://reddit.com{post_data.get('permalink', '')}"
            post_info = {
                "source": f"Reddit/r/{subreddit}",
                "title": post_data.get("title"),
                "description": post_data.get("selftext"),
                "url": post_url,
                "date": post_data.get("created_utc"),
                "comments": []
            }
            # Fetch comments for this post
            comments_url = f"https://www.reddit.com{post_data.get('permalink', '')}.json"
            try:
                comments_resp = await client.get(comments_url, headers=headers)
                if comments_resp.status_code == 200:
                    comments_json = comments_resp.json()
                    # Comments are in the second element of the returned list
                    comments = comments_json[1].get("data", {}).get("children", [])
                    post_info["comments"] = [
                        c["data"].get("body")
                        for c in comments
                        if c["kind"] == "t1" and c["data"].get("body")
                    ]
                else:
                    print(f"Failed to fetch comments for {post_url}: status {comments_resp.status_code}")
            except Exception as e:
                print(f"Error fetching comments for {post_url}: {e}")
            results.append(post_info)
        return results

async def fetch_all_news() -> List[Dict]:
    """Return recent posts and all comments from r/Gunners subreddit."""
    try:
        posts_with_comments = await fetch_subreddit_posts_with_comments("Gunners", limit=10)
        return posts_with_comments
    except Exception as e:
        print("Error fetching from Reddit:", e)
        return []
