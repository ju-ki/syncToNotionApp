import os
import json
import requests

notion_token = os.environ["NOTION_API_KEY"]
database_id = os.environ["NOTION_DATABASE_ID"]
issue_json = os.environ["ISSUE_CONTEXT"]
issue = json.loads(issue_json)

def sync_issue_to_notion(issue):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    data = {
        "parent": { "database_id": database_id },
        "properties": {
            "Name": {
                "title": [{"text": {"content": issue["title"]}}]
            },
            "GitHub Number": {
                "number": issue["number"]
            },
            "URL": {
                "url": issue["html_url"]
            },
            "Status": {
                "select": {"name": "Closed" if issue["state"] == "closed" else "Open"}
            }
        }
    }

    requests.post(url, headers=headers, json=data)

sync_issue_to_notion(issue)
