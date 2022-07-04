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
