
import os
import requests

GITHUB_API = "https://api.github.com"
REPO = os.getenv("REPO_GITHUB")
TOKEN = os.getenv("TOKEN_GITHUB")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def commit_file(file_path, content, branch, commit_msg):
    url = f"{GITHUB_API}/repos/{REPO}/contents/{file_path}"
    data = {
        "message": commit_msg,
        "content": content,
        "branch": branch
    }
    response = requests.put(url, json=data, headers=HEADERS)
    return response.json()

def create_branch(branch, from_branch="main"):
    url = f"{GITHUB_API}/repos/{REPO}/git/refs"
    base_sha = get_branch_sha(from_branch)
    data = {
        "ref": f"refs/heads/{branch}",
        "sha": base_sha
    }
    return requests.post(url, json=data, headers=HEADERS).json()

def get_branch_sha(branch):
    url = f"{GITHUB_API}/repos/{REPO}/git/refs/heads/{branch}"
    return requests.get(url, headers=HEADERS).json()["object"]["sha"]

def create_pull_request(title, body, head, base="main"):
    url = f"{GITHUB_API}/repos/{REPO}/pulls"
    data = {
        "title": title,
        "body": body,
        "head": head,
        "base": base
    }
    return requests.post(url, json=data, headers=HEADERS).json()
