#!/usr/bin/env python3
"""
测试后端API连接
"""

import requests
import json

def test_backend_connection():
    print("测试后端API连接...")
    
    base_url = "http://localhost:8000/api"
    
    # 测试基本连接
    try:
        response = requests.get(f"{base_url}/system/dashboard-stats/", timeout=5)
        print(f"Dashboard stats 响应状态: {response.status_code}")
        if response.status_code == 401:
            print("需要认证 - 这是正常的")
        elif response.status_code == 200:
            print(f"数据: {response.json()}")
        else:
            print(f"响应内容: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务器 - 请确保Django服务器正在运行在localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ 连接超时")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False
    
    print("✅ 后端服务器连接正常")
    return True

if __name__ == "__main__":
    test_backend_connection()