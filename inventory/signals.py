from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import ProductOutbound, ProductOutboundItem, ProductMovement

@receiver(post_save, sender=ProductOutboundItem)
def handle_outbound_item_save(sender, instance, created, **kwargs):
    """
    处理出库单明细保存事件
    当出库单明细被创建或修改时，如果出库单状态为已确认，则自动更新产品库存
    """
    # 只处理已确认状态的出库单
    if instance.outbound.status == 'confirmed' and created:
        try:
            with transaction.atomic():
                # 检查库存是否足够
                if instance.product.stock < instance.quantity:
                    raise ValidationError(
                        f'产品 {instance.product.name} 库存不足，'
                        f'需要 {instance.quantity}，'
                        f'当前库存 {instance.product.stock}'
                    )
                
                # 创建产品出库记录
                ProductMovement.objects.create(
                    product=instance.product,
                    movement_type='out',
                    quantity=instance.quantity,
                    unit=instance.product.unit,
                    reference_number=instance.outbound.outbound_number,
                    notes=f'产品出库：{instance.outbound.outbound_number}'
                )
        except Exception as e:
            # 记录错误但不阻止保存
            print(f"出库单明细保存时出错: {str(e)}")

@receiver(pre_delete, sender=ProductOutboundItem)
def handle_outbound_item_delete(sender, instance, **kwargs):
    """
    处理出库单明细删除事件
    当出库单明细被删除时，如果出库单状态为已确认，则自动恢复产品库存
    """
    # 只处理已确认状态的出库单
    if instance.outbound.status == 'confirmed':
        try:
            with transaction.atomic():
                # 创建入库记录，恢复库存
                ProductMovement.objects.create(
                    product=instance.product,
                    movement_type='in',
                    quantity=instance.quantity,
                    unit=instance.product.unit,
                    reference_number=f'撤销-{instance.outbound.outbound_number}',
                    notes=f'撤销出库明细：{instance.outbound.outbound_number}'
                )
        except Exception as e:
            # 记录错误但不阻止删除
            print(f"出库单明细删除时出错: {str(e)}") 