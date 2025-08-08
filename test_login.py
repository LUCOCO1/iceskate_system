#!/usr/bin/env python
import requests
import json

def test_login_api():
    """测试登录API接口"""
    print("=== 测试登录API接口 ===")
    
    # 测试用户凭据
    test_users = [
        {'username': 'admin', 'password': 'admin123'},
        {'username': 'test', 'password': 'test123'},
        {'username': 'user', 'password': 'password'},
    ]
    
    for user_data in test_users:
        try:
            print(f"\n测试用户: {user_data['username']}")
            
            response = requests.post(
                'http://localhost:8000/api/auth/login/',
                json=user_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ 登录成功！Token: {data.get('token', 'N/A')}")
                print(f"  用户信息: {data.get('user', 'N/A')}")
            else:
                print(f"✗ 登录失败")
                
        except requests.ConnectionError:
            print("✗ 无法连接到服务器，请检查Django服务器是否运行")
            break
        except Exception as e:
            print(f"✗ 测试失败: {e}")
    
    print("\n=== 检查现有用户 ===")
    check_users()

def check_users():
    """检查数据库中的用户"""
    import os
    import django
    import sys
    
    # 设置Django环境
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iceskate_backend.settings')
    django.setup()
    
    from django.contrib.auth.models import User
    
    try:
        users = User.objects.all()
        print(f"数据库中的用户数量: {users.count()}")
        
        for user in users:
            print(f"  - {user.username} (管理员: {user.is_staff}, 启用: {user.is_active})")
            
        # 如果没有用户，创建一个测试用户
        if users.count() == 0:
            print("\n正在创建测试用户...")
            User.objects.create_user(username='admin', password='admin123', is_staff=True)
            User.objects.create_user(username='test', password='test123')
            print("✓ 已创建测试用户 admin/admin123 和 test/test123")
            
    except Exception as e:
        print(f"✗ 检查用户失败: {e}")

if __name__ == '__main__':
    test_login_api() 