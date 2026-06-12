from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline
from collections import defaultdict
import torch
import web_scraper
import storage
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()


class SentimentAnalyzer:
    """
    Analyzes the sentiment of Reddit posts using the FinBERT model.
    """

    def __init__(self):
        """
        Initializes the FinBERT model and tokenizer.
        """
        model_name = "ProsusAI/finbert"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")

        self.finbert_pipeline = pipeline("sentiment-analysis",
                                         model=self.model,
                                         tokenizer=self.tokenizer,
                                         device=self.device,
                                         truncation=True,
                                         max_length=512
                                         )

    def get_sentiment(self, text):
        """
        Get the sentiment of a given text using the FinBERT model.
        """
        result = self.finbert_pipeline(text)
        sentiment = result[0]['label']
        confidence = result[0]['score']

        return {"text": text, "sentiment": sentiment, "confidence": round(confidence,4)}
 

if __name__ == "__main__":
    scraper = web_scraper.RedditTickerCollector()
    sentiment_analyzer = SentimentAnalyzer()
    ticker_sentiments = defaultdict(list)
    conn = storage.get_conn()
    run_at = datetime.now(timezone.utc).isoformat()
    rows = []

    for r in scraper.scrape():
        result = sentiment_analyzer.get_sentiment(r["text"])
        for ticker in r["tickers"]:
            rows.append((run_at, r["post_id"], r["subreddit"], ticker,
                        result["sentiment"], result["confidence"], r["title"]))

    storage.save_mentions(conn, rows)
    print("\nSummary")
    for ticker, results in sorted(ticker_sentiments.items(),
                                  key=lambda kv: len(kv[1]), reverse=True):
        if len(results) < 2:
            continue
        labels = [res["sentiment"] for res in results]
        print(f"{ticker}: {len(results)} mentions — "
              f"{labels.count('positive')} pos / "
              f"{labels.count('negative')} neg / "
              f"{labels.count('neutral')} neutral")
