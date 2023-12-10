from datetime import datetime


# TODO extract these from results instead of statically defining
# -> this works for now, but wouldn't work for a different
#       database with identical column names :/
# -> update, it seems to work with my work list and meera's list, so maybe I'm wrong? 
# -> update, seems like it can just be plain text of the property name? Which
#       makes sense because that's how the filters behave...
# XXX define these in a better way that's shared with other files
ID_DONE = "Done" #_D%5ER
ID_DUE = "Due" #bl%3D%3B
ID_NEXT_DUE = "Next Due" #WcB%5C
ID_KANBAN_STATE = "Kanban - State" #xkX~"
ID_PRIORITY = "Priority"  #bbfM

""" 
FILTERS DEFINITIONS

These return a JSON object defining the "Properties" body parameter defined
    here: https://developers.notion.com/reference/post-database-query

TODO: possibly turn all of these into functions, could be useful even just
    to set the max page size, and less confusing to not have a mix of filters
    and statically defined JSON.
"""

"""
Can be used as a default filter, returns all pages up to 100
"""
filter_default = {"page_size": 100}

"""
JSON filter to return all recurring tasks that are marked as "Done"

Recurring tasks are identified by checking if the "Next Due" property 
is not empty.

Task completion is checked in both the "Done" checkbox and Kanban state.
"""
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
}

"""
JSON filter to return all tasks that are in a conflicted state, meaning they 
    are marked completed in either the "Done" Kanban state or the "Done" 
    checkbox, but not both.

The main purpose would be to resolve these conflicts, and with a simple
    filter such as this one, the only way would be to mark them as "Done"
    in both places, so this would only enable a one-way conflict resolution.
"""
filter_done_conflict_tasks = {
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

""" 
PROPERTIES DEFINITIONS

These return a JSON object defining the "Properties" body parameter defined
    here: https://developers.notion.com/reference/patch-page
"""

"""
Properties for updating recurring tasks.

:property Done: Checkbox unchecked
:property Kanban - State: Set to "To Do"
:property Due: Date set equal to "Next Due" property value
"""
def get_prop_recurring(task):
    due_iso = datetime.strptime(task['next_due'], 
        '%B %d, %Y').date().isoformat()
    body = {
                "properties": {
                    "Done": {
                        "checkbox": False
                    },
                    ID_KANBAN_STATE: {
                        "select": {
                            "name": "To Do"
                        }
                    },
                    ID_DUE: {
                        "date": {
                            "start": due_iso
                        }
                    },
                    ID_PRIORITY: {
                        "select": {
                            "name": task['recurring_priority']
                        }
                    }
                }
            }
    return body

"""
Properties for updating conflicted tasks to be in the "Done" state in both
    the checkbox property and the "Kanban - State" property.

:property: Done: Checkbox checked
:property Kanban - State: "Done"
"""
def get_prop_done(task):
    body = {
                "properties": {
                    ID_DONE: {
                        "checkbox": True
                    },
                    ID_KANBAN_STATE: {
                        "select": {
                            "name": "Done"
                        }
                    }
                }
            }
    return body
