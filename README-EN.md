# Secure File Share

Secure File Share is a single-admin file distribution service that listens only on a localhost high port so you can expose it via a reverse proxy such as Nginx. The application ships with a modern web console and a command-line helper script. Key capabilities include:

- Binds to `127.0.0.1` on a configurable high port (≥ 20000) to keep the service off the public Internet by default.
- Requires authentication; the installer lets you set credentials manually or generates strong random values on demand.
- Graphical console lets you browse the server filesystem, add or remove bookmarks, and create or revoke share links. Folders are compressed to ZIP archives automatically when shared.
- Share links use random 8-10 character alphanumeric tokens and support:
  - Download quotas (including unlimited)
  - Expiration by duration or absolute timestamp
  - Optional IP allowlists
- Persistent bookkeeping for download counts, expiration, and archives; logs are written to `logs/server.log`.
- The console can download files directly from URLs. Downloads default to `data/downloads/` (you may create subdirectories there) and attempt a multithreaded transfer, falling back to single-threaded if needed.
- CLI helper `manage.py` handles init/start/stop/status/run workflows.
- The web UI auto-detects the browser language (Chinese or English) and offers a manual toggle.

## Quick Start

1. **Initialize the configuration**

   ```bash
   python3 manage.py init --show-credentials
   ```

   - The script prompts for a listening port (defaults to 23000, must be ≥20000).
   - You can provide an admin username/password or leave the prompts empty to generate random values.
   - Use `--show-credentials` to print generated credentials to stdout.

2. **Start the service in the background**

   ```bash
   python3 manage.py start
   ```

   Logs are written to `logs/server.log`; the PID file lives in `run/server.pid`.

3. **Run in the foreground (development)**

   ```bash
   python3 manage.py run
   ```

   The process blocks in the current terminal and streams logs to stdout/stderr.

4. **Stop the service**

   ```bash
   python3 manage.py stop
   ```

5. **Check status**

   ```bash
   python3 manage.py status
   ```

## Reverse Proxy Example

The service listens on `127.0.0.1:<port>`. If you expose it via `files.example.com`, you can use an Nginx block like:

```nginx
location / {
    proxy_pass http://127.0.0.1:23000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

Protect the public endpoint with HTTPS and, if possible, additional authentication (VPN, IP allowlist, etc.).

## Data Locations

- Configuration: `config/config.json`
- Share metadata: `data/shares.json`
- Bookmark metadata: `data/bookmarks.json`
- ZIP archives for shared folders: `data/archives/`
- Direct-download files: `data/downloads/`
- Runtime PID: `run/server.pid`
- Logs: `logs/server.log`

All directories are created automatically.

## 📖 Important Documentation

- **[Blocked Paths Rules](BLOCKED_PATHS.md)** - Detailed explanation of which directories and files are blocked
- **[Security Fixes](SECURITY_FIXES.md)** - List of fixed security vulnerabilities

## Security Recommendations

- Rotate the admin password periodically. You can rerun `python3 manage.py init --force` to regenerate credentials, or manually edit `config/config.json` and restart the service.
- Restrict access to the reverse proxy endpoint (VPN, firewall, basic auth) in addition to the built-in login.
- Keep the proxy and firewall rules tightened so only trusted hosts can reach the localhost port.
- Review `logs/server.log` regularly or forward it to your central logging platform.

## 🔒 Security Fixes (2025-10-04)

This project has undergone comprehensive security hardening with the following critical vulnerabilities fixed:

### Fixed Security Issues

1. ✅ **Path Traversal Protection** - Blocks access to system sensitive directories (/etc, /root, /home, etc.)
2. ✅ **SSRF Attack Prevention** - Prevents internal network probing and cloud metadata access
3. ✅ **Brute Force Protection** - Login rate limiting (5 attempts / 5 minutes)
4. ✅ **Session Management Enhancement** - Limits concurrent sessions, auto-cleanup expired sessions
5. ✅ **File Size Limits** - Prevents DoS attacks (max 2 GiB)
6. ✅ **Error Message Protection** - Doesn't leak system details
7. ✅ **CSP Policy Hardening** - Prevents XSS attacks
8. ✅ **Cookie Security Attributes** - HttpOnly, Secure, SameSite=Strict

See `SECURITY_FIXES.md` for detailed fix descriptions.

### Production Environment Setup

If using HTTPS reverse proxy, set environment variable before starting:

```bash
export ENABLE_HTTPS=true
python3 manage.py start
```

This enables the `Secure` flag on cookies, ensuring they're only transmitted over HTTPS.

## Development Notes

- The project depends only on the Python standard library (Python ≥ 3.10).
- Front-end assets live under `server/static/` and `server/templates/`; feel free to customize styles or text.
- The UI supports Chinese and English. Language detection happens automatically, and users can toggle languages from the interface.

See `README.md` for the Chinese version.
