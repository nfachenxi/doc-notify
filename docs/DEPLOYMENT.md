# 部署指南

本文档详细说明如何在生产环境中部署 Doc Notify 服务。

## 📋 目录

- [系统要求](#系统要求)
- [快速部署](#快速部署)
- [详细步骤](#详细步骤)
- [反向代理配置](#反向代理配置)
- [SSL/HTTPS 配置](#sslhttps-配置)
- [服务管理](#服务管理)
- [故障排查](#故障排查)

## 系统要求

### 硬件要求
- CPU: 1 核心以上
- 内存: 512MB 以上
- 磁盘: 1GB 以上可用空间

### 软件要求
- 操作系统: Debian 10+ / Ubuntu 18.04+
- Python: 3.7+
- 权限: root 或 sudo 权限

## 快速部署

### 一键部署（推荐）

```bash
# 1. 克隆项目
cd /opt
git clone https://github.com/nfachenxi/doc-notify.git
cd doc-notify

# 2. 编辑配置文件
nano config.yaml

# 3. 运行部署脚本
sudo bash deploy.sh
```

部署脚本会自动完成：
- ✅ 检查并安装 Python 环境
- ✅ 创建虚拟环境
- ✅ 安装依赖包
- ✅ 配置 systemd 服务
- ✅ 启动服务

## 详细步骤

### 1. 安装 Python 环境

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 验证安装
python3 --version
```

### 2. 创建虚拟环境

```bash
cd /opt/doc-notify
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 配置文件

编辑 `config.yaml`：

```yaml
# 全局配置
enable_rate_limit: true
rate_limit_seconds: 60
chinese_only: true

# 默认 webhook
default_webhook: "https://your-webhook-url.com/notify"

# 文档映射
webhooks:
  "产品需求文档": "https://your-webhook-url.com/notify"
```

### 5. 创建 systemd 服务

创建服务文件 `/etc/systemd/system/doc-notify.service`：

```ini
[Unit]
Description=Document Update Notification Service
After=network.target

[Service]
Type=notify
User=your-username
WorkingDirectory=/opt/doc-notify
Environment="PATH=/opt/doc-notify/venv/bin"
ExecStart=/opt/doc-notify/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 6. 启动服务

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start doc-notify

# 设置开机自启
sudo systemctl enable doc-notify

# 查看状态
sudo systemctl status doc-notify
```

## 反向代理配置

### 使用 1Panel（推荐）

1. 登录 1Panel 管理面板
2. 进入 **网站** 模块
3. 点击 **创建网站** → **反向代理**
4. 填写以下信息：
   - 网站名称: `doc-notify`
   - 主域名: `notice.your-domain.com`
   - 代理地址: `http://127.0.0.1:5000`
5. 高级配置中添加：

```nginx
# 传递真实 IP
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header Host $host;

# 支持中文
charset utf-8;
```

### 使用 Nginx

1. **安装 Nginx**

```bash
sudo apt install nginx
```

2. **复制配置文件**

```bash
sudo cp nginx.conf /etc/nginx/sites-available/doc-notify
sudo ln -s /etc/nginx/sites-available/doc-notify /etc/nginx/sites-enabled/
```

3. **修改域名**

```bash
sudo nano /etc/nginx/sites-available/doc-notify
# 将 notice.nfasystem.top 改为您的域名
```

4. **测试并重启**

```bash
sudo nginx -t
sudo systemctl restart nginx
```

## SSL/HTTPS 配置

### 使用 1Panel

1. 在网站配置中找到 **SSL** 选项
2. 选择 **Let's Encrypt**
3. 输入邮箱地址
4. 点击 **申请证书**
5. 启用 **强制 HTTPS**

### 使用 Certbot

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 申请证书
sudo certbot --nginx -d notice.your-domain.com

# 自动续期（已自动配置）
sudo certbot renew --dry-run
```

## 服务管理

### 常用命令

```bash
# 查看状态
sudo systemctl status doc-notify

# 启动服务
sudo systemctl start doc-notify

# 停止服务
sudo systemctl stop doc-notify

# 重启服务
sudo systemctl restart doc-notify

# 重新加载配置
sudo systemctl reload doc-notify

# 查看日志
sudo journalctl -u doc-notify -f
```

### 查看应用日志

```bash
# 实时查看
tail -f /opt/doc-notify/logs/app.log

# 查看最近 100 行
tail -100 /opt/doc-notify/logs/app.log

# 搜索错误
grep "ERROR" /opt/doc-notify/logs/app.log
```

## 性能优化

### Gunicorn 配置

编辑 systemd 服务文件，调整 worker 数量：

```bash
# CPU 核心数 * 2 + 1
# 例如 2 核 CPU: -w 5
ExecStart=/opt/doc-notify/venv/bin/gunicorn -w 5 -b 0.0.0.0:5000 app:app
```

### 日志轮转

创建日志轮转配置：

```bash
sudo nano /etc/logrotate.d/doc-notify
```

添加：

```
/opt/doc-notify/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 your-username your-username
}
```

## 安全加固

### 1. 防火墙配置

```bash
# 使用 ufw
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. 限流配置

在 Nginx 中添加：

```nginx
# 限制请求频率
limit_req_zone $binary_remote_addr zone=doc_limit:10m rate=10r/s;

location / {
    limit_req zone=doc_limit burst=20 nodelay;
    proxy_pass http://127.0.0.1:5000;
}
```

### 3. IP 白名单（可选）

```nginx
# 只允许特定 IP 访问
location / {
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    
    proxy_pass http://127.0.0.1:5000;
}
```

## 监控和维护

### 健康检查

```bash
# 本地检查
curl http://127.0.0.1:5000/health

# 域名检查
curl https://notice.your-domain.com/health
```

### 监控脚本

创建监控脚本 `/opt/doc-notify/monitor.sh`：

```bash
#!/bin/bash
if ! curl -f http://127.0.0.1:5000/health > /dev/null 2>&1; then
    echo "Service is down, restarting..."
    systemctl restart doc-notify
    echo "Service restarted at $(date)" >> /var/log/doc-notify-monitor.log
fi
```

添加到 crontab：

```bash
# 每 5 分钟检查一次
*/5 * * * * /opt/doc-notify/monitor.sh
```

## 故障排查

### 问题 1: 服务无法启动

**检查**：
```bash
# 查看详细错误
sudo journalctl -u doc-notify -n 50

# 检查端口占用
sudo netstat -tlnp | grep 5000

# 手动运行测试
cd /opt/doc-notify
source venv/bin/activate
python app.py
```

### 问题 2: 502 Bad Gateway

**原因**: 后端服务未运行

**解决**：
```bash
sudo systemctl status doc-notify
sudo systemctl restart doc-notify
```

### 问题 3: 无法访问（防火墙）

**检查**：
```bash
# 检查防火墙状态
sudo ufw status

# 开放端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### 问题 4: SSL 证书错误

**检查**：
```bash
# 测试证书
sudo certbot certificates

# 手动续期
sudo certbot renew
```

## 备份和恢复

### 备份

```bash
# 备份配置和代码
tar -czf doc-notify-backup-$(date +%Y%m%d).tar.gz \
    /opt/doc-notify/config.yaml \
    /opt/doc-notify/app.py

# 备份到远程
scp doc-notify-backup-*.tar.gz user@backup-server:/backups/
```

### 恢复

```bash
# 解压备份
tar -xzf doc-notify-backup-20251007.tar.gz

# 恢复配置
cp config.yaml /opt/doc-notify/

# 重启服务
sudo systemctl restart doc-notify
```

## 升级指南

### 从 GitHub 更新

```bash
cd /opt/doc-notify

# 备份配置
cp config.yaml config.yaml.backup

# 拉取更新
git pull

# 恢复配置
cp config.yaml.backup config.yaml

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 重启服务
sudo systemctl restart doc-notify
```

## 完成检查清单

部署完成后，请检查：

- [ ] 服务正常运行: `systemctl status doc-notify`
- [ ] 健康检查通过: `curl http://127.0.0.1:5000/health`
- [ ] 反向代理配置正确
- [ ] SSL 证书已配置
- [ ] 强制 HTTPS 已启用
- [ ] 防火墙规则已设置
- [ ] 日志轮转已配置
- [ ] 监控脚本已部署
- [ ] 配置文件已备份

---

**部署完成！** 🎉

如有问题，请参考 [故障排查](#故障排查) 章节或提交 [Issue](https://github.com/nfachenxi/doc-notify/issues)。
