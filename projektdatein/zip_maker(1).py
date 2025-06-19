# 📦 ZIP-Erstellung
from zipfile import ZipFile
from pathlib import Path

def create_daily_zip(date_str):
    zip_path = Path(f"core/logs/{date_str}.zip")
    with ZipFile(zip_path, 'w') as zipf:
        base = Path("core/logs")
        for file in base.glob(f"*{date_str}.*"):
            zipf.write(file, arcname=file.name)
    print(f"📦 ZIP erstellt: {zip_path}")
