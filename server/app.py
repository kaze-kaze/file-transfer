from __future__ import annotations

import json
import mimetypes
import os
import time
from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus
from http.cookies import CookieError, SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, unquote, urlparse

from .bookmarks import BookmarkManager
from .config import BASE_DIR, ConfigManager
from .downloader import DownloadError, download_from_url
from .security import verify_password
from .session import SessionManager
from .share import ShareManager

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
DATA_DIR = os.path.join(BASE_DIR, "data")


@dataclass
class ServerContext:
    config: ConfigManager
    session_manager: SessionManager
    share_manager: ShareManager
    bookmark_manager: BookmarkManager
    session_timeout_minutes: int


class FileShareRequestHandler(BaseHTTPRequestHandler):
    server_version = "SecureFileShare/1.0"
    context: ServerContext

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        # Silence default stdout logging; production deployments should plug into logging.
        return

    def do_GET(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            route = parsed.path
            if route.startswith("/static/"):
                self._handle_static(route)
                return
            if route == "/":
                self._handle_root()
                return
            if route == "/login":
                self._handle_login_page()
                return
            if route == "/api/session":
                session = self._require_auth()
                self._send_json(HTTPStatus.OK, {
                    "username": session.username,
                    "expires_at": int(session.expires_at),
                })
                return
            if route == "/api/bookmarks":
                self._require_auth()
                bookmarks = self.context.bookmark_manager.list_bookmarks()
                self._send_json(HTTPStatus.OK, {"bookmarks": bookmarks})
                return
            if route == "/api/fs":
                self._require_auth()
                query = parse_qs(parsed.query)
                target = query.get("path", ["/"])[0]
                show_hidden = self._is_truthy(query.get("show_hidden", ["0"])[0])
                listing = self._list_directory(target, show_hidden=show_hidden)
                self._send_json(HTTPStatus.OK, listing)
                return
            if route == "/api/shares":
                self._require_auth()
                shares = self.context.share_manager.list_shares()
                self._send_json(HTTPStatus.OK, {"shares": shares})
                return
            if route.startswith("/d/"):
                token = route.split("/", 2)[2]
                self._handle_download(token)
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
        except AuthRequired:
            self._redirect("/login")
        except Exception as exc:  # pylint: disable=broad-except
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": "Internal server error", "detail": str(exc)},
            )

    def do_POST(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            route = parsed.path
            if route == "/api/login":
                self._handle_login()
                return
            if route == "/api/logout":
                self._require_auth()
                token = self._get_session_token()
                self.context.session_manager.invalidate(token)
                cookie = self._clear_session_cookie()
                self._send_json(HTTPStatus.OK, {"message": "Logged out"}, cookies=[cookie])
                return
            if route == "/api/bookmarks":
                self._require_auth()
                payload = self._read_json()
                label = (payload.get("label") or "").strip()
                path = payload.get("path")
                if not path:
                    self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Path is required"})
                    return
                bookmark = self.context.bookmark_manager.add_bookmark(label, path)
                self._send_json(HTTPStatus.CREATED, bookmark.to_dict())
                return
            if route == "/api/shares":
                self._require_auth()
                payload = self._read_json()
                response = self._create_share(payload)
                self._send_json(HTTPStatus.CREATED, response)
                return
            if route == "/api/downloads":
                self._require_auth()
                payload = self._read_json()
                response = self._handle_download_request(payload)
                self._send_json(HTTPStatus.CREATED, response)
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
        except AuthRequired:
            self._redirect("/login")
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except FileNotFoundError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except NotADirectoryError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except Exception as exc:  # pylint: disable=broad-except
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": "Internal server error", "detail": str(exc)},
            )

    def do_DELETE(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            route = parsed.path
            if route.startswith("/api/bookmarks/"):
                self._require_auth()
                identifier = route.split("/", 3)[3]
                self.context.bookmark_manager.delete_bookmark(identifier)
                self._send_json(HTTPStatus.NO_CONTENT, {})
                return
            if route.startswith("/api/shares/"):
                self._require_auth()
                token = route.split("/", 3)[3]
                self.context.share_manager.delete_share(token)
                self._send_json(HTTPStatus.NO_CONTENT, {})
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
        except AuthRequired:
            self._redirect("/login")
        except Exception as exc:  # pylint: disable=broad-except
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": "Internal server error", "detail": str(exc)},
            )

    def _handle_static(self, route: str) -> None:
        rel_path = route[len("/static/"):]
        safe_path = os.path.normpath(rel_path)
        if safe_path.startswith(".."):
            self._send_json(HTTPStatus.FORBIDDEN, {"error": "Forbidden"})
            return
        file_path = os.path.join(STATIC_DIR, safe_path)
        if not os.path.isfile(file_path):
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        mime, _ = mimetypes.guess_type(file_path)
        mime = mime or "application/octet-stream"
        with open(file_path, "rb") as fh:
            content = fh.read()
        self._send_response(HTTPStatus.OK, mime, content, cache_control="public, max-age=3600")

    def _handle_root(self) -> None:
        try:
            self._require_auth()
        except AuthRequired:
            self._redirect("/login")
            return
        self._serve_template("index.html")

    def _handle_login_page(self) -> None:
        if self._get_session() is not None:
            self._redirect("/")
            return
        self._serve_template("login.html")

    def _serve_template(self, filename: str) -> None:
        file_path = os.path.join(TEMPLATE_DIR, filename)
        if not os.path.isfile(file_path):
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        with open(file_path, "rb") as fh:
            content = fh.read()
        mime, _ = mimetypes.guess_type(file_path)
        mime = mime or "text/html; charset=utf-8"
        self._send_response(HTTPStatus.OK, mime, content)

    def _list_directory(self, path: str, show_hidden: bool = False) -> Dict[str, Any]:
        target = os.path.abspath(unquote(path))
        if not os.path.exists(target):
            raise FileNotFoundError("Path does not exist")
        if not os.path.isdir(target):
            raise NotADirectoryError("Requested path is not a directory")
        entries: List[Dict[str, Any]] = []
        try:
            for name in sorted(os.listdir(target)):
                if not show_hidden and name.startswith("."):
                    continue
                full_path = os.path.join(target, name)
                try:
                    stat = os.stat(full_path)
                except OSError:
                    continue
                entries.append({
                    "name": name,
                    "path": full_path,
                    "is_dir": os.path.isdir(full_path),
                    "size": stat.st_size,
                    "modified": int(stat.st_mtime),
                })
        except PermissionError as exc:
            raise ValueError("Permission denied") from exc
        parent = os.path.abspath(os.path.join(target, os.pardir)) if target != os.path.abspath(os.sep) else None
        return {
            "path": target,
            "parent": parent,
            "entries": entries,
            "show_hidden": show_hidden,
        }

    def _handle_download(self, token: str) -> None:
        client_ip = self._get_client_ip()
        result = self.context.share_manager.validate_and_register_download(token, client_ip)
        if not result:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Link is invalid or expired"})
            return
        file_path = result["path"]
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            self._send_json(HTTPStatus.GONE, {"error": "File no longer available"})
            return
        filename = result.get("filename") or os.path.basename(file_path)
        mime_hint = result.get("mime") or None
        mime = mime_hint or mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        file_size = os.path.getsize(file_path)
        self.send_response(HTTPStatus.OK)
        self._apply_common_headers()
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(file_size))
        self.send_header("Content-Disposition", f"attachment; filename=\"{filename}\"")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        with open(file_path, "rb") as fh:
            while True:
                chunk = fh.read(64 * 1024)
                if not chunk:
                    break
                self.wfile.write(chunk)

    def _handle_login(self) -> None:
        payload = self._read_json()
        username = (payload.get("username") or "").strip()
        password = payload.get("password") or ""
        if not username or not password:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Username and password required"})
            return
        admin = self.context.config.get_admin()
        if username != admin.username:
            self._send_json(HTTPStatus.UNAUTHORIZED, {"error": "Invalid credentials"})
            return
        if not verify_password(password, admin.salt, admin.password_hash, admin.iterations):
            self._send_json(HTTPStatus.UNAUTHORIZED, {"error": "Invalid credentials"})
            return
        token = self.context.session_manager.create_session(admin.username, self.context.session_timeout_minutes)
        cookie = self._set_session_cookie(token)
        self._send_json(HTTPStatus.OK, {"message": "Login successful"}, cookies=[cookie])

    def _create_share(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        path = payload.get("path")
        if not path:
            raise ValueError("File path is required")
        max_downloads = payload.get("max_downloads")
        if isinstance(max_downloads, str) and max_downloads.strip():
            max_downloads = int(max_downloads)
        elif max_downloads in ("", None):
            max_downloads = None
        elif isinstance(max_downloads, (int, float)):
            max_downloads = int(max_downloads)
        else:
            max_downloads = None
        if isinstance(max_downloads, int) and max_downloads <= 0:
            max_downloads = None
        expire_at = None
        expires_in_hours = payload.get("expires_in_hours")
        expires_at_raw = payload.get("expires_at")
        if expires_in_hours not in (None, ""):
            expire_at = time.time() + float(expires_in_hours) * 3600
        elif expires_at_raw:
            expire_at = self._parse_iso_timestamp(expires_at_raw)
        allowed_ips = payload.get("allowed_ips")
        if isinstance(allowed_ips, str):
            tokens = [segment.strip() for segment in allowed_ips.replace("\n", ",").split(",")]
            allowed_ips = [ip for ip in tokens if ip]
        elif isinstance(allowed_ips, list):
            allowed_ips = [str(ip).strip() for ip in allowed_ips if str(ip).strip()]
        else:
            allowed_ips = []
        record = self.context.share_manager.create_share(path, max_downloads, expire_at, allowed_ips)
        return {
            "token": record.token,
            "share_url": f"/d/{record.token}",
            "max_downloads": record.max_downloads,
            "expire_at": int(record.expire_at) if record.expire_at else None,
            "allowed_ips": record.allowed_ips,
            "is_directory": record.is_directory,
        }


    def _handle_download_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = (payload.get("url") or "").strip()
        if not url:
            raise ValueError("Download URL is required")
        target_dir = (payload.get("target_dir") or "").strip()
        if not target_dir:
            target_dir = os.getcwd()
        if not os.path.isabs(target_dir):
            target_dir = os.path.abspath(target_dir)
        if not os.path.isdir(target_dir):
            raise ValueError("Target directory must exist")
        filename = (payload.get("filename") or "").strip() or None
        try:
            result = download_from_url(url, target_dir, filename)
        except DownloadError as exc:
            raise ValueError(str(exc)) from exc
        return {
            "message": "Download completed",
            "path": result.path,
            "filename": result.filename,
            "size": result.size,
            "multithreaded": result.multithreaded,
        }

    def _parse_iso_timestamp(self, value: str) -> Optional[float]:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("Invalid ISO timestamp") from exc
        return parsed.timestamp()

    @staticmethod
    def _is_truthy(value: Optional[str]) -> bool:
        if value is None:
            return False
        return value.lower() in {"1", "true", "yes", "on"}

    def _require_auth(self) -> Any:
        session = self._get_session()
        if session is None:
            raise AuthRequired
        return session

    def _get_session(self) -> Optional[Any]:
        token = self._get_session_token()
        return self.context.session_manager.get_session(token)

    def _get_session_token(self) -> Optional[str]:
        cookie_header = self.headers.get("Cookie")
        if not cookie_header:
            return None
        cookie = SimpleCookie()
        try:
            cookie.load(cookie_header)
        except CookieError:
            return None
        morsel = cookie.get("session_id")
        return morsel.value if morsel else None

    def _get_client_ip(self) -> str:
        forwarded = self.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(',')[0].strip()
        real_ip = self.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        return self.client_address[0]

    def _read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        body = self.rfile.read(length)
        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON payload") from exc

    def _send_json(
        self,
        status: HTTPStatus,
        payload: Dict[str, Any],
        *,
        cookies: Optional[List[str]] = None,
    ) -> None:
        content = json.dumps(payload).encode("utf-8")
        self._send_response(status, "application/json", content, cookies=cookies)

    def _send_response(
        self,
        status: HTTPStatus,
        content_type: str,
        content: bytes,
        cache_control: str = "no-store",
        cookies: Optional[List[str]] = None,
    ) -> None:
        self.send_response(status)
        self._apply_common_headers()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", cache_control)
        if cookies:
            for value in cookies:
                self.send_header("Set-Cookie", value)
        self.end_headers()
        self.wfile.write(content)

    def _apply_common_headers(self) -> None:
        self.send_header("Server", self.server_version)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'")

    def _set_session_cookie(self, token: str) -> str:
        cookie = SimpleCookie()
        cookie["session_id"] = token
        cookie["session_id"]["httponly"] = True
        cookie["session_id"]["secure"] = False
        cookie["session_id"]["samesite"] = "Lax"
        cookie["session_id"]["path"] = "/"
        return cookie.output(header="", sep="").strip()

    def _clear_session_cookie(self) -> str:
        cookie = SimpleCookie()
        cookie["session_id"] = ""
        cookie["session_id"]["path"] = "/"
        cookie["session_id"]["httponly"] = True
        cookie["session_id"]["expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
        cookie["session_id"]["samesite"] = "Lax"
        return cookie.output(header="", sep="").strip()

    def _redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.SEE_OTHER)
        self._apply_common_headers()
        self.send_header("Location", location)
        self.end_headers()


class AuthRequired(Exception):
    pass


def build_context() -> ServerContext:
    config = ConfigManager()
    server_config = config.get_server()
    share_manager = ShareManager(os.path.join(DATA_DIR, "shares.json"))
    bookmark_manager = BookmarkManager(os.path.join(DATA_DIR, "bookmarks.json"))
    return ServerContext(
        config=config,
        session_manager=SessionManager(),
        share_manager=share_manager,
        bookmark_manager=bookmark_manager,
        session_timeout_minutes=server_config.session_timeout_minutes,
    )


def run_server() -> None:
    context = build_context()
    server_config = context.config.get_server()
    FileShareRequestHandler.context = context
    address = (server_config.host, server_config.port)
    httpd = ThreadingHTTPServer(address, FileShareRequestHandler)
    print(f"Serving on http://{server_config.host}:{server_config.port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run_server()
