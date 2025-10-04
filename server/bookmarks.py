import os
import threading
from dataclasses import dataclass, asdict
from typing import Dict, List

from .security import generate_random_string
from .storage import JSONStorage
from .path_validator import validate_path_access, PathValidationError


@dataclass
class Bookmark:
    identifier: str
    label: str
    path: str

    def to_dict(self) -> Dict:
        return asdict(self)


class BookmarkManager:
    def __init__(self, storage_path: str):
        self._storage = JSONStorage(storage_path, [])
        self._lock = threading.RLock()

    def list_bookmarks(self) -> List[Dict]:
        with self._lock:
            return list(self._storage.read())

    def add_bookmark(self, label: str, path: str) -> Bookmark:
        # Validate path security
        try:
            abs_path = validate_path_access(path, allow_custom=True)
        except PathValidationError as exc:
            raise ValueError(str(exc)) from exc

        if not os.path.isdir(abs_path):
            raise NotADirectoryError("Bookmark path must be an existing directory.")

        with self._lock:
            bookmarks = self._storage.read()
            identifier = self._generate_identifier(bookmarks)
            bookmark = Bookmark(identifier=identifier, label=label.strip() or abs_path, path=abs_path)
            bookmarks.append(bookmark.to_dict())
            self._storage.write(bookmarks)
            return bookmark

    def delete_bookmark(self, identifier: str) -> None:
        with self._lock:
            bookmarks = self._storage.read()
            filtered = [b for b in bookmarks if b.get("identifier") != identifier]
            self._storage.write(filtered)

    def _generate_identifier(self, existing: List[Dict]) -> str:
        existing_ids = {b["identifier"] for b in existing}
        while True:
            candidate = generate_random_string(6)
            if candidate not in existing_ids:
                return candidate
