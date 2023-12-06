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
local_dict = {}

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
    league_ids = ["39", "103"]
    match_details = [] 

    for league_id in league_ids:
        query_fixtures = {
            "league": league_id,
            "season": "2023",
            "timezone": "Europe/Oslo",
            "to": today_date,
            "from": formatted_new_date
        }
    
        response = requests.get(api_url, headers=headers, params=query_fixtures)
        # Initialize match_details outside the if statement
        if response.status_code == 200:
            data = response.json()
            for fixture in data['response']:
                match_info = {
                    'match_id': fixture['fixture']['id'],  # Added line to include match ID
                    'date': fixture['fixture']['date'],
                    'current_status': fixture['fixture']['status']['short'],
                    'home_team': fixture['teams']['home']['name']
                }
                match_details.append(match_info)  # Correct indentation, inside the loop
    
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



#Brukes til å hente ut events for en kamp


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

        test = []
        
        for event in data['response']:
        # Initialize assist_info to a default value
            assist_info = ""
            goal_type = ""
            time_played = event['time']['elapsed']
            extra_time = event['time']['extra']

            if extra_time is None:
                time_played = f"{time_played}'"
            else:
                time_played = f"{time_played}+{extra_time}'"
          

            # Check for Normal Goal, Own Goal, Penalty, or VAR
            if event['type'] == 'Goal':
                # Check if the goal is a penalty
                goal_type = "straffe" if 'Penalty' in event['detail'] else "Mål"
            elif event['type'] == 'Own Goal':
                goal_type = "selvmål"


            if (event['type'] == 'VAR') and (event['detail'] == 'Goal cancelled'):
                message += f"Målet til {event['team']['name']} ble annulert\n"
                message += f"{home_team} {home_team_goals} - {away_team_goals} {away_team} {time_played}\n "
                messages.append(message)

            
            if goal_type:
                team_name = event['team']['name']
                player_name = event['player']['name']
                if goal_type in ["Mål", "Straffe", "Selvmål"]:
                    assist_info = event.get('assist', {}).get('name', 'Ingen målgivende')
                
                if goal_type == "Mål":
                    message = f"**{goal_type} for {team_name}!**\n"
                elif goal_type == "Selvmål":
                    message = f"**{team_name} scorer {goal_type}!**\n"
                elif goal_type == "Straffe":
                    message = f"**{team_name} scorer på {goal_type}!**\n"


                if team_name == home_team:
                    message += f"{home_team} [{home_team_goals}] - {away_team_goals} {away_team} {time_played}\n" \
                    f"Mål: {player_name}\n"
                    message += f"Målgivende: {assist_info}"
                    messages.append(message)
            
                else:
                    message += f"{home_team} {home_team_goals} - [{away_team_goals}] {away_team} {time_played}\n" \
                    f"Mål: {player_name}\n"
                    message += f"Målgivende: {assist_info}"
                    messages.append(message)

    print(messages)
    return messages, current_status, home_team, away_team, home_team_goals, away_team_goals


#Her henter vi ut messages[-1] fordi det er det siste som skjedde. 



#Brukes til feilsøking


def get_fixture_events(match_id):
    api_url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/events?fixture={match_id}"
    headers = {
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
        "x-rapidapi-key": API_TOKEN
    }

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        for event in data['response']:
            print(event)
    else:
        return f"Error: Unable to fetch events for match {match_id}, Status Code: {response.status_code}"
    

#print(get_fixture_events(1035309))

#print(get_todays_matches(-3))


check_goals_and_create_message(1035309)