# Sentiment‑Stock Analysis

Analyzes stock sentiment from financial subreddits using VADER (NLTK) and plots interactive visualizations with Yahoo Finance links.

## Features
- **Scrapes** stock discussions from Reddit using PRAW  
- **Performs sentiment analysis** using VADER  
- **Interactive matplotlib plots** with clickable Yahoo Finance links  
- **Ticker search** functionality  

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   python -c "import nltk; nltk.download('vader_lexicon')"
   
# Configure API keys
Copy .env.example to .env and populate with your credentials:

ID=<your_reddit_client_id>
SECRET=<your_reddit_client_secret>
USER_AGENT=<your_reddit_user_agent>
API_KEY=<your_finnhub_api_key>
# Run the analysis

python data_plot.py

# File Structure
.
├── data_plot.py         # Visualization and interactive plot
├── web_scraper.py       # Reddit scraping and sentiment analysis
├── stockprices.py       # Finnhub stock data fetching
├── requirements.txt     # Dependencies
├── .env.example         # API key template
└── .gitignore           # Ignores .env and virtualenv

