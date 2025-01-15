import random

from scrape import X, y

success = 0
total = 0
for (home, away), res in zip(X, y):
    if int(home >= away) == res:
        success += 1
    total += 1

print(success/total)
