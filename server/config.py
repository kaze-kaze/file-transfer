import json
import os
from dataclasses import dataclass
from typing import Any, Dict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")


@dataclass
class AdminConfig:
    username: str
    password_hash: str
    salt: str
    iterations: int


@dataclass
class ServerConfig:
    host: str
    port: int
    session_timeout_minutes: int


class ConfigManager:
    def __init__(self, path: str = CONFIG_PATH):
        self._path = path
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self._path):
            raise FileNotFoundError(
                "Configuration not found. Please run `python3 manage.py init` first."
            )
        with open(self._path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def get_admin(self) -> AdminConfig:
        admin = self._data["admin"]
        return AdminConfig(
            username=admin["username"],
            password_hash=admin["password_hash"],
            salt=admin["salt"],
            iterations=admin.get("iterations", 200_000),
        )

    def get_server(self) -> ServerConfig:
        server = self._data["server"]
        security = self._data.get("security", {})
        return ServerConfig(
            host=server.get("host", "127.0.0.1"),
            port=int(server.get("port", 23000)),
            session_timeout_minutes=int(security.get("session_timeout_minutes", 60)),
        )

    @staticmethod
    def save(path: str, data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp_path = f"{path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        os.replace(tmp_path, path)
