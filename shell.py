#! /usr/bin/python3

import argparse
import os
import logging
import pprint
import json
from notion_client import Client
from notion_client import helpers

import notion_automation.notion_automation as na
import notion_automation.old_notion_automation as old_na
import notion_automation.body_params as bp


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('token', type=str, help='Secret Notion API token')
    parser.add_argument('db_id', type=str, help='Notion Database ID')
    parser.add_argument('db_name', type=str, help='Database name for logging')
    #parser.add_argument('--log_level', type=str, required=False, help='Warning/Info/Debug/etc.')
    args = parser.parse_args()
    
    notion = Client(auth=args.token)

    file = na.createLogFile('logs', args.db_name, 'full_download.json')
    read = na._readFromFile(file)

    for page in read.get('results'):
        page_id = page.get('id') 
        props = helpers.pick(page.get('properties'), 'Done', 'Due', 'Priority')
        
        for prop in props.values():
            type = prop.get('type')
            prop = helpers.pick(prop, 'id', type)

        body = {'properties': props}
        response = notion.pages.update(page_id, **body)

        print(response.get('properties').get('Done').get('checkbox'))
