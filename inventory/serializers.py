from rest_framework import serializers
from .models import (
    Material,
    MaterialMovement,
    Supplier,
    MaterialPurchase,
    PurchaseItem,
    MaterialBatch,
    Inventory,
    InventoryItem,
    Product,
    ProductMovement,
    ProductOutbound,
    ProductOutboundItem
)

class MaterialSerializer(serializers.ModelSerializer):
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Material
        fields = '__all__'
    
    def get_stock_status(self, obj):
        if obj.stock <= obj.min_stock:
            return "低库存"
        return "正常"

class MaterialMovementSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    source_info = serializers.SerializerMethodField()
    
    class Meta:
        model = MaterialMovement
        fields = '__all__'
    
    def get_source_info(self, obj):
        if obj.purchase:
            return f"采购单：{obj.purchase.purchase_number}"
        return None

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class PurchaseItemSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    material_specification = serializers.CharField(source='material.specification', read_only=True)
    
    class Meta:
        model = PurchaseItem
        fields = ['id', 'material', 'material_name', 'material_specification',
                 'control_number', 'specification', 'quantity', 'unit', 
                 'material_type', 'notes']

class MaterialPurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, required=False)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = MaterialPurchase
        fields = '__all__'
        
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        purchase = MaterialPurchase.objects.create(**validated_data)
        
        for item_data in items_data:
            PurchaseItem.objects.create(purchase=purchase, **item_data)
            
        return purchase
        
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        # 更新采购单主表字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 处理明细项
        if items_data:
            # 可以选择删除已有明细后重建，或者更新已有明细
            instance.items.all().delete()  # 删除已有明细
            for item_data in items_data:
                PurchaseItem.objects.create(purchase=instance, **item_data)
                
        return instance

class ProductMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    
    class Meta:
        model = ProductMovement
        fields = '__all__'

class MaterialBatchSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    
    class Meta:
        model = MaterialBatch
        fields = '__all__'

class InventoryItemSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    items = InventoryItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Inventory
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    stock_status = serializers.SerializerMethodField()
    customer_names = serializers.SerializerMethodField()
    customers_display = serializers.SerializerMethodField()
    material_requirement = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def get_stock_status(self, obj):
        if obj.stock <= obj.min_stock:
            return "低库存"
        elif obj.stock <= obj.warning_stock:
            return "库存预警"
        elif obj.stock >= obj.max_stock:
            return "库存过高"
        return "正常"
    
    def get_customer_names(self, obj):
        """获取客户名称列表"""
        return [customer.name for customer in obj.customers.all()]
    
    def get_customers_display(self, obj):
        """获取客户显示字符串"""
        customers = obj.customers.all()
        if customers.exists():
            customer_names = [customer.name for customer in customers[:3]]
            display_text = ', '.join(customer_names)
            if customers.count() > 3:
                display_text += f' 等{customers.count()}个客户'
            return display_text
        return '暂无关联客户'
    
    def get_material_requirement(self, obj):
        """获取材料需求量计算信息"""
        return {
            'unit_weight': float(obj.unit_weight),
            'unit_weight_display': f'{obj.unit_weight} kg/件'
        }

class ProductOutboundItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_code = serializers.ReadOnlyField(source='product.code')
    
    class Meta:
        model = ProductOutboundItem
        fields = ['id', 'outbound', 'product', 'product_name', 'product_code', 'quantity', 'unit', 'notes']
        read_only_fields = ['id', 'outbound', 'product_name', 'product_code']  # outbound设为只读
    
    def validate_product(self, value):
        """验证产品字段"""
        if not value:
            raise serializers.ValidationError("产品不能为空")
        return value
    
    def validate_quantity(self, value):
        """验证数量字段"""
        if not value or value <= 0:
            raise serializers.ValidationError("数量必须大于0")
        return value
    
    def create(self, validated_data):
        # 确保单位有值
        if not validated_data.get('unit'):
            product = validated_data.get('product')
            if product and hasattr(product, 'unit'):
                validated_data['unit'] = product.unit
            else:
                validated_data['unit'] = '个'
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # 确保单位有值
        if not validated_data.get('unit'):
            product = validated_data.get('product', instance.product)
            if product and hasattr(product, 'unit'):
                validated_data['unit'] = product.unit
            else:
                validated_data['unit'] = '个'
                
        return super().update(instance, validated_data)

class ProductOutboundSerializer(serializers.ModelSerializer):
    items = ProductOutboundItemSerializer(many=True, required=False)
    order_number = serializers.ReadOnlyField(source='order.order_number', allow_null=True)
    status_display = serializers.ReadOnlyField(source='get_status_display')
    created_by_name = serializers.ReadOnlyField(source='created_by.username', allow_null=True)
    
    class Meta:
        model = ProductOutbound
        fields = '__all__'
        read_only_fields = ['order_number', 'status_display', 'created_by_name']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        
        # 验证必须有明细项
        if not items_data:
            raise serializers.ValidationError({"items": "出库单必须包含至少一个明细项"})
        
        # 详细验证明细项
        for i, item_data in enumerate(items_data):
            item_errors = {}
            
            # 验证产品
            if not item_data.get('product'):
                item_errors['product'] = f"第{i+1}行明细项必须选择产品"
            
            # 验证数量
            quantity = item_data.get('quantity')
            if not quantity:
                item_errors['quantity'] = f"第{i+1}行明细项必须输入数量"
            elif quantity <= 0:
                item_errors['quantity'] = f"第{i+1}行明细项数量必须大于0，当前值：{quantity}"
            
            # 如果有错误，抛出明细错误
            if item_errors:
                raise serializers.ValidationError({"items": item_errors})
        
        # 创建出库单
        try:
            outbound = ProductOutbound.objects.create(**validated_data)
        except Exception as e:
            raise serializers.ValidationError({"non_field_errors": f"创建出库单失败：{str(e)}"})
        
        # 创建明细项
        for i, item_data in enumerate(items_data):
            try:
                # 清理数据，移除前端可能传递但不需要的字段
                clean_item_data = {
                    'product': item_data.get('product'),
                    'quantity': item_data.get('quantity'),
                    'unit': item_data.get('unit'),
                    'notes': item_data.get('notes', ''),
                }
                
                # 设置默认单位
                if not clean_item_data.get('unit'):
                    product = clean_item_data.get('product')
                    if product and hasattr(product, 'unit'):
                        clean_item_data['unit'] = product.unit
                    else:
                        clean_item_data['unit'] = '个'
                
                # 创建明细项，明确指定outbound
                ProductOutboundItem.objects.create(
                    outbound=outbound,
                    **clean_item_data
                )
            except Exception as e:
                # 如果明细项创建失败，删除已创建的出库单
                outbound.delete()
                raise serializers.ValidationError({
                    "items": f"第{i+1}行明细项创建失败：{str(e)}"
                })
            
        return outbound
        
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        
        # 更新出库单主表字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 处理明细项
        if items_data:
            # 验证必须有明细项
            if not items_data:
                raise serializers.ValidationError({"items": "出库单必须包含至少一个明细项"})
            
            # 删除已有明细后重建
            instance.items.all().delete()
            for i, item_data in enumerate(items_data):
                # 验证明细项数据
                if not item_data.get('product'):
                    raise serializers.ValidationError({
                        "items": f"第{i+1}行明细项必须选择产品"
                    })
                
                quantity = item_data.get('quantity')
                if not quantity:
                    raise serializers.ValidationError({
                        "items": f"第{i+1}行明细项必须输入数量"
                    })
                elif quantity <= 0:
                    raise serializers.ValidationError({
                        "items": f"第{i+1}行明细项数量必须大于0，当前值：{quantity}"
                    })
                
                # 清理数据，只保留需要的字段
                clean_item_data = {
                    'product': item_data.get('product'),
                    'quantity': item_data.get('quantity'),
                    'unit': item_data.get('unit'),
                    'notes': item_data.get('notes', ''),
                }
                
                # 设置默认单位
                if not clean_item_data.get('unit'):
                    product = clean_item_data.get('product')
                    if product and hasattr(product, 'unit'):
                        clean_item_data['unit'] = product.unit
                    else:
                        clean_item_data['unit'] = '个'
                
                try:
                    ProductOutboundItem.objects.create(
                        outbound=instance,
                        **clean_item_data
                    )
                except Exception as e:
                    raise serializers.ValidationError({
                        "items": f"第{i+1}行明细项创建失败：{str(e)}"
                    })
                
        return instance 