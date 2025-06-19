# 🧠 FUR GitHub Agent
from github_push import push_logs_to_github
from zip_maker import create_daily_zip
from datetime import datetime

def run():
    today = datetime.now().strftime('%Y-%m-%d')
    create_daily_zip(today)
    push_logs_to_github(today)

if __name__ == "__main__":
    run()
