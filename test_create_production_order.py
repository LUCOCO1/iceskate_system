#!/usr/bin/env python
"""
测试创建生产订单
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iceskate_backend.settings')
django.setup()

from production.models import ProductionOrder, MaterialRequirement
from inventory.models import Product, Material
from datetime import datetime, timedelta

def test_create_production_order():
    # 获取一个产品
    product = Product.objects.first()
    if not product:
        print("错误：没有找到产品，请先创建产品")
        return
    
    # 获取一些材料
    materials = Material.objects.all()[:2]
    if len(materials) < 1:
        print("错误：没有找到材料，请先创建材料")
        return
    
    # 创建生产订单数据
    order_data = {
        'product': product,
        'planned_quantity': 100,
        'start_date': datetime.now().date(),
        'end_date': (datetime.now() + timedelta(days=7)).date(),
        'priority': 'medium',
        'responsible_person': '张三',
        'notes': '测试订单'
    }
    
    # 创建生产订单
    print("创建生产订单...")
    order = ProductionOrder.objects.create(**order_data)
    print(f"生产订单创建成功: {order.order_number}")
    
    # 创建材料需求
    print("\n创建材料需求...")
    for i, material in enumerate(materials):
        requirement = MaterialRequirement.objects.create(
            production_order=order,
            material=material,
            required_quantity=(i + 1) * 10,
            notes=f'测试材料需求{i + 1}'
        )
        print(f"- 材料需求创建成功: {material.name}, 数量: {requirement.required_quantity}")
    
    # 验证材料需求
    print(f"\n订单 {order.order_number} 的材料需求:")
    for req in order.material_requirements.all():
        print(f"- {req.material.name}: {req.required_quantity} {req.material.unit}")
    
    print("\n测试完成！")

if __name__ == '__main__':
    test_create_production_order()