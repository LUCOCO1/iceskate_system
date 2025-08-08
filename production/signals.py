from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import ProductionOrder, ProcessSchedule
from inventory.models import ProductMovement
from django.db import transaction
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Sum

@receiver(pre_save, sender=ProductionOrder)
def handle_production_order_status_change(sender, instance, **kwargs):
    """处理生产订单状态变更"""
    try:
        # 获取原始对象
        if instance.pk:
            original = ProductionOrder.objects.get(pk=instance.pk)
            
            # 状态从生产中变更为已完成
            if original.status == 'in_production' and instance.status == 'completed':
                # 检查是否完成生产数量
                if instance.completed_quantity < instance.planned_quantity:
                    raise ValidationError('生产数量未达到计划数量，无法完成')
                
                # 设置实际完成日期
                if not instance.actual_end_date:
                    instance.actual_end_date = timezone.now().date()
                
                # 创建入库记录并更新库存
                with transaction.atomic():
                    ProductMovement.objects.create(
                        product=instance.product,
                        movement_type='in',
                        quantity=instance.completed_quantity,
                        unit=instance.product.unit,
                        reference_number=instance.order_number,
                        notes=f'生产完成入库 - 生产单号：{instance.order_number}'
                    )
            
            # 状态从其他状态变更为生产中
            elif instance.status == 'in_production' and original.status != 'in_production':
                # 设置实际开始日期
                if not instance.actual_start_date:
                    instance.actual_start_date = timezone.now().date()
            
    except ProductionOrder.DoesNotExist:
        pass

@receiver(post_save, sender=ProductionOrder)
def update_sales_order_status(sender, instance, **kwargs):
    """根据生产订单状态更新销售订单状态"""
    if not instance.sales_order:
        return
    
    sales_order = instance.sales_order
    
    # 根据生产订单状态更新销售订单状态
    if instance.status == 'in_production':
        # 生产开始时，销售订单状态变为生产中
        if sales_order.status == 'pending':
            sales_order.status = 'processing'
            sales_order.save()
    
    elif instance.status == 'completed':
        # 生产完成时，销售订单状态变为已完成
        if sales_order.status == 'processing':
            sales_order.status = 'completed'
            sales_order.save()

@receiver(post_save, sender=ProcessSchedule)
def check_capacity_warning(sender, instance, **kwargs):
    # 检查工序负荷
    process_load = calculate_process_load(instance.process)
    capacity_threshold = 90  # 设置90%为预警阈值
    
    if process_load > capacity_threshold:
        # 发送预警邮件
        send_mail(
            subject='产能预警通知',
            message=f'工序 {instance.process.name} 当前负荷率达到 {process_load}%，超过预警阈值',
            from_email='system@example.com',
            recipient_list=['manager@example.com'],
        ) 

def calculate_process_load(process):
    """计算工序负荷率"""
    # 获取当前日期
    today = timezone.now().date()
    
    # 计算当前工序的所有未完成任务的总工作量
    total_work = ProcessSchedule.objects.filter(
        process=process,
        status__in=['pending', 'in_progress'],
        planned_start_time__date__lte=today,
        planned_end_time__date__gte=today
    ).aggregate(
        total=Sum('production_order__planned_quantity')
    )['total'] or 0
    
    # 获取工序的日产能
    daily_capacity = process.daily_capacity
    
    # 计算负荷率
    if daily_capacity > 0:
        return (total_work / daily_capacity) * 100
    return 0 