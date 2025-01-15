import os
import sqlite3

from bs4 import BeautifulSoup, Comment
from datetime import date
from utils import parse_log

db = sqlite3.connect('baseball.db')
cur = db.cursor()

cur.execute('DROP TABLE IF EXISTS CumulativeERA')


cur.execute("""
CREATE TABLE CumulativeERA (
    date INTEGER,
    name TEXT,
    game_id TEXT,
    cumulative_IP REAL,
    cumulative_ER INTEGER,
    cumulative_ERA REAL,
    FOREIGN KEY (game_id) REFERENCES Game(id)
);
""")

# Get all unique pitchers
cur.execute("SELECT DISTINCT name FROM Pitching")
pitchers = cur.fetchall()

# Loop over each pitcher to calculate cumulative stats
for i, pitcher in enumerate(pitchers):
    name = pitcher[0]

    # Get all games for this pitcher ordered by date
    cur.execute("""
    SELECT date, game_id, IP, ER
    FROM Pitching
    WHERE name = ?
    ORDER BY date
    """, (name,))

    games = cur.fetchall()

    # Initialize cumulative stats
    cumulative_IP = 0
    cumulative_ER = 0

    # Loop through each game to calculate cumulative stats up to each game
    for game in games:
        date, game_id, IP, ER = game

        # Calculate cumulative ERA up to but not including the current game
        cumulative_ERA = (cumulative_ER * 9 / cumulative_IP) if cumulative_IP > 0 else None

        # Insert cumulative data into CumulativeERA table
        cur.execute("""
        INSERT INTO CumulativeERA (date, name, game_id, cumulative_IP, cumulative_ER, cumulative_ERA)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (date, name, game_id, cumulative_IP, cumulative_ER, cumulative_ERA))

        # Update cumulative stats by adding current game's IP and ER
        cumulative_IP += IP
        cumulative_ER += ER

    if i % 10 == 0:
        print(i, len(pitchers))

db.commit()