import requests
import pandas as pd
from datetime import datetime
import os
import json
import time

# Get today's date in DD-MM-YYYY format
today = datetime.now().strftime('%d-%m-%Y')
# today = '2-10-2025'  # For testing purposes

# File path
file_path = f'data/futbol/{today}-promiedos.json'

# Threshold for refetch: 3 hours for close events (within 48 hours)
threshold = 3 * 3600  # seconds

# Check if file exists and is recent
if os.path.exists(file_path):
    mtime = os.path.getmtime(file_path)
    if time.time() - mtime < threshold:
        print("Loading recent data from file...")
        # Load from file
        with open(file_path, 'r') as f:
            data = json.load(f)
    else:
        print("Data is old, refetching from API...")
        # Refetch
        url = f'https://api.promiedos.com.ar/games/{today}'
        response = requests.get(url)
        data = response.json()
        # Save to file
        os.makedirs('data/futbol', exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f)
else:
    print("Fetching new data from API...")
    # Fetch the data
    url = f'https://api.promiedos.com.ar/games/{today}'
    response = requests.get(url)
    data = response.json()
    # Save to file
    os.makedirs('data/futbol', exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f)

# Extract games from leagues
leagues = data.get('leagues', [])
games = []
for league in leagues:
    games.extend(league.get('games', []))

# Create DataFrame and describe
df = pd.DataFrame(games)
print(df.info())

# example data structure
#  {
#     "name": "Ligue 1",
#     "id": "df",
#     "url_name": "ligue-1",
#     "country_id": "f",
#     "show_country_flags": false,
#     "allow_open": true,
#     "country_name": "Francia",
#     "is_international": false,
#     "games": [
#         {
#             "id": "eegecgc",
#             "stage_round_name": "Fecha 7",
#             "winner": -1,
#             "teams": [
#                 {
#                     "name": "Paris FC",
#                     "short_name": "Paris FC",
#                     "url_name": "paris-fc",
#                     "id": "gahf",
#                     "country_id": "f",
#                     "allow_open": true,
#                     "colors": {
#                         "color": "#19204B",
#                         "text_color": "#FFFFFF"
#                     },
#                     "red_cards": 0
#                 },
#                 {
#                     "name": "Lorient",
#                     "short_name": "Lorient",
#                     "url_name": "lorient",
#                     "id": "ehc",
#                     "country_id": "f",
#                     "allow_open": true,
#                     "colors": {
#                         "color": "#F4521D",
#                         "text_color": "#000000"
#                     },
#                     "red_cards": 0
#                 }
#             ],
#             "url_name": "paris-fc-vs-lorient",
#             "status": {
#                 "enum": 1,
#                 "name": "Prog.",
#                 "short_name": "Prog.",
#                 "symbol_name": "Prog."
#             },
#             "start_time": "03-10-2025 15:45",
#             "game_time": -1,
#             "game_time_to_display": "",
#             "game_time_status_to_display": "Prog.",
#             "tv_networks": [
#                 {
#                     "id": "hhgb",
#                     "name": "Disney+ Premium"
#                 }
#             ],
#             "main_odds": {
#                 "options": [
#                     {
#                         "name": "1",
#                         "value": 1.83,
#                         "trend": 2
#                     },
#                     {
#                         "name": "X",
#                         "value": 3.9,
#                         "trend": 1
#                     },
#                     {
#                         "name": "2",
#                         "value": 4.0,
#                         "trend": 1
#                     }
#                 ]
#             }
#         }

# Show only the games with Team 1 vs Team 2 (league) - start time - tv_networks (name)
for league in leagues:
    league_name = league.get('name', 'Unknown League')
    for game in league.get('games', []):
        teams = game.get('teams', [])
        if len(teams) == 2:
            team1 = teams[0].get('name', 'Team 1')
            team2 = teams[1].get('name', 'Team 2')
            start_time = game.get('start_time', 'Unknown Time')
            tv_networks = game.get('tv_networks', [])
            tv_names = [tv.get('name', '') for tv in tv_networks]
            tv_str = ', '.join(tv_names) if tv_names else 'No TV'
            print(f"{team1} vs {team2} ({league_name}) - {start_time} - {tv_str}")