# 路径访问限制规则

本文档详细说明了 Secure File Share 项目中实施的路径访问限制规则。

---

## 📋 目录

- [概述](#概述)
- [完全阻止的系统目录](#完全阻止的系统目录)
- [/root 下的敏感子目录](#root-下的敏感子目录)
- [敏感文件关键词过滤](#敏感文件关键词过滤)
- [允许访问的路径](#允许访问的路径)
- [配置文件位置](#配置文件位置)
- [自定义规则](#自定义规则)

---

## 概述

为了防止任意文件读取、分享泄露等安全漏洞，系统采用**智能白名单 + 黑名单**机制：

- ✅ **白名单**: 项目目录及其父目录可访问
- ❌ **黑名单**: 系统敏感目录、配置文件、凭据文件被阻止
- 🔍 **关键词过滤**: 包含敏感关键词的文件名被阻止

---

## 🔴 完全阻止的系统目录

以下系统目录**完全禁止访问**，无论是浏览、分享还是下载：

| 目录 | 说明 | 风险 |
|------|------|------|
| `/etc` | 系统配置文件 | 包含密码、服务配置等敏感信息 |
| `/home` | 其他用户主目录 | 用户隐私数据 |
| `/usr` | 系统程序和库 | 系统完整性 |
| `/boot` | 内核和启动文件 | 系统安全 |
| `/sys` | 内核接口 | 系统内部信息 |
| `/proc` | 进程信息 | 运行时敏感信息 |
| `/dev` | 设备文件 | 硬件访问 |
| `/tmp` | 临时文件 | 可能包含敏感临时数据 |
| `/opt` | 第三方软件 | 应用程序配置 |
| `/var/log` | 系统日志 | 系统活动记录 |
| `/var/www` | Web 服务器目录 | 其他 Web 应用数据 |

**示例被阻止的路径**:
```
/etc/passwd           ❌ 系统用户列表
/etc/shadow           ❌ 密码哈希
/etc/ssh/sshd_config  ❌ SSH 服务器配置
/home/user/.bashrc    ❌ 其他用户配置
/usr/bin/sudo         ❌ 系统程序
/boot/vmlinuz         ❌ 内核文件
/proc/self/environ    ❌ 进程环境变量
/var/log/auth.log     ❌ 认证日志
```

---

## 🔴 /root 下的敏感子目录

`/root` 目录本身**可以浏览**，但以下敏感子目录**禁止访问**：

| 路径模式 | 说明 | 包含内容 |
|----------|------|----------|
| `/.ssh` | SSH 配置和密钥 | 私钥、公钥、authorized_keys、known_hosts |
| `/.aws` | AWS 云服务凭据 | access_key、secret_key、配置文件 |
| `/.config` | 用户配置文件 | 各种应用程序配置 |
| `/.gnupg` | GPG 密钥环 | 加密密钥、签名密钥 |
| `/.kube` | Kubernetes 配置 | 集群凭据、kubeconfig |
| `/.docker` | Docker 配置 | 镜像仓库凭据 |

**示例被阻止的路径**:
```
/root/.ssh/id_rsa              ❌ SSH 私钥
/root/.ssh/authorized_keys     ❌ SSH 授权密钥
/root/.aws/credentials         ❌ AWS 访问密钥
/root/.config/gcloud/          ❌ Google Cloud 配置
/root/.gnupg/secring.gpg       ❌ GPG 私钥环
/root/.kube/config             ❌ Kubernetes 集群配置
/root/.docker/config.json      ❌ Docker 仓库凭据
```

**注意**: 这些目录即使在 `/root/project/file-transfer` 项目内创建同名目录也会被阻止。

---

## 🔴 敏感文件关键词过滤

**任何路径**（包括项目目录内）中包含以下关键词的文件都会被阻止访问：

### SSH 相关
```
id_rsa              - RSA 私钥
id_dsa              - DSA 私钥
id_ecdsa            - ECDSA 私钥
id_ed25519          - Ed25519 私钥
authorized_keys     - SSH 授权密钥列表
known_hosts         - SSH 已知主机
.ssh                - SSH 配置目录
```

### 系统敏感文件
```
passwd              - 系统用户密码文件
shadow              - 影子密码文件
```

### 云服务凭据
```
.aws                - AWS 配置和凭据
credentials         - 通用凭据文件
```

### 配置和环境
```
.env                - 环境变量配置
config.json         - JSON 配置文件
.git                - Git 版本控制
```

**示例被阻止的路径**:
```
/root/project/file-transfer/data/id_rsa           ❌ 包含 "id_rsa"
/root/project/file-transfer/backup/passwd.bak     ❌ 包含 "passwd"
/root/project/file-transfer/.env                  ❌ 包含 ".env"
/root/project/file-transfer/config/config.json    ❌ 包含 "config.json"
/root/test/.ssh/test.txt                          ❌ 包含 ".ssh"
```

**检测方式**: 使用**不区分大小写**的子串匹配
- `ID_RSA` ❌ 被阻止
- `my_id_rsa_backup` ❌ 被阻止
- `credentials.txt` ❌ 被阻止

---

## ✅ 允许访问的路径

以下路径**允许访问**（浏览、分享、下载）：

### 项目相关目录
```
/root/project/file-transfer/          ✅ 项目根目录（完全可访问）
/root/project/file-transfer/data/     ✅ 数据目录
/root/project/file-transfer/server/   ✅ 服务器代码
/root/project/file-transfer/config/   ✅ 配置目录（但 config.json 被过滤）
```

### 导航目录
```
/root/                                 ✅ 可浏览（但敏感子目录被阻止）
/root/project/                         ✅ 可浏览
/root/other_project/                   ✅ 可访问其他项目
```

### 数据存储目录（推荐）
```
/root/project/file-transfer/data/downloads/     ✅ URL 下载目录
/root/project/file-transfer/data/archives/      ✅ ZIP 打包目录
```

**最佳实践**:
- 所有需要分享的文件应放在项目 `data/` 目录下
- 避免使用敏感关键词命名文件

---

## 📂 配置文件位置

路径访问规则定义在：
```
server/path_validator.py
```

### 关键配置段

#### 1. 系统目录黑名单 (第 25-37 行)
```python
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
```

#### 2. /root 敏感子目录 (第 40-47 行)
```python
ROOT_BLOCKED_PATTERNS = [
    "/.ssh",
    "/.aws",
    "/.config",
    "/.gnupg",
    "/.kube",
    "/.docker",
]
```

#### 3. 敏感文件关键词 (第 50-62 行)
```python
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
```

---

## 🔧 自定义规则

### 添加新的阻止目录

编辑 `server/path_validator.py`，在相应列表中添加：

```python
# 添加系统目录
BLOCKED_PATH_PREFIXES = [
    "/etc",
    "/your/custom/path",  # 添加这里
]

# 添加 /root 下的敏感目录
ROOT_BLOCKED_PATTERNS = [
    "/.ssh",
    "/.your_sensitive_dir",  # 添加这里
]

# 添加敏感文件关键词
BLOCKED_FILE_PATTERNS = [
    "passwd",
    "your_pattern",  # 添加这里
]
```

### 移除某个限制（不推荐）

⚠️ **警告**: 移除限制可能导致安全漏洞！

如果确实需要，可以从对应列表中删除相应项：

```python
# 示例：允许访问 /tmp（不推荐）
BLOCKED_PATH_PREFIXES = [
    "/etc",
    "/home",
    # "/tmp",  # 注释掉这行
]
```

### 修改后重启服务

```bash
python3 manage.py stop
python3 manage.py start
```

---

## 🧪 测试规则

使用测试脚本验证规则：

```bash
python3 test_security.py
```

或手动测试：

```python
from server.path_validator import validate_path_access, PathValidationError

# 测试路径
try:
    validate_path_access("/etc/passwd", allow_custom=True)
    print("允许访问")
except PathValidationError as e:
    print(f"禁止访问: {e}")
```

---

## 📊 规则优先级

路径验证按以下顺序执行：

1. **路径规范化** - 转换为绝对路径
2. **敏感关键词检查** - 检查文件名是否包含敏感词
3. **项目路径检查** - 判断是否在项目目录内
4. **系统目录检查** - 如果在项目外，检查系统目录黑名单
5. **/root 子目录检查** - 检查 /root 下的敏感子目录

**示例流程**:
```
/root/project/file-transfer/data/test.txt
  ↓ 规范化
/root/project/file-transfer/data/test.txt
  ↓ 检查关键词 "test.txt"
✓ 不包含敏感关键词
  ↓ 检查是否在项目内
✓ 在项目目录内
  ↓ 结果
✅ 允许访问
```

```
/root/.ssh/id_rsa
  ↓ 规范化
/root/.ssh/id_rsa
  ↓ 检查关键词 ".ssh"
❌ 包含敏感关键词 ".ssh"
  ↓ 结果
❌ 禁止访问: Access denied: path contains sensitive pattern '.ssh'
```

---

## 🔒 安全建议

1. **不要修改默认规则**，除非你完全理解安全影响
2. **定期审查分享链接**，检查是否有敏感文件被意外分享
3. **使用专用目录**存放需要分享的文件（如 `data/downloads/`）
4. **避免使用敏感关键词**命名文件
5. **定期更新密码**，即使文件访问受限

---

## ❓ 常见问题

### Q: 为什么 /root 可以访问但 /root/.ssh 不行？
A: 允许浏览 /root 是为了方便导航到项目目录，但 `.ssh` 等敏感子目录包含密钥，必须阻止。

### Q: 我的文件名包含 "password" 能分享吗？
A: 不能。系统会检查文件名中的 "passwd" 关键词（password 包含 passwd）并阻止访问。

### Q: 能否临时允许访问某个被阻止的路径？
A: 可以编辑 `server/path_validator.py` 移除相应规则，但**强烈不推荐**。更好的做法是将文件复制到允许的目录。

### Q: 项目内创建 .ssh 目录会怎样？
A: 即使在项目内，包含 `.ssh` 的路径也会被阻止。这是额外的安全保护。

### Q: 如何查看当前有哪些文件被阻止？
A: 在 Web 界面尝试访问时，会显示 "Access denied" 错误。或运行 `test_security.py` 查看规则测试结果。

---

## 📞 支持

如有疑问或需要自定义规则，请：
1. 查看 `server/path_validator.py` 源代码
2. 运行 `python3 test_security.py` 测试
3. 查看 `SECURITY_FIXES.md` 了解安全修复详情

---

**最后更新**: 2025-10-04
**版本**: 1.0
