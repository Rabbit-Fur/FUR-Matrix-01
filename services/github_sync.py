import logging
import os
from datetime import datetime
from typing import Optional

from github import Github


log = logging.getLogger(__name__)


class GitHubSyncService:
    """Sync chat completions to GitHub issues using PyGithub."""

    def __init__(
        self,
        *,
        token: Optional[str] = None,
        repo: Optional[str] = None,
        issue_title_prefix: str = "Chat Log",
    ) -> None:
        self.token = token or os.getenv("TOKEN_GITHUB_SYNC")
        self.repo_name = repo or os.getenv("REPO_GITHUB")
        self.issue_title_prefix = issue_title_prefix
        self.client = Github(self.token) if self.token else None
        self.repo = self._get_repo()

    def _get_repo(self):
        if not (self.client and self.repo_name):
            if not self.token or not self.repo_name:
                log.warning("GitHub sync not configured – skipping")
            return None
        try:
            return self.client.get_repo(self.repo_name)
        except Exception:  # pragma: no cover - network errors
            log.warning("Failed to access repo %s", self.repo_name, exc_info=True)
            return None

    def post_chat_completion(self, prompt: str, answer: str) -> Optional[int]:
        """Create or update a GitHub issue with the chat completion."""
        if not self.repo:
            log.warning("GitHub repo not available – skipping sync")
            return None
        truncated = prompt[:50].replace("\n", " ")
        title = f"{self.issue_title_prefix}: {truncated}"
        body = (
            f"**Prompt:**\n{prompt}\n\n**Answer:**\n{answer}\n\n"
            f"_Time: {datetime.utcnow().isoformat()}Z_"
        )
        # look for existing open issue with the same title
        issue = next((i for i in self.repo.get_issues(state="open") if i.title == title), None)
        if issue:
            issue.create_comment(body)
        else:
            issue = self.repo.create_issue(title=title, body=body)
        return issue.number


__all__ = ["GitHubSyncService"]
