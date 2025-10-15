from fastapi import FastAPI, Query
from app.news_fetcher import fetch_all_news
from app.sentiment_analyzer import SocialSentiment
import uvicorn

app = FastAPI(title="Arsenal Sentiment Analyzer")
model = SocialSentiment()

@app.get("/average-sentiment")
async def average_sentiment():
    articles = await fetch_all_news()

    if not articles:
        return {"team": "Arsenal", "error": "No news found"}

    sentiments = {"positive": 0, "neutral": 0, "negative": 0}
    total = 0

    for a in articles:
        # Analyze post itself
        text = a.get("title", "") + " " + (a.get("description") or "")
        if text.strip():
            result = model.analyze(text)
            sentiments[result["sentiment"]] += 1
            total += 1
        # Analyze all comments
        for comment in a.get("comments", []):
            if comment and isinstance(comment, str) and comment.strip():
                result = model.analyze(comment)
                sentiments[result["sentiment"]] += 1
                total += 1

    avg_sentiment = {s: round(count / total, 3) for s, count in sentiments.items()} if total else {s: 0 for s in sentiments}

    dominant = max(avg_sentiment, key=avg_sentiment.get) if total else None

    return {
        "team": "Arsenal",
        "average_sentiment": avg_sentiment,
        "dominant_sentiment": dominant,
        "items_analyzed": total
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
