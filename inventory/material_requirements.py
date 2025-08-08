"""
材料需求计算模块
"""
from decimal import Decimal
from typing import List, Dict, Any
from .models import Product
from orders.models import Order, OrderItem


class MaterialRequirementCalculator:
    """材料需求计算器"""
    
    @staticmethod
    def calculate_from_order_items(order_items_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        根据订单明细计算材料需求
        
        Args:
            order_items_data: 订单明细数据列表
                [{
                    "product_id": int,
                    "quantity": float,
                    "product_name": str (可选),
                    "notes": str (可选)
                }]
        
        Returns:
            Dict: 计算结果
        """
        material_requirements = {}
        calculation_details = []
        errors = []
        
        for i, item in enumerate(order_items_data):
            try:
                product_id = item.get('product_id')
                quantity = Decimal(str(item.get('quantity', 0)))
                
                if not product_id:
                    errors.append(f"第{i+1}行：产品ID不能为空")
                    continue
                
                if quantity <= 0:
                    errors.append(f"第{i+1}行：数量必须大于0")
                    continue
                
                try:
                    product = Product.objects.get(id=product_id, is_active=True)
                except:
                    errors.append(f"第{i+1}行：产品ID {product_id} 不存在或已禁用")
                    continue
                
                # 计算材料重量
                unit_weight = product.unit_weight
                material_weight = unit_weight * quantity
                
                # 累计材料需求
                product_key = f"product_{product_id}"
                if product_key not in material_requirements:
                    material_requirements[product_key] = {
                        'product_id': product_id,
                        'product_name': product.name,
                        'product_code': product.code,
                        'specification': product.specification,
                        'unit_weight': float(unit_weight),
                        'total_quantity': Decimal('0'),
                        'total_material_weight': Decimal('0')
                    }
                
                material_requirements[product_key]['total_quantity'] += quantity
                material_requirements[product_key]['total_material_weight'] += material_weight
                
                # 计算详情
                calculation_details.append({
                    'row_number': i + 1,
                    'product_id': product_id,
                    'product_name': product.name,
                    'product_code': product.code,
                    'quantity': float(quantity),
                    'unit_weight': float(unit_weight),
                    'material_weight': float(material_weight),
                    'calculation_formula': f'{quantity} × {unit_weight}kg = {material_weight}kg',
                    'notes': item.get('notes', '')
                })
                
            except Exception as e:
                errors.append(f"第{i+1}行：计算出错 - {str(e)}")
        
        # 转换结果格式
        requirements_list = []
        total_material_weight = Decimal('0')
        
        for req in material_requirements.values():
            req['total_quantity'] = float(req['total_quantity'])
            req['total_material_weight'] = float(req['total_material_weight'])
            total_material_weight += Decimal(str(req['total_material_weight']))
            requirements_list.append(req)
        
        return {
            'success': len(errors) == 0,
            'errors': errors,
            'material_requirements': requirements_list,
            'calculation_details': calculation_details,
            'summary': {
                'total_product_types': len(requirements_list),
                'total_items_processed': len(calculation_details),
                'total_material_weight': float(total_material_weight),
                'total_material_weight_display': f'{total_material_weight:.3f} kg'
            }
        }
    
    @staticmethod
    def calculate_from_order(order_id: int) -> Dict[str, Any]:
        """
        根据订单ID计算材料需求
        
        Args:
            order_id: 订单ID
            
        Returns:
            Dict: 计算结果
        """
        try:
            order = Order.objects.get(id=order_id)
            order_items = order.items.all()
            
            # 转换为统一格式
            order_items_data = []
            for item in order_items:
                order_items_data.append({
                    'product_id': item.product.id,
                    'quantity': float(item.quantity),
                    'product_name': item.product.name,
                    'notes': f"订单{order.order_number} - {item.notes}" if item.notes else f"订单{order.order_number}"
                })
            
            result = MaterialRequirementCalculator.calculate_from_order_items(order_items_data)
            result['order_info'] = {
                'order_id': order.id,
                'order_number': order.order_number,
                'customer_name': order.customer.name,
                'order_date': order.order_date.strftime('%Y-%m-%d'),
                'delivery_date': order.delivery_date.strftime('%Y-%m-%d')
            }
            
            return result
            
        except Order.DoesNotExist:
            return {
                'success': False,
                'errors': [f'订单ID {order_id} 不存在'],
                'material_requirements': [],
                'calculation_details': [],
                'summary': {
                    'total_product_types': 0,
                    'total_items_processed': 0,
                    'total_material_weight': 0,
                    'total_material_weight_display': '0.000 kg'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [f'计算订单材料需求时出错: {str(e)}'],
                'material_requirements': [],
                'calculation_details': [],
                'summary': {
                    'total_product_types': 0,
                    'total_items_processed': 0,
                    'total_material_weight': 0,
                    'total_material_weight_display': '0.000 kg'
                }
            } 