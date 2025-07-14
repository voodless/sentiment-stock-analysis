import praw
from dotenv import load_dotenv
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re

#initialising sentiment analyser globally to avoid repeated loading
analyser = SentimentIntensityAnalyzer()

load_dotenv() #Loading API credentials from .env file
class webScraper:
    """
    Scrapes financial subreddits for stock tickers and analyses sentiments using VADER
    attributes:
    secret(str) : reddit API secret key
    id(str) : reddit API client ID
    agent(str) : Reddit user agent
    analyser : VADER sentiment analyser instance
    ticker_pattern: Regex pattern to match stock tickers
    
    """
    def __init__(self):
        """
        initialise reddit API credentials and sentiment analyser
        """
        self.secret = os.getenv("SECRET")
        self.id = os.getenv("ID")
        self.agent = os.getenv("USER_AGENT")
        self.analyser = SentimentIntensityAnalyzer() #Vader to determine sentiment
        self.ticker_pattern = re.compile(r"(?:\$)?\b[A-Z]{2,5}\b")
    def scrape(self):
        """
        Scrapes Reddit for stock tickers and returns sentiment scores.
    Analyzes the top 100 posts from financial subreddits using VADER.
    Returns: {ticker: {'compound': sentiment_score}}
        """    
        reddit = praw.Reddit(
            client_id = self.id,
            client_secret = self.secret,
            user_agent = self.agent
            )

        #Combined subreddit search across multiple financial communities
        subreddit = reddit.subreddit("Stocks+WallStreetBets+Investing+personalfinance+StockMarket+financialindependence+securityanalysis")
        tickers_sentiment = {}
        

        for submission in subreddit.hot(limit=10):
            text = submission.title + " " + submission.selftext #looking at text and title
            tickers = set(self.ticker_pattern.findall(text)) #Only looking for tickers with regex pattern
            if tickers:
                scores = self.analyser.polarity_scores(text) #Analysing the sentiment behind each submission on reddit within limit of 100
                for ticker in set(tickers):
                    if ticker not in tickers_sentiment or (scores['compound'] > tickers_sentiment[ticker]['compound']):
                        tickers_sentiment[ticker] = scores

        for ticker,sentiment in tickers_sentiment.items():
            print(f"ticker: {ticker} | sentiment: {sentiment['compound']}" ) #Only using compound as that is the aggregate of pos and neg
        
        if tickers_sentiment: #Determining the best stock based on sentiment 
            best_ticker = max( #using max to determine which sentiment has highest value int ticker_sentiment dict
                tickers_sentiment.items(),
                key=lambda item:item[1]['compound']
            )
        print(f"ticker :{best_ticker[0]} has sentiment of : {best_ticker[1]['compound']} which may be a good buy")

        return tickers_sentiment
if __name__ == "__main__":
    scraper = webScraper()
    scraper.scrape()