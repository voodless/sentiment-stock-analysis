import matplotlib.pyplot as plt
import csv
import webbrowser
from matplotlib.widgets import TextBox, Button
#This program makes a scatter plot of stock sentiment vs price
#When you click a point you will be taken to the stock's Yahoo Finance

#Step 1: Load the data from the CSV file
tkr = []
close_price = []
sentiment = []
wst = [] #web scraper ticker 

with open('quotes.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            tkr.append(row['ticker']) #Stock symbol
            close_price.append(float(row['c']))#Closing price
            sentiment.append(float(row['sentiment'])) #Sentiment score ranging from -1 to 1
        except ValueError: #Skips rows with bad data
            continue

#Create the scatter plot
fig, ax = plt.subplots(figsize=(12,8)) 
sc = ax.scatter(sentiment, close_price, alpha=1, picker=5) #Plot each stock as a point, picker=5 makes points easier to click
ax.set_title("Online Sentiment vs Stock Price at Previous Close")
ax.set_xlabel('Sentiment Score')
ax.set_ylabel('Stock Price ($)')
ax.grid(True,alpha=0.3)

#annotating each point with its ticker
for i, ticker in enumerate(tkr):
    plt.annotate(ticker, (sentiment[i], close_price[i]), 
                 fontsize=6,alpha=0.6,
                 xytext=(5,5),textcoords="offset points")


axbox = plt.axes([0.15,0.93,0.7,0.05])
axbox.set_xticks([])  # Removing scale
axbox.set_yticks([])  # removing scale
for spine in ['top', 'right', 'bottom', 'left']:
    axbox.spines[spine].set_visible(False)
text_box = TextBox(axbox,'Search Ticker:',initial="")
def search_ticker(ticker):
    """Jump to a specific ticker when searched"""
    ticker = ticker.upper().strip()
    if ticker in tkr:
        plt.draw()  # Update the plot
        # Open the link
        webbrowser.open(f"https://finance.yahoo.com/quote/{ticker}")
    else:
        print(f"Ticker {ticker} not found in data")
        
text_box.on_submit(search_ticker)

ax_button = plt.axes([0.87,0.93,0.12,0.05])
button = Button(ax_button,"Show All")
def show_all_tickers(event):
    """ Print all tickers to console"""
    sorted_tickers = sorted(tkr)
    print("\n" + "=" *50)
    print("ALL AVAILABLE TICKERS: ")
    print("="*50)

    for i in range(0, len(sorted_tickers), 5):
        row = sorted_tickers[i:i+5]
        print("  ".join(f"{ticker:8}" for ticker in row))
    
    print(f"\nTotal: {len(sorted_tickers)} tickers")
    print("="*50)

button.on_clicked(show_all_tickers)


#making the points interactive 
def on_pick(event):
    """
    Once clicking one of the points, you will be taken to a yahoo finance page
    Done using matplotlib pixel based region clicks

    """
    ind = event.ind[0] #Getting which point was clicked               # index of the picked point
    ticker = tkr[ind] #Getting that stock's ticker
    webbrowser.open(f"https://finance.yahoo.com/quote/{ticker}") #Opening tickers yahoo finance

                    
#connect click function to plot
plt.gcf().canvas.mpl_connect('pick_event',on_pick)

#setting x and y axis limits for better visualisation
plt.show()
