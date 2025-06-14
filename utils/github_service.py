"""
github_service.py – Utilities für GitHub API Integration

Bietet Funktionen, um mit dem GitHub REST API Repos, Commits, Branches und Pull Requests programmatisch zu verwalten.
Alle API-Keys werden aus Umgebungsvariablen geladen.
"""

import base64
import os
from typing import Optional

import requests

GITHUB_API = "https://api.github.com"
REPO = os.getenv("REPO_GITHUB")
TOKEN = os.getenv("TOKEN_GITHUB_API")

if not REPO or not TOKEN:
    raise RuntimeError(
        "Bitte Umgebungsvariablen REPO_GITHUB und TOKEN_GITHUB_API setzen!"
    )

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def fetch_repo_info(owner: Optional[str] = None, repo: Optional[str] = None) -> dict:
    """
    Holt Repo-Infos vom GitHub-API.
    Owner/Repo können als Argument oder aus Umgebungsvariablen übergeben werden.

    Args:
        owner (str, optional): Repo-Owner (GitHub-Username/Org).
        repo (str, optional): Repo-Name (im Format 'owner/repo').

    Returns:
        dict: JSON-Antwort von GitHub mit den Repo-Infos.
    """
    repo_full = repo or REPO
    owner = owner or (repo_full.split("/")[0] if repo_full else None)
    repo_name = repo_full.split("/")[1] if repo_full else None
    if not (owner and repo_name and TOKEN):
        raise RuntimeError(
            "TOKEN_GITHUB_API und REPO_GITHUB (owner/repo) müssen in der Umgebung gesetzt sein!"
        )

    url = f"{GITHUB_API}/repos/{owner}/{repo_name}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def commit_file(file_path: str, content: str, branch: str, commit_msg: str) -> dict:
    """
    Committet eine Datei in das Repository.

    Args:
        file_path (str): Pfad zur Datei im Repo.
        content (str): Dateiinhalte (wird base64-codiert!).
        branch (str): Ziel-Branch.
        commit_msg (str): Commit-Message.

    Returns:
        dict: Antwort des GitHub-APIs als Dictionary.
    """
    url = f"{GITHUB_API}/repos/{REPO}/contents/{file_path}"
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    data = {"message": commit_msg, "content": encoded_content, "branch": branch}
    response = requests.put(url, json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def create_branch(branch: str, from_branch: str = "main") -> dict:
    """
    Erstellt einen neuen Branch von einem bestehenden Branch.

    Args:
        branch (str): Neuer Branchname.
        from_branch (str, optional): Quell-Branch. Standard: "main".

    Returns:
        dict: Antwort des GitHub-APIs als Dictionary.
    """
    url = f"{GITHUB_API}/repos/{REPO}/git/refs"
    base_sha = get_branch_sha(from_branch)
    data = {"ref": f"refs/heads/{branch}", "sha": base_sha}
    response = requests.post(url, json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def get_branch_sha(branch: str) -> str:
    """
    Holt die Commit-SHA eines Branches.

    Args:
        branch (str): Name des Branches.

    Returns:
        str: Commit-SHA.
    """
    url = f"{GITHUB_API}/repos/{REPO}/git/refs/heads/{branch}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["object"]["sha"]


def create_pull_request(title: str, body: str, head: str, base: str = "main") -> dict:
    """
    Erstellt einen Pull Request von einem Branch zu einem anderen.

    Args:
        title (str): Titel des Pull Requests.
        body (str): Beschreibung.
        head (str): Quell-Branch.
        base (str, optional): Ziel-Branch. Standard: "main".

    Returns:
        dict: Antwort des GitHub-APIs als Dictionary.
    """
    url = f"{GITHUB_API}/repos/{REPO}/pulls"
    data = {"title": title, "body": body, "head": head, "base": base}
    response = requests.post(url, json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()
