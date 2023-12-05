import requests
from datetime import timedelta, datetime
import pytz  # This library is used for time zone conversions
from perms import API_TOKEN
from dateutil import parser
import discord
import perms

channel_id = perms.CHANNEL_ID

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.message_content = True
client = discord.Client(intents=intents)
channel = client.get_channel(channel_id)

#Returnerer liste over kamper denne dagen. Kjør denne en gang daglig klokka 00:00


def get_todays_matches(x_days):
    today_date = datetime.now().strftime("%Y-%m-%d")
    new_date = datetime.now() + timedelta(days=x_days)
    formatted_new_date = new_date.strftime("%Y-%m-%d")  

    api_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
        "x-rapidapi-key": API_TOKEN  # Be cautious with your API key
    }
    query_fixtures = {
        "league": "39",
        "season": "2023",
        "timezone": "Europe/Oslo",
        "from": today_date,
        "to": formatted_new_date 
    }
    
    response = requests.get(api_url, headers=headers, params=query_fixtures)
    match_details = []  # Initialize match_details outside the if statement
    if response.status_code == 200:
        data = response.json()
        for fixture in data['response']:
            match_info = {
                'match_id': fixture['fixture']['id'],  # Added line to include match ID
                'date': fixture['fixture']['date'],
                'current_status': fixture['fixture']['status']['short']
            }
            match_details.append(match_info)  # Correct indentation, inside the loop
            print(match_info)
    return match_details



def check_if_game_started():
    api_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
        "x-rapidapi-key": API_TOKEN
    }
    query_fixtures = {
        "league": "39",  # Use the desired league ID
        "season": "2023",  # Adjust season as needed
        "timezone": "Europe/Oslo",
        "status": "LIVE"
    }

    response = requests.get(api_url, headers=headers, params=query_fixtures)
    if response.status_code == 200:
        data = response.json()
        for fixture in data['response']:
            if fixture['fixture']['status']['short'] in ['1H', '2H', 'HT', 'ET', 'P']:  # These statuses indicate the game is in progress
                return True
            elif fixture['fixture']['status']['short'] == 'FT':
                return None
    return False






def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")




def check_goals_and_create_message(match_id):
    api_url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/events?fixture={match_id}"
    headers = {
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
        "x-rapidapi-key": API_TOKEN
    }

    api_url2 = f"https://api-football-v1.p.rapidapi.com/v3/fixtures"

    query_fixtures = {
       "id": match_id
    }


    response = requests.get(api_url, headers=headers)
    specific_match = requests.get(api_url2, headers=headers, params=query_fixtures)
    messages = []
    
    if (response.status_code == 200) and (specific_match.status_code == 200):
        data = response.json()
        data2 = specific_match.json()

        fixture = data2['response'][0]
        current_status = fixture['fixture']['status']['short']
        home_team_goals = fixture['goals']['home']
        away_team_goals = fixture['goals']['away']
        home_team = fixture['teams']['home']['name']
        away_team = fixture['teams']['away']['name']
        
        for event in data['response']:
        # Initialize assist_info to a default value
            assist_info = ""

            if event['type'] == 'Normal Goal' or event['type'] == 'Own Goal':
                goal_type = "Mål" if event['type'] == 'Normal Goal' else "Selvmål"
                team_name = event['team']['name']
                player_name = event['player']['name']
            
            if goal_type == "Mål":
                assist_info = event.get('assist', {}).get('name', 'Ingen målgivende')

                # Construct the message based on goal type
            if event['type'] == "Normal Goal":
                message = f"{goal_type} for {team_name}!\n"
            elif event['type'] == "Own Goal":
                message = f"{team_name} scorer {goal_type}!\n"

        # Common part of the message
            message += f"{home_team} {home_team_goals} - {away_team_goals} {away_team}\n" \
                   f"Mål: {player_name}\n"
            if assist_info:
                message += f"Målgivende: {assist_info}"
                messages.append(message)
            
            else:
                message = "No goals yet.\n"
                messages.append(message)

    return messages, current_status, home_team, away_team, home_team_goals, away_team_goals






