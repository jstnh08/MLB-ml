import os

from bs4 import BeautifulSoup, Comment
from datetime import date
from utils import parse_log
import sqlite3

db = sqlite3.connect('baseball.db')
cur = db.cursor()

cur.execute('DROP TABLE IF EXISTS Batting')
#
cur.execute("""
CREATE TABLE Batting (
    AB INTEGER,
    R INTEGER,
    H INTEGER,
    RBI INTEGER,
    BB INTEGER,
    SO INTEGER,
    PA INTEGER,
    DB INTEGER,
    TP INTEGER,
    HR INTEGER,
    HBP INTEGER,
    CS INTEGER,
    SB INTEGER,
    SF INTEGER,
    SH INTEGER,
    IW INTEGER,
    date INTEGER,
    name TEXT,
    year INTEGER,
    game_id TEXT,
    FOREIGN KEY (game_id) REFERENCES Game(id)
);
""")

files = [f for f in os.listdir("boxscores") if os.path.isfile(os.path.join("boxscores", f))]
for i, filename in enumerate(files):
    full = filename[3:-6]
    year, month, day = map(lambda x: int(x), [full[:4], full[4:6], full[6:]])
    game_date = date(year, month, day)

    with open(f"boxscores/{filename}") as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    batting_logs = soup.find_all(text=lambda text: isinstance(text, Comment) and 'class="table_container"' in text)[:2]

    useful_headers = ["AB", "R", "H", "RBI", "BB", "SO", "PA"]
    useful_details = ["2B", "3B", "HR", "HBP", "CS", "SB", "SF", "SH", "IW"]

    for log in batting_logs:
        players = parse_log(log, game_date, useful_headers, useful_details, filename[:-5])
        for player in players:
            columns = ', '.join(player.keys())
            placeholders = ':' + ', :'.join(player.keys())
            query = 'INSERT INTO Batting (%s) VALUES (%s)' % (columns, placeholders)
            cur.execute(query, player)

    if i % 100 == 0:
        print(i)

db.commit()
