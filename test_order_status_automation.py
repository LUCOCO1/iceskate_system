#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iceskate_backend.settings')
django.setup()

from orders.models import Order, Customer, OrderItem
from production.models import ProductionOrder
from inventory.models import Product
from django.contrib.auth import get_user_model

def test_order_status_automation():
    """测试订单状态自动化功能"""
    print("开始测试订单状态自动化...")
    
    try:
        # 获取或创建测试数据
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        
        customer, _ = Customer.objects.get_or_create(
            code='TEST001',
            defaults={
                'name': '测试客户',
                'contact': '测试联系人',
                'phone': '13800138000'
            }
        )
        
        product, _ = Product.objects.get_or_create(
            code='PROD001',
            defaults={
                'name': '测试产品',
                'unit': '个'
            }
        )
        
        # 创建销售订单
        order = Order.objects.create(
            order_number='SO20250115001',
            customer=customer,
            order_date='2025-01-15',
            delivery_date='2025-01-22',
            customer_order_number='CUST001',
            created_by=user
        )
        
        # 创建订单明细
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=100,
            unit='个',
            color='本色',
            material='铝合金'
        )
        
        print(f"1. 创建销售订单：{order.order_number}，初始状态：{order.get_status_display()}")
        
        # 创建生产订单
        production_order = ProductionOrder.objects.create(
            order_number='PO20250115001',
            sales_order=order,
            product=product,
            planned_quantity=100,
            start_date='2025-01-15',
            end_date='2025-01-22',
            priority='medium',
            responsible_person='测试负责人'
        )
        
        print(f"2. 创建生产订单：{production_order.order_number}，状态：{production_order.get_status_display()}")
        
        # 开始生产
        production_order.status = 'in_production'
        production_order.save()
        
        # 重新加载销售订单以查看状态变化
        order.refresh_from_db()
        print(f"3. 生产开始后，销售订单状态：{order.get_status_display()}")
        
        # 完成生产
        production_order.status = 'completed'
        production_order.completed_quantity = 100
        production_order.save()
        
        # 重新加载销售订单以查看状态变化
        order.refresh_from_db()
        print(f"4. 生产完成后，销售订单状态：{order.get_status_display()}")
        
        print("✅ 订单状态自动化测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_order_status_automation() 