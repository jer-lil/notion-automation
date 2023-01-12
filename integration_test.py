#! /usr/bin/python3

import json
import requests
import datetime
import os
import notion_filters as filters
from hidden import tokens





logs_folder_path = 'logs'
output_file_default = '/log_default.json'

def _mapNotionResultToTask(result):
        # you can print result here and check the format of the answer.
        task_id = result['id']
        properties = result['properties']
        task_name = properties['Task']['title'][0]['text']['content']
        due_date = properties['Due']['date']['start']
        next_due = properties['Next Due']['formula']['string']
        kanban_state = properties['Kanban - State']['select']['name']
        done = properties['Done']['checkbox']
        return {
            'task_name': task_name,
            'due_date': due_date,
            'next_due': next_due,
            'kanban_state': kanban_state,
            'done': done,
            'task_id': task_id
        }

def getTasks(token, db_id, json_filter, output_file):
    url = f'https://api.notion.com/v1/databases/{db_id}/query'
    headers={
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-02-22"
        }
    r = requests.post(url, headers=headers, json=json_filter)
    result_dict = r.json()
    assert result_dict['object'] != "error", result_dict['message']

    # Write raw json results to file for debugging
    with open(f'{logs_folder_path}/result_dump.json', 'w+') as f:
        json.dump(result_dict, f, indent=4)

    list_result = result_dict['results']
    tasks = []
    for task in list_result:
        task_dict = _mapNotionResultToTask(task)
        tasks.append(task_dict)

    # Write recurring tasks to file
    with open(output_file, 'w+') as f:
        json.dump(tasks, f, indent=4)

    return tasks

def _updateTask(token, page_id, body):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Notion-Version": "2022-02-22",
        "Content-Type": "application/json"
    }
    try:
        res = requests.patch(url, headers=headers, json=body)
    except requests.exceptions.Timeout as errt:
        print(f"Timeout. {errt}")
    except requests.exceptions.TooManyRedirects as errr:
        print(f"Too many redirects, bad URL. {errr}")
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        raise SystemExit(e)


def updateTasks(token, tasks, body_func):
    for task in tasks:
        body = body_func(task)
        _updateTask(token, task['task_id'], body)
    return

def updateDatabase(token, db_id, filter_get, filter_update, output_file):
    # Grab all recurring tasks that are completed
    tasks_recurring = getTasks(token, db_id, filter_get, output_file)
    # Uncheck "Done" and update "Due" to "Next Due"
    updateTasks(token, tasks_recurring, filter_update)
    
if __name__ == "__main__":
    # First make sure the "logs" folder exists:
    assert os.path.isdir(logs_folder_path), f"logs folder doesn't exist, please create it"

    filter_get = filters.filter_recurring_tasks
    filter_update = filters.properties_recurring

    # UPDATE JEREMIAH'S PERSONAL DATABASE
    updateDatabase(tokens.TOKEN_JEREMIAH, tokens.DB_ID_TODO_PERSONAL, 
        filter_get, filter_update,
        output_file = f'{logs_folder_path}/recurring_tasks_jeremiah_personal.json',
        )
    
    # UPDATE JEREMIAH'S WORK DATABASE
    updateDatabase(tokens.TOKEN_JEREMIAH, tokens.DB_ID_TODO_WORK, 
        filter_get, filter_update,
        output_file = f'{logs_folder_path}/recurring_tasks_jeremiah_work.json',
        )

    # UPDATE MEERA'S DATABASE
    updateDatabase(tokens.TOKEN_MEERA, tokens.DB_ID_TODO_MEERA, 
        filter_get, filter_update,
        output_file = f'{logs_folder_path}/recurring_tasks_meera.json',
        )

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Updating Notion Databases at \n{now}") 
'''
    tasks_done = getTasks(json_filter=filters.filter_done_tasks, 
        output_file="/logs/done_tasks.json"
    )
'''   