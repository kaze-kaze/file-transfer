# Secure File Share

<div align="center">
  <a href="README-EN.md">📖 English Version</a></sub>
</div>

Secure File Share 是一个面向单管理员的文件分享服务，可在本地端口运行，并通过反向代理对外提供下载链接。主要特性如下：

- 仅监听 `127.0.0.1` 上 20000 以上的高位端口，方便配合 Nginx 等反向代理使用。
- 管理端需要登录，默认管理员账号在安装时手动设置，支持自动生成随机凭据。
- 图形化控制台可浏览服务器文件系统、添加/删除路径书签、创建/撤销分享链接，可一键切换隐藏文件显示状态，并支持将文件夹自动打包为 ZIP 后分享。
- 分享链接使用 8-10 位大小写字母+数字随机串，支持：
  - 设置最大访问次数（可无限制）
  - 设置有效期（小时或指定时间点）
  - 限制访问 IP（白名单）
- 控制台支持直接输入外部 URL 下载文件，默认保存到 `data/downloads/` 目录（可在其下新建子目录）；优先使用多线程加速下载，不支持时自动回退单线程。
- 已下载计数与过期控制持久化存储，并提供访问日志输出。
- 提供命令行管理脚本 `manage.py`，支持初始化、启动、停止、状态查询以及前台运行模式。

## 快速开始

1. **初始化配置**

   ```bash
   python3 manage.py init --show-credentials
   ```

   - 脚本会提示输入监听端口（默认 23000，要求 ≥20000）。
   - 可输入自定义管理员账号与密码，也可留空使用自动生成的随机值。
   - 使用 `--show-credentials` 可在终端打印随机生成的账号密码，方便记录。

2. **后台启动服务**

   ```bash
   python3 manage.py start
   ```

   日志默认写入 `logs/server.log`，PID 文件位于 `run/server.pid`。

3. **前台运行（调试）**

   ```bash
   python3 manage.py run
   ```

   前台模式会在当前终端输出日志，仅适合调试环境。

4. **停止服务**

   ```bash
   python3 manage.py stop
   ```

5. **查看状态**

   ```bash
   python3 manage.py status
   ```

## 反向代理示例

服务默认监听 `127.0.0.1:<port>`。假设外部访问域名为 `files.example.com`，可在 Nginx 中配置：

```nginx
location / {
    proxy_pass http://127.0.0.1:23000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

请确保在前端代理层启用 HTTPS，并限制对管理界面的访问来源（如内网或 VPN）。

## 数据储存位置

- 配置文件：`config/config.json`
- 分享链接数据：`data/shares.json`
- 书签数据：`data/bookmarks.json`
- URL 下载文件：`data/downloads/`
- 运行时 PID：`run/server.pid`
- 日志文件：`logs/server.log`

以上文件在服务运行时会自动创建。

## 📖 重要文档

- **[路径访问限制规则](BLOCKED_PATHS.md)** - 详细说明哪些目录和文件被阻止访问

## 安全加固建议

- 使用强随机密码并定期轮换，或在初始化后通过编辑 `config/config.json` 并重新启动服务来更新管理员密码。
- 在反向代理层启用 HTTP 基本认证或基于 IP 的访问控制，进一步保护管理界面。
- 结合防火墙规则，仅允许代理服务器访问服务监听端口。
- 定期查看 `logs/server.log` 以获取访问情况，并根据需要将日志接入集中式日志平台。

## 🔒 安全修复（2025-10-04）

本项目已实施全面安全加固，修复了以下关键漏洞：

### 已修复的安全问题

1. ✅ **路径遍历防护** - 阻止访问系统敏感目录（/etc, /root, /home 等）
2. ✅ **SSRF 攻击防护** - 阻止内网探测和云元数据访问
3. ✅ **暴力破解防护** - 登录速率限制（5 次/5 分钟）
4. ✅ **会话管理增强** - 限制并发会话数，自动清理过期会话
5. ✅ **文件大小限制** - 防止 DoS 攻击（最大 2 GiB）
6. ✅ **错误信息保护** - 不泄露系统详细信息
7. ✅ **CSP 策略加固** - 防止 XSS 攻击
8. ✅ **Cookie 安全属性** - HttpOnly, Secure, SameSite=Strict

详细修复说明请查看 `SECURITY_FIXES.md`。

### 生产环境配置

如果使用 HTTPS 反向代理，启动前设置环境变量：

```bash
export ENABLE_HTTPS=true
python3 manage.py start
```

这将启用 Cookie 的 `Secure` 标志，确保 Cookie 仅通过 HTTPS 传输。

## 开发说明

- 本项目仅依赖 Python 标准库，无需额外安装第三方依赖。
- 部署或运行前请确保系统安装 Python 3.10 及以上版本。
- 若需调整 UI 或策略，可直接修改 `server/static` 和 `server/templates` 目录下的文件。

如需进一步自定义功能，欢迎在现有结构上扩展 API 或前端模块。
