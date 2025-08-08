from rest_framework import serializers
from .models import (
    ProductionOrder,
    ProcessStep,
    ProcessSchedule,
    ProductionMaterial,
    MaterialRequirement,
    ProductionProgress,
    Equipment
)
from inventory.models import Product
from datetime import datetime

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class MaterialRequirementSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    material_code = serializers.CharField(source='material.code', read_only=True)
    material_unit = serializers.CharField(source='material.unit', read_only=True)
    material_specification = serializers.CharField(source='material.specification', read_only=True)
    production_order_number = serializers.CharField(source='production_order.order_number', read_only=True)
    unit = serializers.CharField(source='material.unit', read_only=True)  # 前端期望的字段名
    
    class Meta:
        model = MaterialRequirement
        fields = '__all__'

class ProductionProgressSerializer(serializers.ModelSerializer):
    production_order_number = serializers.CharField(source='production_order.order_number', read_only=True)
    product_name = serializers.CharField(source='production_order.product.name', read_only=True)
    
    class Meta:
        model = ProductionProgress
        fields = '__all__'

class MaterialRequirementCreateSerializer(serializers.ModelSerializer):
    """用于创建和更新材料需求的序列化器"""
    material_name = serializers.CharField(write_only=True)
    material_specification = serializers.CharField(read_only=True, source='material.specification')
    
    class Meta:
        model = MaterialRequirement
        fields = ['material_name', 'material_specification', 'required_quantity', 'notes']
    
    def validate_material_name(self, value):
        """验证材料名称并返回材料对象"""
        from inventory.models import Material
        try:
            # 首先尝试使用名称和规格匹配
            # 安全地获取 initial_data，如果不存在则使用空字典
            initial_data = getattr(self, 'initial_data', {})
            material_specification = initial_data.get('material_specification', '')
            if material_specification:
                return Material.objects.get(name=value, specification=material_specification)
            
            # 如果没有规格信息，尝试只用名称匹配
            materials = Material.objects.filter(name=value)
            if materials.count() == 1:
                return materials.first()
            elif materials.count() > 1:
                # 如果有多个同名材料，返回第一个（按ID排序）
                return materials.order_by('id').first()
            else:
                raise Material.DoesNotExist()
                
        except Material.DoesNotExist:
            raise serializers.ValidationError(f"材料 '{value}' 不存在")

class ProductionOrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    sales_order_number = serializers.CharField(source='sales_order.order_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    material_requirements = MaterialRequirementSerializer(many=True, read_only=True)
    material_requirements_data = MaterialRequirementCreateSerializer(many=True, write_only=True, required=False)
    progress_records = ProductionProgressSerializer(many=True, read_only=True)
    order_number = serializers.CharField(required=False)  # 设置为非必填，让create方法自动生成
    
    class Meta:
        model = ProductionOrder
        fields = '__all__'
    
    def create(self, validated_data):
        # 提取材料需求数据
        material_requirements_data = validated_data.pop('material_requirements_data', [])
        
        # 自动生成生产订单号
        if not validated_data.get('order_number'):
            today = datetime.now().strftime('%Y%m%d')
            # 获取当天的最大序号
            latest_order = ProductionOrder.objects.filter(
                order_number__startswith=f'PO{today}'
            ).order_by('-order_number').first()
            
            if latest_order:
                # 提取序号并加1
                sequence = int(latest_order.order_number[-2:]) + 1
            else:
                sequence = 1
            
            validated_data['order_number'] = f'PO{today}{sequence:02d}'
        
        # 创建生产订单
        production_order = super().create(validated_data)
        
        # 创建材料需求记录
        try:
            for material_data in material_requirements_data:
                # material_name 已经被 validate_material_name 转换为 Material 对象
                material = material_data.get('material_name')
                
                # 创建材料需求记录
                MaterialRequirement.objects.create(
                    production_order=production_order,
                    material=material,
                    required_quantity=material_data.get('required_quantity', 0),
                    notes=material_data.get('notes', '')
                )
        except Exception as e:
            # 如果创建材料需求失败，删除已创建的订单
            production_order.delete()
            raise serializers.ValidationError(f"创建材料需求失败: {str(e)}")
        
        return production_order
    
    def update(self, instance, validated_data):
        # 提取材料需求数据
        material_requirements_data = validated_data.pop('material_requirements_data', None)
        
        # 更新生产订单
        instance = super().update(instance, validated_data)
        
        # 如果提供了材料需求数据，更新材料需求
        if material_requirements_data is not None:
            # 删除现有的材料需求
            instance.material_requirements.all().delete()
            
            # 创建新的材料需求记录
            for material_data in material_requirements_data:
                # material_name 已经被 validate_material_name 转换为 Material 对象
                material = material_data.get('material_name')
                MaterialRequirement.objects.create(
                    production_order=instance,
                    material=material,
                    required_quantity=material_data.get('required_quantity', 0),
                    notes=material_data.get('notes', '')
                )
        
        return instance

class ProcessStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessStep
        fields = '__all__'

class ProcessScheduleSerializer(serializers.ModelSerializer):
    production_order_number = serializers.CharField(source='production_order.order_number', read_only=True)
    process_name = serializers.CharField(source='process.name', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ProcessSchedule
        fields = '__all__'

class ProductionMaterialSerializer(serializers.ModelSerializer):
    production_order_number = serializers.CharField(source='production_order.order_number', read_only=True)
    material_name = serializers.CharField(source='material_batch.material.name', read_only=True)
    batch_number = serializers.CharField(source='material_batch.batch_number', read_only=True)
    unit = serializers.CharField(source='material_batch.material.unit', read_only=True)
    used_date = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductionMaterial
        fields = '__all__'
    
    def get_used_date(self, obj):
        # 从材料批次的创建时间获取使用日期
        if hasattr(obj, 'material_batch') and hasattr(obj.material_batch, 'created_at'):
            return obj.material_batch.created_at.date().strftime('%Y-%m-%d')
        return None

class EquipmentSerializer(serializers.ModelSerializer):
    process_step_name = serializers.CharField(source='process_step.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Equipment
        fields = '__all__' 