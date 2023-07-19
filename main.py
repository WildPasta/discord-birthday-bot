import sys
import sqlite3
from datetime import datetime
import init
import discord
from dotenv import load_dotenv
import os

version = "1.0.1"
database = "database.db"
logger = init.setup_logger(__name__)

def main():
    load_dotenv()
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    DISCORD_CHANNEL = os.getenv('DISCORD_CHANNEL')

    # Load the discord intents
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'BirthdayBuddy v{version} bot has connected to Discord!')
        logger.info(f'BirthdayBuddy v{version} bot has connected to Discord!')

        today = datetime.today()

        dbSocket = sqlite3.connect(database)
        cursor = dbSocket.cursor()

        req = "SELECT discord_id FROM USERS WHERE strftime('%m-%d', birthday) = ?"
        data = [today.strftime('%m-%d')]
        cursor.execute(req, data,)
        birthdays_today = cursor.fetchall()

        cursor.close()

        logger.info("Birthdays have been requested from the database")
        
        if birthdays_today:
            print("Birthdays today:")
            for discord_id in birthdays_today:
                print(f"Discord ID: {discord_id[0]}")
                logger.info("Birthday today: " + str(discord_id[0]))
                channel = client.get_channel(int(DISCORD_CHANNEL))
                if channel:
                    message = f"🎉 Bon anniversaire <@{discord_id[0]}> ! 🎉"
                    await channel.send(message)

    client.run(DISCORD_TOKEN)

if __name__ == "__main__":
    sys.exit(main())
