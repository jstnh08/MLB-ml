import os
import sqlite3

from bs4 import BeautifulSoup, Comment
from datetime import date
from utils import parse_log

db = sqlite3.connect('baseball.db')
cur = db.cursor()


# Get all unique pitchers
cur.execute("SELECT * FROM CumulativeTeamStats")
pitchers = cur.fetchall()

for x in pitchers:
    print(x)