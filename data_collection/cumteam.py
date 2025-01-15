import sqlite3

from bs4 import BeautifulSoup, Comment
from datetime import date
from utils import parse_log

db = sqlite3.connect('baseball.db')
cur = db.cursor()

cur.execute("DROP TABLE IF EXISTS CumulativeTeamStats")
cur.execute("""
CREATE TABLE CumulativeTeamStats (
    date INTEGER,
    team_id TEXT,
    game_id TEXT,
    cumulative_games_played INTEGER,
    cumulative_wins INTEGER,
    cumulative_losses INTEGER,
    cumulative_runs_scored INTEGER,
    cumulative_runs_allowed INTEGER,
    cumulative_win_percentage REAL,
    FOREIGN KEY (game_id) REFERENCES Game(id)
);
""")

# Get all unique teams
cur.execute("""
SELECT DISTINCT home_team_id AS team_id FROM Game
UNION
SELECT DISTINCT away_team_id AS team_id FROM Game
""")
teams = cur.fetchall()

# Loop over each team to calculate cumulative stats
for team in teams:
    team_id = team[0]

    # Get all games for this team ordered by date
    cur.execute("""
    SELECT date, id, home_team_id, away_team_id, home_team_runs, away_team_runs
    FROM Game
    WHERE home_team_id = ? OR away_team_id = ?
    ORDER BY date
    """, (team_id, team_id))

    games = cur.fetchall()

    # Initialize cumulative stats
    cumulative_games_played = 0
    cumulative_wins = 0
    cumulative_losses = 0
    cumulative_runs_scored = 0
    cumulative_runs_allowed = 0

    # Loop through each game to calculate cumulative stats up to each game
    for game in games:
        date, game_id, home_team_id, away_team_id, home_team_runs, away_team_runs = game

        # Determine if the team is the home or away team for this game
        if team_id == home_team_id:
            runs_scored = home_team_runs
            runs_allowed = away_team_runs
            won = home_team_runs > away_team_runs
        else:
            runs_scored = away_team_runs
            runs_allowed = home_team_runs
            won = away_team_runs > home_team_runs

        # Calculate cumulative win percentage up to but not including the current game
        cumulative_win_percentage = (cumulative_wins / cumulative_games_played) if cumulative_games_played > 0 else None

        # Insert cumulative data into CumulativeTeamStats table
        cur.execute("""
        INSERT INTO CumulativeTeamStats (
            date, team_id, game_id, cumulative_games_played,
            cumulative_wins, cumulative_losses, cumulative_runs_scored,
            cumulative_runs_allowed, cumulative_win_percentage
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (date, team_id, game_id, cumulative_games_played, cumulative_wins,
              cumulative_losses, cumulative_runs_scored, cumulative_runs_allowed,
              cumulative_win_percentage))

        # Update cumulative stats by adding the current game's stats
        cumulative_games_played += 1
        cumulative_runs_scored += runs_scored
        cumulative_runs_allowed += runs_allowed
        if won:
            cumulative_wins += 1
        else:
            cumulative_losses += 1

db.commit()