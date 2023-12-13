#! /usr/bin/python3

import os
import logging
import pprint
import json
from notion_client import Client
from notion_client import helpers

import notion_automation.notion_automation as na
import notion_automation.body_params as bp
from hidden import tokens


if __name__ == "__main__":  

    notion = Client(auth=tokens.TOKEN_JEREMIAH)

    # Update recurring tasks
    na.updateDbItems(
        client=notion,
        db_id=tokens.DB_ID_TEST_JER,
        token=tokens.TOKEN_JEREMIAH,
        filt_get=bp.get_filter_recurring_tasks,
        filt_set=bp.get_prop_recurring)

    # Update "Done Conflict" tasks
    na.updateDbItems(
        client=notion,
        db_id=tokens.DB_ID_TEST_JER,
        token=tokens.TOKEN_JEREMIAH,
        filt_get=bp.get_filter_done_conflict,
        filt_set=bp.get_prop_done)
