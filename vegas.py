import time

import requests
from bs4 import BeautifulSoup

x = 0
success = 0
total = 0
for month in range(4, 9):
    for day in range(1, 32):
        m, d = str(month).zfill(2), str(day).zfill(2)

        r = requests.get(f"https://www.sportsbookreview.com/betting-odds/mlb-baseball/?date=2023-{m}-{d}")
        if r.status_code != 200:
            print(f"{m}-{d} isnt real")
            continue

        soup = BeautifulSoup(r.content, "lxml")

        body = soup.find("div", {"id": "tbody-mlb"})
        if not body:
            continue

        for row in body.find_all("div", {"class": "d-flex flex-row flex-nowrap border position-relative mt-0 GameRows_eventMarketGridContainer__GuplK GameRows_neverWrap__gnQNO"}):
            a_score, b_score = [int(i.text) for i in row.find_all("div", {"class": "d-flex flex-column flex-wrap justify-content-around align-items-center fs-9 fw-bold mb-n1 GameRows_scores__YkN24"})]
            a_odd, b_odd = [int(i.text) for i in row.find_all("span", {"data-cy": "odd-grid-opener-homepage"})[-2:]]

            if a_odd == b_odd:
                continue

            if (a_score > b_score if a_odd < b_odd else a_score < b_score):
                success += 1
            total += 1

        time.sleep(3)
        print(f"day {day} month {month}")

    print(f"month {month} is done")

print(success/total)