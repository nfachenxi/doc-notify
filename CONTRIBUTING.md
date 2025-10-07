# 贡献指南

感谢您对 Doc Notify 项目的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 报告 Bug

如果您发现了 bug，请：

1. 在 [Issues](https://github.com/nfachenxi/doc-notify/issues) 中搜索是否已有相关问题
2. 如果没有，创建一个新的 Issue，包含：
   - 清晰的标题
   - 详细的问题描述
   - 复现步骤
   - 期望行为
   - 实际行为
   - 环境信息（操作系统、Python 版本等）
   - 相关日志或截图

### 提出新功能

如果您有新功能建议：

1. 先在 Issues 中讨论您的想法
2. 说明功能的用途和价值
3. 如果可能，提供实现思路

### 提交代码

1. **Fork 仓库**

```bash
git clone https://github.com/nfachenxi/doc-notify.git
cd doc-notify
```

2. **创建分支**

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

3. **进行开发**

- 遵循现有的代码风格
- 添加必要的注释
- 更新相关文档

4. **测试**

```bash
# 运行测试
python test_webhook.py https://webhook-test.com/notify 测试文档

# 本地测试
python app.py
curl http://127.0.0.1:5000/health
```

5. **提交更改**

```bash
git add .
git commit -m "feat: 添加新功能描述"
# 或
git commit -m "fix: 修复bug描述"
```

提交信息格式：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具变动

6. **推送分支**

```bash
git push origin feature/your-feature-name
```

7. **创建 Pull Request**

- 在 GitHub 上创建 Pull Request
- 填写清晰的 PR 描述
- 关联相关的 Issue（如有）
- 等待 Review

## 代码规范

### Python 代码风格

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 使用 4 个空格缩进
- 函数和类添加 docstring
- 变量命名使用有意义的名称

示例：

```python
def send_webhook(webhook_url, doc_name, ip_address):
    """发送 webhook 通知
    
    Args:
        webhook_url (str): Webhook 地址
        doc_name (str): 文档名称
        ip_address (str): 访问者 IP
        
    Returns:
        bool: 发送是否成功
    """
    try:
        # 实现代码
        pass
    except Exception as e:
        logger.error(f"发送失败: {str(e)}")
        return False
```

### 配置文件

- YAML 文件使用 2 个空格缩进
- 添加清晰的注释说明

### 文档规范

- 使用 Markdown 格式
- 中文文档使用简体中文
- 添加必要的示例代码
- 保持文档更新

## 开发环境设置

### 本地开发

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py
```

### 调试

在 `app.py` 中启用调试模式：

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

## 文档贡献

文档同样重要！您可以：

- 修正拼写错误
- 改进表述
- 添加示例
- 翻译文档

## 社区准则

请遵守以下准则：

- 保持友善和尊重
- 接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表现同理心

## 许可证

通过贡献代码，您同意您的贡献将在 MIT 许可证下发布。

## 需要帮助？

如有任何问题，可以：

- 查看现有的 [Issues](https://github.com/nfachenxi/doc-notify/issues)
- 查看 [文档](docs/)
- 提交新的 Issue

感谢您的贡献！🎉
