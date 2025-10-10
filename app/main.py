from fastapi import FastAPI, Query
from app.news_fetcher import fetch_all_news
from app.sentiment_analyzer import FinBERTSentiment
import uvicorn

app = FastAPI(title="Financial Sentiment Analyzer")
model = FinBERTSentiment()

# @app.get("/analyze")
# async def analyze_ticker(ticker: str = Query(..., description="Stock ticker symbol, e.g. AAPL")):
#     articles = await fetch_all_news(ticker)
#     analyzed = []
#     for a in articles:
#         text = a["title"] + " " + (a["description"] or "")
#         sentiment = model.analyze(text)
#         analyzed.append({**a, **sentiment})
#     return {"ticker": ticker, "results": analyzed}

@app.get("/average-sentiment")
async def average_sentiment(ticker: str = Query(..., description="Stock ticker symbol, e.g. AAPL")):
    articles = await fetch_all_news(ticker)

    if not articles:
        return {"ticker": ticker, "error": "No news found"}

    sentiments = {"positive": 0, "neutral": 0, "negative": 0}
    total = 0

    for a in articles:
        text = a["title"] + " " + (a["description"] or "")
        result = model.analyze(text)
        sentiments[result["sentiment"]] += 1
        total += 1

    avg_sentiment = {s: round(count / total, 3) for s, count in sentiments.items()}

    dominant = max(avg_sentiment, key=avg_sentiment.get)

    return {
        "ticker": ticker,
        "average_sentiment": avg_sentiment,
        "dominant_sentiment": dominant,
        "articles_analyzed": total
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
