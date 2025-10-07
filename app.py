#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档更新通知服务
当用户点击特定链接时，自动发送 webhook 通知
"""

from flask import Flask, request, render_template_string, jsonify
import requests
import json
import yaml
from datetime import datetime
from pathlib import Path
import logging
from urllib.parse import unquote
import time
from collections import defaultdict

app = Flask(__name__)

# 确保日志目录存在
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 防刷机制：记录最近的访问
recent_visits = defaultdict(lambda: defaultdict(float))
RATE_LIMIT_SECONDS = 60  # 同一IP同一文档60秒内只通知一次


def load_config():
    """加载配置文件"""
    default_config = {
        'webhooks': {},
        'default_webhook': None,
        'enable_rate_limit': True,
        'rate_limit_seconds': 60
    }
    
    config_file = Path('config.yaml')
    if not config_file.exists():
        logger.warning("配置文件不存在，使用默认配置")
        return default_config
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # 如果配置文件为空或解析失败，返回默认配置
        if config is None:
            logger.warning("配置文件为空，使用默认配置")
            return default_config
        
        # 确保必要的键存在
        if 'webhooks' not in config:
            config['webhooks'] = {}
        if 'enable_rate_limit' not in config:
            config['enable_rate_limit'] = True
        if 'rate_limit_seconds' not in config:
            config['rate_limit_seconds'] = 60
            
        return config
        
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")
        return default_config


def should_notify(ip, doc_id):
    """检查是否应该发送通知（防刷机制）"""
    config = load_config()
    if not config.get('enable_rate_limit', True):
        return True
    
    rate_limit = config.get('rate_limit_seconds', RATE_LIMIT_SECONDS)
    current_time = time.time()
    last_visit = recent_visits[ip][doc_id]
    
    if current_time - last_visit < rate_limit:
        return False
    
    recent_visits[ip][doc_id] = current_time
    return True


def send_webhook(webhook_url, doc_name, ip_address):
    """发送 webhook 通知 - 简化版本，只发送文档名称等基础参数"""
    try:
        # 获取当前时间
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 构造简单的 POST 数据，由接收端自行处理
        payload = {
            "doc_name": doc_name,
            "access_time": current_time,
            "ip_address": ip_address
        }
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 200:
            logger.info(f"Webhook 发送成功: {doc_name} -> {webhook_url}")
            return True
        else:
            logger.error(f"Webhook 发送失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"发送 webhook 时出错: {str(e)}")
        return False


@app.route('/')
def index():
    """首页"""
    html = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>文档更新通知服务</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 10px;
                padding: 40px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 10px;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 30px;
            }
            .info-box {
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }
            .info-box h3 {
                margin-top: 0;
                color: #667eea;
            }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            .example {
                background: #e8f4f8;
                padding: 15px;
                border-radius: 4px;
                margin: 10px 0;
            }
            .footer {
                text-align: center;
                margin-top: 30px;
                color: #999;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 文档更新通知服务</h1>
            <p class="subtitle">自动化文档更新提醒系统</p>
            
            <div class="info-box">
                <h3>🚀 使用方法</h3>
                <p>在腾讯文档中插入以下格式的超链接：</p>
                <div class="example">
                    <code>https://notice.nfasystem.top/文档名称</code>
                </div>
                <p>当有人点击链接时，系统会自动发送通知到配置的 webhook 地址。</p>
            </div>
            
            <div class="info-box">
                <h3>📝 示例</h3>
                <ul>
                    <li><code>https://notice.nfasystem.top/产品需求文档</code></li>
                    <li><code>https://notice.nfasystem.top/技术方案</code></li>
                    <li><code>https://notice.nfasystem.top/项目进度表</code></li>
                </ul>
            </div>
            
            <div class="info-box">
                <h3>⚙️ 配置</h3>
                <p>请在 <code>config.yaml</code> 中配置文档与 webhook 的映射关系。</p>
            </div>
            
            <div class="footer">
                <p>Powered by Flask | 部署于 Debian 服务器</p>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route('/<path:doc_id>')
def notify(doc_id):
    """处理文档通知请求"""
    # URL 解码，支持中文
    doc_name = unquote(doc_id)
    
    # 获取访问者 IP
    if request.headers.get('X-Forwarded-For'):
        ip_address = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        ip_address = request.remote_addr
    
    # 加载配置（提前加载以获取黑名单）
    config = load_config()
    
    # 黑名单：忽略常见的扫描路径和系统文件
    default_blocked_paths = [
        'sitemap.xml', 'robots.txt', 'favicon.ico',
        'login', 'admin', 'wp-admin', 'wp-login.php',
        'phpmyadmin', '.env', '.git', 'config',
        'api', 'test', 'debug', 'upload',
        '.well-known', 'xmlrpc.php', 'wp-content',
        'administrator', 'manager', 'console',
        'shell', 'cmd', 'sql', 'backup',
        'index.php', 'index.html', 'index.htm',
        'default.asp', 'default.aspx',
    ]
    
    # 合并配置文件中的黑名单
    custom_blocked = config.get('blocked_paths', [])
    blocked_paths = default_blocked_paths + [str(p).lower() for p in custom_blocked]
    
    # 检查是否为扫描路径
    doc_lower = doc_name.lower()
    for blocked in blocked_paths:
        if blocked in doc_lower:
            logger.info(f"忽略扫描请求: {doc_name} from {ip_address}")
            return '', 404  # 返回 404，不显示任何页面
    
    # 检查是否包含常见的文件扩展名（扫描器特征）
    scan_extensions = ['.php', '.asp', '.aspx', '.jsp', '.cgi', '.xml', '.json', '.txt', '.sql', '.zip', '.tar', '.gz']
    if any(doc_lower.endswith(ext) for ext in scan_extensions):
        logger.info(f"忽略文件扫描: {doc_name} from {ip_address}")
        return '', 404
    
    # 检查是否包含特殊字符（可能是攻击尝试）
    if any(char in doc_name for char in ['..', '//', '\\', '<', '>', '|', '&', ';', '`']):
        logger.warning(f"检测到可疑路径: {doc_name} from {ip_address}")
        return '', 404
    
    # 检查是否包含中文字符（只要有一个中文字符即可）
    if config.get('chinese_only', False):
        # 检测常用汉字、扩展汉字、符号等
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in doc_name)  # 常用汉字
        has_chinese = has_chinese or any('\u3400' <= char <= '\u4dbf' for char in doc_name)  # 扩展A
        has_chinese = has_chinese or any('\uf900' <= char <= '\ufaff' for char in doc_name)  # 兼容汉字
        
        if not has_chinese:
            logger.info(f"忽略非中文路径: {doc_name} from {ip_address}")
            return '', 404
    
    logger.info(f"收到访问请求: {doc_name} from {ip_address}")
    
    # 查找对应的 webhook
    webhook_url = config.get('webhooks', {}).get(doc_name)
    if not webhook_url:
        webhook_url = config.get('default_webhook')
    
    if not webhook_url:
        logger.warning(f"未找到文档 {doc_name} 的 webhook 配置")
        return render_success_page(doc_name, notified=False, reason="未配置 webhook")
    
    # 检查是否需要通知（防刷）
    if not should_notify(ip_address, doc_name):
        logger.info(f"跳过通知（防刷限制）: {doc_name} from {ip_address}")
        return render_success_page(doc_name, notified=False, reason="请勿频繁访问")
    
    # 发送 webhook
    success = send_webhook(webhook_url, doc_name, ip_address)
    
    return render_success_page(doc_name, notified=success)


def render_success_page(doc_name, notified=True, reason=""):
    """渲染成功页面"""
    if notified:
        status_icon = "✅"
        status_text = "通知已发送"
        status_color = "#10b981"
        message = f"已成功通知相关人员查看文档 <strong>{doc_name}</strong>"
    else:
        status_icon = "⚠️"
        status_text = "未发送通知"
        status_color = "#f59e0b"
        message = f"文档 <strong>{doc_name}</strong> 的访问已记录"
        if reason:
            message += f"<br><small>原因: {reason}</small>"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{status_text}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .card {{
                background: white;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
                max-width: 500px;
                animation: slideIn 0.5s ease-out;
            }}
            @keyframes slideIn {{
                from {{
                    opacity: 0;
                    transform: translateY(-20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            .icon {{
                font-size: 64px;
                margin-bottom: 20px;
            }}
            h1 {{
                color: {status_color};
                margin: 0 0 20px 0;
                font-size: 28px;
            }}
            .message {{
                color: #666;
                font-size: 16px;
                line-height: 1.6;
                margin-bottom: 30px;
            }}
            .back-link {{
                display: inline-block;
                padding: 12px 30px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 25px;
                transition: all 0.3s;
            }}
            .back-link:hover {{
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }}
            .timestamp {{
                margin-top: 20px;
                font-size: 12px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="icon">{status_icon}</div>
            <h1>{status_text}</h1>
            <div class="message">{message}</div>
            <a href="/" class="back-link">返回首页</a>
            <div class="timestamp">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route('/api/stats')
def stats():
    """API: 获取访问统计"""
    # 读取日志文件统计（简单实现）
    try:
        log_file = Path('logs') / 'app.log'
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                total_visits = len([l for l in lines if '收到访问请求' in l])
        else:
            total_visits = 0
            
        return jsonify({
            'status': 'success',
            'total_visits': total_visits,
            'active_rate_limits': len(recent_visits)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })


@app.route('/health')
def health():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/favicon.ico')
def favicon():
    """处理 favicon 请求，避免触发文档路由"""
    return '', 204


if __name__ == '__main__':
    # 开发环境运行
    app.run(host='0.0.0.0', port=5000, debug=False)
