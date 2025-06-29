import importlib


def _reload_without_token(monkeypatch):
    monkeypatch.delenv("TOKEN_GITHUB_API", raising=False)
    monkeypatch.delenv("REPO_GITHUB", raising=False)
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: None)
    import utils.github_service as gh_mod

    return importlib.reload(gh_mod)


def test_fetch_repo_info_without_token(monkeypatch):
    gh = _reload_without_token(monkeypatch)
    assert gh.fetch_repo_info() == {}


def test_commit_file_without_token(monkeypatch):
    gh = _reload_without_token(monkeypatch)
    assert gh.commit_file("test.txt", "content", "main", "msg") == {}


def test_get_branch_sha_without_token(monkeypatch):
    gh = _reload_without_token(monkeypatch)
    assert gh.get_branch_sha("main") == ""
