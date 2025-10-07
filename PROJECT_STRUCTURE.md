# 项目结构

Doc Notify 项目的文件组织说明。

## 目录结构

```
doc-notify/
├── app.py                  # Flask 主应用程序
├── config.yaml             # 配置文件（示例）
├── requirements.txt        # Python 依赖包
├── deploy.sh               # 一键部署脚本
├── nginx.conf              # Nginx 配置示例
├── test_webhook.py         # Webhook 测试工具
│
├── docs/                   # 文档目录
│   ├── API.md             # API 接口文档
│   ├── DEPLOYMENT.md      # 部署指南
│   └── SECURITY.md        # 安全策略
│
├── README.md              # 项目说明
├── LICENSE                # MIT 开源协议
├── CHANGELOG.md           # 更新日志
├── CONTRIBUTING.md        # 贡献指南
├── .gitignore             # Git 忽略文件
└── PROJECT_STRUCTURE.md   # 本文件
```

## 核心文件说明

### 应用核心

#### `app.py`
- **作用**: Flask Web 应用主程序
- **功能**:
  - HTTP 路由处理
  - Webhook 发送
  - 安全防护（黑名单、中文检测、防刷）
  - 日志记录
- **依赖**: Flask, requests, PyYAML

#### `config.yaml`
- **作用**: 服务配置文件
- **内容**:
  - 全局配置（防刷、中文检测）
  - Webhook 映射
  - 黑名单配置
- **注意**: 包含敏感信息，部署时需修改

#### `requirements.txt`
- **作用**: Python 依赖包清单
- **包含**:
  - Flask 3.0.0
  - requests 2.31.0
  - PyYAML 6.0.1
  - gunicorn 21.2.0

### 部署文件

#### `deploy.sh`
- **作用**: 自动化部署脚本
- **功能**:
  - 环境检查
  - 虚拟环境创建
  - 依赖安装
  - systemd 服务配置
  - 服务启动
- **用法**: `sudo bash deploy.sh`

#### `nginx.conf`
- **作用**: Nginx 反向代理配置示例
- **功能**:
  - HTTP/HTTPS 配置
  - 反向代理设置
  - SSL 证书配置
  - 性能优化

### 工具文件

#### `test_webhook.py`
- **作用**: Webhook 测试工具
- **功能**:
  - 发送测试 POST 请求
  - 验证 webhook 配置
  - 调试通知功能
- **用法**: `python test_webhook.py <url> [文档名]`

### 文档目录

#### `docs/API.md`
- **内容**: API 接口详细说明
- **包含**:
  - 所有 HTTP 接口
  - 请求/响应格式
  - Webhook 集成指南
  - 客户端示例代码

#### `docs/DEPLOYMENT.md`
- **内容**: 完整部署指南
- **包含**:
  - 系统要求
  - 详细部署步骤
  - 反向代理配置
  - SSL/HTTPS 设置
  - 故障排查

#### `docs/SECURITY.md`
- **内容**: 安全策略和最佳实践
- **包含**:
  - 安全漏洞报告流程
  - 安全加固建议
  - 威胁防护措施
  - 应急响应指南

### 元文件

#### `README.md`
- **作用**: 项目主文档
- **内容**:
  - 项目介绍
  - 快速开始
  - 功能特性
  - 使用方法
  - 配置说明

#### `LICENSE`
- **作用**: 开源许可证
- **类型**: MIT License
- **说明**: 允许自由使用、修改和分发

#### `CHANGELOG.md`
- **作用**: 版本更新日志
- **内容**:
  - 版本历史
  - 功能变更
  - Bug 修复
  - 重大更新

#### `CONTRIBUTING.md`
- **作用**: 贡献指南
- **内容**:
  - 如何报告 Bug
  - 如何提交代码
  - 代码规范
  - 开发流程

#### `.gitignore`
- **作用**: Git 忽略规则
- **忽略**:
  - Python 缓存文件
  - 虚拟环境
  - 日志文件
  - IDE 配置

## 运行时生成的目录

以下目录和文件在运行时自动生成，不包含在仓库中：

```
doc-notify/
├── venv/                  # Python 虚拟环境
├── logs/                  # 日志目录
│   ├── app.log           # 应用日志
│   ├── access.log        # 访问日志
│   └── error.log         # 错误日志
└── __pycache__/          # Python 缓存
```

## 文件关系图

```
用户请求
    ↓
nginx.conf (反向代理)
    ↓
app.py (Flask 应用)
    ↓
config.yaml (读取配置)
    ↓
发送到 Webhook
    ↓
记录到 logs/
```

## 开发工作流

### 本地开发

1. 克隆仓库
2. 创建虚拟环境
3. 安装依赖
4. 修改代码
5. 本地测试
6. 提交代码

### 部署流程

1. 推送到 GitHub
2. 服务器拉取更新
3. 运行 `deploy.sh`
4. 重启服务
5. 验证功能

## 配置管理

### 开发环境

```yaml
# config.yaml (开发)
chinese_only: false
default_webhook: "http://localhost:8080/test"
```

### 生产环境

```yaml
# config.yaml (生产)
chinese_only: true
default_webhook: "https://your-webhook.com/notify"
```

## 依赖关系

### 核心依赖

- **Flask**: Web 框架
- **requests**: HTTP 请求库
- **PyYAML**: YAML 解析器
- **gunicorn**: WSGI 服务器

### 系统依赖

- **Python 3.7+**: 运行环境
- **systemd**: 服务管理
- **Nginx**: 反向代理（可选）

## 版本控制

### 分支策略

- `main`: 稳定版本
- `develop`: 开发分支
- `feature/*`: 新功能分支
- `fix/*`: Bug 修复分支

### 标签规范

- `v1.0.0`: 主版本
- `v1.1.0`: 次版本
- `v1.0.1`: 补丁版本

## 部署环境

### 目标路径

- 推荐: `/opt/doc-notify`
- 备选: `/var/www/doc-notify`
- 自定义: 任意路径

### 服务名称

- systemd 服务: `doc-notify`
- 进程名: `gunicorn`
- 监听端口: `5000`

## 维护说明

### 日志管理

- 位置: `logs/`
- 轮转: 每天
- 保留: 7 天
- 压缩: gzip

### 备份策略

需要备份的文件：
- `config.yaml` (配置)
- `logs/*.log` (日志，可选)

不需要备份：
- `app.py` (在 Git 中)
- `venv/` (可重建)

### 更新流程

1. 备份配置
2. 拉取最新代码
3. 更新依赖
4. 重启服务
5. 验证功能

## 文件大小参考

```
app.py           ~15 KB
config.yaml      ~2 KB
requirements.txt ~100 B
deploy.sh        ~5 KB
README.md        ~10 KB
```

## 授权和许可

所有文件遵循 MIT License，详见 `LICENSE` 文件。

---

**最后更新**: 2025-10-07
