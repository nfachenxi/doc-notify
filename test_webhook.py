#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webhook 测试脚本
用于测试 webhook 接收端是否正常工作
"""

import requests
import json
import sys
from datetime import datetime

def test_webhook(webhook_url, doc_name="测试文档"):
    """测试 webhook - 发送标准格式的数据"""
    
    # 构造与实际程序相同的 POST 数据
    payload = {
        "doc_name": doc_name,
        "access_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "ip_address": "127.0.0.1"
    }
    
    print(f"发送数据:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print()
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        print()
        
        if response.status_code == 200:
            print("✅ Webhook 测试成功！")
            return True
        else:
            print(f"⚠️  Webhook 返回非 200 状态码")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时（5秒）")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败，请检查 webhook 地址是否正确")
        return False
    except Exception as e:
        print(f"❌ 发送失败: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("Webhook 测试工具")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python test_webhook.py <webhook_url> [文档名称]")
        print()
        print("示例:")
        print("  python test_webhook.py https://your-endpoint.com/notify")
        print("  python test_webhook.py https://your-endpoint.com/notify 产品需求文档")
        print()
        print("发送的 POST 数据格式:")
        print(json.dumps({
            "doc_name": "文档名称",
            "access_time": "2025-10-05 14:30:00",
            "ip_address": "192.168.1.100"
        }, indent=2, ensure_ascii=False))
        sys.exit(1)
    
    webhook_url = sys.argv[1]
    doc_name = sys.argv[2] if len(sys.argv) > 2 else "测试文档"
    
    print(f"目标 URL: {webhook_url}")
    print(f"文档名称: {doc_name}")
    print("-" * 60)
    print()
    
    test_webhook(webhook_url, doc_name)


if __name__ == '__main__':
    main()
