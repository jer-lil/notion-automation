#! /usr/bin/python3

import os
import logging
from notion_client import Client

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


def getTasks(client, db_id, body_filter):
    
    results = client.databases.query(
        **{
            "database_id": db_id,
            "filter": body_filter,
        }
    ).get("results")
    return results