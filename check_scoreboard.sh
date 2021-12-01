#!/bin/bash
## NOTICE
# Dirty quick script to track the NPST2021 scoreboard. Buy me a beer :))

## CONSTANTS
BASE_URL="https://wiarnvnpsjysgqbwigrn.supabase.co"
LOGIN_URL="$BASE_URL/auth/v1/token?grant_type=password"
SCOREBOARD_URL="$BASE_URL/rest/v1/scoreboard?select=*"
SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

## GOGO
echo "Starting script..."
cd $SCRIPT_PATH # dirty
source "$SCRIPT_PATH/.env"

# Login
DASS_TOKEN=$(curl -s "$LOGIN_URL" -H "apikey: $DASS_APIKEY" -H "content-type: application/json" -d "{\"email\":\"$DASS_EMAIL\",\"password\":\"$DASS_PASSWORD\"}" | jq -r '.access_token')

# Download newest scoreboard
curl -s "$SCOREBOARD_URL" -H "apikey: $DASS_APIKEY" -H "authorization: Bearer $DASS_TOKEN" -o "$SCRIPT_PATH/scoreboard.min.json"
# Let's "prettify" the json as well
cat "$SCRIPT_PATH/scoreboard.min.json" | jq > "$SCRIPT_PATH/scoreboard.json"

if [[ `git status --porcelain` ]]; then
	echo "There are differences, updating"
	git add -A
	git commit -m "[SCOREBOARD] update"
	git push origin main
  # TODO:
  # python3 ./generate_series.py
else
	echo "No differences"
fi
