def send_discord_webhook(content, file_path):
    import requests

    from config import DISCORD_WEBHOOK_URL

    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"content": content}
        response = requests.post(DISCORD_WEBHOOK_URL, data=data, files=files)
    return response.status_code
