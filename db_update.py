#! /usr/bin/python3

import argparse
import os
import logging
import pprint
import json
from notion_client import Client
from notion_client import helpers

import notion_automation.notion_automation as na
import notion_automation.body_params as bp


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('token', type=str, help='Secret Notion API token')
    parser.add_argument('db_id', type=str, help='Notion Database ID')
    parser.add_argument('db_name', type=str, help='Database name for logging')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.db_id == "":
        raise ValueError("Database ID cannot be blank!")
    if args.token == "":
        raise ValueError("Notion API Token cannot be blank!")
    if args.db_name == "":
        raise ValueError("Database Name cannot be blank!")

    notion = Client(auth=args.token)

    # Update recurring tasks
    na.updateDbItems(
        client=notion,
        db_id=args.db_id,
        filt_get=bp.filter_recurring_tasks,
        filt_set=bp.get_prop_recurring)

    # Update "Done Conflict" tasks
    na.updateDbItems(
        client=notion,
        db_id=args.db_id,
        filt_get=bp.filter_done_conflict_tasks,
        filt_set=bp.get_prop_done)
