import json
import os
import threading
from typing import Any


class JSONStorage:
    def __init__(self, path: str, default: Any):
        self._path = path
        self._default = default
        self._lock = threading.RLock()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            self._write(default)

    def _write(self, data: Any) -> None:
        tmp_path = f"{self._path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        os.replace(tmp_path, self._path)

    def read(self) -> Any:
        with self._lock:
            with open(self._path, "r", encoding="utf-8") as fh:
                return json.load(fh)

    def atomic_update(self, update_fn) -> Any:
        with self._lock:
            data = self.read()
            new_data = update_fn(data)
            self._write(new_data)
            return new_data

    def write(self, data: Any) -> None:
        with self._lock:
            self._write(data)
