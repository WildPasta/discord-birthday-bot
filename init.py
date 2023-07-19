from datetime import datetime
import logging
import sqlite3
import os
import sys
from pythonjsonlogger import jsonlogger
import json

version = "1.0.1"
database="database.db"

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        log_record['source'] = log_record.pop('name')
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

def setup_logger(name):
    # Initialize logger
    logger = logging.getLogger(name)

    # Set up logger debug level
    logger.setLevel(logging.DEBUG)
    
    # Set up the format of the log file
    formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')

    # Set up file 
    file_handler = logging.FileHandler(('birthday_bot.log'))
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger

def sql_create_database(logger):
    """
    Build a database using the SQL file
    """

    tables_sql = "create.sql"

    # check if files exists
    if not os.path.exists(tables_sql):
        logger.debug("missing .sql files")
        exit(1)

    dbSocket = sqlite3.connect(database)
    cursor = dbSocket.cursor()

    logger.debug("SQL file is OK")

    with open(tables_sql, 'r') as file:
        req = ""
        for line in file:
            req += line
        cursor.executescript(req)
        dbSocket.commit()

    logger.debug("Tables are created")

def is_user_unique(discord_id):
    """
    Check if the user with the given discord_id is unique in the database.
    Return True if the user is unique (not in the database), False otherwise.
    """
    
    dbSocket = sqlite3.connect(database)
    cursor = dbSocket.cursor()

    req = "SELECT discord_id FROM USERS WHERE discord_id=?"
    data = [discord_id]
    cursor.execute(req, data)
    user = cursor.fetchone()
    cursor.close()

    return not user

def sql_insert_person(discord_id, birthday, logger):
    """
    Insert a person in the database
    """
    if not is_user_unique(discord_id):
            logger.debug("User with discord_id: {} already exists in the database. Skipping insertion.".format(discord_id))
            return
    try:
        dbSocket = sqlite3.connect(database)
        cursor = dbSocket.cursor()

        req = "INSERT INTO USERS (discord_id, birthday) VALUES (?, ?)"
        data = [discord_id, birthday]
        cursor.execute(req, data)
        dbSocket.commit()
        cursor.close()
        
        logger.debug("Inserted user in database: " + str(discord_id) + " " + str(birthday))

    except sqlite3.OperationalError:
        logger.debug("Database has been locked because of a previous error for user: " + str(discord_id))
    except Exception as e:
        logger.debug("Unexpected error: " + str(e))

def validate_user_data(user_data):
    """
    Validate user data from the JSON file
    """
    if not isinstance(user_data, dict) or "discord_id" not in user_data or "birthday" not in user_data:
        return False

    discord_id = user_data["discord_id"]
    birthday = user_data["birthday"]

    if not isinstance(discord_id, str) or not isinstance(birthday, str):
        return False

    return True

def main():
    # Set up the logger
    logger = setup_logger(__name__)

    try:
        # Create database if not exists
        if not os.path.exists(database):
            sql_create_database(logger)

        # Insert birthday in the database from the JSON file
        if not os.path.exists("birthdays.json"):
            logger.debug("missing birthdays.json file")
            exit(1)

        # Parse json file to insert data in the database
        with open("birthdays.json", "r") as file:
            data = json.load(file)

            for user in data['users']:
                if validate_user_data(user):
                    discord_id = user['discord_id']
                    birthday = user['birthday']
                    sql_insert_person(discord_id, birthday, logger)
                else:
                    logger.debug("Invalid user data in the JSON file")

    except Exception as e:
        logger.debug("Unexpected error: " + str(e))

if __name__ == "__main__":
    sys.exit(main())