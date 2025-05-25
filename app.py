import os
import json
import requests
from typing import Dict, Any, Optional, List

NOTION_VERSION = "2022-06-28"
NOTION_URL = "https://api.notion.com/v1"

# 環境変数の読み込み
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

# すでにNotionにあるIssue番号をすべて取得
def get_existing_github_numbers() -> List[int]:
    query_url = f"{NOTION_URL}/databases/{database_id}/query"
    existing_numbers = []
    start_cursor = None

    while True:
        payload = {"page_size": 100}
        if start_cursor:
            payload["start_cursor"] = start_cursor

        res = requests.post(query_url, headers=headers_notion, json=payload)
        if not res.ok:
            print("Failed to query Notion:", res.text)
            break

        data = res.json()
        for result in data.get("results", []):
            props = result.get("properties", {})
            number = props.get("Github Number", {}).get("number")
            if number is not None:
                existing_numbers.append(number)

        if not data.get("has_more"):
            break
        start_cursor = data.get("next_cursor")

    return existing_numbers

# GitHubからOpen Issueのみ取得
def fetch_open_github_issues() -> List[Dict[str, Any]]:
    headers_github = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }
    page = 1
    per_page = 100
    issues = []

    while True:
        url = f"https://api.github.com/repos/{github_repo}/issues?state=open&per_page={per_page}&page={page}"
        res = requests.get(url, headers=headers_github)
        if not res.ok:
            print("GitHub API error:", res.text)
            break

        page_issues = res.json()
        if not page_issues:
            break

        issues.extend([i for i in page_issues if "pull_request" not in i])
        page += 1

    return issues

# Notionページの作成・更新
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

# メイン同期処理
def sync_issues():
    github_issues = fetch_open_github_issues()
    existing_numbers = get_existing_github_numbers()

    if not existing_numbers:
        print("Notion DB is empty. Performing bulk insert...")
        for issue in github_issues:
            create_page(issue)
    else:
        print("Notion DB already has issues. Syncing updates...")
        for issue in github_issues:
            if issue["number"] in existing_numbers:
                page_id = search_notion_issue(issue["number"])
                if page_id:
                    update_page(page_id, issue)
            else:
                create_page(issue)

# 実行
if __name__ == "__main__":
    sync_issues()
