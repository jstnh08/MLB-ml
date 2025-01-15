import calendar
import os
import sqlite3
from datetime import date

from bs4 import BeautifulSoup, Comment

db = sqlite3.connect('baseball.db')
cur = db.cursor()

cur.execute('DROP TABLE IF EXISTS Game')

cur.execute("""
CREATE TABLE Game (
    id TEXT PRIMARY KEY,
    date INTEGER,
    year INTEGER,
    day_game INTEGER,
    
    home_team_id TEXT,
    away_team_id TEXT,
    home_team_runs INTEGER,
    away_team_runs INTEGER,
    
    home_team_starting_pitcher_id TEXT,
    away_team_starting_pitcher_id TEXT,
    
    home_team_batter_1_id TEXT,
    home_team_batter_2_id TEXT,
    home_team_batter_3_id TEXT,
    home_team_batter_4_id TEXT,
    home_team_batter_5_id TEXT,
    home_team_batter_6_id TEXT,
    home_team_batter_7_id TEXT,
    home_team_batter_8_id TEXT,
    home_team_batter_9_id TEXT,
    
    away_team_batter_1_id TEXT,
    away_team_batter_2_id TEXT,
    away_team_batter_3_id TEXT,
    away_team_batter_4_id TEXT,
    away_team_batter_5_id TEXT,
    away_team_batter_6_id TEXT,
    away_team_batter_7_id TEXT,
    away_team_batter_8_id TEXT,
    away_team_batter_9_id TEXT
);
""")

files = [f for f in os.listdir("boxscores") if os.path.isfile(os.path.join("boxscores", f))]
for num, filename in enumerate(files):
    full = filename[3:-6]
    year, month, day = map(lambda x: int(x), [full[:4], full[4:6], full[6:]])
    game_date = date(year, month, day)
    timestamp = calendar.timegm(game_date.timetuple())

    with open(f"boxscores/{filename}") as fp:
        soup = BeautifulSoup(fp, "html.parser")

    scorebox = soup.find("div", {"class": "scorebox"})

    away_id, home_id, = [x.find("a")["href"].strip("/").split("/")[1] for x in scorebox.find_all("strong")[:2]]
    away_score, home_score = [x.text for x in scorebox.find_all("div", {"class": "score"})]
    day_game = "Day" in soup.find("div", {"class": "scorebox_meta"}).text

    game = {
        "id": filename[:-5],
        "date": timestamp,
        "year": game_date.year,
        "day_game": day_game,
        "home_team_id": home_id,
        "away_team_id": away_id,
        "home_team_runs": home_score,
        "away_team_runs": away_score
    }

    comment = soup.find(text=lambda text: isinstance(text, Comment) and 'id="div_lineups"' in text)
    stats_page = BeautifulSoup(comment, "lxml")

    for table, team in zip(stats_page.find_all("table"), ["away", "home"]):
        for i, row in enumerate(table.find_all("tr")):
            try:
                name = row.find("a")["href"].replace(".shtml", "").split("/")[-1]
            except TypeError:
                name = None
            if i < 9:
                game[f"{team}_team_batter_{i+1}_id"] = name
            else:
                game[f"{team}_team_starting_pitcher_id"] = name

    columns = ', '.join(game.keys())
    placeholders = ':' + ', :'.join(game.keys())
    query = 'INSERT INTO Game (%s) VALUES (%s)' % (columns, placeholders)
    cur.execute(query, game)

    if num % 100 == 0:
        print(num)

db.commit()