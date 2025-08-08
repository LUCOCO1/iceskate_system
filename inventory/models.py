# type: ignore
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from decimal import Decimal
from django.utils import timezone
import datetime
from django.db import transaction
from django.db.models import Sum, Max
from django.urls import reverse

class Material(models.Model):
    """材料"""
    objects = models.Manager()  # 显式声明管理器
    code = models.CharField(max_length=50, unique=True, verbose_name='材料编码')
    name = models.CharField(max_length=100, verbose_name='材料名称')
    specification = models.CharField(max_length=200, blank=True, verbose_name='规格')
    dimensions = models.CharField(max_length=100, verbose_name='尺寸', null=True, blank=True)
    supply_method = models.CharField(max_length=50, verbose_name='来料方式', null=True, blank=True)
    unit = models.CharField(max_length=20, verbose_name='单位')
    stock = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='库存')
    min_stock = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='最小库存')
    warning_stock = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='预警库存'
    )
    max_stock = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='最大库存'
    )
    last_purchase_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='最近采购价'
    )
    notes = models.TextField(blank=True, verbose_name='备注')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = '材料'
        verbose_name_plural = '材料'
        ordering = ['code']

    def get_stock_status(self):
        """获取库存状态"""
        if self.stock <= self.min_stock:
            return 'danger', '库存不足'
        elif self.stock <= self.warning_stock:
            return 'warning', '库存预警'
        elif self.stock >= self.max_stock:
            return 'info', '库存过高'
        return 'normal', '正常'
    
    def should_send_alert(self):
        """判断是否需要发送预警"""
        status, _ = self.get_stock_status()
        return status in ['danger', 'warning']

class MaterialMovement(models.Model):
    """原材料变动记录"""
    objects = models.Manager()  # 显式声明管理器
    MOVEMENT_TYPES = [
        ('in', '入库'),
        ('out', '出库'),
        ('adjust', '调整'),
    ]
    
    material = models.ForeignKey(Material, on_delete=models.PROTECT, verbose_name='材料')
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES, verbose_name='变动类型')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='数量')
    unit = models.CharField(max_length=20, verbose_name='单位')
    movement_date = models.DateTimeField(auto_now_add=True, verbose_name='变动时间')
    reference_number = models.CharField(max_length=50, blank=True, verbose_name='关联单号')
    purchase = models.ForeignKey(
        'MaterialPurchase',
        on_delete=models.CASCADE,  # 采购单删除时同步删除相关记录
        related_name='materialmovements',
        null=True,
        blank=True,
        verbose_name='采购单'
    )
    notes = models.TextField(blank=True, verbose_name='备注')
    operator = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='操作人'
    )
    location = models.CharField(
        max_length=50,
        verbose_name='库位',
        blank=True
    )
    batch = models.ForeignKey(
        'MaterialBatch',
        on_delete=models.CASCADE,  # 改为 CASCADE，这样删除批次时会同步删除相关的变动记录
        null=True,
        blank=True,
        verbose_name='批次'
    )

    def save(self, *args, **kwargs):
        is_new = not self.pk  # 判断是否新记录
        
        if is_new:  # 只在创建新记录时更新库存
            with transaction.atomic():
                # 更新材料库存
                if self.movement_type == 'in':
                    self.material.stock += self.quantity
                elif self.movement_type == 'out':
                    if self.material.stock < self.quantity:
                        raise ValidationError(f'库存不足，当前库存: {self.material.stock}, 需要: {self.quantity}')
                    self.material.stock -= self.quantity
                elif self.movement_type == 'adjust':
                    # 调整不改变库存，由调整单独处理
                    pass
                
                self.material.save()
                # 保存变动记录
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.material.name} - {self.get_movement_type_display()} - {self.quantity}{self.unit}"

    class Meta:
        verbose_name = '材料变动'
        verbose_name_plural = '材料变动'
        ordering = ['-movement_date']

class Supplier(models.Model):
    """供应商"""
    objects = models.Manager()  # 显式声明管理器
    name = models.CharField(max_length=100, verbose_name='名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='编码')
    contact = models.CharField(max_length=50, blank=True, verbose_name='联系人')
    phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')
    address = models.TextField(blank=True, verbose_name='地址')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    notes = models.TextField(blank=True, verbose_name='备注')

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = '供应商'
        verbose_name_plural = '供应商'
        ordering = ['code']

class MaterialPurchase(models.Model):
    """材料采购单"""
    objects = models.Manager()  # 显式声明管理器
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('pending', '待入库'),
        ('received', '已入库'),
        ('completed', '已完成'),
        ('cancelled', '已取消')
    ]
    
    purchase_number = models.CharField(max_length=50, unique=True, verbose_name='采购单号')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='供应商')
    purchase_date = models.DateField(verbose_name='采购日期')
    delivery_date = models.DateField(verbose_name='交货日期', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 保存原始状态，用于检测状态变化
        self._original_status = self.status if self.pk else None

    def __str__(self):
        return self.purchase_number

    def delete(self, *args, **kwargs):
        """重写删除方法，确保关联数据一起删除"""
        from django.db import transaction
        with transaction.atomic():
            # 删除相关的入库记录（会触发库存回滚）
            self.materialmovements.all().delete()
            # 删除采购单
            super().delete(*args, **kwargs)

    def receive_materials(self):
        """处理采购单入库"""
        if self.status != 'pending':
            raise ValidationError('只能对待入库状态的采购单进行入库操作')
        
        # 检查是否已经有入库记录
        if MaterialMovement.objects.filter(purchase=self, movement_type='in').exists():
            raise ValidationError('该采购单已有入库记录，请先撤销入库')
        
        try:
            with transaction.atomic():
                for item in self.items.all():
                    # 创建材料批次
                    batch = MaterialBatch.objects.create(
                        material=item.material,
                        batch_number=f"{self.purchase_number}-{item.id}",
                        purchase=self,
                        production_date=timezone.now().date(),
                        initial_quantity=item.quantity,
                        remaining_quantity=item.quantity
                    )
                    
                    # 创建入库记录 - 这会通过MaterialMovement的save方法自动更新库存
                    MaterialMovement.objects.create(
                        material=item.material,
                        movement_type='in',
                        quantity=item.quantity,
                        unit=item.unit,
                        reference_number=self.purchase_number,
                        purchase=self,
                        batch=batch,
                        notes=f'采购入库：{self.purchase_number}'
                    )
                    
                    # 不需要再次更新库存，因为MaterialMovement的save方法已经更新过库存了
                    # item.material.stock += item.quantity
                    # item.material.save()
                    
                    # 更新采购项的已入库数量
                    item.received_quantity = item.quantity
                    item.save()
                
                # 更新采购单状态
                self.status = 'received'
                self.save()
                
        except Exception as e:
            raise ValidationError(f'入库处理失败：{str(e)}')

    def cancel_inbound(self):
        """撤销入库"""
        try:
            with transaction.atomic():
                # 检查批次是否已被用于生产
                used_batches = self.material_batches.filter(
                    productionmaterial__isnull=False
                )
                if used_batches.exists():
                    raise ValidationError(
                        f'以下批次已用于生产，无法撤销：'
                        f'{", ".join([b.batch_number for b in used_batches])}'
                    )

                # 获取相关的所有入库记录
                inbound_movements = MaterialMovement.objects.filter(
                    purchase=self, 
                    movement_type='in'
                )
                
                if not inbound_movements.exists():
                    raise ValidationError('未找到相关入库记录')
                
                for movement in inbound_movements:
                    # 检查库存是否足够
                    if movement.material.stock < movement.quantity:
                        raise ValidationError(
                            f'材料 {movement.material.name} 当前库存不足，无法撤销。'
                            f'需要: {movement.quantity}, '
                            f'当前库存: {movement.material.stock}'
                        )

                    # 不需要手动更新库存，MaterialMovement.save会自动处理
                    # movement.material.stock -= movement.quantity
                    # movement.material.save()

                    # 创建出库记录 - 这会通过MaterialMovement的save方法自动减少库存
                    MaterialMovement.objects.create(
                        material=movement.material,
                        movement_type='out',
                        quantity=movement.quantity,
                        unit=movement.unit,
                        reference_number=self.purchase_number,
                        purchase=self,
                        notes=f'撤销入库：{self.purchase_number}'
                    )
                
                # 删除批次记录
                self.material_batches.all().delete()
                
                # 重置采购项的已入库数量
                for item in self.items.all():
                    item.received_quantity = Decimal('0.00')
                    item.save()

                # 更新状态
                self.status = 'pending'
                self.save()

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f'撤销入库失败：{str(e)}')

    def cancel_receive(self):
        return self.cancel_inbound()

    class Meta:
        verbose_name = '采购单'
        verbose_name_plural = '采购单'
        ordering = ['-purchase_date']

@receiver(post_save, sender=MaterialPurchase)
def update_original_status(sender, instance, **kwargs):
    """更新原始状态"""
    instance._original_status = instance.status

class PurchaseItem(models.Model):
    """采购单明细"""
    objects = models.Manager()  # 显式声明管理器
    purchase = models.ForeignKey(MaterialPurchase, on_delete=models.CASCADE, 
                               related_name='items', verbose_name='采购单')
    material = models.ForeignKey(Material, on_delete=models.PROTECT, verbose_name='材料')
    control_number = models.CharField(max_length=50, verbose_name='管制编号')
    specification = models.CharField(max_length=100, verbose_name='规格尺寸')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='数量')
    received_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='已入库数量'
    )
    unit = models.CharField(max_length=20, verbose_name='单位')
    material_type = models.CharField(
        max_length=20,
        default='平板料',
        verbose_name='采料方式'
    )
    notes = models.TextField(blank=True, verbose_name='备注')

    def __str__(self):
        return f"{self.purchase.purchase_number} - {self.material.name}"

    class Meta:
        verbose_name = '采购明细'
        verbose_name_plural = '采购明细'
        unique_together = ['purchase', 'material']

    def clean(self):
        """数据验证"""
        if self.quantity <= 0:
            raise ValidationError('数量必须大于0')
        if self.received_quantity > self.quantity:
            raise ValidationError('已入库数量不能大于采购数量')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

@receiver(pre_delete, sender=MaterialPurchase)
def reverse_material_purchase(sender, instance, **kwargs):
    """在删除采购单时回滚库存"""
    if instance.status == 'received':
        for item in instance.items.all():
            # 创建出库记录
            MaterialMovement.objects.create(
                material=item.material,
                movement_type='out',
                quantity=item.quantity,
                unit=item.unit,
                reference_number=instance.purchase_number,
                notes=f'采购单删除：{instance.purchase_number}'
            )
            
            # 更新材料库存
            material = item.material
            material.stock -= item.quantity
            material.save()

# 在订单状态变为生产中时自动扣减原材料
@receiver(post_save, sender='orders.Order')
def handle_order_material_consumption(sender, instance, **kwargs):
    """处理订单原材料消耗"""
    if not hasattr(instance, '_original_status'):
        return
        
    old_status = instance._original_status
    new_status = instance.status
    
    if old_status == new_status:
        return
    
    # 当订单状态变为生产中时，扣减原材料
    if new_status == 'processing':
        for item in instance.items.all():
            # 获取产品所需的原材料清单
            material_requirements = item.product.productmaterial_set.all()
            for requirement in material_requirements:
                # 计算所需原材料总量
                total_needed = requirement.quantity * item.quantity
                # 创建原材料出库记录
                MaterialMovement.objects.create(
                    material=requirement.material,
                    movement_type='out',
                    quantity=total_needed,
                    order=instance,
                    notes=f'生产领料 - 订单号：{instance.order_number}'
                )

class MaterialBatch(models.Model):
    """材料批次"""
    objects = models.Manager()  # 显式声明管理器
    material = models.ForeignKey(
        Material, 
        on_delete=models.PROTECT,
        related_name='batches',
        verbose_name='材料'
    )
    batch_number = models.CharField(max_length=50, verbose_name='批次号')
    purchase = models.ForeignKey(
        'MaterialPurchase',
        on_delete=models.CASCADE,  # 修改为 CASCADE，允许随采购单一起删除
        related_name='material_batches',
        verbose_name='采购单'
    )
    production_date = models.DateField(
        verbose_name='生产日期',
        default='2025-01-01'
    )
    expiry_date = models.DateField(
        verbose_name='有效期',
        null=True,
        blank=True
    )
    initial_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='初始数量'
    )
    remaining_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='剩余数量'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('normal', '正常'),
            ('expired', '已过期'),
            ('depleted', '已耗尽'),
        ],
        default='normal',
        verbose_name='状态'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return f"{self.material.name} - {self.batch_number}"

    class Meta:
        verbose_name = '材料批次'
        verbose_name_plural = '材料批次'

class Inventory(models.Model):
    """库存盘点"""
    objects = models.Manager()  # 显式声明管理器
    INVENTORY_STATUS = [
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('cancelled', '已取消')
    ]
    
    inventory_number = models.CharField(max_length=50, unique=True, verbose_name='盘点单号')
    inventory_date = models.DateField(verbose_name='盘点日期')
    status = models.CharField(
        max_length=20, 
        choices=INVENTORY_STATUS,
        default='draft',
        verbose_name='状态'
    )
    adjustment_type = models.CharField(
        max_length=20,
        choices=[
            ('profit', '盘盈'),
            ('loss', '盘亏'),
            ('normal', '正常')
        ],
        default='normal',
        verbose_name='盘点类型'
    )
    total_difference = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='差异总量'
    )
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        related_name='inventories',
        verbose_name='创建人'
    )

    def calculate_differences(self):
        """计算盘点差异"""
        total_diff = 0
        for item in self.items.all():
            diff = item.actual_quantity - item.system_quantity
            item.difference = diff
            item.save()
            total_diff += diff
        self.total_difference = total_diff
        self.adjustment_type = 'profit' if total_diff > 0 else 'loss' if total_diff < 0 else 'normal'
        self.save()

    class Meta:
        verbose_name = '库存盘点'
        verbose_name_plural = '库存盘点'
        ordering = ['-inventory_date']

class InventoryItem(models.Model):
    """盘点明细"""
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='盘点单'
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        verbose_name='材料'
    )
    system_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='系统数量'
    )
    actual_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='实际数量'
    )
    difference = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='差异数量'
    )
    notes = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        verbose_name = '盘点明细'
        verbose_name_plural = '盘点明细'

class Product(models.Model):
    """产品"""
    objects = models.Manager()  # 显式声明管理器
    name = models.CharField(max_length=100, verbose_name='产品名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='产品编码')
    specification = models.CharField(max_length=200, blank=True, verbose_name='规格')
    unit = models.CharField(max_length=20, verbose_name='单位')
    unit_weight = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        default=Decimal('0.000'),
        verbose_name='单重(kg)',
        help_text='产品单件重量，用于计算材料需求量'
    )
    stock = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='库存数量'
    )
    min_stock = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='最小库存')
    warning_stock = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='预警库存'
    )
    max_stock = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='最大库存'
    )
    customers = models.ManyToManyField(
        'orders.Customer',
        blank=True,
        verbose_name='关联客户',
        help_text='选择该产品关联的客户'
    )
    notes = models.TextField(blank=True, verbose_name='备注')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    def __str__(self):
        # 修改这里，返回中文名称
        return f"{self.name} ({self.specification})" if self.specification else self.name

    class Meta:
        verbose_name = '产品'
        verbose_name_plural = '产品'
        ordering = ['code']

    def update_stock(self, quantity, movement_type):
        """更新库存"""
        with transaction.atomic():
            if movement_type == 'in':
                self.stock += quantity
            elif movement_type == 'out':
                if self.stock < quantity:
                    raise ValidationError(f'库存不足，当前库存: {self.stock}, 需要: {quantity}')
                self.stock -= quantity
            self.save()

class ProductMovement(models.Model):
    """产品变动记录"""
    objects = models.Manager()  # 显式声明管理器
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='产品')
    movement_type = models.CharField(
        max_length=10,
        choices=[('in', '入库'), ('out', '出库')],
        verbose_name='变动类型'
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='数量')
    unit = models.CharField(max_length=20, verbose_name='单位')
    movement_date = models.DateTimeField(auto_now_add=True, verbose_name='变动时间')
    reference_number = models.CharField(max_length=50, verbose_name='关联单号')
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def save(self, *args, **kwargs):
        is_new = not self.pk  # 判断是否新记录
        
        if is_new:  # 只在创建新记录时更新库存
            with transaction.atomic():
                # 更新产品库存
                self.product.update_stock(self.quantity, self.movement_type)
                # 保存变动记录
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        """优化显示格式"""
        return f"{self.product.name} - {self.get_movement_type_display()} - {self.quantity}{self.unit} ({self.movement_date.strftime('%Y-%m-%d %H:%M')})"

    class Meta:
        verbose_name = '产品变动'
        verbose_name_plural = '产品变动'
        ordering = ['-movement_date']

class InventoryStatistics(models.Model):
    """库存统计"""
    date = models.DateField(
        verbose_name='统计日期',
        default='2025-01-01'
    )
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='材料')
    opening_stock = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='期初库存')
    incoming = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='入库量')
    outgoing = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='出库量')
    closing_stock = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='期末库存')
    
    class Meta:
        unique_together = ['date', 'material']
        verbose_name = '库存统计'
        verbose_name_plural = '库存统计'

class MaterialCost(models.Model):
    """材料成本"""
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='材料')
    date = models.DateField(
        verbose_name='日期',
        default='2025-01-01'
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='数量')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='总金额')
    
    class Meta:
        verbose_name = '材料成本'
        verbose_name_plural = '材料成本'

@receiver(post_save, sender=MaterialMovement)
def update_batch_quantity(sender, instance, **kwargs):
    """更新批次剩余数量"""
    if instance.batch:
        movements = MaterialMovement.objects.filter(batch=instance.batch)
        total_out = movements.filter(movement_type='out').aggregate(
            total=Sum('quantity'))['total'] or 0
        instance.batch.remaining_quantity = instance.batch.initial_quantity - total_out
        instance.batch.save()

class ProductOutbound(models.Model):
    """产品出库单"""
    objects = models.Manager()  # 显式声明管理器
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('cancelled', '已取消')
    ]
    
    outbound_number = models.CharField(max_length=50, unique=True, verbose_name='出库单号', blank=True)
    outbound_date = models.DateField(verbose_name='出库日期', default=timezone.now)
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.PROTECT,
        related_name='product_outbounds',
        null=True,
        blank=True,
        verbose_name='客户订单'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='状态'
    )
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='创建人'
    )

    def generate_outbound_number(self):
        """生成出库单号：日期+序号（如：20250626001）"""
        today = timezone.now().date()
        date_str = today.strftime('%Y%m%d')
        
        # 查询当天已有的出库单号，获取最大序号
        existing_numbers = ProductOutbound.objects.filter(
            outbound_date=today,
            outbound_number__startswith=date_str
        ).values_list('outbound_number', flat=True)
        
        max_sequence = 0
        for number in existing_numbers:
            try:
                # 提取序号部分（最后3位）
                sequence = int(number[-3:])
                max_sequence = max(max_sequence, sequence)
            except (ValueError, IndexError):
                continue
        
        # 生成新的序号
        new_sequence = max_sequence + 1
        return f"{date_str}{new_sequence:03d}"

    def save(self, *args, **kwargs):
        # 如果是新记录且没有出库单号，则自动生成
        if not self.pk and not self.outbound_number:
            self.outbound_number = self.generate_outbound_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.outbound_number

    def confirm_outbound(self):
        """确认出库"""
        if self.status != 'draft':
            raise ValidationError('只能确认草稿状态的出库单')
        
        if not self.items.exists():
            raise ValidationError('出库单没有明细，无法确认')
        
        try:
            with transaction.atomic():
                for item in self.items.all():
                    # 检查库存是否足够
                    if item.product.stock < item.quantity:
                        raise ValidationError(
                            f'产品 {item.product.name} 库存不足，'
                            f'需要 {item.quantity}，'
                            f'当前库存 {item.product.stock}'
                        )
                    
                    # 创建产品出库记录
                    ProductMovement.objects.create(
                        product=item.product,
                        movement_type='out',
                        quantity=item.quantity,
                        unit=item.product.unit,
                        reference_number=self.outbound_number,
                        notes=f'产品出库：{self.outbound_number}'
                    )
                
                # 更新出库单状态
                self.status = 'confirmed'
                self.save()
                
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f'确认出库失败：{str(e)}')
    
    def cancel_outbound(self):
        """取消出库"""
        if self.status != 'confirmed':
            raise ValidationError('只能取消已确认状态的出库单')
        
        try:
            with transaction.atomic():
                # 查找相关的产品变动记录
                movements = ProductMovement.objects.filter(
                    reference_number=self.outbound_number,
                    movement_type='out'
                )
                
                # 检查是否存在相关记录
                if not movements.exists():
                    raise ValidationError('未找到相关的出库记录')
                
                # 创建入库记录，恢复库存
                for movement in movements:
                    ProductMovement.objects.create(
                        product=movement.product,
                        movement_type='in',
                        quantity=movement.quantity,
                        unit=movement.unit,
                        reference_number=f'撤销-{self.outbound_number}',
                        notes=f'撤销出库：{self.outbound_number}'
                    )
                
                # 更新状态
                self.status = 'cancelled'
                self.save()
                
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f'取消出库失败：{str(e)}')
    
    def get_print_url(self):
        """获取打印URL"""
        return reverse('inventory:print-outbound', args=[self.pk])
    
    class Meta:
        verbose_name = '产品出库单'
        verbose_name_plural = '产品出库单'
        ordering = ['-outbound_date']

class ProductOutboundItem(models.Model):
    """出库单明细"""
    objects = models.Manager()  # 显式声明管理器
    outbound = models.ForeignKey(
        ProductOutbound,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='出库单'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='产品'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='数量'
    )
    unit = models.CharField(max_length=20, verbose_name='单位')
    notes = models.TextField(blank=True, verbose_name='备注')
    
    def __str__(self):
        return f"{self.outbound.outbound_number} - {self.product.name}"
    
    def clean(self):
        """验证数据"""
        super().clean()
        
        # 设置单位与产品一致
        if self.product and not self.unit:
            self.unit = self.product.unit
    
    class Meta:
        verbose_name = '出库单明细'
        verbose_name_plural = '出库单明细'
        unique_together = ['outbound', 'product']