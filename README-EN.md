# Secure File Share

<div align="center">
  <sub><a href="README.md">📖 中文版</a></sub>
</div>

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
- CLI helper `manage.py` handles init/start/stop/status/run/uninstall workflows.
- The web UI auto-detects the browser language (Chinese or English) and offers a manual toggle.

## Installation

1. **Download the source code**

   ```bash
   git clone https://github.com/kaze-kaze/file-transfer.git
   cd file-transfer
   ```

2. **Check Python version**

   ```bash
   python3 --version  # Requires Python 3.10 or higher
   ```

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

6. **Uninstall the service**

   ```bash
   # Interactive uninstall (prompts for confirmation)
   python3 manage.py uninstall

   # Skip confirmation and uninstall directly
   python3 manage.py uninstall -y
   ```

   Uninstall will:
   - ✓ Stop the running service
   - ✓ Remove configuration files (`config/`)
   - ✓ Remove data files (`data/`)
   - ✓ Remove log files (`logs/`)
   - ✓ Remove runtime files (`run/`)
   - ✓ Keep source code files

   To completely remove the project (including source code):
   ```bash
   cd ..
   rm -rf file-transfer
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

- **[Command Reference](COMMANDS.md)** - Complete guide to all available commands and tools
- **[Blocked Paths Rules](BLOCKED_PATHS.md)** - Detailed explanation of which directories and files are blocked

## Security Recommendations

- Rotate the admin password periodically. You can rerun `python3 manage.py init --force` to regenerate credentials, or manually edit `config/config.json` and restart the service.
- Restrict access to the reverse proxy endpoint (VPN, firewall, basic auth) in addition to the built-in login.
- Keep the proxy and firewall rules tightened so only trusted hosts can reach the localhost port.
- Review `logs/server.log` regularly or forward it to your central logging platform.



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
