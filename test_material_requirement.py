#!/usr/bin/env python
"""
材料需求计算功能测试
"""
import os
import sys
import django
import json
from decimal import Decimal

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'iceskate_system'))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iceskate_backend.settings')
django.setup()

from inventory.models import Product
from inventory.material_requirements import MaterialRequirementCalculator
from orders.models import Order, Customer

def test_material_requirement_calculation():
    """测试材料需求计算功能"""
    print("=== 材料需求计算功能测试 ===\n")
    
    # 1. 创建测试产品（如果不存在）
    print("1. 检查并创建测试产品...")
    
    products_data = [
        {
            'name': '铁板A型',
            'code': 'TB001',
            'specification': '1000x500x5mm',
            'unit': '张',
            'unit_weight': Decimal('19.625'),  # 1m x 0.5m x 5mm x 7.85g/cm³
        },
        {
            'name': '铁板B型',
            'code': 'TB002',
            'specification': '800x400x3mm',
            'unit': '张',
            'unit_weight': Decimal('7.536'),   # 0.8m x 0.4m x 3mm x 7.85g/cm³
        },
        {
            'name': '钢管C型',
            'code': 'GM001',
            'specification': '直径50mm 长度2m',
            'unit': '根',
            'unit_weight': Decimal('12.280'),  # 假设重量
        }
    ]
    
    created_products = []
    for data in products_data:
        product, created = Product.objects.get_or_create(
            code=data['code'],
            defaults=data
        )
        if created:
            print(f"   创建产品: {product.name} ({product.code}) - 单重: {product.unit_weight}kg")
        else:
            # 更新单重信息
            product.unit_weight = data['unit_weight']
            product.save()
            print(f"   更新产品: {product.name} ({product.code}) - 单重: {product.unit_weight}kg")
        created_products.append(product)
    
    # 2. 测试手动输入计算
    print("\n2. 测试手动输入材料需求计算...")
    
    order_items_data = [
        {
            'product_id': created_products[0].id,
            'quantity': 10,
            'product_name': created_products[0].name,
            'notes': '测试订单项1'
        },
        {
            'product_id': created_products[1].id,
            'quantity': 20,
            'product_name': created_products[1].name,
            'notes': '测试订单项2'
        },
        {
            'product_id': created_products[2].id,
            'quantity': 5,
            'product_name': created_products[2].name,
            'notes': '测试订单项3'
        }
    ]
    
    result = MaterialRequirementCalculator.calculate_from_order_items(order_items_data)
    
    print(f"   计算结果: {'成功' if result['success'] else '失败'}")
    if result['errors']:
        print(f"   错误信息: {result['errors']}")
    
    print(f"   产品种类: {result['summary']['total_product_types']}")
    print(f"   处理明细数: {result['summary']['total_items_processed']}")
    print(f"   总材料重量: {result['summary']['total_material_weight_display']}")
    
    print("\n   材料需求汇总:")
    for req in result['material_requirements']:
        print(f"     - {req['product_name']} ({req['product_code']}): "
              f"{req['total_quantity']}件 × {req['unit_weight']}kg = {req['total_material_weight']:.3f}kg")
    
    print("\n   计算详情:")
    for detail in result['calculation_details']:
        print(f"     第{detail['row_number']}行: {detail['calculation_formula']} - {detail['notes']}")
    
    # 3. 测试订单导入计算（如果有订单数据）
    print("\n3. 测试从订单导入计算...")
    
    orders = Order.objects.all()[:1]  # 取第一个订单测试
    if orders:
        order = orders[0]
        print(f"   使用订单: {order.order_number}")
        
        result = MaterialRequirementCalculator.calculate_from_order(order.id)
        
        print(f"   计算结果: {'成功' if result['success'] else '失败'}")
        if result['errors']:
            print(f"   错误信息: {result['errors']}")
        else:
            print(f"   订单信息: {result['order_info']['order_number']} - {result['order_info']['customer_name']}")
            print(f"   总材料重量: {result['summary']['total_material_weight_display']}")
    else:
        print("   没有找到订单数据，跳过订单导入测试")
    
    # 4. 测试错误处理
    print("\n4. 测试错误处理...")
    
    error_test_data = [
        {
            'product_id': 99999,  # 不存在的产品ID
            'quantity': 10,
            'notes': '错误测试1'
        },
        {
            'product_id': created_products[0].id,
            'quantity': 0,  # 数量为0
            'notes': '错误测试2'
        },
        {
            'quantity': 5,  # 缺少product_id
            'notes': '错误测试3'
        }
    ]
    
    result = MaterialRequirementCalculator.calculate_from_order_items(error_test_data)
    
    print(f"   计算结果: {'成功' if result['success'] else '失败'}")
    print(f"   错误数量: {len(result['errors'])}")
    for error in result['errors']:
        print(f"     - {error}")
    
    print("\n=== 测试完成 ===")

def test_product_unit_weight():
    """测试产品单重字段"""
    print("\n=== 产品单重字段测试 ===\n")
    
    # 检查所有产品的单重设置
    products = Product.objects.all()
    print(f"共有 {products.count()} 个产品:")
    
    has_unit_weight = 0
    no_unit_weight = 0
    
    for product in products:
        if product.unit_weight and product.unit_weight > 0:
            print(f"  ✓ {product.name} ({product.code}): {product.unit_weight} kg/件")
            has_unit_weight += 1
        else:
            print(f"  ✗ {product.name} ({product.code}): 未设置单重")
            no_unit_weight += 1
    
    print(f"\n统计: {has_unit_weight} 个已设置单重, {no_unit_weight} 个未设置单重")
    
    if no_unit_weight > 0:
        print("\n建议: 为未设置单重的产品添加单重信息以便进行材料需求计算")

if __name__ == '__main__':
    try:
        test_product_unit_weight()
        test_material_requirement_calculation()
        
        print("\n所有测试完成! ✓")
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc() 