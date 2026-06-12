"""Interactive scatter plot of Reddit sentiment vs stock price movement.

Each point is a ticker. Clicking a point (or submitting it in the search box)
opens its Yahoo Finance page. The "Show All" button lists every plotted
ticker in the console.
"""

import csv
import webbrowser

import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox

YAHOO_URL = "https://finance.yahoo.com/quote/{}"


def load_from_csv(path="quotes.csv"):
    """Read tickers, % change and sentiment from a CSV produced by main.py."""
    tickers, pct_changes, sentiments = [], [], []
    with open(path, newline="") as csvfile:
        for row in csv.DictReader(csvfile):
            try:
                tickers.append(row["ticker"])
                pct_changes.append(float(row["pct_change"]))
                sentiments.append(float(row["sentiment"]))
            except (KeyError, ValueError):
                continue  # skip malformed rows
    return tickers, sentiments, pct_changes


def plot_data(df=None):
    """Create the interactive sentiment-vs-price-move scatter plot.

    Args:
        df: optional DataFrame with 'ticker', 'sentiment' and 'pct_change'
            columns. If omitted, data is read from quotes.csv instead.
    """
    if df is not None:
        tickers = df["ticker"].tolist()
        sentiments = df["sentiment"].tolist()
        pct_changes = df["pct_change"].tolist()
    else:
        tickers, sentiments, pct_changes = load_from_csv()

    if not tickers:
        print("No data to plot.")
        return

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_title("Reddit Sentiment vs Daily Price Change")
    ax.set_xlabel("Sentiment score (−1 to 1)")
    ax.set_ylabel("Daily price change (%)")
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color="grey", lw=0.8)
    ax.axvline(0, color="grey", lw=0.8)
    ax.scatter(sentiments, pct_changes, alpha=1, picker=True, pickradius=5)

    # Annotate each point with its ticker
    for x, y, ticker in zip(sentiments, pct_changes, tickers):
        ax.annotate(ticker, (x, y), fontsize=6, alpha=0.6,
                    xytext=(5, 5), textcoords="offset points")

    axbox = fig.add_axes([0.15, 0.93, 0.7, 0.05])
    axbox.set_xticks([])
    axbox.set_yticks([])
    for spine in axbox.spines.values():
        spine.set_visible(False)
    text_box = TextBox(axbox, "Search Ticker:", initial="")

    def search_ticker(query):
        """Open the Yahoo Finance page for a searched ticker."""
        query = query.upper().strip()
        if query in tickers:
            webbrowser.open(YAHOO_URL.format(query))
        else:
            print(f"Ticker {query} not found in data")

    text_box.on_submit(search_ticker)

    ax_button = fig.add_axes([0.87, 0.93, 0.12, 0.05])
    button = Button(ax_button, "Show All")

    def show_all_tickers(_event):
        """Print all plotted tickers to the console in columns."""
        sorted_tickers = sorted(tickers)
        print("\n" + "=" * 50)
        print("ALL AVAILABLE TICKERS:")
        print("=" * 50)
        for i in range(0, len(sorted_tickers), 5):
            print("  ".join(f"{t:8}" for t in sorted_tickers[i:i + 5]))
        print(f"\nTotal: {len(sorted_tickers)} tickers")
        print("=" * 50)

    button.on_clicked(show_all_tickers)

    # --- Clickable points -------------------------------------------------
    def on_pick(event):
        """Open Yahoo Finance for whichever point was clicked."""
        ticker = tickers[event.ind[0]]
        webbrowser.open(YAHOO_URL.format(ticker))

    fig.canvas.mpl_connect("pick_event", on_pick)

    plt.show()


if __name__ == "__main__":
    plot_data()  # standalone: reads quotes.csv
