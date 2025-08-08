#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
前后端系统测试脚本
"""
import urllib.request
import urllib.error
import json
import time

def test_system():
    print("="*50)
    print("冰刀系统前后端测试")
    print("="*50)
    
    # 测试后端
    print("正在测试后端服务器...")
    try:
        resp = urllib.request.urlopen('http://localhost:8000/admin/', timeout=5)
        print(f"✓ Django后端: HTTP {resp.status}")
        backend_ok = True
    except Exception as e:
        print(f"✗ Django后端连接失败: {e}")
        backend_ok = False
    
    # 测试前端
    print("正在测试前端服务器...")
    try:
        resp = urllib.request.urlopen('http://localhost:5173/', timeout=5)
        print(f"✓ Vue.js前端: HTTP {resp.status}")
        frontend_ok = True
    except Exception as e:
        print(f"✗ Vue.js前端连接失败: {e}")
        frontend_ok = False
    
    print("="*50)
    print("测试结果:")
    print(f"后端: {'正常' if backend_ok else '异常'}")
    print(f"前端: {'正常' if frontend_ok else '异常'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 系统运行正常!")
        print("前端: http://localhost:5173/")
        print("后端: http://localhost:8000/")
        print("管理: http://localhost:8000/admin/")
    
    print("="*50)

if __name__ == '__main__':
    test_system() 