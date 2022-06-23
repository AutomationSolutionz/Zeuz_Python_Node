# Author: Sazid

import json
from pathlib import Path
import time
from typing import Any, Dict, Union


class AttachmentDB:
    def __init__(self, db_directory: Path) -> None:
        self.db_directory = db_directory
        self.db_file = db_directory / "db.json"
        self.init_db()


    def exists(self, hash: str) -> Union[Path, None]:
        """
        exists returns a Path indicating whether the attachment exists in the
        database. None is returned if it does not exist.
        """

        db = self.get_db()

        # TODO: Cleanup old attachments/db entries here.

        if hash in db:
            entry = db[hash]
            return Path(entry["path"])

        return None


    def put(self, filepath: Path, hash: str):
        """
        put puts the attachment into the db.
        """

        if len(hash) == 0 or hash == "0":
            return False

        modified_at = time.time()
        entry = {
            "hash": hash,
            "path": str(filepath),
            "modified_at": modified_at,
        }

        db = self.get_db()

        # Add new entry to db with the given hash.
        db[hash] = entry

        self.save_db(db)

        return True


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
