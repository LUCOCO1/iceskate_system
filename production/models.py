from django.db import models
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal
from django.utils import timezone
from inventory.models import Material, MaterialMovement, ProductMovement
from datetime import timedelta
from django.urls import reverse
from django.db.models import Sum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import Manager
    from django.db import transaction as transaction_module
    from inventory.models import Product
    from orders.models import Order

def get_default_end_date():
    """获取默认结束日期（当前日期+7天）"""
    return timezone.now().date() + timedelta(days=7)

class Equipment(models.Model):
    """设备管理"""
    objects = models.Manager()  # 显式声明管理器
    name = models.CharField(max_length=100, verbose_name='设备名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='设备编号')
    model = models.CharField(max_length=100, verbose_name='设备型号')
    status = models.CharField(
        max_length=20,
        choices=[
            ('normal', '正常'),
            ('maintenance', '维护中'),
            ('malfunction', '故障'),
            ('scrapped', '报废')
        ],
        default='normal',
        verbose_name='设备状态'
    )
    process_step = models.ForeignKey(
        'ProcessStep',
        on_delete=models.PROTECT,
        verbose_name='所属工序'
    )
    daily_capacity = models.IntegerField(verbose_name='日产能')
    purchase_date = models.DateField(verbose_name='购入日期')
    last_maintenance = models.DateField(
        null=True,
        blank=True,
        verbose_name='上次维护日期'
    )
    next_maintenance = models.DateField(
        null=True,
        blank=True,
        verbose_name='下次维护日期'
    )
    notes = models.TextField(blank=True, verbose_name='备注')

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = '设备'
        verbose_name_plural = '设备'
        ordering = ['code']

class ProductionOrder(models.Model):
    """生产订单"""
    objects = models.Manager()  # 显式声明管理器
    
    if TYPE_CHECKING:
        material_requirements: Manager
        progress_records: Manager
    STATUS_CHOICES = [
        ('pending', '待生产'),
        ('material_ready', '备料完成'),
        ('in_production', '生产中'),
        ('completed', '已完成')
    ]

    PRIORITY_CHOICES = [
        ('high', '高'),
        ('medium', '中'),
        ('low', '低')
    ]

    order_number = models.CharField(max_length=50, unique=True, verbose_name='生产单号')
    sales_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.PROTECT,
        related_name='production_orders',
        null=True,
        blank=True,
        verbose_name='销售订单'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.PROTECT,
        verbose_name='产品'
    )
    planned_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='计划数量'
    )
    completed_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='完成数量'
    )
    start_date = models.DateField(
        verbose_name='计划开始日期',
        default=timezone.now
    )
    end_date = models.DateField(
        verbose_name='计划完成日期',
        default=get_default_end_date
    )
    actual_start_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name='实际开始日期'
    )
    actual_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='实际完成日期'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='优先级'
    )
    progress = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='进度(%)'
    )
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    estimated_completion_time = models.DateTimeField(
        '预计完成时间',
        null=True,
        blank=True
    )
    actual_production_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='实际生产成本'
    )
    quality_check_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '待检'),
            ('passed', '合格'),
            ('failed', '不合格')
        ],
        default='pending',
        verbose_name='质检状态'
    )

    def __str__(self):
        return f"{self.order_number} - {self.product.name}"

    def material_ready(self):
        """确认订单并准备材料"""
        if self.status != 'pending':
            raise ValidationError('只能将待生产状态的订单标记为备料完成')
        
        # 检查材料库存
        insufficient_materials = []
        for requirement in self.material_requirements.all():
            if requirement.material.stock < requirement.required_quantity:
                insufficient_materials.append(f"{requirement.material.name}: 需要{requirement.required_quantity}, 库存{requirement.material.stock}")
        
        if insufficient_materials:
            raise ValidationError(f'以下材料库存不足：\n' + '\n'.join(insufficient_materials))
        
        try:
            with transaction.atomic():
                self.status = 'material_ready'
                self.save()
        except Exception as e:
            raise ValidationError(f'备料完成操作失败：{str(e)}')

    def start_production(self):
        """开始生产"""
        if self.status != 'material_ready':
            raise ValidationError('只能开始备料完成状态的订单')
        
        try:
            with transaction.atomic():  # type: ignore
                # 扣减材料库存
                self.consume_materials()
                
                self.status = 'in_production'
                self.actual_start_date = timezone.now()
                self.save()
        except Exception as e:
            raise ValidationError(f'开始生产操作失败：{str(e)}')

    def record_progress(self, completed_quantity, notes=''):
        """记录生产进度"""
        if self.status != 'in_production':
            raise ValidationError('只能记录生产中订单的进度')
        
        if completed_quantity <= 0:
            raise ValidationError('完成数量必须大于0')
        
        try:
            with transaction.atomic():  # type: ignore
                # 创建进度记录
                # ProductionProgress.save() 方法会自动更新生产订单的completed_quantity
                progress = self.progress_records.create(
                    quantity=completed_quantity,
                    notes=notes
                )
                
                # 不需要在这里手动更新completed_quantity，因为ProductionProgress.save()已经处理了
                
                return progress
        except Exception as e:
            raise ValidationError(f'记录进度失败：{str(e)}')

    def cancel_progress(self, progress_id):
        """撤销进度记录"""
        try:
            with transaction.atomic():  # type: ignore
                progress = self.progress_records.get(id=progress_id)
                
                # 检查是否是最新的记录
                if progress != self.progress_records.latest('created_at'):
                    raise ValidationError('只能撤销最新的进度记录')
                
                # 更新总完成数量
                self.completed_quantity -= progress.quantity
                self.save()
                
                # 删除进度记录
                progress.delete()
        except Exception as e:
            raise ValidationError(f'撤销进度失败：{str(e)}')

    def complete_production(self, completed_quantity):
        """完成生产"""
        if self.status != 'in_production':
            raise ValidationError('只能完成生产中状态的订单')
        
        try:
            with transaction.atomic():  # type: ignore
                # 注意：产品入库记录的创建已移至信号处理函数中
                # 避免重复创建入库记录
                
                self.status = 'completed'
                self.actual_end_date = timezone.now()
                self.completed_quantity = completed_quantity
                self.save()
        except Exception as e:
            raise ValidationError(f'完成生产操作失败：{str(e)}')

    def consume_materials(self):
        """领用生产材料"""
        material_requirements = self.material_requirements.all()
        
        if not material_requirements.exists():
            raise ValidationError('未设置物料清单，无法领料')

        try:
            with transaction.atomic():  # type: ignore
                for requirement in material_requirements:
                    # 检查库存是否足够
                    if requirement.material.stock < requirement.required_quantity:
                        raise ValidationError(
                            f'材料 {requirement.material.name} 库存不足，'
                            f'需要 {requirement.required_quantity}，'
                            f'当前库存 {requirement.material.stock}'
                        )

                    # 获取可用的材料批次，按先进先出原则排序
                    available_batches = requirement.material.batches.filter(
                        remaining_quantity__gt=0,
                        status='normal'
                    ).order_by('production_date')
                    
                    if not available_batches.exists():
                        raise ValidationError(f'材料 {requirement.material.name} 没有可用批次')
                    
                    remaining_quantity = requirement.required_quantity
                    
                    # 从多个批次中领料
                    for batch in available_batches:
                        if remaining_quantity <= 0:
                            break
                            
                        # 确定从当前批次领用的数量
                        quantity_from_batch = min(batch.remaining_quantity, remaining_quantity)
                        
                        # 创建材料出库记录，关联批次
                        MaterialMovement.objects.create(
                            material=requirement.material,
                            movement_type='out',
                            quantity=quantity_from_batch,
                            unit=requirement.material.unit,
                            reference_number=self.order_number,
                            notes=f'生产领料：{self.order_number}',
                            batch=batch  # 关联批次
                        )
                        
                        # 创建生产用料记录
                        ProductionMaterial.objects.create(
                            production_order=self,
                            material_batch=batch,
                            quantity_used=quantity_from_batch
                        )
                        
                        # 更新剩余需求量
                        remaining_quantity -= quantity_from_batch
                    
                    # 如果仍有未满足的需求量，抛出异常
                    if remaining_quantity > 0:
                        raise ValidationError(
                            f'材料 {requirement.material.name} 可用批次库存不足，'
                            f'还需要 {remaining_quantity}'
                        )

                    # 记录实际领用数量
                    requirement.actual_quantity = requirement.required_quantity
                    requirement.save()

        except Exception as e:
            raise ValidationError(f'领料失败：{str(e)}')

    def update_progress(self, quantity):
        """更新生产进度"""
        if self.status != 'in_production':
            raise ValidationError('只能更新生产中的订单进度')
            
        if quantity <= 0:
            raise ValidationError('生产数量必须大于0')

        try:
            with transaction.atomic():  # type: ignore
                # 不再在这里创建进度记录，由视图函数负责创建
                # 这个方法只负责状态检查
                pass
                
        except Exception as e:
            raise ValidationError(f'更新进度失败：{str(e)}')

    def get_print_url(self):
        """获取打印URL"""
        return reverse('admin:production_productionorder_print', args=[self.pk])

    def cancel_completion(self):
        """撤销完成状态"""
        if self.status != 'completed':
            raise ValidationError('只能撤销已完成状态的生产单')
        
        try:
            with transaction.atomic():  # type: ignore
                # 创建出库记录
                ProductMovement.objects.create(
                    product=self.product,
                    movement_type='out',
                    quantity=self.completed_quantity,
                    unit=self.product.unit,  # type: ignore
                    reference_number=self.order_number,
                    notes=f'撤销生产完成 - 生产单号：{self.order_number}'
                )
                # ProductMovement 的 save 方法会自动更新产品库存
                
                # 恢复状态
                self.status = 'in_production'
                self.actual_end_date = None
                self.save()
                
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f'撤销完成失败：{str(e)}')

    def calculate_delay_days(self):
        if self.actual_end_date and self.end_date:
            return (self.actual_end_date - self.end_date).days  # type: ignore
        return 0

    def calculate_process_schedules(self):
        """计算并生成工序排程"""
        try:
            process_steps = ProcessStep.objects.all().order_by('sequence')
            if not process_steps.exists():
                raise ValidationError('没有找到工序步骤配置，请先配置工序步骤')
            
            # 使用Python的datetime模块而不是Django的timezone
            from datetime import datetime, timedelta
            current_time = datetime.now()
            work_hours_per_day = 10  # 标准工作时间：10小时/天
            
            for step in process_steps:
                if step.daily_capacity <= 0:
                    raise ValidationError(f'工序 {step.name} 的日产能必须大于0')
                
                # 计算该工序需要的时间
                quantity = float(str(self.planned_quantity))
                # 根据日产能计算所需天数，向上取整
                import math
                days_needed = math.ceil(quantity / step.daily_capacity)
                # 转换为小时
                hours_needed = days_needed * work_hours_per_day
                
                # 创建工序排程
                ProcessSchedule.objects.create(
                    production_order=self,
                    process=step,
                    planned_start_time=current_time,
                    planned_end_time=current_time + timedelta(hours=hours_needed),
                    status='pending'
                )
                
                # 更新下一工序的开始时间
                current_time = current_time + timedelta(hours=hours_needed)
            
        except Exception as e:
            raise ValidationError(f'生成工序排程失败：{str(e)}')

    def clean(self):
        """验证模型数据"""
        super().clean()
        
        # 验证销售订单唯一性
        if self.sales_order:
            existing_orders = ProductionOrder.objects.filter(sales_order=self.sales_order)
            if self.pk:  # 如果是更新现有记录
                existing_orders = existing_orders.exclude(pk=self.pk)
            if existing_orders.exists():
                raise ValidationError({'sales_order': f'销售订单 {self.sales_order.order_number} 已经有关联的生产单，不能重复创建'})  # type: ignore

    class Meta:
        verbose_name = '生产订单'
        verbose_name_plural = '生产订单'
        ordering = ['-created_at']

class MaterialRequirement(models.Model):
    """材料需求清单"""
    objects = models.Manager()  # 显式声明管理器
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.CASCADE,
        related_name='material_requirements',
        verbose_name='生产订单'
    )
    material = models.ForeignKey(
        'inventory.Material',
        on_delete=models.PROTECT,
        verbose_name='材料'
    )
    required_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='需求数量'
    )
    actual_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='实际领用数量'
    )
    notes = models.TextField(blank=True, verbose_name='备注')

    def __str__(self):
        return f"{self.production_order.order_number} - {self.material.name}"  # type: ignore

    class Meta:
        verbose_name = '材料需求'
        verbose_name_plural = '材料需求'
        unique_together = ['production_order', 'material']

class ProductionProgress(models.Model):
    """生产进度记录"""
    objects = models.Manager()  # 显式声明管理器
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.CASCADE,
        related_name='progress_records',
        verbose_name='生产订单'
    )
    record_date = models.DateField(
        verbose_name='记录日期',
        default=timezone.now
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='本次数量',
        default=Decimal('0.00')
    )
    accumulated_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='累计数量',
        default=Decimal('0.00')
    )
    progress = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='进度(%)',
        default=Decimal('0.00')
    )
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    can_edit = models.BooleanField(default=True, verbose_name='可修改')  # type: ignore
    actual_efficiency = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='实际效率',
        help_text='实际完成数量/计划数量的百分比'
    )
    delay_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name='延迟原因'
    )
    quality_issues = models.IntegerField(
        default=0,  # type: ignore
        verbose_name='质量问题数量'
    )
    
    def save(self, *args, **kwargs):
        if not self.pk:  # 新记录
            # 获取之前的累计数量
            previous_record = ProductionProgress.objects.filter(
                production_order=self.production_order
            ).order_by('-created_at').first()
            
            previous_quantity = Decimal('0.00')
            if previous_record:
                previous_quantity = previous_record.accumulated_quantity
            
            # 计算新的累计数量
            self.accumulated_quantity = previous_quantity + Decimal(str(self.quantity))
            
            # 计算进度
            self.progress = (self.accumulated_quantity / self.production_order.planned_quantity) * 100  # type: ignore
            
            # 更新生产订单的完成数量
            self.production_order.completed_quantity = self.accumulated_quantity  # type: ignore
            self.production_order.progress = self.progress  # type: ignore
            self.production_order.save()  # type: ignore
        
        super().save(*args, **kwargs)

    def cancel(self):
        """撤销进度记录"""
        if not self.can_edit:
            raise ValidationError('该记录已不能修改')
            
        try:
            with transaction.atomic():
                # 获取后续记录
                later_records = ProductionProgress.objects.filter(
                    production_order=self.production_order,
                    created_at__gt=self.created_at
                )
                
                if later_records.exists():
                    raise ValidationError('存在更新的进度记录，请先撤销最新的记录')
                
                # 获取前一条记录
                previous_record = ProductionProgress.objects.filter(
                    production_order=self.production_order,
                    created_at__lt=self.created_at
                ).order_by('-created_at').first()
                
                # 更新生产订单的完成数量和进度
                self.production_order.completed_quantity = (
                    previous_record.accumulated_quantity if previous_record 
                    else Decimal('0.00')
                )
                self.production_order.progress = (
                    previous_record.progress if previous_record 
                    else Decimal('0.00')
                )
                self.production_order.save()
                
                # 删除当前记录
                self.delete()
                
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f'撤销失败：{str(e)}')

    def calculate_efficiency(self):
        if self.production_order.planned_quantity:
            return (self.accumulated_quantity / self.production_order.planned_quantity) * 100
        return 0

    class Meta:
        verbose_name = '生产进度'
        verbose_name_plural = '生产进度'
        ordering = ['-record_date']

class ProductionMaterial(models.Model):
    """生产用料记录"""
    objects = models.Manager()  # 显式声明管理器
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.PROTECT,
        related_name='materials_used',
        verbose_name='生产单'
    )
    material_batch = models.ForeignKey(
        'inventory.MaterialBatch',
        on_delete=models.PROTECT,
        verbose_name='材料批次'
    )
    quantity_used = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='使用数量'
    )

    class Meta:
        verbose_name = '生产用料'
        verbose_name_plural = '生产用料'

class ProcessStep(models.Model):
    """工序步骤"""
    objects = models.Manager()  # 显式声明管理器
    name = models.CharField(max_length=50, verbose_name='工序名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='工序编码')
    daily_capacity = models.IntegerField(verbose_name='日产能')
    is_bottleneck = models.BooleanField(default=False, verbose_name='是否瓶颈工序')
    sequence = models.IntegerField(verbose_name='序号')
    notes = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '工序'
        verbose_name_plural = '工序'
        ordering = ['sequence']

    def __str__(self):
        return f"{self.name} ({self.code})"

class ProcessSchedule(models.Model):
    """工序排程"""
    objects = models.Manager()  # 显式声明管理器
    STATUS_CHOICES = [
        ('pending', '待开始'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('delayed', '延迟')
    ]

    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.CASCADE,
        related_name='process_schedules',
        verbose_name='生产订单'
    )
    process = models.ForeignKey(
        ProcessStep,
        on_delete=models.PROTECT,
        verbose_name='工序'
    )
    planned_start_time = models.DateTimeField('计划开始时间')
    planned_end_time = models.DateTimeField('计划结束时间')
    actual_start_time = models.DateTimeField('实际开始时间', null=True, blank=True)
    actual_end_time = models.DateTimeField('实际结束时间', null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态'
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='设备'
    )
    operator = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='操作员'
    )

    class Meta:
        ordering = ['planned_start_time']
        verbose_name = '工序排程'
        verbose_name_plural = '工序排程'