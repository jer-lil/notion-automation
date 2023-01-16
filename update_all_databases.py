#! /usr/bin/python3

import datetime
import os
import notion_automation
from hidden import tokens

logs_folder_path = '/logs'

if __name__ == "__main__":
    # First make sure the "logs" folder exists:
    # TODO this is dumb, need to figure out cron folder permissions
    assert os.path.isdir(logs_folder_path), f"logs folder doesn't exist, \
        please create it"

    # UPDATE JEREMIAH'S PERSONAL DATABASE
    notion_automation.updateDatabase(tokens.TOKEN_JEREMIAH, 
        tokens.DB_ID_TODO_PERSONAL, db_name = 'TODO_JER_PERSONAL')
    
    # UPDATE JEREMIAH'S WORK DATABASE
    notion_automation.updateDatabase(tokens.TOKEN_JEREMIAH, 
        tokens.DB_ID_TODO_WORK, db_name = 'TODO_JER_WORK')

    # UPDATE MEERA'S DATABASE
    notion_automation.updateDatabase(tokens.TOKEN_MEERA, 
        tokens.DB_ID_TODO_MEERA, db_name = 'TODO_MEERA')

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nFinished updating Notion databases at {now}")