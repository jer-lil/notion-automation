#! /usr/bin/python3

import json
import requests
import datetime
import body_params as params

logs_folder_path = 'logs'
errors_filename = 'errors'

def _jsonLogDump(file_path, contents):
    now = datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
    file_path = f'{file_path}--{now}.json'
    with open(file_path, 'w+') as f:
        f.write(f"File updated at {now}\n\n")
        json.dump(contents, f, indent=4)

"""
Takes in raw JSON params for a page and returns a dict with usable 
    values extracted

#TODO tasks should probably be a class

:param task_raw: JSON object with raw params for that notion page
"""
def _extractParameters(task_raw):
        # 
        properties = task_raw['properties']
        return {
            'task_name': task_raw['properties']['Task']['title'][0]['text']['content'],
            'due_date': task_raw['properties']['Due']['date']['start'],
            'next_due': task_raw['properties']['Next Due']['formula']['string'],
            'kanban_state': task_raw['properties']['Kanban - State']['select']['name'],
            'done': task_raw['properties']['Done']['checkbox'],
            'recurring_priority': task_raw['properties']['Recurring Priority']['select']['name'],
            'task_id': task_raw['id']
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

    # Uncomment for debug purposes, don't normally need all of this raw data
    # _jsonLogDump(output_file, result_dict)

    list_result = result_dict['results']
    tasks = []
    for task_raw in list_result:
        task_dict = _extractParameters(task_raw)
        tasks.append(task_dict)
    
    _jsonLogDump(output_file, tasks)

    return tasks

def _updateTask(token, task, body):
    url = f'https://api.notion.com/v1/pages/{task["task_id"]}'
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
    e = f'Got error code {res.status_code} when updating task \
        \n -> Task Name: "{task["task_name"]}" \
        \n -> Page ID: {task["task_id"]} \
        \n -> Reason: {res.reason}'
    assert res.status_code == 200, e



def updateTasks(token, tasks, body_func):
    for task in tasks:
        body = body_func(task)
        print(f'Updating Task: {task["task_name"]}')
        print(f'Updating Parameters: {body}\n')
        _updateTask(token, task, body)
    return

"""
For now this is kind of a "do it all" function that just performs the database
    updates that we want performed every day.

:param token: 
:param db_id: 
:param db_name: database name, used to sort log files

TODO: do something smarter with output files to support multiple data dumps per
    database update. Maybe take in a folder name (db name) and put files in
    that subfolder. 
"""
def updateDatabase(token, db_id, db_name):

    # Update recurring tasks that are marked as complete
    output_file = 'recurring_tasks'
    output_path = f'{logs_folder_path}/{db_name}/{output_file}'
    tasks_recurring = getTasks(token, db_id, params.filter_recurring_tasks,
        output_path)
    updateTasks(token, tasks_recurring, params.get_prop_recurring)

    # Resolve conflicts of "Done" checkbox and Kanban State
    output_file = 'done_conflict_tasks'
    output_path = f'{logs_folder_path}/{db_name}/{output_file}'
    tasks_done_conflicted = getTasks(token, db_id, 
        params.filter_done_conflict_tasks, output_path)
    updateTasks(token, tasks_done_conflicted, params.get_prop_done)

if __name__ == "__main__":
    from hidden import tokens    