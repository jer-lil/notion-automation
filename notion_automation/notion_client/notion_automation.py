#! /usr/bin/python3

import traceback
import json
import requests
import datetime
import os
from os.path import join
import notion_client.body_params as params

LOGS_FOLDER = 'logs'

def _jsonLogDump(file_path, contents, file_mode='w+'):
    with open(file_path, file_mode) as f:
        json.dump(contents, f, indent=4)

"""
Takes in raw JSON params for a page and returns a dict with usable 
    values extracted

TODO tasks should probably be a class

TODO fix / make more robust. Should method-ize repeated code

Some things are just hard coded if they don't exist
   -> Priority defaults to Medium
   -> Kanban State follows Done checkbox
   -> Due date gets left blank

:param task_raw: JSON object with raw params for that notion page
"""
def _extractParameters(task_raw):
    task_id = task_raw['id']
    properties = task_raw['properties']
    done = properties['Done']['checkbox']
    task_name = properties['Task']['title'][0]['text']['content']
    # Next due is a formula, it at least contains blank string
    next_due = properties['Next Due']['formula']['string']

    # Priority/Recurring Priority Check
    if properties['Recurring Priority']['select'] is not None:
        recurring_priority = properties['Recurring Priority']['select']['name']
    elif properties['Priority']['select'] is not None:
        recurring_priority = properties['Priority']['select']['name']
    else:
        # TODO at least make this not hard-coded...
        recurring_priority = "\ud83e\uddc0 Medium"
    
    # Kanban State Check
    if properties['Kanban - State']['select'] is not None:
        kanban_state = properties['Kanban - State']['select']['name']
    else:
        # If kanban state is empty, set it based on "Done" checkbox
        if done:
            print(f'    -> Kanban State missing, setting to "Done"')
            kanban_state = "Done"
        else:
            kanban_state = "To Do"
            print(f'    -> Kanban State missing, setting to "To Do"')
    
    # Due date check
    if properties['Due']['date'] is not None:
        due_date = properties['Due']['date']['start']
    else:
        # Leave due date blank
        due_date = None
        print(f'    -> Due Date missing, leaving blank')
    
    return {
        'task_name': task_name,
        'due_date': due_date,
        'next_due': next_due,
        'kanban_state': kanban_state,
        'done': done,
        'recurring_priority': recurring_priority,
        'task_id': task_id
    }

def getTasks(token, db_id, json_filter, log_file):
    url = f'https://api.notion.com/v1/databases/{db_id}/query'
    headers={
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-02-22"
        }
    r = requests.post(url, headers=headers, json=json_filter)
    result_dict = r.json()
    assert result_dict['object'] != "error", result_dict['message']

    # Uncomment for debug purposes, don't normally need all of this raw data
    #file_raw = log_file + "_raw" 
    #_jsonLogDump(file_raw, result_dict)

    list_result = result_dict['results']
    if len(list_result) < 1: 
        raise RuntimeError(f' -> No tasks found, moving on...')

    # Build usable list of Task dicts from raw json results 
    tasks = []
    for task_raw in list_result:
        task_name = task_raw["properties"]["Task"]["title"][0][
                "text"]["content"]
        print(f' -> Extracting Parameters from Task "{task_name}"')
        # skip task if any of the required properties are blank
        try:
            task_dict = _extractParameters(task_raw)
        except TypeError as e:
            #print(e)
            print(f'    -> Unhandled missing parameter, skipping this Task"')
            print("         -> Traceback below:\n")
            traceback.print_exc()
            print("")
        else:
            tasks.append(task_dict)
    
    _jsonLogDump(log_file, tasks)

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
        \n -> Reason: {res.reason} \
        \n -> Request Body: {body}' 
    assert res.status_code == 200, e

def updateTasks(token, tasks, body_func, log_file):
    for task in tasks:
        body = body_func(task)
        print(f' -> Updating Task: {task["task_name"]}')
        # Append task name to body parameters for logging
        log_contents = {"task_name": task["task_name"]}
        log_contents.update(body)
        _jsonLogDump(log_file, log_contents, file_mode='a+')
        _updateTask(token, task, body)
    return

"""
Creates a logs file including all intermediate directories.
Returns full path of logs file
"""
def createLogsFile(logs_folder_base, update_type, filename):
    log_folder = os.path.join(logs_folder_base, update_type)
    print(log_folder)
    os.makedirs(log_folder, exist_ok=True)
    return os.path.join(log_folder, filename)

"""
For now this is kind of a "do it all" function that just performs the database
    updates that we want performed every day.

Logs folder directory structure:

logs/
├─ DATABASE_A/
│  ├─ 2023-01-15--03-00-00/
│  │  ├─ update_type_a/
│  │  │  ├─ read.json
│  │  │  ├─ write.json
│  │  ├─ update_type_B/
│  │  │  ├─ read.json
│  │  │  ├─ write.json
│  ├─ 2023-01-15--03-00-00/
├─ DATABASE_B/

:param token: 
:param db_id: 
:param db_name: database name, used to sort log files

"""
def updateDatabase(token, db_id, db_name):
    # Create log folder for this database update
    now = datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")  
    log_folder = os.path.join(LOGS_FOLDER, db_name, now)

    # Update recurring tasks that are marked as complete
    update_type = 'recurring_tasks'
    try:
        print(f'\nAttempting to update "{update_type}" in database "{db_name}"')
        log_file_path = createLogsFile(log_folder, update_type, 'read.json')
        tasks_recurring = getTasks(token, db_id, params.filter_recurring_tasks,
            log_file_path)
    except RuntimeError as e:
        print(e)
    else:
        log_file_path = createLogsFile(log_folder, update_type, 'write.json')
        updateTasks(token, tasks_recurring, params.get_prop_recurring,
            log_file_path)
        print(" -> Finished updating")

    # Resolve conflicts of "Done" checkbox and Kanban State
    update_type = 'done_conflict_tasks'
    try:
        print(f'\nAttempting to update "{update_type}" in database "{db_name}"')
        log_file_path = createLogsFile(log_folder, update_type, 'read.json')
        tasks_done_conflicted = getTasks(token, db_id, 
            params.filter_done_conflict_tasks, log_file_path)
    except RuntimeError as e:
        print(e)
    else:
        log_file_path = createLogsFile(log_folder, update_type, 'write.json')
        updateTasks(token, tasks_done_conflicted, params.get_prop_done,
            log_file_path)
        print(" -> Finished updating")

if __name__ == "__main__":
    from hidden import tokens    