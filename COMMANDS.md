# 命令参考手册

本文档列出了所有可用的命令和工具。

---

## 📋 目录

- [管理命令](#管理命令)
- [直接运行](#直接运行)
- [代码验证](#代码验证)
- [开发调试](#开发调试)
- [项目信息](#项目信息)
- [系统命令](#系统命令)

---

## 🔧 管理命令

### 查看帮助

```bash
python3 manage.py --help
```

### 初始化配置

```bash
# 交互式初始化
python3 manage.py init

# 显示生成的凭据
python3 manage.py init --show-credentials

# 强制重新初始化（覆盖现有配置）
python3 manage.py init --force
```

### 启动服务

```bash
# 后台启动
python3 manage.py start

# 前台运行（开发/调试模式）
python3 manage.py run
```

### 停止服务

```bash
python3 manage.py stop
```

### 查看状态

```bash
python3 manage.py status
```

### 卸载服务

```bash
# 交互式卸载（推荐）
python3 manage.py uninstall

# 静默卸载
python3 manage.py uninstall -y

# 查看卸载帮助
python3 manage.py uninstall --help
```

---

## 🚀 直接运行

### 直接启动服务器

```bash
# 相当于 manage.py run，但更简洁
python3 -m server.app
```

**注意**: 需要先运行 `python3 manage.py init` 初始化配置。

---

## ✅ 代码验证

### 语法检查和预编译

```bash
# 检查所有代码
python3 -m compileall server manage.py

# 静默模式（不显示过程）
python3 -m compileall -q server manage.py

# 强制重新编译
python3 -m compileall -f server manage.py

# 编译整个项目
python3 -m compileall .
```

### 编译单个文件

```bash
python3 -m py_compile server/app.py
```

### 检查导入

```bash
# 测试导入是否正常
python3 -c "from server.app import build_context; print('✓ 导入成功')"

# 检查所有模块
python3 -c "
from server import app, security, session, share
from server import bookmarks, config, downloader
from server import path_validator, rate_limiter, storage
print('✓ 所有模块导入成功')
"
```

---

## 🐛 开发调试

### 使用调试器

```bash
# 启动 Python 调试器
python3 -m pdb manage.py run

# 常用调试命令:
# n - 下一行
# s - 进入函数
# c - 继续执行
# p <变量> - 打印变量
# q - 退出
```

### 查看代码覆盖率

```bash
# 跟踪代码执行
python3 -m trace --count -C . server/app.py

# 查看结果
cat server/app.cover
```

### 性能分析

```bash
# 简单性能测试
python3 -m timeit -s "from server.security import hash_password" "hash_password('test')"

# 使用 cProfile
python3 -m cProfile -s cumulative manage.py status
```

---

## 📊 项目信息

### Python 版本

```bash
python3 --version
python3 -c "import sys; print(f'Python {sys.version}')"
```

### 依赖检查

```bash
# 检查标准库是否完整
python3 -c "
import json, os, sys, time, signal, shutil
import secrets, hashlib, threading, subprocess
import mimetypes, ipaddress, socket
from pathlib import Path
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
print('✓ 所有依赖正常')
"
```

### 代码统计

```bash
# 统计代码行数
find server -name "*.py" | xargs wc -l

# 统计总行数
find . -name "*.py" | xargs wc -l | tail -1

# 统计文件数量
find server -name "*.py" | wc -l
```

### 项目大小

```bash
# 查看项目总大小
du -sh .

# 查看各目录大小
du -sh */ | sort -h

# 查看数据目录大小
du -sh data/ logs/ config/ 2>/dev/null
```

### Git 信息（如果使用 Git）

```bash
# 查看最近提交
git log --oneline -10

# 查看当前分支
git branch

# 查看文件变更
git status

# 查看远程仓库
git remote -v
```

---

## 🔍 系统命令

### 查看进程

```bash
# 查看服务进程
ps aux | grep "server.app"

# 查看端口占用
netstat -tlnp | grep 23000
# 或
ss -tlnp | grep 23000
# 或
lsof -i :23000
```

### 查看日志

```bash
# 实时查看日志
tail -f logs/server.log

# 查看最后 100 行
tail -100 logs/server.log

# 搜索日志
grep "ERROR" logs/server.log
grep "Login" logs/server.log
```

### 查看配置

```bash
# 查看配置文件
cat config/config.json | python3 -m json.tool

# 查看分享链接
cat data/shares.json | python3 -m json.tool

# 查看书签
cat data/bookmarks.json | python3 -m json.tool
```

### 监控系统资源

```bash
# CPU 和内存使用
top -p $(cat run/server.pid)

# 或使用 htop（如已安装）
htop -p $(cat run/server.pid)
```

### 网络测试

```bash
# 测试本地连接
curl http://127.0.0.1:23000/

# 测试响应时间
time curl -o /dev/null -s http://127.0.0.1:23000/

# 查看 HTTP 头
curl -I http://127.0.0.1:23000/
```

---

## 🛠️ 高级用法

### 环境变量

```bash
# 启用 HTTPS Cookie（生产环境）
export ENABLE_HTTPS=true
python3 manage.py start

# 临时设置（仅当次有效）
ENABLE_HTTPS=true python3 manage.py start
```

### 后台运行（替代方法）

```bash
# 使用 nohup
nohup python3 -m server.app > logs/server.log 2>&1 &

# 使用 screen
screen -S file-transfer
python3 manage.py run
# Ctrl+A, D 分离会话
# screen -r file-transfer 重新连接

# 使用 tmux
tmux new -s file-transfer
python3 manage.py run
# Ctrl+B, D 分离会话
# tmux attach -t file-transfer 重新连接
```

### 使用 systemd（系统服务）

创建 `/etc/systemd/system/file-transfer.service`:

```ini
[Unit]
Description=Secure File Transfer Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/project/file-transfer
ExecStart=/usr/bin/python3 -m server.app
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用和管理：

```bash
# 重载配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start file-transfer

# 停止服务
sudo systemctl stop file-transfer

# 开机自启
sudo systemctl enable file-transfer

# 查看状态
sudo systemctl status file-transfer

# 查看日志
sudo journalctl -u file-transfer -f
```

---

## 📝 快速参考

### 常用命令速查

```bash
# 快速启动
cd /root/project/file-transfer && python3 manage.py start

# 快速停止
python3 manage.py stop

# 快速重启
python3 manage.py stop && sleep 1 && python3 manage.py start

# 查看日志
tail -f logs/server.log

# 检查状态
python3 manage.py status && curl -I http://127.0.0.1:23000/
```

### 故障排查

```bash
# 1. 检查配置是否存在
test -f config/config.json && echo "配置存在" || echo "配置缺失"

# 2. 检查端口是否被占用
netstat -tlnp | grep 23000

# 3. 检查进程是否运行
ps aux | grep server.app

# 4. 验证代码语法
python3 -m compileall server manage.py

# 5. 测试导入
python3 -c "from server.app import build_context; build_context()"

# 6. 查看最近错误
tail -50 logs/server.log | grep -i error
```

---

## 🔗 相关文档

- [README.md](README.md) - 项目说明和快速开始
- [BLOCKED_PATHS.md](BLOCKED_PATHS.md) - 路径访问限制规则
- [SECURITY_FIXES.md](SECURITY_FIXES.md) - 安全修复说明

---

**最后更新**: 2025-10-04
**版本**: 1.0
