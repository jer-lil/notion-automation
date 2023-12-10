#! /usr/bin/python3

import argparse
import notion_client.notion_automation as notion

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('token', type=str, help='Secret Notion API token')
    parser.add_argument('db_id', type=str, help='Notion Database ID')
    parser.add_argument('db_name', type=str, help='Database name for logging')

    args = parser.parse_args()

    notion.updateDatabase(db_id=args.db_id,
                          db_name=args.db_name,
                          token=args.token)
