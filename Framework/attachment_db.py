# Author: Sazid

import json
from pathlib import Path
import time
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
        self.db_directory = db_directory
        self.db_file = db_directory / "db.json"
        self.init_db()


    def exists(self, hash: str) -> Union[Dict[str, str], None]:
        """
        exists returns a Path indicating whether the attachment exists in the
        database. None is returned if it does not exist.
        """

        db = self.get_db()

        # TODO: Cleanup old attachments/db entries here.

        if hash in db:
            entry = db[hash]
            return entry

        return None


    def remove(self, hash: str) -> bool:
        """
        remove removes an attachment with the given hash from the db and returns
        True if successful.
        """

        db = self.get_db()

        if hash in db:
            del db[hash]
            self.save_db(db)
            return True

        return False


    def put(self, filepath: Path, hash: str):
        """
        put puts the attachment into the db.
        """

        if len(hash) == 0 or hash == "0":
            return None

        db = self.get_db()

        if hash in db:
            return None

        modified_at = time.time()

        # We add a random suffix to the filepath to make sure files with same
        # names but different hashes do not overwrite each other. Specially
        # important if there are multiple attachments across multiple test
        # cases/steps with the same file name.
        path = filepath.with_name(str(hash))

        entry = {
            "hash": hash,
            "path": str(path),
            "modified_at": modified_at,
        }

        # Add new entry to db with the given hash.
        db[hash] = entry

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
            
            with RequestFormatter.request("get", url, stream=True, verify=False,**headers) as r:
                r.raise_for_status()
                with open(path_to_downloaded_attachment, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        except Exception as e:
            return CommonUtil.Exception_Handler(sys.exc_info())
        
        return path_to_downloaded_attachment