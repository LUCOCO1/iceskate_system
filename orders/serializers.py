from rest_framework import serializers
from .models import Customer, Order, OrderItem
from inventory.models import Product
from django.contrib.auth import get_user_model
from django.db import transaction
import datetime

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderItemCreateSerializer(serializers.ModelSerializer):
    """用于创建订单明细的序列化器"""
    class Meta:
        model = OrderItem
        fields = ['product', 'color', 'material', 'quantity', 'unit', 'notes']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    items_data = OrderItemCreateSerializer(many=True, write_only=True, required=False)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['order_number', 'created_by', 'created_at', 'updated_at']

    def generate_order_number(self):
        """生成订单号"""
        today = datetime.date.today()
        date_str = today.strftime('%Y%m%d')
        
        # 查找今天最大的订单号
        latest_order = Order.objects.filter(
            order_number__startswith=f'SO{date_str}'
        ).order_by('-order_number').first()
        
        if latest_order:
            # 提取序号部分并加1
            sequence = int(latest_order.order_number[-3:]) + 1
        else:
            sequence = 1
        
        return f'SO{date_str}{sequence:03d}'

    def create(self, validated_data):
        """创建订单及其明细"""
        items_data = validated_data.pop('items_data', [])
        
        # 设置创建人
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        
        # 生成订单号
        validated_data['order_number'] = self.generate_order_number()
        
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            
            # 创建订单明细
            for item_data in items_data:
                OrderItem.objects.create(order=order, **item_data)
        
        return order

    def update(self, instance, validated_data):
        """更新订单及其明细"""
        items_data = validated_data.pop('items_data', [])
        
        with transaction.atomic():
            # 更新订单基本信息
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            # 删除现有明细
            instance.items.all().delete()
            
            # 创建新明细
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)
        
        return instance

    def to_internal_value(self, data):
        """处理前端传来的items字段"""
        if 'items' in data:
            data['items_data'] = data.pop('items')
        return super().to_internal_value(data) 