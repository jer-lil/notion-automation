#! /usr/bin/python3

import os
import logging
import json
from typing import Callable
from notion_client import Client
#import old_notion_automation as old_na
import notion_automation.old_notion_automation as old_na

"""

"""
def createLogFile(folder_base: str, subfolder:str, filename:str) -> str:
    """_summary_

    Args:
        folder_base (str): base folder, e.g. "logs/"
        subfolder (str): subfolder, e.g. "recurring_tasks" or "" if unused
        filename (str): name of file, for example "mylog.json"

    Returns:
        str: path of output file
    """
    log_folder = os.path.join(folder_base, subfolder)
    logging.info(f'Creating log folder: {log_folder}')
    os.makedirs(log_folder, exist_ok=True)
    return os.path.join(log_folder, filename) 


def getDbMembers(client: Client, db_id: str, body_filter: dict) -> list:
    """ Returns list of database members matching body_filter

    Args:
        client (Client): _description_
        db_id (str): _description_
        body_filter (dict): _description_

    Returns:
        list: _description_
    """
    results = client.databases.query(
        **{
            "database_id": db_id,
            "filter": body_filter,
        }
    ).get("results")
    return results


def updateDbItems(
        client: Client,
        db_id: str,
        filt_get: dict,
        filt_set: Callable):
    """_summary_

    Args:
        client (Client): _description_
        db_id (str): _description_
        token (str): _description_
        filt_get (Callable): _description_
        filt_set (Callable): _description_
    """

    tasks_raw = getDbMembers(client, db_id, filt_get)
    logging.debug(f'tasks_raw = {json.dumps(tasks_raw, indent=4)}')
    #json.dumps(tasks_raw, indent=4)
    
    #TODO get rid of this old method of filtering out JSON into properties
    # it's only necessary to pass in a stripped list of properties into
    #   the filt_set body function (for now)
    tasks = [old_na._extractParameters(task) for task in tasks_raw]
    logging.info(f'tasks = {json.dumps(tasks, indent=4)}')
      
    # Update tasks
    for task in tasks:
        filt = filt_set(task)
        logging.debug(f'filt_set = {json.dumps(filt, indent=4)}')
        client.pages.update(task.get('id'), **filt)
