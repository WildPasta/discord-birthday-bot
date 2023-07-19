# Discord Birthday Bot

## Purpose

The purpose of this bot is to tag users on their birthday.

## Setup

First, you have to fill out the `birthdays.json` file with the user's ID and their birthday.
An example is provided in the repository.
Then, you have to run `init.py` to create the database from the json data.

Also, you have to create a `.env` file next to main.py with the following content:

```bash
DISCORD_CHANNEL="channel_to_post_in"
DISCORD_TOKEN="your_discord_token"
```

To add the cronjob, run `crontab -e` and add the following line:

```bash
# Run every day at 10:00
0 10 * * * /usr/bin/python3 /path/to/main.py
```

You can check the list of existing cron jobs by running `crontab -l` on the terminal. 

## Add birthday

To update the database with birthdays, either you can edit with software such as SQLiteStudio or you can edit `birthdays.json` file and run `init.py` again.

## Troubleshooting

Ensure that the date in `birthdays.json` are in format `YYYY-MM-DD`.