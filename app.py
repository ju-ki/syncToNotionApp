import os
import json
import requests
from typing import Dict, Any


def get_env_var(name: str) -> str:
    """環境変数を取得し、なければ例外を投げる"""
    value = os.environ.get(name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{name}' is not set.")
    return value


def build_payload(issue: Dict[str, Any], database_id: str, project_id: str) -> Dict[str, Any]:
    """Notion API に送信するための payload を構築する"""
    return {
        "parent": {
            "type": "database_id",
            "database_id": database_id
        },
        "properties": {
            "Name": {
                "title": [{"text": {"content": issue.get("title", "Untitled Issue")}}]
            },
            "Github Number": {
                "number": issue.get("number", 0)
            },
            "URL": {
                "url": issue.get("html_url", "")
            },
            "Status": {
                "status": {"name": "Closed" if issue.get("state") == "closed" else "Open"}
            },
            "Multi-select": {
                "relation": [
                    {"id": project_id}
                ]
            }
        }
    }


def sync_issue_to_notion():
    """GitHub Issue を Notion に同期する"""
    try:
        notion_token = get_env_var("NOTION_API_KEY")
        database_id = get_env_var("NOTION_DATABASE_ID")
        project_id = get_env_var("PROJECT_ID")

        issue_json = get_env_var("ISSUE_CONTEXT")
        issue = json.loads(issue_json)

        headers = {
            "Authorization": f"Bearer {notion_token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

        payload = build_payload(issue, database_id, project_id)
        response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)

        print("Status Code:", response.status_code)
        if response.ok:
            print("✅ Issue successfully synced to Notion.")
        else:
            print("❌ Failed to sync issue.")
            print("Response:", response.text)

    except Exception as e:
        print("❌ An error occurred:", str(e))


if __name__ == "__main__":
    sync_issue_to_notion()
