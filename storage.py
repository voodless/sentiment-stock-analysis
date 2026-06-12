import sqlite3

DB_PATH = "sentiment.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS mentions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_at      TEXT NOT NULL,        -- ISO timestamp of the run
    post_id     TEXT NOT NULL,        -- reddit submission id
    subreddit   TEXT NOT NULL,
    ticker      TEXT NOT NULL,
    sentiment   TEXT NOT NULL,        -- positive / negative / neutral
    confidence  REAL NOT NULL,
    title       TEXT,
    UNIQUE(post_id, ticker)           -- same post+ticker never counted twice
);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(SCHEMA)
    return conn


def save_mentions(conn, rows):
    conn.executemany(
        """INSERT OR IGNORE INTO mentions
           (run_at, post_id, subreddit, ticker, sentiment, confidence, title)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )
    conn.commit()