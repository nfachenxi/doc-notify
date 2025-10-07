# 安全策略

## 支持的版本

当前支持的版本及其安全更新状态：

| 版本 | 支持状态 |
| ---- | -------- |
| 1.2.x | ✅ 支持 |
| 1.1.x | ✅ 支持 |
| 1.0.x | ⚠️ 有限支持 |
| < 1.0 | ❌ 不支持 |

## 报告安全漏洞

如果您发现了安全漏洞，请**不要**通过公开的 Issue 报告。

### 报告方式

1. **邮件报告**（推荐）
   - 发送至: security@your-domain.com
   - 主题: [SECURITY] 简要描述
   - 内容包括:
     - 漏洞详细描述
     - 复现步骤
     - 影响范围
     - 可能的修复方案

2. **私密 Issue**
   - 联系维护者获取私密报告渠道

### 响应时间

- **24 小时内**: 确认收到报告
- **48 小时内**: 初步评估
- **7 天内**: 提供修复方案或补丁
- **14 天内**: 发布安全更新

## 安全最佳实践

### 1. 部署安全

#### 使用 HTTPS
```nginx
# 强制 HTTPS
server {
    listen 80;
    server_name notice.your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

#### 配置防火墙
```bash
# 只开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### 限制访问
```nginx
# IP 白名单
location / {
    allow 192.168.1.0/24;  # 内网
    deny all;
    proxy_pass http://127.0.0.1:5000;
}
```

### 2. 配置安全

#### 保护敏感信息
```yaml
# config.yaml 不要提交到公开仓库
# 使用环境变量存储敏感信息
```

```bash
# 设置文件权限
chmod 600 config.yaml
chown your-user:your-user config.yaml
```

#### 定期更新密钥
- 定期更换 webhook URL 中的 token
- 使用强随机字符串

### 3. 防护机制

#### 启用所有防护功能
```yaml
# config.yaml
enable_rate_limit: true    # 防刷
rate_limit_seconds: 60     # 限制频率
chinese_only: true         # 中文检测
blocked_paths:             # 黑名单
  - "admin"
  - "login"
```

#### 限流配置
```nginx
# Nginx 限流
limit_req_zone $binary_remote_addr zone=doc_limit:10m rate=10r/s;

location / {
    limit_req zone=doc_limit burst=20 nodelay;
    proxy_pass http://127.0.0.1:5000;
}
```

#### 设置超时
```nginx
# 防止慢速攻击
proxy_connect_timeout 10s;
proxy_send_timeout 10s;
proxy_read_timeout 10s;
```

### 4. 日志安全

#### 日志轮转
```bash
# /etc/logrotate.d/doc-notify
/opt/doc-notify/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

#### 敏感信息过滤
- 不记录完整的 webhook URL
- IP 地址脱敏（可选）
- 定期清理旧日志

### 5. 依赖安全

#### 定期更新
```bash
# 检查过期依赖
pip list --outdated

# 更新依赖
pip install -r requirements.txt --upgrade

# 安全审计
pip-audit
```

#### 固定版本
```txt
# requirements.txt
Flask==3.0.0  # 固定版本避免意外更新
requests==2.31.0
PyYAML==6.0.1
gunicorn==21.2.0
```

## 已知安全措施

### 1. 输入验证

- ✅ URL 解码后验证
- ✅ 特殊字符检测
- ✅ 路径遍历防护（`..`、`//`）
- ✅ 文件扩展名过滤

### 2. 防护机制

- ✅ 防刷限制（基于 IP + 文档）
- ✅ 黑名单过滤（30+ 常见攻击路径）
- ✅ 中文检测（过滤扫描器）
- ✅ 请求日志记录

### 3. 网络安全

- ✅ 支持 HTTPS
- ✅ 反向代理支持
- ✅ 真实 IP 传递
- ✅ 请求头验证

## 安全检查清单

### 部署前

- [ ] 修改默认配置
- [ ] 设置强 webhook token
- [ ] 配置 HTTPS
- [ ] 启用防火墙
- [ ] 设置文件权限
- [ ] 启用所有防护功能

### 运行中

- [ ] 定期检查日志
- [ ] 监控异常访问
- [ ] 更新依赖包
- [ ] 备份配置文件
- [ ] 审查访问权限

### 定期维护

- [ ] 更新 SSL 证书
- [ ] 清理旧日志
- [ ] 检查安全更新
- [ ] 审查配置变更
- [ ] 测试恢复流程

## 常见威胁防护

### 1. 路径遍历攻击

**威胁**: `../../../etc/passwd`

**防护**:
```python
# 检测特殊字符
if any(char in doc_name for char in ['..', '//', '\\']):
    return '', 404
```

### 2. SQL 注入

**威胁**: `'; DROP TABLE--`

**防护**: 
- 不使用数据库
- 所有输入仅用于字符串匹配
- 不执行动态 SQL

### 3. XSS 攻击

**威胁**: `<script>alert('xss')</script>`

**防护**:
```python
# Flask 自动转义 HTML
# render_template_string 默认转义
```

### 4. CSRF 攻击

**威胁**: 跨站请求伪造

**防护**:
- GET 请求不改变状态
- 使用 Referer 验证（可选）

### 5. DDoS 攻击

**威胁**: 大量请求导致服务不可用

**防护**:
- Nginx 限流
- 防刷机制
- Fail2ban 自动封禁
- CDN/WAF 防护

### 6. 端口扫描

**威胁**: 扫描开放端口

**防护**:
- 只开放必要端口（80、443）
- 使用防火墙
- 隐藏服务器指纹

### 7. 暴力破解

**威胁**: 尝试常见路径

**防护**:
- 黑名单过滤
- 中文检测
- 限流机制
- 404 响应（不暴露信息）

## 应急响应

### 发现安全事件

1. **立即行动**
   ```bash
   # 停止服务
   sudo systemctl stop doc-notify
   
   # 查看日志
   tail -1000 /opt/doc-notify/logs/app.log
   
   # 检查进程
   ps aux | grep python
   ```

2. **隔离影响**
   - 切断网络连接
   - 备份日志文件
   - 保留现场证据

3. **分析原因**
   - 检查访问日志
   - 分析攻击模式
   - 确定影响范围

4. **修复问题**
   - 应用安全补丁
   - 修改配置
   - 更换凭证

5. **恢复服务**
   ```bash
   # 验证修复
   python app.py  # 测试运行
   
   # 重启服务
   sudo systemctl start doc-notify
   
   # 监控日志
   tail -f /opt/doc-notify/logs/app.log
   ```

### 报告模板

```markdown
## 安全事件报告

**发现时间**: 2025-10-07 14:30:00
**影响范围**: 
**威胁类型**: 
**攻击源**: 

### 事件描述
[详细描述]

### 影响评估
[影响分析]

### 应对措施
[已采取的措施]

### 防范建议
[未来防范措施]
```

## 联系方式

- **安全团队**: security@your-domain.com
- **紧急联系**: [电话/即时通讯]
- **GitHub**: [Private Security Advisory](https://github.com/nfachenxi/doc-notify/security/advisories)

## 致谢

感谢以下安全研究人员的贡献：

- [待添加]

---

**最后更新**: 2025-10-07
