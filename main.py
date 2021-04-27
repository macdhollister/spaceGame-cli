import os

from dotenv import load_dotenv

import facility
import faction
import planet
import report
import ship

from InquirerPy import inquirer as iq

from src.utils.db import Database

if __name__ == '__main__':
    script_choice = iq.select(
        message="Which script should be run?",
        choices=[
            {'name': 'facility', 'value': facility},
            {'name': 'faction', 'value': faction},
            {'name': 'planet', 'value': planet},
            {'name': 'report', 'value': report},
            {'name': 'ship', 'value': ship}
        ]
    ).execute()

    action = iq.select(
        message="Action:",
        choices=list(script_choice.switcher.keys())
    ).execute()

    load_dotenv()
    database_url = os.environ['DATABASE_URL'] if 'DATABASE_URL' in os.environ else 'sqlite://'
    database = Database(database_url).get_db()

    script_choice.switcher.get(action)(database)
