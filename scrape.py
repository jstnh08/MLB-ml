import pprint
import random

import numpy as np
import requests
from bs4 import BeautifulSoup

r = requests.get("https://www.baseball-reference.com/leagues/majors/2023-schedule.shtml")
soup = BeautifulSoup(r.content, "lxml")

content = soup.find("div", {"class": "section_content"})

teams = [
    'Baltimore Orioles', 'Boston Red Sox', 'Chicago Cubs', 'Milwaukee Brewers',
    'Pittsburgh Pirates', 'Cincinnati Reds', 'Chicago White Sox', 'Houston Astros',
    'Minnesota Twins', 'Kansas City Royals', 'Los Angeles Dodgers', "Arizona D'Backs",
    'New York Mets', 'Miami Marlins', 'New York Yankees', 'San Francisco Giants',
    'Oakland Athletics', 'Los Angeles Angels', 'Colorado Rockies', 'San Diego Padres',
    'Seattle Mariners', 'Cleveland Guardians', 'Toronto Blue Jays', 'St. Louis Cardinals',
    'Tampa Bay Rays', 'Detroit Tigers', 'Texas Rangers', 'Philadelphia Phillies',
    'Atlanta Braves', 'Washington Nationals'
]

records = {
    team: {"wins": 0, "losses": 0}
    for team in teams
}

runs = {
    team: {"scored": 0, "allowed": 0}
    for team in teams
}
games = []

rolling = {
    team: {
        "runs_scored": [],
        "runs_allowed": [],
        "results": []
    }
    for team in teams
}


def calc_win_perc(*, wins, losses):
    try:
        return round(wins/(wins+losses), 3)
    except ZeroDivisionError:
        return 0

for game in content.find_all("p", {"class":"game"}):
    a, b = game.find_all("a")[:2]
    away, home = a, b

    # if random.random() < 0.5:
    #     a, b = b, a
    # not smart to add thios as a feature in logistic regression cause no hiden layers

    a_score, b_score = map(lambda tag: int(tag.next_sibling.strip().strip("@").strip().strip("()")), [a,b])

    winner = a if a_score > b_score else b
    loser = b if winner == a else a

    winner, loser = map(lambda tag: tag.text, [winner, loser])

    pa = calc_win_perc(**records[a.text])
    pb = calc_win_perc(**records[b.text])

    pythag = lambda rs, ra: (rs**1.83) / (rs**1.83 + ra**1.83)

    if (records[winner]["wins"] + records[winner]["losses"] >= 20) and (records[loser]["wins"] + records[loser]["losses"] >= 20):
        log_5 = (pa - (pa * pb)) / (pa + pb - (2 * pa * pb))

        rolling_a_s = sum(rolling[a.text]["runs_scored"])
        rolling_b_s = sum(rolling[b.text]["runs_scored"])
        rolling_a_a = sum(rolling[a.text]["runs_allowed"])
        rolling_b_a = sum(rolling[b.text]["runs_allowed"])

        games.append({
            "a": pa,
            "b": pb,
            "a_win": int(a.text == winner),
            "log_5": log_5,
            "a_home": int(a == home),
            "a_scored": runs[a.text]["scored"],
            "a_allowed": runs[a.text]["allowed"],
            "b_scored": runs[b.text]["scored"],
            "b_allowed": runs[b.text]["allowed"],
            "a_pythag": pythag(runs[a.text]["scored"], runs[a.text]["allowed"]),
            "b_pythag": pythag(runs[b.text]["scored"], runs[b.text]["allowed"]),
            "rolling_a_pythag": pythag(rolling_a_s, rolling_a_a),
            "rolling_b_pythag": pythag(rolling_b_s, rolling_b_a),
            "rolling_a": rolling[a.text]["results"].count(True) / len(rolling[a.text]["results"]),
            "rolling_b": rolling[b.text]["results"].count(True) / len(rolling[b.text]["results"]),
        })

    records[winner]["wins"] += 1
    records[loser]["losses"] += 1

    runs[a.text]["scored"] += a_score
    runs[b.text]["scored"] += b_score

    runs[b.text]["allowed"] += a_score
    runs[a.text]["allowed"] += b_score

    for team in [a.text, b.text]:
        if len(rolling[team]["results"]) == 10:
            for x in ["runs_allowed", "runs_scored", "results"]:
                rolling[team][x].pop(0)

    rolling[a.text]["runs_scored"].append(a_score)
    rolling[b.text]["runs_scored"].append(b_score)

    rolling[a.text]["runs_allowed"].append(b_score)
    rolling[b.text]["runs_allowed"].append(a_score)

    rolling[a.text]["results"].append(a.text == winner)
    rolling[b.text]["results"].append(b.text == winner)

features = ['log_5', 'a_pythag', 'b_pythag', 'a', 'b', 'a_scored', 'b_scored', 'a_allowed', 'b_allowed', 'rolling_pytha', "roll b [yth"]
X = np.array([
    [g['a'], g['b'],
     ] for g in games])
y = np.array([g['a_win'] for g in games])

