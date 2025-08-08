# type: ignore
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from decimal import Decimal
from inventory.models import Product, ProductMovement
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

class Customer(models.Model):
    """客户"""
    objects = models.Manager()  # 显式声明管理器
    code = models.CharField(max_length=50, unique=True, verbose_name='客户编码')
    name = models.CharField(max_length=100, verbose_name='客户名称')
    contact = models.CharField(max_length=50, blank=True, verbose_name='联系人')
    phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')
    address = models.TextField(blank=True, verbose_name='地址')
    email = models.EmailField(blank=True, verbose_name='邮箱')
    notes = models.TextField(blank=True, verbose_name='备注')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = '客户'
        verbose_name_plural = '客户'
        ordering = ['code']

class Order(models.Model):
    """订单"""
    objects = models.Manager()  # 显式声明管理器
    class DoesNotExist(Exception):  # 显式声明异常类
        pass
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '生产中'),
        ('completed', '已完成'),
        ('shipped', '已发货'),
        ('cancelled', '已取消')
    ]
    
    order_number = models.CharField(max_length=50, unique=True, verbose_name='订单编号')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name='客户')
    order_date = models.DateField(verbose_name='下单日期')
    delivery_date = models.DateField(verbose_name='交货日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                            default='pending', verbose_name='状态')
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    customer_order_number = models.CharField(max_length=50, verbose_name='客户订单号')
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='创建人'
    )

    def __str__(self):
        return self.order_number

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-order_date']

@receiver(pre_save, sender=Order)
def handle_order_status_change(sender, instance, **kwargs):
    """处理订单状态变更"""
    try:
        old_instance = Order.objects.get(pk=instance.pk)
        old_status = old_instance.status
    except Order.DoesNotExist:
        old_status = None
    
    new_status = instance.status
    
    if old_status == 'completed' and new_status == 'processing':
        # 从生产完成回退到生产中，需要撤销入库记录
        movements = ProductMovement.objects.filter(
            reference_number=instance.order_number,
            movement_type='in',
            notes__contains='生产完成入库'
        )
        for movement in movements:
            # 先恢复产品的库存数量
            product = movement.product
            product.stock -= movement.quantity
            product.save()
            # 然后删除入库记录
            movement.delete()
            
    elif old_status == 'shipped' and new_status in ['completed', 'processing']:
        # 从已发货回退，需要撤销出库记录
        movements = ProductMovement.objects.filter(
            reference_number=instance.order_number,
            movement_type='out',
            notes__contains='订单发货出库'
        )
        for movement in movements:
            # 先恢复产品的库存数量
            product = movement.product
            product.stock += movement.quantity
            product.save()
            # 然后删除出库记录
            movement.delete()
            
        # 如果回退到生产完成，需要重新创建入库记录
        if new_status == 'completed':
            for item in instance.items.all():
                ProductMovement.objects.create(
                    product=item.product,
                    movement_type='in',
                    quantity=item.quantity,
                    reference_number=instance.order_number,
                    notes=f'生产完成入库（状态回退） - 订单号：{instance.order_number}'
                )
                # 更新产品库存
                product = item.product
                product.stock += item.quantity
                product.save()
    
    # 处理正常的状态推进
    elif new_status == 'completed':
        # 检查是否已经有入库记录
        existing_movement = ProductMovement.objects.filter(
            reference_number=instance.order_number,
            movement_type='in',
            notes__contains='生产完成入库'
        ).exists()
        
        if not existing_movement:
            # 生产完成时，增加产品库存
            for item in instance.items.all():
                ProductMovement.objects.create(
                    product=item.product,
                    movement_type='in',
                    quantity=item.quantity,
                    reference_number=instance.order_number,
                    notes=f'生产完成入库 - 订单号：{instance.order_number}'
                )
                # 更新产品库存
                product = item.product
                product.stock += item.quantity
                product.save()
    
    elif new_status == 'shipped':
        # 检查是否已经有出库记录
        existing_movement = ProductMovement.objects.filter(
            reference_number=instance.order_number,
            movement_type='out',
            notes__contains='订单发货出库'
        ).exists()
        
        if not existing_movement:
            # 发货时，减少产品库存
            for item in instance.items.all():
                ProductMovement.objects.create(
                    product=item.product,
                    movement_type='out',
                    quantity=item.quantity,
                    reference_number=instance.order_number,
                    notes=f'订单发货出库 - 订单号：{instance.order_number}'
                )
                # 更新产品库存
                product = item.product
                product.stock -= item.quantity
                product.save()

class OrderItem(models.Model):
    """订单明细"""
    objects = models.Manager()  # 显式声明管理器
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='订单')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='产品')
    color = models.CharField(max_length=50, blank=True, verbose_name='颜色')
    material = models.CharField(max_length=50, blank=True, verbose_name='材料')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='数量')
    unit = models.CharField(max_length=20, verbose_name='单位')
    notes = models.TextField(blank=True, verbose_name='备注')

    def __str__(self):
        return f"{self.order.order_number} - {self.product.name}"

    class Meta:
        verbose_name = '订单明细'
        verbose_name_plural = '订单明细'
        unique_together = ['order', 'product']