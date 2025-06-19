# 🔁 GitHub Push Logik
import requests
import base64
from config import GITHUB_TOKEN, REPO_NAME

def push_logs_to_github(date_str):
    filepath = f"core/logs/FUR_v.1.1.1.3_Reflexion_{date_str}.md"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{filepath}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None

    data = {
        "message": f"🧠 Add FUR GPT Reflexion ({date_str})",
        "content": content_b64,
        "branch": "main",
        "committer": {"name": "FUR Agent", "email": "noreply@fur.system"}
    }
    if sha:
        data["sha"] = sha

    r = requests.put(url, headers=headers, json=data)
    print("✅ GitHub Upload:", r.status_code)
