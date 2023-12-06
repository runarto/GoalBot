
from perms import API_TOKEN
import requests

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
            goal_type = ""

            # Check for Normal Goal, Own Goal, Penalty, or VAR
            if event['type'] == 'Goal':
                # Check if the goal is a penalty
                goal_type = "straffe" if 'Penalty' in event['detail'] else "Mål"
            elif event['type'] == 'Own Goal':
                goal_type = "selvmål"


            if (event['type'] == 'VAR') and (event['detail'] == 'Goal cancelled'):
                message += f"Målet til {event['team']['name']} ble annulert\n"
                message += f"{home_team} {home_team_goals} - {away_team_goals} {away_team}\n"
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
                    message += f"{home_team} [{home_team_goals}] - {away_team_goals} {away_team}\n" \
                    f"Mål: {player_name}\n"
                    message += f"Målgivende: {assist_info}"
                    messages.append(message)
            
                else:
                    message += f"{home_team} {home_team_goals} - [{away_team_goals}] {away_team}\n" \
                    f"Mål: {player_name}\n"
                    message += f"Målgivende: {assist_info}"
                    messages.append(message)

    return messages, current_status, home_team, away_team, home_team_goals, away_team_goals