from dotenv import load_dotenv
import os
import finnhub
import time 
import web_scraper
import csv
import datetime
import pytz
load_dotenv()

#initialisation
api_key = os.getenv('API_KEY')
finnhub_client = finnhub.Client(api_key=api_key)
scraper = web_scraper.webScraper()
tickers = scraper.scrape()

#writing stock data and vader sentiment into a csv
with open("quotes.csv","w", newline="") as csvfile:
    fieldnames = ['ticker','c','d','dp','h','l','o','pc','t','sentiment']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    if tickers:
        for ticker in tickers.keys():
            cticker = ticker.replace("$", "")
            try:   
                res = finnhub_client.quote(cticker) #fetch quote from finnhub api
                res['t'] = datetime.datetime.fromtimestamp(res['t'], tz=pytz.utc).strftime('%Y-%m-%d %H:%M:%S %Z') #turning epoch time into utf 
                if res['c'] == 0 and res['h'] == 0 and res['l'] == 0:
                    print(f"No price data for {cticker}...") # handling false stock data / poor readings
                    continue
                res["ticker"] = cticker
                res["sentiment"] = tickers[ticker]['compound']
                writer.writerow(res)
                print(f"${cticker} quote: {res}")
                time.sleep(0.5) #slowing down fetching rate so api limit is not reached (60pm)
            except finnhub.FinnhubAPIException as e:
                if e.status_code == 429: # finnhub limit
                    print("Rate limit hit. Sleeping for 60 seconds")
                    time.sleep(60) # if limit is reached stop for 1 min
                else:
                    print(f"Error for {cticker}: {e}") #all other api errors
                    continue #skip to next ticker