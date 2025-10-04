from __future__ import annotations

import math
import os
import re
import tempfile
import threading
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, List, Optional


class DownloadError(Exception):
    """Raised when a download cannot be completed."""


@dataclass
class DownloadResult:
    path: str
    filename: str
    size: Optional[int]
    multithreaded: bool


USER_AGENT = "SecureFileShare/1.0"
MIN_MULTI_SIZE = 1 * 1024 * 1024  # 1 MiB
MAX_THREADS = 4
CHUNK_SIZE = 256 * 1024  # 256 KiB


def download_from_url(url: str, target_dir: str, filename: Optional[str] = None) -> DownloadResult:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise DownloadError("Only HTTP and HTTPS URLs are supported.")
    if not os.path.isdir(target_dir):
        raise DownloadError("Target directory does not exist or is not a directory.")

    head_info = _fetch_head(url)
    size = head_info.get("content_length")
    accept_ranges = head_info.get("accept_ranges") == "bytes"
    final_name = _ensure_unique_filename(target_dir, filename or _infer_filename(url, head_info))
    destination = os.path.join(target_dir, final_name)

    if size and size >= MIN_MULTI_SIZE and accept_ranges:
        try:
            _download_multi(url, destination, size)
            return DownloadResult(path=destination, filename=final_name, size=size, multithreaded=True)
        except Exception:  # noqa: BLE001
            if os.path.exists(destination):
                os.remove(destination)

    _download_single(url, destination)
    final_size = os.path.getsize(destination)
    return DownloadResult(path=destination, filename=final_name, size=final_size, multithreaded=False)


def _fetch_head(url: str) -> Dict[str, Optional[str]]:
    info: Dict[str, Optional[str]] = {"content_length": None, "accept_ranges": None, "filename": None}
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            info["content_length"] = _safe_int(resp.headers.get("Content-Length"))
            info["accept_ranges"] = resp.headers.get("Accept-Ranges")
            info["filename"] = _filename_from_headers(resp.headers.get("Content-Disposition"))
            return info
    except Exception:  # noqa: BLE001
        pass

    req = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            info["content_length"] = _safe_int(resp.headers.get("Content-Length"))
            info["accept_ranges"] = resp.headers.get("Accept-Ranges")
            info["filename"] = _filename_from_headers(resp.headers.get("Content-Disposition"))
            return info
    except Exception as exc:  # noqa: BLE001
        raise DownloadError(f"Unable to initiate download: {exc}") from exc


def _download_multi(url: str, destination: str, total_size: int) -> None:
    num_threads = min(MAX_THREADS, max(2, total_size // (2 * MIN_MULTI_SIZE) + 1))
    part_files: List[str] = []
    ranges = _split_ranges(total_size, num_threads)
    os.makedirs(os.path.dirname(destination), exist_ok=True)

    try:
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for idx, (start, end) in enumerate(ranges):
                part_path = f"{destination}.part{idx}"
                part_files.append(part_path)
                futures.append(executor.submit(_download_range, url, start, end, part_path))
            for future in futures:
                future.result()
        _merge_parts(part_files, destination)
    finally:
        for part in part_files:
            try:
                os.remove(part)
            except FileNotFoundError:
                pass


def _download_range(url: str, start: int, end: int, part_path: str) -> None:
    headers = {
        "User-Agent": USER_AGENT,
        "Range": f"bytes={start}-{end}",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
        if resp.status not in (200, 206):
            raise DownloadError(f"Server did not honor range request (status {resp.status}).")
        with open(part_path, "wb") as fh:
            while True:
                chunk = resp.read(CHUNK_SIZE)
                if not chunk:
                    break
                fh.write(chunk)


def _merge_parts(part_files: List[str], destination: str) -> None:
    with open(destination, "wb") as dest:
        for part in part_files:
            with open(part, "rb") as src:
                while True:
                    chunk = src.read(1024 * 1024)
                    if not chunk:
                        break
                    dest.write(chunk)


def _download_single(url: str, destination: str) -> None:
    headers = {"User-Agent": USER_AGENT}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
        if resp.status >= 400:
            raise DownloadError(f"Download failed with status {resp.status}.")
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(destination, "wb") as fh:
            while True:
                chunk = resp.read(CHUNK_SIZE)
                if not chunk:
                    break
                fh.write(chunk)


def _split_ranges(total_size: int, num_parts: int) -> List[tuple[int, int]]:
    ranges: List[tuple[int, int]] = []
    part_size = math.ceil(total_size / num_parts)
    for idx in range(num_parts):
        start = idx * part_size
        end = min(total_size - 1, start + part_size - 1)
        ranges.append((start, end))
        if end >= total_size - 1:
            break
    if ranges[-1][1] < total_size - 1:
        ranges[-1] = (ranges[-1][0], total_size - 1)
    return ranges


def _infer_filename(url: str, head_info: Dict[str, Optional[str]]) -> str:
    if head_info.get("filename"):
        return head_info["filename"]  # type: ignore[return-value]
    parsed = urllib.parse.urlparse(url)
    candidate = os.path.basename(parsed.path.rstrip("/"))
    if candidate:
        return candidate
    return "download.bin"


def _filename_from_headers(content_disposition: Optional[str]) -> Optional[str]:
    if not content_disposition:
        return None
    match = re.search(r'filename\*=UTF-8\'\'([^;]+)', content_disposition)
    if match:
        return urllib.parse.unquote(match.group(1))
    match = re.search(r'filename="?([^";]+)"?', content_disposition)
    if match:
        return match.group(1)
    return None


def _ensure_unique_filename(target_dir: str, filename: str) -> str:
    safe_name = _sanitize_filename(filename)
    candidate = safe_name
    counter = 1
    while os.path.exists(os.path.join(target_dir, candidate)):
        stem, suffix = os.path.splitext(safe_name)
        candidate = f"{stem}({counter}){suffix}"
        counter += 1
    return candidate


def _sanitize_filename(name: str) -> str:
    name = name.strip()
    if not name:
        return "download.bin"
    name = re.sub(r"[\\/:*?\"<>|]", "_", name)
    if name in {".", ".."}:
        return "download.bin"
    return name


def _safe_int(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None
