from datetime import datetime


# TODO extract these from results instead of statically defining
# -> this works for now, but wouldn't work for a different
#       database with identical column names :/
ID_DONE = "_D%5ER"
ID_DUE = "bl%3D%3B"
ID_NEXT_DUE = "WcB%5C"




filter_default = {"page_size": 100}

filter_recurring_tasks = {
    "page_size": 10000,
    "filter": {
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
                "property": "Done",
                        "checkbox": {
                            "equals": True
                        }
            }
        ]
        
  }
}

filter_done_tasks = {
    "page_size": 10000,
    "filter": {
        "or": [
            {
                "and": [
                    {
                        "property": "Done",
                        "checkbox": {
                            "equals": True
                        }
                    },
                    {
                        "property": "Kanban - State",
                        "select": {
                            "does_not_equal": "Done"
                        }
                    },
                    {
                        "property": "Task",
                        "title": {
                            "is_not_empty": True
                        }
                    },     
                ]
            },
            {
                "and": [
                    {
                        "property": "Done",
                        "checkbox": {
                            "equals": False
                        }
                    },
                    {
                        "property": "Kanban - State",
                        "select": {
                            "equals": "Done"
                        }
                    },
                    {
                        "property": "Task",
                        "title": {
                            "is_not_empty": True
                        }
                    },    
                ]
            }
        ]       
    }
}

# json body for updating recurring tasks
def properties_recurring(task):
    due_iso = datetime.strptime(task['next_due'], 
        '%B %d, %Y').date().isoformat()
    body = {
                "properties": {
                    ID_DONE: {
                        "checkbox": False
                    },
                    ID_DUE: {
                        "date": {
                            "start": due_iso
                        }
                    }

                }
            }
    return body