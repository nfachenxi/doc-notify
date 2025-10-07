# API 文档

Doc Notify 提供的 HTTP API 接口说明。

## 基础信息

- **基础 URL**: `https://your-domain.com`
- **数据格式**: JSON
- **字符编码**: UTF-8

## 接口列表

### 1. 健康检查

检查服务是否正常运行。

**请求**

```http
GET /health
```

**响应**

```json
{
  "status": "healthy",
  "timestamp": "2025-10-07T14:30:00.123456"
}
```

**状态码**
- `200`: 服务正常

**示例**

```bash
curl https://your-domain.com/health
```

---

### 2. 访问统计

获取服务的访问统计信息。

**请求**

```http
GET /api/stats
```

**响应**

```json
{
  "status": "success",
  "total_visits": 123,
  "active_rate_limits": 5
}
```

**字段说明**
- `status`: 状态（success/error）
- `total_visits`: 总访问次数
- `active_rate_limits`: 当前活跃的防刷限制数量

**状态码**
- `200`: 请求成功
- `500`: 内部错误

**示例**

```bash
curl https://your-domain.com/api/stats
```

---

### 3. 文档通知触发

触发文档更新通知。

**请求**

```http
GET /{doc_name}
```

**路径参数**
- `doc_name`: 文档名称（支持中文、URL 编码）

**请求头**
- `X-Forwarded-For`: 客户端真实 IP（由反向代理传递）

**行为流程**

1. **安全检查**
   - 黑名单过滤
   - 文件扩展名检测
   - 特殊字符检测
   - 中文字符检测（如果启用）

2. **配置查找**
   - 查找文档对应的 webhook
   - 如果未配置，使用 default_webhook

3. **防刷检查**
   - 检查同一 IP 的访问频率
   - 在限定时间内不重复通知

4. **发送 Webhook**
   - 构造 POST 数据
   - 发送到配置的 webhook 地址

5. **返回结果**
   - 渲染成功/失败页面

**Webhook POST 数据格式**

```json
{
  "doc_name": "产品需求文档",
  "access_time": "2025-10-07 14:30:00",
  "ip_address": "192.168.1.100"
}
```

**响应**

成功时返回 HTML 页面：

```html
<!DOCTYPE html>
<html>
  <!-- 友好的通知成功页面 -->
</html>
```

失败场景：

- **404 Not Found**: 路径被过滤（扫描路径、非中文路径等）
- **200 OK**: 显示未配置 webhook 或防刷限制的提示页面

**示例**

```bash
# 中文路径（自动 URL 编码）
curl https://your-domain.com/产品需求文档

# 已编码的路径
curl https://your-domain.com/%E4%BA%A7%E5%93%81%E9%9C%80%E6%B1%82%E6%96%87%E6%A1%A3
```

---

### 4. 首页

显示服务介绍页面。

**请求**

```http
GET /
```

**响应**

返回 HTML 首页，包含：
- 服务介绍
- 使用方法
- 配置说明

**状态码**
- `200`: 成功

---

## 错误响应

### 格式

```json
{
  "status": "error",
  "message": "错误描述"
}
```

### 常见错误

#### 404 Not Found

**原因**：
- 访问了被过滤的路径
- 纯英文路径（启用中文检测时）
- 黑名单中的路径

**示例**：
```bash
curl https://your-domain.com/admin
# 返回: 404（空响应）
```

#### 500 Internal Server Error

**原因**：
- 服务内部错误
- 配置文件错误
- Webhook 发送失败

**响应**：
```html
Internal Server Error
The server encountered an internal error...
```

## Webhook 集成

### 发送格式

Doc Notify 会向配置的 webhook 地址发送 POST 请求：

**请求头**
```
Content-Type: application/json
```

**请求体**
```json
{
  "doc_name": "文档名称",
  "access_time": "2025-10-07 14:30:00",
  "ip_address": "192.168.1.100"
}
```

### 接收端示例

#### Python (Flask)

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json()
    doc_name = data.get('doc_name')
    access_time = data.get('access_time')
    ip_address = data.get('ip_address')
    
    # 处理通知
    print(f"文档 {doc_name} 被访问")
    
    return jsonify({"status": "success"}), 200
```

#### Node.js (Express)

```javascript
const express = require('express');
const app = express();

app.use(express.json());

app.post('/notify', (req, res) => {
    const { doc_name, access_time, ip_address } = req.body;
    
    // 处理通知
    console.log(`文档 ${doc_name} 被访问`);
    
    res.json({ status: 'success' });
});

app.listen(8080);
```

#### PHP

```php
<?php
$data = json_decode(file_get_contents('php://input'), true);

$docName = $data['doc_name'] ?? '';
$accessTime = $data['access_time'] ?? '';
$ipAddress = $data['ip_address'] ?? '';

// 处理通知
error_log("文档 {$docName} 被访问");

echo json_encode(['status' => 'success']);
?>
```

## 请求限制

### 防刷机制

- **默认间隔**: 60 秒
- **规则**: 同一 IP 对同一文档在指定时间内只通知一次
- **配置**: `config.yaml` 中的 `rate_limit_seconds`

### 黑名单过滤

以下路径会被自动拒绝（返回 404）：

- `sitemap.xml`
- `robots.txt`
- `admin`
- `login`
- `wp-admin`
- `.env`
- `.git`
- 更多...（参见 `config.yaml`）

### 中文检测

当 `chinese_only: true` 时：
- ✅ 包含中文字符的路径：允许
- ❌ 纯英文/数字路径：拒绝（404）

## 客户端集成

### JavaScript

```javascript
// 触发通知
fetch('https://your-domain.com/产品需求文档')
  .then(response => response.text())
  .then(html => {
    // 处理响应
    console.log('通知已发送');
  });
```

### Python

```python
import requests

# 触发通知
response = requests.get('https://your-domain.com/产品需求文档')
print(f"状态码: {response.status_code}")
```

### cURL

```bash
# 基本请求
curl https://your-domain.com/产品需求文档

# 查看响应头
curl -I https://your-domain.com/产品需求文档

# 跟随重定向
curl -L https://your-domain.com/产品需求文档
```

## 监控和调试

### 查看请求日志

```bash
tail -f /opt/doc-notify/logs/app.log
```

### 测试接口

```bash
# 健康检查
curl https://your-domain.com/health

# 统计信息
curl https://your-domain.com/api/stats

# 触发通知
curl https://your-domain.com/测试文档
```

### 调试模式

在开发环境中启用调试：

```python
# app.py
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

## 版本历史

- **v1.2.0**: 添加中文检测功能
- **v1.1.0**: 添加防扫描机制
- **v1.0.0**: 初始版本

---

**需要帮助？** 请查看 [部署指南](DEPLOYMENT.md) 或提交 [Issue](https://github.com/nfachenxi/doc-notify/issues)。
