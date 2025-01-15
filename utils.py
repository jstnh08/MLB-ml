import datetime

from bs4 import BeautifulSoup
import calendar


def parse_log(log, game_date: datetime.date, useful_headers, useful_details, game_id):
    rename = {
        "2B": "DB",
        "3B": "TP"
    }
    soup = BeautifulSoup(log, "lxml")
    headers = [x.text for x in soup.find("thead").find_all("th")]
    players = []
    timestamp = calendar.timegm(game_date.timetuple())

    for row in soup.find("tbody").find_all("tr"):
        if row.get("class") == ["spacer"]:
            break

        stats = [row.find("th")["data-append-csv"]] + [x.text for x in row.find_all("td")]

        player = {rename.get(x) or x: 0 for x in useful_headers + useful_details}
        player["date"] = timestamp
        player["name"] = stats[0]
        player["year"] = game_date.year
        player["game_id"] = game_id

        for useful_header in useful_headers:
            if useful_header == "IP":
                inning = stats[headers.index(useful_header)].split(".")
                player[useful_header] = int(inning[0]) + int(inning[1] if len(inning) == 2 else 0)/3
            else:
                player[useful_header] = int(stats[headers.index(useful_header)])

        for detail in stats[-1].split(","):
            stat = detail.split("·")
            if stat[-1] in useful_details:
                if len(stat) == 2:
                    player[rename.get(stat[1]) or stat[1]] = int(stat[0])
                else:
                    player[rename.get(stat[0]) or stat[0]] = 1

        players.append(player)

    return players
