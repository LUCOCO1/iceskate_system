#!/usr/bin/env python
import os
import django
import sys

# 添加项目目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iceskate_backend.settings')
django.setup()

import requests
from orders.models import Customer, Order
from inventory.models import Product
from django.contrib.auth.models import User
from django.db import connection

def test_database():
    """测试数据库连接和数据"""
    print("=== 数据库状态检查 ===")
    try:
        # 检查数据库连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ 数据库连接正常")
        
        # 检查数据
        customer_count = Customer.objects.count()
        order_count = Order.objects.count()
        product_count = Product.objects.count()
        user_count = User.objects.count()
        
        print(f"客户数量: {customer_count}")
        print(f"订单数量: {order_count}")
        print(f"产品数量: {product_count}")
        print(f"用户数量: {user_count}")
        
        # 如果没有客户数据，创建一些测试数据
        if customer_count == 0:
            print("正在创建测试客户数据...")
            Customer.objects.create(
                code='CUST001',
                name='测试客户A',
                contact='张三',
                phone='13800138001',
                email='test@example.com',
                address='北京市朝阳区',
                is_active=True
            )
            Customer.objects.create(
                code='CUST002', 
                name='测试客户B',
                contact='李四',
                phone='13800138002',
                email='test2@example.com',
                address='上海市浦东区',
                is_active=True
            )
            print("✓ 已创建测试客户数据")
            
        # 显示现有客户
        customers = Customer.objects.all()[:5]
        print("客户列表:")
        for customer in customers:
            print(f"  {customer.name} ({customer.code}) - {customer.is_active}")
            
    except Exception as e:
        print(f"✗ 数据库检查失败: {e}")

def test_api():
    """测试API接口"""
    print("\n=== API接口测试 ===")
    base_url = 'http://localhost:8000'
    
    # 测试客户接口
    try:
        response = requests.get(f'{base_url}/api/orders/customers/', timeout=5)
        print(f"客户接口状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据类型: {type(data)}")
            if isinstance(data, dict):
                print(f"返回结果数: {data.get('count', '未知')}")
                results = data.get('results', [])
                print(f"客户列表长度: {len(results)}")
            elif isinstance(data, list):
                print(f"客户列表长度: {len(data)}")
        else:
            print(f"客户接口错误: {response.text}")
    except requests.ConnectionError:
        print("✗ 无法连接到Django服务器，请检查服务器是否启动")
    except Exception as e:
        print(f"✗ 客户接口测试失败: {e}")
    
    # 测试订单接口
    try:
        response = requests.get(f'{base_url}/api/orders/orders/', timeout=5)
        print(f"订单接口状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据类型: {type(data)}")
            if isinstance(data, dict):
                print(f"返回结果数: {data.get('count', '未知')}")
            elif isinstance(data, list):
                print(f"订单列表长度: {len(data)}")
    except requests.ConnectionError:
        print("✗ 无法连接到Django服务器")
    except Exception as e:
        print(f"✗ 订单接口测试失败: {e}")

def check_frontend_config():
    """检查前端配置"""
    print("\n=== 前端配置检查 ===")
    try:
        import json
        
        # 检查前端API配置
        api_file = 'frontend/src/api/orders.ts'
        if os.path.exists(api_file):
            with open(api_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if '/orders/customers/' in content:
                    print("✓ 前端客户API配置正确")
                else:
                    print("✗ 前端客户API配置异常")
                    
                if '/orders/orders/' in content:
                    print("✓ 前端订单API配置正确")
                else:
                    print("✗ 前端订单API配置异常")
        else:
            print(f"✗ 前端API文件不存在: {api_file}")
            
    except Exception as e:
        print(f"✗ 前端配置检查失败: {e}")

if __name__ == '__main__':
    test_database()
    test_api()
    check_frontend_config() 