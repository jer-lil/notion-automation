#! /usr/bin/python3

import os
import logging
import pprint
import json
from notion_client import Client
from notion_client import helpers

import notion_automation.notion_automation as na
from hidden import tokens

filter_recurring_tasks = {
        "and": [
            {
                "property": "Next Due",
                "formula": {
                    "string": {
                        "is_not_empty": True
                    }
                }
            },
            {
                "or": [
                    {
                        "property": "Done",
                        "checkbox": {
                            "equals": True
                        }
                    },
                    {
                        "property": "Kanban - State",
                        "select": {
                            "equals": "Done"
                        }
                    }
                ]
                
            }
        ]
}

filter_done = {
    "property": "Done", 
    "checkbox": { 
        "equals": True, 
    }
}

if __name__ == "__main__":  

    filter = {"property": "Name", "text": {"contains": "Recurring"}}

    notion = Client(auth=tokens.TOKEN_JEREMIAH)

    tasks = na.getDbMembers(notion, tokens.DB_ID_TODO_PERSONAL, filter_done)

    # Need to filter out properties that we care about.
    # Or do we? Could just make a shorthand way to read properties 
    #   vs. filtering it down and getting rid of the data
    # It might be nice as a utility function to output readable data

    for task in tasks:
        task = helpers.pick(task.get('properties'), 'Task', 'Done')
        print(json.dumps(task, indent=4))
    
    for task in tasks:

