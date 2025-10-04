import os
import re
import secrets
import threading
import time
import zipfile
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from .security import generate_random_string
from .storage import JSONStorage
from .path_validator import validate_share_path, PathValidationError


@dataclass
class ShareRecord:
    token: str
    path: str
    is_directory: bool
    archive_name: Optional[str]
    created_at: float
    max_downloads: Optional[int]
    download_count: int
    expire_at: Optional[float]
    allowed_ips: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


class ShareManager:
    def __init__(self, storage_path: str):
        self._storage = JSONStorage(storage_path, {})
        self._lock = threading.RLock()
        self._data_dir = os.path.dirname(storage_path)
        self._archive_dir = os.path.join(self._data_dir, "archives")
        os.makedirs(self._archive_dir, exist_ok=True)

    def _load(self) -> Dict[str, Dict]:
        return self._storage.read()

    def _save(self, data: Dict[str, Dict]) -> None:
        self._storage.write(data)

    def list_shares(self) -> List[Dict]:
        with self._lock:
            now = time.time()
            data = self._load()
            active: List[Dict] = []
            changed = False
            for token, entry in list(data.items()):
                expire_at = entry.get("expire_at")
                if expire_at and expire_at < now:
                    archive_name = entry.get("archive_name")
                    if archive_name:
                        self._remove_archive(archive_name)
                    del data[token]
                    changed = True
                    continue
                sanitized = {
                    "token": token,
                    "path": entry.get("path"),
                    "is_directory": entry.get("is_directory", False),
                    "download_count": entry.get("download_count", 0),
                    "max_downloads": entry.get("max_downloads"),
                    "expire_at": expire_at,
                    "allowed_ips": entry.get("allowed_ips", []),
                    "created_at": entry.get("created_at"),
                }
                active.append(sanitized)
            if changed:
                self._save(data)
            return active

    def create_share(
        self,
        path: str,
        max_downloads: Optional[int],
        expire_at: Optional[float],
        allowed_ips: Optional[List[str]] = None,
    ) -> ShareRecord:
        # Validate path security before checking existence
        try:
            abs_path = validate_share_path(path)
        except PathValidationError as exc:
            raise ValueError(str(exc)) from exc

        if not os.path.exists(abs_path):
            raise FileNotFoundError("Path to share does not exist.")

        is_directory = os.path.isdir(abs_path)
        if not (is_directory or os.path.isfile(abs_path)):
            raise FileNotFoundError("Only files or directories can be shared.")

        with self._lock:
            data = self._load()
            token = self._generate_unique_token(data)
            archive_name = None
            if is_directory:
                archive_name = self._build_archive(abs_path, token)
            record = ShareRecord(
                token=token,
                path=abs_path,
                is_directory=is_directory,
                archive_name=archive_name,
                created_at=time.time(),
                max_downloads=max_downloads if max_downloads else None,
                download_count=0,
                expire_at=expire_at,
                allowed_ips=[ip.strip() for ip in (allowed_ips or []) if ip.strip()],
            )
            data[token] = record.to_dict()
            self._save(data)
            return record

    def _generate_unique_token(self, existing: Optional[Dict[str, Dict]] = None) -> str:
        existing = existing or self._load()
        while True:
            token = generate_random_string(secrets_length())
            if token not in existing:
                return token

    def get_share(self, token: str) -> Optional[Dict]:
        with self._lock:
            return self._load().get(token)

    def delete_share(self, token: str) -> None:
        with self._lock:
            data = self._load()
            record = data.pop(token, None)
            if record:
                archive_name = record.get("archive_name")
                if archive_name:
                    self._remove_archive(archive_name)
                self._save(data)

    def validate_and_register_download(self, token: str, client_ip: str) -> Optional[Dict[str, str]]:
        with self._lock:
            data = self._load()
            record = data.get(token)
            if not record:
                return None
            now = time.time()
            expire_at = record.get("expire_at")
            if expire_at and expire_at < now:
                archive_name = record.get("archive_name")
                if archive_name:
                    self._remove_archive(archive_name)
                data.pop(token, None)
                self._save(data)
                return None
            allowed_ips = record.get("allowed_ips") or []
            if allowed_ips and client_ip not in allowed_ips:
                return None
            max_downloads = record.get("max_downloads")
            current = record.get("download_count", 0)
            if max_downloads is not None and current >= max_downloads:
                archive_name = record.get("archive_name")
                if archive_name:
                    self._remove_archive(archive_name)
                data.pop(token, None)
                self._save(data)
                return None

            is_directory = record.get("is_directory", False)
            if is_directory:
                try:
                    archive_name = self._build_archive(record["path"], record["token"])
                except FileNotFoundError:
                    archive_name = record.get("archive_name")
                    if archive_name:
                        self._remove_archive(archive_name)
                    data.pop(token, None)
                    self._save(data)
                    return None
                record["archive_name"] = archive_name
                download_path = os.path.join(self._archive_dir, archive_name)
                filename = archive_name
                mime = "application/zip"
            else:
                download_path = record["path"]
                filename = os.path.basename(download_path)
                mime = None

            record["download_count"] = current + 1
            data[token] = record
            self._save(data)

            return {
                "path": download_path,
                "filename": filename,
                "mime": mime,
                "is_directory": is_directory,
            }

    def _build_archive(self, source_path: str, token: str) -> str:
        if not os.path.exists(source_path):
            raise FileNotFoundError('Directory to share is no longer available.')
        base_name = os.path.basename(source_path.rstrip(os.sep)) or "root"
        safe_base = re.sub(r"[^A-Za-z0-9._-]", "_", base_name)[:80] or "archive"
        archive_name = f"{safe_base}-{token}.zip"
        archive_path = os.path.join(self._archive_dir, archive_name)

        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            zf.writestr(f"{safe_base}/", "")
            for root, dirs, files in os.walk(source_path):
                rel_root = os.path.relpath(root, start=source_path)
                folder_arc = os.path.join(safe_base, rel_root) if rel_root != "." else safe_base
                if not files and not dirs:
                    zf.writestr(f"{folder_arc}/", "")
                for name in files:
                    file_path = os.path.join(root, name)
                    rel_path = os.path.relpath(file_path, start=source_path)
                    arcname = os.path.join(safe_base, rel_path)
                    zf.write(file_path, arcname=arcname)
        return archive_name

    def _remove_archive(self, archive_name: str) -> None:
        archive_path = os.path.join(self._archive_dir, archive_name)
        try:
            os.remove(archive_path)
        except FileNotFoundError:
            pass


def secrets_length() -> int:
    return 8 + secrets.randbelow(3)
