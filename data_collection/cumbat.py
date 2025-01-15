import os
import sqlite3

from bs4 import BeautifulSoup, Comment
from datetime import date
from utils import parse_log

db = sqlite3.connect('baseball.db')
cur = db.cursor()

cur.execute('DROP TABLE IF EXISTS CumulativeBatting')


cur.execute("""
CREATE TABLE CumulativeBatting (
    date INTEGER,
    name TEXT,
    game_id TEXT,
    cumulative_AB INTEGER,
    cumulative_hits INTEGER,
    cumulative_BA REAL,
    FOREIGN KEY (game_id) REFERENCES Game(id)
);
""")

# Get all unique players
cur.execute("SELECT DISTINCT name FROM Batting")
players = cur.fetchall()

# Loop over each player to calculate cumulative stats
for player in players:
    name = player[0]

    # Get all games for this player ordered by date
    cur.execute("""
    SELECT date, game_id, AB, H
    FROM Batting
    WHERE name = ?
    ORDER BY date
    """, (name,))

    games = cur.fetchall()

    # Initialize cumulative stats
    cumulative_AB = 0
    cumulative_hits = 0

    # Loop through each game to calculate cumulative stats up to each game
    for game in games:
        date, game_id, AB, H = game

        # Calculate cumulative batting average up to but not including the current game
        cumulative_BA = (cumulative_hits / cumulative_AB) if cumulative_AB > 0 else None

        # Insert cumulative data into CumulativeBatting table
        cur.execute("""
        INSERT INTO CumulativeBatting (date, name, game_id, cumulative_AB, cumulative_hits, cumulative_BA)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (date, name, game_id, cumulative_AB, cumulative_hits, cumulative_BA))

        # Update cumulative stats by adding current game's AB and H
        cumulative_AB += AB
        cumulative_hits += H

db.commit()
