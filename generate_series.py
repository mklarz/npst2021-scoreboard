import json
import bleach
from datetime import datetime, timezone
from git import Repo

# Quick, dirty and very inefficent script to generate formatted data for the line graph
LIMIT = 10
START_TIMESTAMP = datetime(2021, 12, 1, 17, tzinfo=timezone.utc).isoformat()

def format_item(timestamp, value):
    return [timestamp, value]

repo = Repo(".")
master = repo.heads.main
commits = list(repo.iter_commits(master))[::-1]

last_scoreboard = None
users = {}
print("Parsing {} commits and creating series.json".format(len(commits)))
for commit in commits:
    print("Parsing: {} - {}".format(commit.hexsha, commit.committed_date))
    content = repo.git.show('{}:{}'.format(commit.hexsha, "scoreboard.min.json")).strip()
    try:
        scoreboard = json.loads(content)
    except Exception as e:
        # print(scoreboard)
        # print("Error for scoreboard ", e)
        continue
    last_scoreboard = scoreboard
    for scoreboard_user in scoreboard:
        current_score = int(scoreboard_user["score"])
        current_solves = int(scoreboard_user["num_solves"])
        user_id = scoreboard_user["user_id"]
        last_solve = scoreboard_user["latest_solve_time"]

        if user_id not in users:
            users[user_id] = {
                "name": scoreboard_user["username"],
                "last_solve": last_solve,
                "solves": [format_item(START_TIMESTAMP, 0), format_item(last_solve, current_solves)],
                "score": [format_item(START_TIMESTAMP, 0), format_item(last_solve, current_score)],
            }
            continue

        user = users[user_id]

        if len(user["solves"]) > 0:
            last_challenge = user["solves"][-1]
            if current_solves != last_challenge[1]:
                user["solves"].append(format_item(last_solve, current_solves))
                user["score"].append(format_item(last_solve, current_score))

        users[user_id] = user

series = {
    "users": [],
}

# Only extract topp <LIMIT> users
for index, scoreboard_user in enumerate(last_scoreboard[:LIMIT]):
    user_id = scoreboard_user["user_id"]
    user = users[user_id]
    last_challenge = scoreboard_user["num_solves"]
    base = {
        "name": bleach.clean(user["name"]), # there's a xss in the legend tooltip
        "type": "line",
    } 
    series["users"].append({**base, **{"data": user["score"]}});

with open("series.json", "w") as f:
    json.dump(series, f)

print("Done!")
