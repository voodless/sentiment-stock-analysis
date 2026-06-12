import praw
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

SUBREDDITS = [
    "stocks",
    "wallstreetbets",
    "investing",
    "personalfinance",
    "StockMarket",
    "financialindependence",
    "SecurityAnalysis",
]


def load_valid_tickers():
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "StockSentimentScraper (eliebapaga@gmail.com)"} 
    data = requests.get(url, headers=headers, timeout=10).json()
    return {entry["ticker"] for entry in data.values()}


class RedditTickerCollector:
    """
    secret(str) : reddit API secret key
    id(str) : reddit API client ID
    agent(str) : Reddit user agent
    ticker_pattern: Regex pattern to match stock tickers
    """

    def __init__(self):
        """
        initialise reddit API credentials
        """
        self.secret = os.getenv("SECRET")
        self.id = os.getenv("ID")
        self.agent = os.getenv("USERAGENT")
        self.valid_tickers = load_valid_tickers()
        self.ticker_pattern = re.compile(r"\$[A-Z]{1,5}\b|\b[A-Z]{2,5}\b")
        self.blocklist = {"NOT", "ALL", "SO", "IT", "WM", "JOE", "CC", "DO",
                          "OR", "BUT", "FU", "RE", "ET", "FWD", "CAP", "WILL",
                          "WIN", "WHO", "GW", "ND", "MW", "PE", "TA", "IP", "EOY"}
        self.blocklist |= {"AI", "DD", "USA", "EU", "IRS", "API", "NYC",
                           "CPA", "ACA", "SBC", "STEM", "USO"}
        if not all([self.secret, self.id, self.agent]):
            raise ValueError("Reddit API credentials are not fully set in environment variables.")
        
        self.reddit = praw.Reddit(client_id=self.id,
                                  client_secret=self.secret,
                                  user_agent=self.agent)

    def scrape(self, lim=50):
        """
        Scrapes Reddit for stock tickers
        """

        results = []

        for subreddit_name in SUBREDDITS:
            subreddit = self.reddit.subreddit(subreddit_name)
            for submission in subreddit.hot(limit=lim):
                text = self.preprocess(submission.title + " " + submission.selftext)
                
                tickers = {t.lstrip('$') for t in self.ticker_pattern.findall(text)}
                tickers = (tickers & self.valid_tickers) - self.blocklist
                results.append({"subreddit": subreddit_name,
                                "post_id": submission.id,
                                "tickers": tickers,
                                "text": text,
                                "title": submission.title})

        return results

    def preprocess(self, text):
        """
        Preprocesses text by removing unnecessary characters.
        """
        return text.strip().replace("\n", " ").replace("\r", " ")


if __name__ == "__main__":
    scraper = RedditTickerCollector()
    for r in scraper.scrape():
        print(f"Subreddit: {r['subreddit']}, Tickers: {r['tickers']}, Title: {r['title']}")
