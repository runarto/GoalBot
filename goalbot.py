import logic
import sched
import time
from datetime import datetime
from dateutil import parser
import perms
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import timedelta, datetime
import asyncio
from apscheduler.jobstores.base import JobLookupError
from apscheduler.triggers.date import DateTrigger

channel_id = perms.CHANNEL_ID

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.message_content = True
client = discord.Client(intents=intents)
channel = client.get_channel(channel_id)
scheduler = AsyncIOScheduler()

# Assuming get_todays_matches is defined as you provided

client.event
async def check_for_goals(match_id, matches):

    current_status = check_for_goals_and_status(match_id)

    job_id = f"match_{match_id}"

    if current_status in ["1H", "2H", "HT", "ET", "BT", "P", "LIVE"]:
        return
    
    if current_status in ["FT", "AET", "PEN", "PST", "CANC", "ABD", "AWD", "WO"]:
        for job in scheduler.get_jobs():
            if job.id.startswith(f"check_goals_{match_id}"):
                try:
                    scheduler.remove_job(job.id)
                except JobLookupError:
                    pass  # Job was not found, no action needed
        scheduler.remove(job_id)

        

async def schedule_goal_checks(matches, channel):
    for match in matches:
        match_start_time = parser.isoparse(match['date'])
        job_id = f"check_goals_{match['match_id']}"  # Unique identifier for the job
        scheduler.add_job(check_for_goals, 'interval', minutes=1, 
                          start_date=match_start_time, 
                          args=[match['match_id'], matches], 
                          misfire_grace_time=60, id=job_id)
        
        game_started_job_id = f"game_started_{match['home_team']}"
        scheduler.add_job(lambda: asyncio.create_task(game_started(match['match_id'])),
                          trigger=DateTrigger(run_date=match_start_time),
                          id=game_started_job_id)
        
    jobs = scheduler.get_jobs()

    print("Scheduled Jobs:")
    for job in jobs:
        print(f"Job ID: {job.id}")
        print(f"Next Run Time: {job.next_run_time}")
        print(f"Job Function: {job.func_ref}")
        print("-" * 20)



async def main():
    
    # Schedule get_todays_matches at midnight
    matches = scheduler.add_job(lambda: asyncio.create_task(logic.get_todays_matches(0)), 'cron', hour=0, id = "get_todays_matches")

    # Start the scheduler
    scheduler.start()

    # Get today's matches and schedule goal checks (if bot was down)
    matches = logic.get_todays_matches(0)
    
    await schedule_goal_checks(matches, channel)

    # Start the Discord bot
    await client.start(perms.TOKEN)  # Replace 'your_token' with your bot's token


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')



@client.event 
async def game_started(match_id):
    messages, current_status, home_team, away_team, home_team_goals, away_team_goals = logic.check_goals_and_create_message(match_id)
    if current_status in ['1H', '2H', 'HT', 'ET', 'P', 'LIVE']:
        message = f"Kamp startet: {home_team} - {away_team}"
        await channel.send(message)
    

@client.event
async def check_for_goals_and_status(match_id):

    # Check the current status of the match
    messages, current_status, home_team, away_team, home_team_goals, away_team_goals = logic.check_goals_and_create_message(match_id)

    for message in messages:
        if message in logic.local_dict:
            messages.remove(message)
        else:
            logic.local_dict[home_team] = message


    # If the game just finished, send a message
    if current_status in  ["FT", "AET", "PEN"]:
        await channel.send(f"FT: {home_team} {home_team_goals} - {away_team_goals} {away_team}\n")
        return  # Stop further checks for this match

    # Check and send goal messages if the game is still ongoing
    if current_status in ["1H", "2H", "HT", "ET", "BT", "P", "LIVE"]:
        for message in messages:
            await channel.send(message)
        
    return current_status

