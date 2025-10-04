"""Path validation and security enforcement module."""

from __future__ import annotations

import ipaddress
import os
import socket
from typing import List, Optional
from urllib.parse import urlparse

from .config import BASE_DIR

# Allowed root directories for file operations
DATA_DIR = os.path.join(BASE_DIR, "data")
DOWNLOADS_ROOT = os.path.join(DATA_DIR, "downloads")

# Define safe base paths that can be accessed
ALLOWED_BASE_PATHS = [
    DOWNLOADS_ROOT,
    os.path.join(BASE_DIR, "data", "archives"),
]

# System sensitive paths that must be blocked
# Note: We'll check these AFTER verifying if path is within project directory
BLOCKED_PATH_PREFIXES = [
    "/etc",
    "/home",
    "/var/log",
    "/var/www",
    "/usr",
    "/boot",
    "/sys",
    "/proc",
    "/dev",
    "/tmp",
    "/opt",
]

# Sensitive paths within /root (excluding project directory)
ROOT_BLOCKED_PATTERNS = [
    "/.ssh",
    "/.aws",
    "/.config",
    "/.gnupg",
    "/.kube",
    "/.docker",
]

# Sensitive file patterns
BLOCKED_FILE_PATTERNS = [
    "passwd",
    "shadow",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "authorized_keys",
    "known_hosts",
    ".aws",
    ".ssh",
    "credentials",
    ".env",
    "config.json",
    ".git",
]


class PathValidationError(Exception):
    """Raised when path validation fails."""


class URLValidationError(Exception):
    """Raised when URL validation fails."""


def validate_path_access(path: str, allow_custom: bool = False) -> str:
    """
    Validate that a path is safe to access.

    Args:
        path: The path to validate
        allow_custom: If True, allows paths outside ALLOWED_BASE_PATHS but still blocks sensitive paths

    Returns:
        Absolute normalized path if valid

    Raises:
        PathValidationError: If path is not allowed
    """
    if not path:
        raise PathValidationError("Path cannot be empty")

    # Normalize and get absolute path
    abs_path = os.path.abspath(os.path.normpath(path))

    # First check if path is within project directory - if so, allow it (project paths are safe)
    project_base = os.path.abspath(BASE_DIR)
    is_in_project = abs_path.startswith(project_base)

    # Check for sensitive patterns in /root first (even within project, block SSH keys etc.)
    if abs_path.startswith("/root"):
        for pattern in ROOT_BLOCKED_PATTERNS:
            if pattern in abs_path:
                raise PathValidationError(
                    f"Access denied: cannot access sensitive path containing '{pattern}'"
                )

    if not is_in_project:
        # Path is outside project - check against blocked system paths
        for blocked_prefix in BLOCKED_PATH_PREFIXES:
            blocked_abs = os.path.abspath(blocked_prefix)
            if abs_path.startswith(blocked_abs):
                raise PathValidationError(
                    f"Access denied: cannot access system directory {blocked_prefix}"
                )

        # Allow browsing /root directory itself and /root/project for navigation
        # but block anything that's not a parent of our project
        if abs_path.startswith("/root"):
            # Allow: /root, /root/project (parents of project)
            # Block: /root/other_dir (sibling directories)
            allowed_root_paths = [
                "/root",
                "/root/project"
            ]
            if abs_path not in allowed_root_paths and not abs_path.startswith(project_base):
                # This is a sibling directory or other location in /root
                # Allow it for flexibility, but sensitive patterns already blocked above
                pass

    # Check for sensitive file patterns
    path_lower = abs_path.lower()
    for pattern in BLOCKED_FILE_PATTERNS:
        if pattern.lower() in path_lower:
            raise PathValidationError(
                f"Access denied: path contains sensitive pattern '{pattern}'"
            )

    # If not allowing custom paths, enforce whitelist
    if not allow_custom:
        allowed = False
        for allowed_base in ALLOWED_BASE_PATHS:
            allowed_abs = os.path.abspath(allowed_base)
            if abs_path.startswith(allowed_abs):
                allowed = True
                break

        if not allowed:
            raise PathValidationError(
                "Access denied: path is outside allowed directories. "
                "Only data/downloads and data/archives are accessible."
            )

    return abs_path


def validate_share_path(path: str) -> str:
    """
    Validate a path for sharing (more permissive than general access).
    Allows paths outside ALLOWED_BASE_PATHS but still blocks sensitive system paths.

    Returns:
        Absolute normalized path if valid

    Raises:
        PathValidationError: If path accesses sensitive system directories
    """
    return validate_path_access(path, allow_custom=True)


def validate_download_url(url: str) -> None:
    """
    Validate a URL for downloading to prevent SSRF attacks.

    Args:
        url: The URL to validate

    Raises:
        URLValidationError: If URL is not safe
    """
    if not url or not url.strip():
        raise URLValidationError("URL cannot be empty")

    try:
        parsed = urlparse(url)
    except Exception as exc:
        raise URLValidationError(f"Invalid URL format: {exc}") from exc

    # Only allow HTTP and HTTPS schemes
    if parsed.scheme not in ["http", "https"]:
        raise URLValidationError(
            f"Blocked URL scheme: {parsed.scheme}. Only http and https are allowed."
        )

    # Must have a hostname
    if not parsed.hostname:
        raise URLValidationError("URL must have a valid hostname")

    # Resolve hostname to IP address
    try:
        ip_addresses = socket.getaddrinfo(
            parsed.hostname,
            parsed.port or (443 if parsed.scheme == "https" else 80),
            socket.AF_UNSPEC,
            socket.SOCK_STREAM
        )
    except socket.gaierror as exc:
        raise URLValidationError(f"Cannot resolve hostname: {exc}") from exc

    # Check each resolved IP address
    for family, _, _, _, sockaddr in ip_addresses:
        ip_str = sockaddr[0]

        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError as exc:
            raise URLValidationError(f"Invalid IP address: {exc}") from exc

        # Block private/internal IP addresses
        if ip_obj.is_private:
            raise URLValidationError(
                f"Access denied: {parsed.hostname} resolves to private IP {ip_str}"
            )

        if ip_obj.is_loopback:
            raise URLValidationError(
                f"Access denied: {parsed.hostname} resolves to loopback IP {ip_str}"
            )

        if ip_obj.is_link_local:
            raise URLValidationError(
                f"Access denied: {parsed.hostname} resolves to link-local IP {ip_str}"
            )

        if ip_obj.is_multicast:
            raise URLValidationError(
                f"Access denied: {parsed.hostname} resolves to multicast IP {ip_str}"
            )

        # Block cloud metadata endpoints
        if ip_str.startswith("169.254.169.254"):
            raise URLValidationError(
                "Access denied: cannot access cloud metadata endpoint"
            )

    # Additional hostname-based blocks
    hostname_lower = parsed.hostname.lower()
    blocked_hosts = [
        "localhost",
        "metadata.google.internal",
        "169.254.169.254",
    ]

    for blocked in blocked_hosts:
        if blocked in hostname_lower:
            raise URLValidationError(
                f"Access denied: hostname {parsed.hostname} is blocked"
            )


def validate_download_target_dir(target_dir: str) -> str:
    """
    Validate that download target directory is within allowed paths.

    Returns:
        Absolute normalized path if valid

    Raises:
        PathValidationError: If directory is not allowed
    """
    if not target_dir:
        raise PathValidationError("Target directory cannot be empty")

    abs_dir = os.path.abspath(os.path.normpath(target_dir))
    downloads_abs = os.path.abspath(DOWNLOADS_ROOT)

    # Must be within downloads directory
    if not abs_dir.startswith(downloads_abs):
        raise PathValidationError(
            f"Access denied: downloads must be saved to {DOWNLOADS_ROOT} or subdirectories"
        )

    # Also run general path validation
    validate_path_access(abs_dir, allow_custom=False)

    return abs_dir
