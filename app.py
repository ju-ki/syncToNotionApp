import os
import json
import requests
from typing import Dict, Any, Optional

NOTION_VERSION = "2022-06-28"
NOTION_URL = "https://api.notion.com/v1"

def get_env_var(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise EnvironmentError(f"Missing environment variable: {name}")
    return value

notion_token = get_env_var("NOTION_API_KEY")
database_id = get_env_var("NOTION_DATABASE_ID")
project_id = get_env_var("PROJECT_ID")
github_token = get_env_var("GITHUB_TOKEN")
github_repo = get_env_var("GITHUB_REPO")

headers_notion = {
    "Authorization": f"Bearer {notion_token}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

def search_notion_issue(number: int) -> Optional[str]:
    """GitHub番号でNotion内のページを検索し、存在すればページIDを返す"""
    query_url = f"{NOTION_URL}/databases/{database_id}/query"
    payload = {
        "filter": {
            "property": "Github Number",
            "number": {"equals": number}
        }
    }
    res = requests.post(query_url, headers=headers_notion, json=payload)
    if res.ok:
        results = res.json().get("results", [])
        if results:
            return results[0]["id"]
    return None

def build_payload(issue: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {"title": [{"text": {"content": issue["title"]}}]},
            "Github Number": {"number": issue["number"]},
            "URL": {"url": issue["html_url"]},
            "Status": {"status": {"name": "Closed" if issue["state"] == "closed" else "Open"}},
            "Multi-select": {"relation": [{"id": project_id}]}
        }
    }

def create_page(issue: Dict[str, Any]):
    payload = build_payload(issue)
    res = requests.post(f"{NOTION_URL}/pages", headers=headers_notion, json=payload)
    print(f"[CREATE] Issue #{issue['number']} → {res.status_code}")

def update_page(page_id: str, issue: Dict[str, Any]):
    payload = {"properties": build_payload(issue)["properties"]}
    res = requests.patch(f"{NOTION_URL}/pages/{page_id}", headers=headers_notion, json=payload)
    print(f"[UPDATE] Issue #{issue['number']} → {res.status_code}")

def sync_issue(issue: Dict[str, Any]):
    page_id = search_notion_issue(issue["number"])
    if page_id:
        update_page(page_id, issue)
    else:
        create_page(issue)

def bulk_sync_all_issues():
    headers_github = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }
    issues_url = f"https://api.github.com/repos/{github_repo}/issues?state=all"
    res = requests.get(issues_url, headers=headers_github)
    if not res.ok:
        print("Failed to fetch GitHub issues:", res.text)
        return

    issues = res.json()
    for issue in issues:
        if "pull_request" in issue:
            continue  # Skip PRs
        sync_issue(issue)

if __name__ == "__main__":
    issue_context = os.environ.get("ISSUE_CONTEXT")
    if issue_context:
        issue = json.loads(issue_context)
        sync_issue(issue)
    else:
        bulk_sync_all_issues()
