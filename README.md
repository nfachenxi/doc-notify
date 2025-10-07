# 📄 Doc Notify - 文档更新通知服务

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)

一个轻量级的文档更新通知服务，当用户点击特定链接时自动发送 webhook 通知。

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [部署指南](#-部署指南) • [配置说明](#️-配置说明) • [API 文档](#-api-文档)

</div>

---

## 🎯 应用场景

适用于团队协作文档更新通知，例如：

- ✅ 在腾讯文档中插入链接，点击后通知相关人员
- ✅ 在飞书文档中分享链接，触发团队通知
- ✅ 在任何文档系统中创建通知触发器

## ✨ 功能特性

### 🔔 核心功能
- **智能通知**: 点击链接即发送 webhook 通知
- **中文检测**: 自动过滤扫描器，只处理包含中文的路径
- **防刷机制**: 同一 IP 在指定时间内不重复通知
- **自定义配置**: 灵活的文档与 webhook 映射

### 🛡️ 安全防护
- **黑名单过滤**: 自动拦截常见的扫描路径
- **扩展名检测**: 过滤 `.php`、`.asp` 等扫描文件
- **特殊字符检测**: 识别并拦截可疑路径
- **IP 记录**: 记录所有访问者 IP

### 🎨 用户体验
- **美观界面**: 现代化的响应式 Web UI
- **友好反馈**: 清晰的操作结果提示
- **实时日志**: 完整的访问和错误日志

## 🚀 快速开始

### 环境要求

- Python 3.7+
- Debian/Ubuntu 服务器（推荐）
- 域名（可选，用于 HTTPS）

### 安装步骤

1. **克隆项目**

```bash
git clone https://github.com/nfachenxi/doc-notify.git
cd doc-notify
```

2. **配置文件**

编辑 `config.yaml`：

```yaml
# 开启中文检测（推荐）
chinese_only: true

# 配置 webhook
webhooks:
  "产品需求文档": "https://your-webhook-url.com/notify"
  "技术方案": "https://your-webhook-url.com/notify"
```

3. **一键部署**

```bash
sudo bash deploy.sh
```

4. **验证安装**

```bash
curl http://127.0.0.1:5000/health
```

## 📖 使用方法

### 1. 配置 Webhook

在 `config.yaml` 中添加文档与 webhook 的映射：

```yaml
webhooks:
  "产品需求文档": "https://your-webhook-url.com/notify"
```

### 2. 创建链接

在腾讯文档或其他平台插入链接：

```
https://your-domain.com/产品需求文档
```

### 3. 点击触发

当有人点击链接时，系统会：
- 识别文档名称
- 发送 POST 请求到配置的 webhook
- 返回友好的通知页面

### 4. Webhook 数据格式

接收端会收到以下 JSON 数据：

```json
{
  "doc_name": "产品需求文档",
  "access_time": "2025-10-07 14:30:00",
  "ip_address": "192.168.1.100"
}
```

## 🔧 部署指南

### Debian/Ubuntu 服务器

使用提供的自动化部署脚本：

```bash
# 1. 上传项目到服务器
cd /opt
git clone https://github.com/nfachenxi/doc-notify.git
cd doc-notify

# 2. 运行部署脚本
sudo bash deploy.sh

# 3. 配置反向代理（使用 1Panel 或 Nginx）
```

### 使用 1Panel 面板

1. 创建反向代理网站
2. 域名：`notice.your-domain.com`
3. 代理地址：`http://127.0.0.1:5000`
4. 启用 HTTPS（推荐使用 Let's Encrypt）

### 使用 Nginx

```bash
# 复制配置文件
sudo cp nginx.conf /etc/nginx/sites-available/doc-notify
sudo ln -s /etc/nginx/sites-available/doc-notify /etc/nginx/sites-enabled/

# 修改域名
sudo nano /etc/nginx/sites-available/doc-notify

# 重启 Nginx
sudo nginx -t
sudo systemctl restart nginx
```

## ⚙️ 配置说明

### config.yaml

```yaml
# 全局配置
enable_rate_limit: true    # 启用防刷机制
rate_limit_seconds: 60     # 防刷间隔（秒）
chinese_only: true         # 只允许包含中文的路径

# 默认 webhook
default_webhook: https://your-default-webhook.com/notify

# 黑名单（可选）
blocked_paths:
  - "sitemap.xml"
  - "robots.txt"
  - "admin"

# 文档映射
webhooks:
  "产品需求文档": "https://webhook1.com/notify"
  "技术方案": "https://webhook2.com/notify"
```

### 配置项说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `enable_rate_limit` | boolean | true | 是否启用防刷机制 |
| `rate_limit_seconds` | int | 60 | 同一IP的通知间隔（秒） |
| `chinese_only` | boolean | false | 是否只允许包含中文的路径 |
| `default_webhook` | string | null | 默认 webhook 地址 |
| `blocked_paths` | array | [] | 自定义黑名单路径 |
| `webhooks` | object | {} | 文档与 webhook 的映射 |

## 📡 API 文档

### 健康检查

```bash
GET /health
```

**响应**：
```json
{
  "status": "healthy",
  "timestamp": "2025-10-07T14:30:00"
}
```

### 访问统计

```bash
GET /api/stats
```

**响应**：
```json
{
  "status": "success",
  "total_visits": 123,
  "active_rate_limits": 5
}
```

### 文档通知

```bash
GET /{doc_name}
```

**参数**：
- `doc_name`: 文档名称（支持中文）

**行为**：
1. 检查路径是否合法
2. 查找对应的 webhook
3. 发送 POST 请求
4. 返回结果页面

## 🛠️ 服务管理

### 查看状态

```bash
sudo systemctl status doc-notify
```

### 启动/停止/重启

```bash
sudo systemctl start doc-notify
sudo systemctl stop doc-notify
sudo systemctl restart doc-notify
```

### 查看日志

```bash
# 应用日志
tail -f logs/app.log

# 系统日志
sudo journalctl -u doc-notify -f
```

## 🔒 安全建议

1. **使用 HTTPS**: 配置 SSL 证书保护数据传输
2. **IP 白名单**: 在 Nginx 中配置允许的 IP 范围
3. **定期更新**: 及时更新依赖包修复安全漏洞
4. **监控日志**: 定期检查异常访问

## 🧪 测试工具

### 测试 Webhook

```bash
python test_webhook.py <webhook_url> [文档名称]
```

**示例**：
```bash
python test_webhook.py https://your-webhook.com/notify 产品需求文档
```

### 本地测试

```bash
# 测试健康检查
curl http://127.0.0.1:5000/health

# 测试文档路由
curl http://127.0.0.1:5000/测试文档

# 测试扫描过滤
curl http://127.0.0.1:5000/admin  # 应该返回 404
```

## 📊 工作原理

```
用户点击链接
    ↓
https://notice.your-domain.com/产品需求文档
    ↓
Nginx/1Panel 反向代理
    ↓
Flask 应用 (Port 5000)
    ↓
1. 中文检测 ✓
2. 黑名单过滤 ✓
3. 防刷检查 ✓
    ↓
发送 POST 到 Webhook
    ↓
{
  "doc_name": "产品需求文档",
  "access_time": "2025-10-07 14:30:00",
  "ip_address": "192.168.1.100"
}
    ↓
返回友好页面
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 开源协议

本项目采用 [MIT](LICENSE) 协议开源。

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [Gunicorn](https://gunicorn.org/) - WSGI HTTP 服务器
- [PyYAML](https://pyyaml.org/) - YAML 解析器

## 📮 联系方式

- 提交 Issue: [GitHub Issues](https://github.com/nfachenxi/doc-notify/issues)
- 邮箱: your-email@example.com

## ⭐ Star History

如果这个项目对您有帮助，请给它一个 Star ⭐

---

<div align="center">
Made with ❤️ by Your Name
</div>