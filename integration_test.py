import json
import requests

import notion_filters as filters



token = 'secret_OGasRVOcWYlxjfObQUILjZiwbfEzVUTQypReFsYLyv0'
database_id_todo_personal = '598c0b54b17d423a8c7d4acc57fda8fc'
database_id_todo_work = 'e951bc881e0e4053a6ef4b9202520550'

output_file_default = 'tasks_default.json'

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

def getTasks(db_id, filter=filters.filter_default,
        output_file=output_file_default,
    ):
    url = f'https://api.notion.com/v1/databases/{db_id}/query'
    headers={
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-02-22"
        }
    r = requests.post(url, headers=headers, json=filter)
    result_dict = r.json()
    assert result_dict['object'] != "error", result_dict['message']

    # Write raw json results to file for debugging
    with open('result_dump.json', 'w') as f:
        json.dump(result_dict, f, indent=4)

    list_result = result_dict['results']
    tasks = []
    for task in list_result:
        task_dict = _mapNotionResultToTask(task)
        tasks.append(task_dict)

    # Write recurring tasks to file
    with open(output_file, 'w') as f:
        json.dump(tasks, f, indent=4)

    return tasks

def _updateTask(page_id, body):
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


def updateTasks(tasks, body_func):
    for task in tasks:
        body = body_func(task)
        _updateTask(task['task_id'], body)
    return
    
if __name__ == "__main__":
    # Grab all recurring tasks that are completed
    tasks_recurring = getTasks(db_id = database_id_todo_personal, 
        filter=filters.filter_recurring_tasks, 
        output_file="recurring_tasks.json"
    )
    # Uncheck "Done" and update "Due" to "Next Due"
    updateTasks(tasks_recurring, filters.properties_recurring)

    # Grab all recurring tasks that are completed
    tasks_recurring = getTasks(db_id = database_id_todo_work, 
        filter=filters.filter_recurring_tasks, 
        output_file="recurring_tasks.json"
    )
    # Uncheck "Done" and update "Due" to "Next Due"
    updateTasks(tasks_recurring, filters.properties_recurring)

'''
    tasks_done = getTasks(filter=filters.filter_done_tasks, 
        output_file="done_tasks.json"
    )
'''   
