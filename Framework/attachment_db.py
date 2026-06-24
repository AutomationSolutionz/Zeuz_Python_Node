# Author: Sazid

import json
from pathlib import Path
from typing import Any, Dict, Union
import os
import requests
import sys
from Framework.Utilities.ConfigModule import get_config_value
from Framework.Utilities import RequestFormatter
from Framework.Utilities import CommonUtil
from Framework.Utilities import ConfigModule

temp_ini_file = (
    Path.cwd().parent 
    / "AutomationLog"
    / ConfigModule.get_config_value("Advanced Options", "_file")
)
class AttachmentDB:
    def __init__(self, db_directory: Path) -> None:
        self.db_directory = db_directory.resolve()
        self.db_file = self.db_directory / "db.json"
        self.init_db()

    @staticmethod
    def make_key(path: str, uploaded_at: str) -> str:
        if not path or uploaded_at is None or str(uploaded_at).strip() == "":
            return ""
        return f"{path.strip()}|{str(uploaded_at).strip()}"

    def exists(self, path: str, uploaded_at: str) -> Union[Dict[str, str], None]:
        """
        exists returns an entry if the attachment is recorded in the database.
        None is returned if it does not exist.
        """
        key = self.make_key(path, uploaded_at)
        if not key:
            return None

        db = self.get_db()

        # TODO: Cleanup old attachments/db entries here.

        if key not in db:
            return None

        return db[key]

    def remove(self, path: str, uploaded_at: str) -> bool:
        """
        remove removes an attachment with the given path and uploaded_at from
        the db and returns True if successful.
        """
        key = self.make_key(path, uploaded_at)
        if not key:
            return False

        db = self.get_db()

        if key in db:
            del db[key]
            self.save_db(db)
            return True

        return False

    def put(self, filepath: Path, path: str, uploaded_at: str):
        """
        put records the attachment's local file path in the db.
        """
        key = self.make_key(path, uploaded_at)
        if not key:
            return None

        db = self.get_db()

        entry = {
            "path": str(filepath.resolve()),
            "server_path": path.strip(),
            "uploaded_at": str(uploaded_at).strip(),
        }

        db[key] = entry
        self.save_db(db)

        return entry


    def get_db(self) -> Dict[str, Any]:
        db = None
        with open(self.db_file, "r", encoding="utf-8") as f:
            db = json.loads(f.read())
        return db


    def save_db(self, data: Dict[str, Any]) -> None:
        with open(self.db_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(data))


    def init_db(self) -> None:
        if self.db_file.exists():
            return

        self.db_directory.mkdir(parents=True, exist_ok=True)

        data = {}
        with open(self.db_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(data))

class GlobalAttachment:
    # Download attachment from global when global_attachments variable is called
    # Returns the path to the local file
    def __init__(self):
        pass

    def __getitem__(self, file_name: str):
        url_prefix = get_config_value("Authentication", "server_address") + "/static/global_folder/"
        return str(self.download_attachment(url_prefix + file_name))

    def download_attachment(self, url: str):
        try:
            path_to_global_attachment_folder = Path(ConfigModule.get_config_value("sectionOne", "temp_run_file_path", temp_ini_file)) / "attachments" / "global"
            path_to_global_attachment_folder.mkdir(parents=True, exist_ok=True)

            file_name = url.split("/")[-1].strip()
            path_to_downloaded_attachment = Path.joinpath(path_to_global_attachment_folder,file_name)
            
            headers = RequestFormatter.add_api_key_to_headers({})
            
            with RequestFormatter.request("get", url, stream=True, timeout=600,**headers) as r:
                r.raise_for_status()
                with open(path_to_downloaded_attachment, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        except Exception as e:
            return CommonUtil.Exception_Handler(sys.exc_info())
        
        return path_to_downloaded_attachment
