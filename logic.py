import requests
from datetime import timedelta, datetime
import pytz  # This library is used for time zone conversions
from perms import API_TOKEN
from dateutil import parser

    

#Returnerer liste over kamper denne dagen. Kjør denne en gang daglig klokka 00:00

def get_todays_matches(x_days=1):
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
    if response.status_code == 200:
        data = response.json()
        match_details = []
        for fixture in data['response']:
                match_info = {
                    'match_id': fixture['fixture']['id'],  # Added line to include match ID
                    'date': fixture['fixture']['date'],
            }
        match_details.append(match_info)
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
        "from": datetime.now().strftime("%Y-%m-%d"),
        "to": datetime.now().strftime("%Y-%m-%d")
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

    response = requests.get(api_url, headers=headers)
    messages = []

    if response.status_code == 200:
        data = response.json()
        
        for event in data['response']:
            if event['type'] == 'Goal':
                # Fetch current score
                current_status = event['fixture']['status']['short']
                home_team_goals = event['goals']['home']
                away_team_goals = event['goals']['away']
                home_team = event['fixture']['teams']['home']['name']
                away_team = event['fixture']['teams']['away']['name']

                goal_info = {
                    'team_name': event['team']['name'],
                    'player_goal': event['player']['name'],
                    'player_assist': event.get('assist', {}).get('name', 'Ingen målgivende'),
                }

                message = f"Mål for {goal_info['team_name']}!\n" \
                          f"{home_team} {home_team_goals} - {away_team_goals} {away_team}\n" \
                          f"Mål: {goal_info['player_goal']}\n" \
                          f"Målgivende: {goal_info['player_assist']}"
                messages.append(message)

    return messages, current_status, home_team, away_team, home_team_goals, away_team_goals 


print(get_todays_matches(2))