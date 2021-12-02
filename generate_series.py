import json
from datetime import datetime
from git import Repo

LIMIT = 50

# Quick, dirty and very inefficent script to generate formatted data for the line graph

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
        current_challenges = int(scoreboard_user["num_solves"])
        name = scoreboard_user["username"]
        last_solve = int(datetime.strptime(scoreboard_user["latest_solve_time"], "%Y-%m-%dT%H:%M:%S.%f+00:00").timestamp())

        if name not in users:
            users[name] = {
                "last_solve": last_solve,
                "challenges": [format_item(last_solve, current_challenges)],
            }
            continue

        user = users[name]

        if len(user["challenges"]) > 0:
            last_challenge = user["challenges"][-1]
            if current_challenges != last_challenge[1]:
                user["challenges"].append(format_item(last_solve, current_challenges))

        users[name] = user

series = {
    "challenges": [],
}

# Only extract topp <LIMIT> users
for index, scoreboard_user in enumerate(last_scoreboard[:LIMIT]):
    name = scoreboard_user["username"]
    user = users[name]
    last_challenge = scoreboard_user["num_solves"]
    base = {
        "name": f"#{index + 1}. {name} {last_challenge}🏆",
        "step": "left",
    } 
    series["challenges"].append({**base, **{"data": user["challenges"]}});

with open("series.json", "w") as f:
    json.dump(series, f)

print("Done!")
