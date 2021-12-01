import json
import dateutil.parser
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
challenges = {}
print("Parsing {} commits and creating series.json".format(len(commits)))
for commit in commits:
    print("Parsing: {} - {}".format(commit.hexsha, commit.committed_date))
    content = repo.git.show('{}:{}'.format(commit.hexsha, "scoreboard.min.json")).strip()
    try:
        scoreboard = json.loads(content)["result"]
    except Exception as e:
        # print(scoreboard)
        # print("Error for scoreboard ", e)
        continue
    last_scoreboard = scoreboard
    for scoreboard_user in scoreboard:
        current_challenges = int(scoreboard_user["challenges_solved"])
        current_eggs = int(scoreboard_user["eggs_solved"])
        name = scoreboard_user["display_name"]
        print(scoreboard_user)
        print(name)
        exit(0)
        # FIXME: Dateparsing is extremly costly, see if we can just pass the last_solved isoformat to frontend
        # Let's use the commit date for now...
        # last_solve = round(dateutil.parser.parse(scoreboard_user["last_solved"]).timestamp()) * 1000
        last_solve = round(commit.committed_date * 1000)

        if name not in users:
            users[name] = {
                "last_solve": last_solve,
                "challenges": [format_item(last_solve, current_challenges)],
                "eggs": [format_item(last_solve, current_eggs)],
            }
            continue

        user = users[name]

        if len(user["challenges"]) > 0:
            last_challenge = user["challenges"][-1]
            if current_challenges != last_challenge[1]:
                user["challenges"].append(format_item(last_solve, current_challenges))


        if len(user["eggs"]) > 0:
            last_egg = user["eggs"][-1]
            if current_eggs != last_egg[1]:
                user["eggs"].append(format_item(last_solve, current_eggs))

        users[name] = user

exit(0)
series = {
    "challenges": [],
    "eggs": [],
}

# Only extract topp <LIMIT> users
for index, scoreboard_user in enumerate(last_scoreboard[:LIMIT]):
    name = scoreboard_user["display_name"]
    user = users[name]
    last_challenge = scoreboard_user["challenges_solved"]
    last_egg = scoreboard_user["eggs_solved"]
    base = {
        "name": "#{}. {} ({}🏆 - {}🥚)".format(index + 1, name, last_challenge, last_egg),
        "step": "left",
    } 
    series["challenges"].append({**base, **{
        "data": user["challenges"],
    }});
    series["eggs"].append({**base, **{
        "data": user["eggs"],
    }});

with open("series.json", "w") as f:
    json.dump(series, f)

print("Done!")
