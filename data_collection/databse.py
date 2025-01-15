import sqlite3

import numpy as np

# remove data_collection if soleley running this
db = sqlite3.connect('data_collection/baseball.db')
cur = db.cursor()

cur.execute("""
SELECT
    strftime('%Y-%m-%d', g.date, 'unixepoch') AS date,
    g.id AS game_id,
    g.home_team_id AS home_id,
    g.away_team_id AS away_id,
    CASE WHEN g.home_team_runs > g.away_team_runs THEN 1 ELSE 0 END AS home_win,
    
    h_era.cumulative_ERA AS home_era,
    a_era.cumulative_ERA AS away_era,
    
    CASE 
        WHEN (COALESCE(SUM(h_b1.cumulative_AB), 0) +
              COALESCE(SUM(h_b2.cumulative_AB), 0) +
              COALESCE(SUM(h_b3.cumulative_AB), 0) +
              COALESCE(SUM(h_b4.cumulative_AB), 0) +
              COALESCE(SUM(h_b5.cumulative_AB), 0) +
              COALESCE(SUM(h_b6.cumulative_AB), 0) +
              COALESCE(SUM(h_b7.cumulative_AB), 0) +
              COALESCE(SUM(h_b8.cumulative_AB), 0) +
              COALESCE(SUM(h_b9.cumulative_AB), 0)) > 0 
        THEN (COALESCE(SUM(h_b1.cumulative_hits), 0) +
              COALESCE(SUM(h_b2.cumulative_hits), 0) +
              COALESCE(SUM(h_b3.cumulative_hits), 0) +
              COALESCE(SUM(h_b4.cumulative_hits), 0) +
              COALESCE(SUM(h_b5.cumulative_hits), 0) +
              COALESCE(SUM(h_b6.cumulative_hits), 0) +
              COALESCE(SUM(h_b7.cumulative_hits), 0) +
              COALESCE(SUM(h_b8.cumulative_hits), 0) +
              COALESCE(SUM(h_b9.cumulative_hits), 0)) * 1.0 /
             (COALESCE(SUM(h_b1.cumulative_AB), 0) +
              COALESCE(SUM(h_b2.cumulative_AB), 0) +
              COALESCE(SUM(h_b3.cumulative_AB), 0) +
              COALESCE(SUM(h_b4.cumulative_AB), 0) +
              COALESCE(SUM(h_b5.cumulative_AB), 0) +
              COALESCE(SUM(h_b6.cumulative_AB), 0) +
              COALESCE(SUM(h_b7.cumulative_AB), 0) +
              COALESCE(SUM(h_b8.cumulative_AB), 0) +
              COALESCE(SUM(h_b9.cumulative_AB), 0))
        ELSE NULL
    END AS home_ba,
    
    CASE 
        WHEN (COALESCE(SUM(a_b1.cumulative_AB), 0) +
              COALESCE(SUM(a_b2.cumulative_AB), 0) +
              COALESCE(SUM(a_b3.cumulative_AB), 0) +
              COALESCE(SUM(a_b4.cumulative_AB), 0) +
              COALESCE(SUM(a_b5.cumulative_AB), 0) +
              COALESCE(SUM(a_b6.cumulative_AB), 0) +
              COALESCE(SUM(a_b7.cumulative_AB), 0) +
              COALESCE(SUM(a_b8.cumulative_AB), 0) +
              COALESCE(SUM(a_b9.cumulative_AB), 0)) > 0 
        THEN (COALESCE(SUM(a_b1.cumulative_hits), 0) +
              COALESCE(SUM(a_b2.cumulative_hits), 0) +
              COALESCE(SUM(a_b3.cumulative_hits), 0) +
              COALESCE(SUM(a_b4.cumulative_hits), 0) +
              COALESCE(SUM(a_b5.cumulative_hits), 0) +
              COALESCE(SUM(a_b6.cumulative_hits), 0) +
              COALESCE(SUM(a_b7.cumulative_hits), 0) +
              COALESCE(SUM(a_b8.cumulative_hits), 0) +
              COALESCE(SUM(a_b9.cumulative_hits), 0)) * 1.0 /
             (COALESCE(SUM(a_b1.cumulative_AB), 0) +
              COALESCE(SUM(a_b2.cumulative_AB), 0) +
              COALESCE(SUM(a_b3.cumulative_AB), 0) +
              COALESCE(SUM(a_b4.cumulative_AB), 0) +
              COALESCE(SUM(a_b5.cumulative_AB), 0) +
              COALESCE(SUM(a_b6.cumulative_AB), 0) +
              COALESCE(SUM(a_b7.cumulative_AB), 0) +
              COALESCE(SUM(a_b8.cumulative_AB), 0) +
              COALESCE(SUM(a_b9.cumulative_AB), 0))
        ELSE NULL
    END AS away_ba,
    
    h_stats.cumulative_runs_scored AS home_runs_scored,
    h_stats.cumulative_runs_allowed AS home_runs_allowed,
    h_stats.cumulative_win_percentage AS home_win_p,
    h_stats.cumulative_runs_scored - h_stats.cumulative_runs_allowed AS home_run_diff,

    a_stats.cumulative_runs_scored AS away_runs_scored,
    a_stats.cumulative_runs_allowed AS away_runs_allowed,
    a_stats.cumulative_win_percentage AS away_win_p,
    a_stats.cumulative_runs_scored - a_stats.cumulative_runs_allowed AS away_run_diff

FROM Game g

LEFT JOIN CumulativeERA h_era
ON g.home_team_starting_pitcher_id = h_era.name
AND g.date = h_era.date

LEFT JOIN CumulativeERA a_era
ON g.away_team_starting_pitcher_id = a_era.name
AND g.date = a_era.date

LEFT JOIN CumulativeBatting h_b1 ON g.home_team_batter_1_id = h_b1.name AND g.date = h_b1.date
LEFT JOIN CumulativeBatting h_b2 ON g.home_team_batter_2_id = h_b2.name AND g.date = h_b2.date
LEFT JOIN CumulativeBatting h_b3 ON g.home_team_batter_3_id = h_b3.name AND g.date = h_b3.date
LEFT JOIN CumulativeBatting h_b4 ON g.home_team_batter_4_id = h_b4.name AND g.date = h_b4.date
LEFT JOIN CumulativeBatting h_b5 ON g.home_team_batter_5_id = h_b5.name AND g.date = h_b5.date
LEFT JOIN CumulativeBatting h_b6 ON g.home_team_batter_6_id = h_b6.name AND g.date = h_b6.date
LEFT JOIN CumulativeBatting h_b7 ON g.home_team_batter_7_id = h_b7.name AND g.date = h_b7.date
LEFT JOIN CumulativeBatting h_b8 ON g.home_team_batter_8_id = h_b8.name AND g.date = h_b8.date
LEFT JOIN CumulativeBatting h_b9 ON g.home_team_batter_9_id = h_b9.name AND g.date = h_b9.date

LEFT JOIN CumulativeBatting a_b1 ON g.away_team_batter_1_id = a_b1.name AND g.date = a_b1.date
LEFT JOIN CumulativeBatting a_b2 ON g.away_team_batter_2_id = a_b2.name AND g.date = a_b2.date
LEFT JOIN CumulativeBatting a_b3 ON g.away_team_batter_3_id = a_b3.name AND g.date = a_b3.date
LEFT JOIN CumulativeBatting a_b4 ON g.away_team_batter_4_id = a_b4.name AND g.date = a_b4.date
LEFT JOIN CumulativeBatting a_b5 ON g.away_team_batter_5_id = a_b5.name AND g.date = a_b5.date
LEFT JOIN CumulativeBatting a_b6 ON g.away_team_batter_6_id = a_b6.name AND g.date = a_b6.date
LEFT JOIN CumulativeBatting a_b7 ON g.away_team_batter_7_id = a_b7.name AND g.date = a_b7.date
LEFT JOIN CumulativeBatting a_b8 ON g.away_team_batter_8_id = a_b8.name AND g.date = a_b8.date
LEFT JOIN CumulativeBatting a_b9 ON g.away_team_batter_9_id = a_b9.name AND g.date = a_b9.date

LEFT JOIN CumulativeTeamStats h_stats
ON g.home_team_id = h_stats.team_id
AND g.date = h_stats.date

LEFT JOIN CumulativeTeamStats a_stats
ON g.away_team_id = a_stats.team_id
AND g.date = a_stats.date

GROUP BY g.id
ORDER BY date
""")


names = [description[0] for description in cur.description]
results = cur.fetchall()

cur.close()
db.close()

trimmed_results = list(filter(lambda x: None not in x, results))[249:]

print(len(trimmed_results))
print(names)

x_train_columns = ['home_era', 'away_era', 'home_ba', 'away_ba', 'home_runs_scored', 'home_runs_allowed', 'home_win_p', 'away_runs_scored', 'away_runs_allowed', 'away_win_p']
# x_train_columns = ['home_win_p', 'away_win_p']

X = np.array([
    [
        row[names.index(x)] for x in x_train_columns
     ] for row in trimmed_results])
y = np.array([row[names.index("home_win")] for row in trimmed_results])

np.save("X.npy", X)
np.save("y.npy", y)