"""
DeploymentAgent – automatisiert Build, ZIP, Release und CI-Aktionen
"""

import logging
import shutil
from pathlib import Path


class DeploymentAgent:
    def __init__(self, output_path="dist"):
        self.output_path = Path(output_path)
        self.output_path.mkdir(exist_ok=True)

    def create_release_zip(self, source_folder: str = ".", zip_name: str = "fur_release") -> str:
        try:
            zip_path = self.output_path / zip_name
            shutil.make_archive(str(zip_path), "zip", root_dir=source_folder)
            logging.info(f"📦 Release ZIP erstellt: {zip_path}.zip")
            return f"{zip_path}.zip"
        except Exception as e:
            logging.error("❌ Fehler beim Erstellen der ZIP: %s", e)
            return ""
