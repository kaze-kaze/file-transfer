#!/usr/bin/env python3
"""Management script for Secure File Share."""

from __future__ import annotations

import argparse
import getpass
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from server.config import CONFIG_PATH, ConfigManager
from server.security import generate_random_string, hash_password

CONFIG_FILE = Path(CONFIG_PATH)

BASE_DIR = Path(__file__).resolve().parent
RUN_DIR = BASE_DIR / "run"
LOG_DIR = BASE_DIR / "logs"
PID_FILE = RUN_DIR / "server.pid"
LOG_FILE = LOG_DIR / "server.log"


def ensure_directories() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def command_init(args: argparse.Namespace) -> None:
    ensure_directories()
    if CONFIG_FILE.exists() and not args.force:
        print("配置文件已存在。如需重新初始化，请使用 --force 参数。")
        return

    print("=== 初始化 Secure File Share ===")
    host = "127.0.0.1"
    port = prompt_port(default=23000)

    username = input("管理员用户名（留空自动生成）：").strip()
    if not username:
        username = generate_random_string(8)
        print(f"已生成管理员用户名：{username}")

    password = prompt_password()
    salt, hashed, iterations = hash_password(password)

    config_data = {
        "admin": {
            "username": username,
            "password_hash": hashed,
            "salt": salt,
            "iterations": iterations,
        },
        "server": {
            "host": host,
            "port": port,
        },
        "security": {
            "session_timeout_minutes": 60,
        },
    }

    ConfigManager.save(str(CONFIG_FILE), config_data)
    print("配置已写入。")
    if args.show_credentials:
        print(f"管理员用户名：{username}")
        print(f"管理员密码：{password}")


def prompt_password() -> str:
    password = getpass.getpass("管理员密码（留空自动生成）：")
    if password:
        confirm = getpass.getpass("请再次输入密码：")
        if password != confirm:
            print("两次输入的密码不一致，请重试。")
            return prompt_password()
        return password
    password = generate_random_string(10)
    print(f"已生成管理员密码：{password}")
    return password


def prompt_port(default: int) -> int:
    while True:
        raw = input(f"监听端口（>=20000，默认 {default}）：").strip()
        if not raw:
            value = default
        else:
            try:
                value = int(raw)
            except ValueError:
                print("请输入有效的数字端口。")
                continue
        if value < 20000 or value > 65535:
            print("端口需在 20000-65535 范围内。")
            continue
        return value


def command_start(args: argparse.Namespace) -> None:  # noqa: ARG001 - 接口需要参数
    ensure_directories()
    if not CONFIG_FILE.exists():
        print("未找到配置文件，请先运行 `python3 manage.py init`。")
        return
    if PID_FILE.exists():
        pid = PID_FILE.read_text().strip()
        if pid and process_alive(int(pid)):
            print(f"服务已在运行中 (PID {pid})。")
            return
        PID_FILE.unlink(missing_ok=True)

    command = [sys.executable, "-m", "server.app"]
    stdout = None
    try:
        stdout = open(LOG_FILE, "ab", buffering=0)
        process = subprocess.Popen(  # noqa: S603, S607 - 控制的子进程
            command,
            cwd=str(BASE_DIR),
            stdout=stdout,
            stderr=stdout,
            preexec_fn=os.setsid,
        )
    except Exception as exc:  # pylint: disable=broad-except
        print(f"启动失败：{exc}")
        return
    finally:
        if stdout is not None and not stdout.closed:
            stdout.close()
    PID_FILE.write_text(str(process.pid))
    print(f"服务已启动，PID {process.pid}。日志输出：{LOG_FILE}")


def command_stop(args: argparse.Namespace) -> None:  # noqa: ARG001
    if not PID_FILE.exists():
        print("未发现运行中的服务。")
        return
    pid_text = PID_FILE.read_text().strip()
    if not pid_text:
        print("PID 文件为空，无法停止。")
        return
    pid = int(pid_text)
    if not process_alive(pid):
        print("进程未运行，清理 PID 文件。")
        PID_FILE.unlink(missing_ok=True)
        return
    print(f"正在停止进程 {pid} ...")
    os.kill(pid, signal.SIGTERM)
    for _ in range(20):
        if not process_alive(pid):
            PID_FILE.unlink(missing_ok=True)
            print("服务已停止。")
            return
        time.sleep(0.3)
    print("进程未在期望时间内退出，如有需要请手动检查。")


def command_status(args: argparse.Namespace) -> None:  # noqa: ARG001
    if PID_FILE.exists():
        pid_text = PID_FILE.read_text().strip()
        if pid_text and process_alive(int(pid_text)):
            print(f"服务正在运行，PID {pid_text}")
            return
    print("服务未运行。")


def command_run(args: argparse.Namespace) -> None:  # noqa: ARG001
    from server.app import run_server  # 延迟导入以执行实时配置校验

    run_server()


def process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Secure File Share 管理工具")
    sub = parser.add_subparsers(dest="command", required=True)

    init_cmd = sub.add_parser("init", help="初始化配置")
    init_cmd.add_argument("--force", action="store_true", help="覆盖已有配置")
    init_cmd.add_argument(
        "--show-credentials",
        action="store_true",
        help="初始化完成后在控制台显示账号密码",
    )
    init_cmd.set_defaults(func=command_init)

    start_cmd = sub.add_parser("start", help="后台启动服务")
    start_cmd.set_defaults(func=command_start)

    stop_cmd = sub.add_parser("stop", help="停止服务")
    stop_cmd.set_defaults(func=command_stop)

    status_cmd = sub.add_parser("status", help="查看服务状态")
    status_cmd.set_defaults(func=command_status)

    run_cmd = sub.add_parser("run", help="以前台方式运行服务")
    run_cmd.set_defaults(func=command_run)

    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
