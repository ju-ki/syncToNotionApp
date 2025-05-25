import os
import json
import requests

notion_token = os.environ.get("NOTION_API_KEY")
database_id = os.environ.get("NOTION_DATABASE_ID")
project_id = os.environ.get("PROJECT_ID")

notion_token = "ntn_r23692170905aJgPtRZWE63eZOg8ifVuTFI9cOLSozy58Q"
database_id = "1fe08d3762428035bf96ec8a5714167f"
issue_json = os.environ["ISSUE_CONTEXT"]
issue = json.loads(issue_json)

def sync_issue_to_notion(issue=None):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    data = {
        "parent": {"type": "database_id",  "database_id": database_id },
        "properties": {
            "Name": {
                "title": [{"text": {"content": issue["title"]}}]
            },
            "Github Number": {
                "number": issue["number"]
            },
            "URL": {
                "url": issue["html_url"]
            },
            "Status": {
                "status": {"name": "Closed" if issue["state"] == "closed" else "Open"}
            },
            "Multi-select": {
                "relation": [
                    { "id": project_id }
                ]
            }



        }
    }

    res = requests.post(url, headers=headers, json=data)
    print("Status Code:", res.status_code)

sync_issue_to_notion(issue)
