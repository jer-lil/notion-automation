#! /usr/bin/python3

import os
import logging
import notion_automation.util as util
from notion_client import Client

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
    import sys    
    print("In module products sys.path[0], __package__ ==", sys.path[0], __package__)
    
    from hidden import tokens

    filter = {"property": "Name", "text": {"contains": "Recurring"}}

    notion = Client(auth=tokens.TOKEN_JEREMIAH)

    tasks = util.getTasks(notion, tokens.DB_ID_TODO_PERSONAL, filter_done)

    for task in tasks:
        print(task.get("id"))
