import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("github_sync", Path("src/services/github_sync.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class DummyIssue:
    def __init__(self, title, number):
        self.title = title
        self.number = number
        self.comments = []
        self.body = None

    def create_comment(self, body):
        self.comments.append(body)


class DummyRepo:
    def __init__(self):
        self.issues = []

    def get_issues(self, state="open"):
        return self.issues

    def create_issue(self, title, body):
        issue = DummyIssue(title, len(self.issues) + 1)
        issue.body = body
        self.issues.append(issue)
        return issue


class DummyGithub:
    def __init__(self, token):
        self.token = token
        self.repo = DummyRepo()

    def get_repo(self, name):
        return self.repo


def _service(monkeypatch):
    dummy = DummyGithub("t")
    monkeypatch.setattr(mod, "Github", lambda token: dummy)
    return mod.GitHubSyncService(token="t", repo="r/test"), dummy.repo


def test_post_creates_issue(monkeypatch):
    svc, repo = _service(monkeypatch)
    num = svc.post_chat_completion("hello", "world")
    assert num == 1
    assert len(repo.issues) == 1
    assert "hello" in repo.issues[0].body


def test_post_updates_existing_issue(monkeypatch):
    svc, repo = _service(monkeypatch)
    repo.create_issue("Chat Log: hello", "old")
    num = svc.post_chat_completion("hello", "world")
    assert num == 1
    assert len(repo.issues) == 1
    assert repo.issues[0].comments[0].startswith("**Prompt:")
