#!/usr/bin/env python
"""
生产订单创建测试脚本
"""
import os
import django
import requests
import json
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iceskate_system.settings')
django.setup()

# 测试配置
BASE_URL = 'http://localhost:8000'
API_URL = f'{BASE_URL}/api/production/production-orders/'

def test_production_order_creation():
    """测试生产订单创建"""
    print("=== 测试生产订单创建 ===")
    
    # 准备测试数据
    today = datetime.now().date()
    end_date = today + timedelta(days=7)
    
    test_data = {
        "product": 1,  # 假设产品ID为1
        "planned_quantity": 100,
        "start_date": today.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "priority": "medium",
        "responsible_person": "测试负责人",
        "notes": "测试创建生产订单"
    }
    
    print(f"发送数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            API_URL,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ 生产订单创建成功!")
            print(f"订单号: {result.get('order_number')}")
            print(f"产品: {result.get('product_name')}")
            print(f"计划数量: {result.get('planned_quantity')}")
            print(f"状态: {result.get('status_display')}")
            return True
        else:
            print(f"❌ 生产订单创建失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return False

def test_production_order_list():
    """测试生产订单列表"""
    print("\n=== 测试生产订单列表 ===")
    
    try:
        response = requests.get(API_URL)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 获取生产订单列表成功!")
            print(f"总数: {result.get('count', 0)}")
            
            if result.get('results'):
                for order in result['results'][:3]:  # 只显示前3个
                    print(f"- {order.get('order_number')}: {order.get('product_name')} ({order.get('status_display')})")
            return True
        else:
            print(f"❌ 获取生产订单列表失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return False

def check_products():
    """检查产品列表"""
    print("\n=== 检查产品列表 ===")
    
    try:
        response = requests.get(f'{BASE_URL}/api/inventory/products/')
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 获取产品列表成功!")
            
            if result.get('results'):
                print("可用产品:")
                for product in result['results'][:5]:  # 只显示前5个
                    print(f"- ID: {product.get('id')}, 名称: {product.get('name')}")
            else:
                print("⚠️ 没有可用产品，请先创建产品")
            return True
        else:
            print(f"❌ 获取产品列表失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("生产订单功能测试")
    print("=" * 50)
    
    # 检查产品
    if not check_products():
        return
    
    # 测试列表
    if not test_production_order_list():
        return
    
    # 测试创建
    if not test_production_order_creation():
        return
    
    # 再次测试列表
    test_production_order_list()
    
    print("\n✅ 所有测试完成!")

if __name__ == "__main__":
    main() 