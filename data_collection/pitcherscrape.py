import os
import sqlite3

from bs4 import BeautifulSoup, Comment
from datetime import date
from utils import parse_log

db = sqlite3.connect('baseball.db')
cur = db.cursor()

cur.execute('DROP TABLE IF EXISTS Pitching')

cur.execute("""
CREATE TABLE Pitching (
    IP REAL,
    H INTEGER,
    R INTEGER,
    ER INTEGER,
    BB INTEGER,
    SO INTEGER,
    HR INTEGER,
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

    batting_logs = soup.find_all(text=lambda text: isinstance(text, Comment) and 'class="table_container"' in text)[2]

    soup = BeautifulSoup(batting_logs, "lxml")

    useful_headers = ["IP", "H", "R", "ER", "BB", "SO", "HR"]
    for table in soup.find_all("table"):
        players = parse_log(str(table), game_date, useful_headers, [], filename[:-5])
        for player in players:
            columns = ', '.join(player.keys())
            placeholders = ':' + ', :'.join(player.keys())
            query = 'INSERT INTO Pitching (%s) VALUES (%s)' % (columns, placeholders)
            cur.execute(query, player)

    if i % 100 == 0:
        print(i)

db.commit()