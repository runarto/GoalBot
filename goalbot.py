import logic
import sched
import time
from datetime import datetime
from dateutil import parser
import perms
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import timedelta, datetime

channel_id = perms.CHANNEL_ID

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.message_content = True
client = discord.Client(intents=intents)
channel = client.get_channel(channel_id)
scheduler = AsyncIOScheduler()

# Assuming get_todays_matches is defined as you provided


async def check_for_goals(match_id, channel):
    goal_messages, current_status = logic.check_goals_and_create_message(match_id)[:2]

    for message in goal_messages:
        await channel.send(message)

    if current_status != "FT":
        scheduler.add_job(check_for_goals, 'date', run_date=datetime.now() + timedelta(minutes=1), 
                          args=[match_id, channel, scheduler])

async def schedule_goal_checks(matches, channel):
    for match in matches:
        match_start_time = parser.isoparse(match['date'])
        # Schedule check_for_goals to start when the match starts and repeat every minute
        scheduler.add_job(check_for_goals, 'interval', minutes=1, 
                          start_date=match_start_time, 
                          args=[match['match_id'], channel], 
                          misfire_grace_time=60)  # handle slight delays in job execution

async def main():
    await client.wait_until_ready()

    # Schedule get_todays_matches at midnight
    scheduler.add_job(logic.get_todays_matches, 'cron', hour=0)

    # Get today's matches and schedule goal checks (if bot was down)
    matches = logic.get_todays_matches()
    await schedule_goal_checks(matches, channel)

    # Start the scheduler
    scheduler.start()

    # Start the Discord bot
    await client.start(perms.TOKEN)  # Replace 'your_token' with your bot's token


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


async def check_for_goals_and_status(match_id, channel):

    # Check the current status of the match
    messages, current_status, home_team, away_team, home_team_goals, away_team_goals = logic.check_goals_and_create_message(match_id)

    # If the game just finished, send a message
    if current_status == "FT":
        await channel.send(f"FT: {home_team} {home_team_goals} - {away_team_goals} {away_team}\n")
        return  # Stop further checks for this match

    # Check and send goal messages if the game is still ongoing
    if current_status != "FT":
        for message in messages:
            await channel.send(message)

