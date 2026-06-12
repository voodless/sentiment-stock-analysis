
from collections import defaultdict

import pandas as pd
import yfinance as yf

from web_scraper import RedditTickerCollector
from sentiment import SentimentAnalyzer 
from data_plot import plot_data

LABEL_SIGNS = {"positive": 1, "negative": -1, "neutral": 0}

# Minimum number of mentions for a ticker to be included in the plot. Adjust as needed.
MIN_MENTIONS = 2

TICKER_BLOCKLIST = {
    "CEO", "CFO", "USA", "USD", "GDP", "ETF", "IPO", "YOLO", "FOMO",
    "DD", "EPS", "ATH", "IMO", "LOL", "WSB", "API", "AI", "UK", "EU",
}


def collect_sentiments():
    """Scrape Reddit and return {ticker: average signed sentiment score}."""
    scraper = RedditTickerCollector()
    analyzer = SentimentAnalyzer()

    per_ticker = defaultdict(list)
    for post in scraper.scrape():
        result = analyzer.get_sentiment(post["text"])
        score = LABEL_SIGNS[result["sentiment"]] * result["confidence"]
        for ticker in post["tickers"]:
            if ticker not in TICKER_BLOCKLIST:
                per_ticker[ticker].append(score)

    return {
        ticker: sum(scores) / len(scores)
        for ticker, scores in per_ticker.items()
        if len(scores) >= MIN_MENTIONS
    }


def fetch_prices(ticker_sentiments):
    """Batch-download prices and return a DataFrame of valid tickers.

    Uses a 5-day window so the daily % change can be computed from the
    last two closes. Tickers yfinance can't resolve are dropped silently.
    """
    tickers = list(ticker_sentiments.keys())
    if not tickers:
        return pd.DataFrame(columns=["ticker", "close", "pct_change", "sentiment"])

    data = yf.download(tickers, period="5d", group_by="ticker",
                       auto_adjust=True, progress=False)

    rows = []
    for ticker in tickers:
        try:
            closes = data[ticker]["Close"].dropna()
            close = closes.iloc[-1]
            pct_change = (closes.iloc[-1] - closes.iloc[-2]) / closes.iloc[-2] * 100
        except (KeyError, IndexError):
            continue  # invalid ticker or not enough history — drop it
        rows.append({
            "ticker": ticker,
            "close": round(float(close), 2),
            "pct_change": round(float(pct_change), 2),
            "sentiment": round(ticker_sentiments[ticker], 3),
        })
    return pd.DataFrame(rows)


def main():
    print(">>> scraping and scoring sentiment...")
    ticker_sentiments = collect_sentiments()
    print(f">>> {len(ticker_sentiments)} tickers with >= {MIN_MENTIONS} mentions")

    print(">>> fetching prices from yfinance...")
    df = fetch_prices(ticker_sentiments)
    print(f">>> {len(df)} tickers validated with price data")

    if df.empty:
        print("Nothing to plot — try raising the post limit or "
              "loosening MIN_MENTIONS.")
        return

    df.to_csv("quotes.csv", index=False)
    print(">>> saved quotes.csv")

    plot_data(df)


if __name__ == "__main__":
    main()
