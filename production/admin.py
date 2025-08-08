from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.html import format_html
from .models import (
    ProductionOrder,
    MaterialRequirement,
    ProductionProgress,
    ProductionMaterial,
    ProcessStep,
    ProcessSchedule,
    Equipment
)
from inventory.models import (  # 从 inventory 导入产品相关的模型
    Product,
    ProductMovement
)
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.template.response import TemplateResponse
from datetime import datetime, time
import traceback

class MaterialRequirementInline(admin.TabularInline):
    model = MaterialRequirement
    extra = 1
    fields = ['material', 'required_quantity', 'actual_quantity', 'notes']
    readonly_fields = ['actual_quantity']

class ProductionProgressInline(admin.TabularInline):
    model = ProductionProgress
    extra = 0
    readonly_fields = ['created_at']
    can_delete = False

class ProductionMaterialInline(admin.TabularInline):
    model = ProductionMaterial
    extra = 0
    readonly_fields = ['material_batch', 'quantity_used']
    can_delete = False

class ProcessScheduleInline(admin.TabularInline):
    model = ProcessSchedule
    extra = 0
    readonly_fields = ['actual_start_time', 'actual_end_time']
    fields = [
        'process',
        'planned_start_time',
        'planned_end_time',
        'actual_start_time',
        'actual_end_time',
        'status',
        'equipment',
        'operator'
    ]
    can_delete = False
    max_num = 0  # 防止手动添加

@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 
        'get_customer_order_number',
        'product', 
        'planned_quantity',
        'completed_quantity', 
        'progress',
        'priority',
        'status',
        'start_date',
        'end_date',
        'action_buttons'
    ]
    list_filter = ['status', 'priority', 'start_date', 'product']
    search_fields = ['order_number', 'product__name', 'notes', 'sales_order__customer_order_number']
    readonly_fields = ['completed_quantity', 'progress', 'actual_start_date', 
                      'actual_end_date', 'created_at', 'updated_at']
    inlines = [
        MaterialRequirementInline,
        ProductionProgressInline,
        ProductionMaterialInline,
        ProcessScheduleInline
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': (
                'order_number', 'sales_order', 'product', 'planned_quantity', 'status', 
                'priority', 'notes'
            )
        }),
        ('计划日期', {
            'fields': ('start_date', 'end_date')
        }),
        ('进度信息', {
            'fields': (
                'completed_quantity', 'progress', 'actual_start_date', 
                'actual_end_date'
            )
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_customer_order_number(self, obj):
        """获取客户订单号"""
        if obj.sales_order:
            return obj.sales_order.customer_order_number
        return '-'
    get_customer_order_number.short_description = '客户订单号'
    get_customer_order_number.admin_order_field = 'sales_order__customer_order_number'

    def action_buttons(self, obj):
        """显示操作按钮"""
        buttons = []
        
        # 草稿状态显示确认按钮
        if obj.status == 'pending':
            buttons.append(
                format_html(
                    '<a class="button" href="{}">备料完成</a>',
                    reverse('admin:production_productionorder_material_ready', args=[obj.pk])
                )
            )
        
        # 备料完成状态显示开始生产按钮
        elif obj.status == 'material_ready':
            buttons.append(
                format_html(
                    '<a class="button" href="{}">开始生产</a>',
                    reverse('admin:production_productionorder_start_production', args=[obj.pk])
                )
            )
        
        # 生产中状态显示更新进度和完成按钮
        elif obj.status == 'in_production':
            buttons.append(
                format_html(
                    '<a class="button" href="{}">记录进度</a>',
                    reverse('admin:production_productionorder_record_progress', args=[obj.pk])
                )
            )
            buttons.append(
                format_html(
                    '<a class="button" style="background-color: #28a745;" href="{}">完成生产</a>',
                    reverse('admin:production_productionorder_complete_production', args=[obj.pk])
                )
            )
        
        # 已完成状态显示撤销按钮
        elif obj.status == 'completed':
            buttons.append(
                format_html(
                    '<a class="button" style="background-color: #dc3545;" href="{}">撤销完成</a>',
                    reverse('admin:production_productionorder_cancel_completion', args=[obj.pk])
                )
            )
        
        # 非草稿状态显示打印按钮
        if obj.status != 'pending':
            buttons.append(
                format_html(
                    '<a class="button" href="{}">打印</a>',
                    reverse('admin:production_productionorder_print', args=[obj.pk])
                )
            )
        
        return format_html('&nbsp;'.join(buttons)) if buttons else '-'
    action_buttons.short_description = '操作'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'print/<int:object_id>/',
                self.admin_site.admin_view(self.print_order_view),
                name='production_productionorder_print'
            ),
            path(
                'complete/<int:object_id>/',
                self.admin_site.admin_view(self.complete_production_view),
                name='production_productionorder_complete_production'
            ),
            path(
                'update-progress/<int:order_id>/',
                self.admin_site.admin_view(self.update_progress_view),
                name='production_productionorder_update_progress'
            ),
            path(
                'cancel-completion/<int:object_id>/',
                self.admin_site.admin_view(self.cancel_completion_view),
                name='production_productionorder_cancel_completion'
            ),
            path(
                'confirm/<int:order_id>/',
                self.admin_site.admin_view(self.confirm_view),
                name='production_productionorder_confirm'
            ),
            path(
                'material-ready/<int:object_id>/',
                self.admin_site.admin_view(self.material_ready_view),
                name='production_productionorder_material_ready'
            ),
            path(
                'start-production/<int:object_id>/',
                self.admin_site.admin_view(self.start_production_view),
                name='production_productionorder_start_production'
            ),
            path(
                'record-progress/<int:object_id>/',
                self.admin_site.admin_view(self.record_progress_view),
                name='production_productionorder_record_progress'
            ),
            path(
                'create-from-order/',
                self.admin_site.admin_view(self.create_from_order_view),
                name='create-from-order'
            ),
        ]
        return custom_urls + urls
    
    def print_order_view(self, request, object_id):
        """打印生产单视图"""
        try:
            order = self.get_object(request, object_id)
            context = {
                'title': '打印生产单',
                'order': order,
                'opts': self.model._meta,
            }
            
            # 尝试渲染模板
            response = TemplateResponse(
                request,
                'admin/production/productionorder/print_production_order.html',
                context
            )
            
            return response
        except Exception as e:
            # 添加错误处理
            self.message_user(request, f'打印失败：{str(e)}', level='ERROR')
            return redirect('admin:production_productionorder_changelist')

    def complete_production_view(self, request, object_id):
        """完成生产视图"""
        order = self.get_object(request, object_id)
        
        if request.method == 'POST':
            try:
                completed_quantity = Decimal(request.POST.get('completed_quantity', 0))
                order.complete_production(completed_quantity)
                self.message_user(request, '生产完成')
                return redirect('admin:production_productionorder_change', object_id)
            except ValidationError as e:
                self.message_user(request, str(e), level='ERROR')
                return redirect('admin:production_productionorder_change', object_id)
        
        context = {
            'title': '确认完成生产',
            'object': order,
            'opts': self.model._meta,
        }
        
        return TemplateResponse(
            request,
            'admin/production/productionorder/complete_production.html',
            context
        )

    def update_progress_view(self, request, order_id):
        """更新进度视图"""
        order = get_object_or_404(ProductionOrder, id=order_id)
        
        if request.method == 'POST':
            try:
                # 确保转换为 Decimal 类型
                quantity = Decimal(str(request.POST.get('quantity', '0')))
                
                # 添加数值验证
                if quantity <= 0:
                    raise ValidationError('生产数量必须大于0')
                    
                # 创建进度记录（只在这里创建一次）
                ProductionProgress.objects.create(
                    production_order=order,
                    record_date=timezone.now().date(),
                    quantity=quantity,
                    notes=request.POST.get('notes', '')
                )
                
                self.message_user(request, '进度更新成功')
                return redirect('admin:production_productionorder_changelist')
            except ValidationError as e:
                self.message_user(request, str(e), level='ERROR')
            except Exception as e:
                self.message_user(request, f'更新失败：{str(e)}', level='ERROR')
        
        context = {
            'title': '更新生产进度',
            'order': order,
            'opts': self.model._meta,
        }
        return TemplateResponse(
            request,
            'admin/production/productionorder/update_progress.html',
            context
        )

    def cancel_completion_view(self, request, object_id):
        """撤销完成状态视图"""
        order = self.get_object(request, object_id)
        
        if request.method == 'POST':
            try:
                order.cancel_completion()
                self.message_user(request, '已撤销完成状态')
                return redirect('admin:production_productionorder_change', object_id)
            except ValidationError as e:
                self.message_user(request, str(e), level='ERROR')
                return redirect('admin:production_productionorder_change', object_id)
        
        context = {
            'title': '撤销完成状态',
            'order': order,
            'opts': self.model._meta,
        }
        
        return TemplateResponse(
            request,
            'admin/production/productionorder/cancel_completion.html',
            context
        )

    def confirm_view(self, request, order_id):
        """确认生产单"""
        order = get_object_or_404(ProductionOrder, id=order_id)
        if request.method == 'POST':
            try:
                order.status = 'confirmed'
                order.save()
                self.message_user(request, '生产单已确认')
                return redirect('admin:production_productionorder_changelist')
            except Exception as e:
                self.message_user(request, f'确认失败：{str(e)}', level='ERROR')
        
        context = {
            'title': '确认生产单',
            'order': order,
            'opts': self.model._meta,
        }
        return TemplateResponse(
            request,
            'admin/production/productionorder/confirm.html',
            context
        )

    def material_ready_view(self, request, object_id):
        """备料完成视图"""
        order = self.get_object(request, object_id)
        
        if request.method == 'POST':
            try:
                order.material_ready()
                self.message_user(request, '备料完成')
                return redirect('admin:production_productionorder_change', object_id)
            except ValidationError as e:
                self.message_user(request, str(e), level='ERROR')
                return redirect('admin:production_productionorder_change', object_id)
        
        context = {
            'title': '确认备料完成',
            'object': order,
            'opts': self.model._meta,
        }
        
        return TemplateResponse(
            request,
            'admin/production/productionorder/material_ready.html',
            context
        )

    def start_production_view(self, request, object_id):
        """开始生产视图"""
        order = self.get_object(request, object_id)
        
        if request.method == 'POST':
            try:
                order.start_production()
                self.message_user(request, '已开始生产')
                return redirect('admin:production_productionorder_change', object_id)
            except ValidationError as e:
                self.message_user(request, str(e), level='ERROR')
                return redirect('admin:production_productionorder_change', object_id)
        
        context = {
            'title': '确认开始生产',
            'object': order,
            'opts': self.model._meta,
        }
        
        return TemplateResponse(
            request,
            'admin/production/productionorder/start_production.html',
            context
        )

    def record_progress_view(self, request, object_id):
        """记录进度视图"""
        order = self.get_object(request, object_id)
        
        if request.method == 'POST':
            try:
                quantity = Decimal(request.POST.get('quantity', 0))
                notes = request.POST.get('notes', '')
                order.record_progress(quantity, notes)
                self.message_user(request, '进度已记录')
                return redirect('admin:production_productionorder_change', object_id)
            except ValidationError as e:
                self.message_user(request, str(e), level='ERROR')
                return redirect('admin:production_productionorder_change', object_id)
        
        context = {
            'title': '记录生产进度',
            'object': order,
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/production/productionorder/record_progress.html', context)

    def create_from_order_view(self, request):
        """从销售订单创建生产单"""
        from orders.models import Order, OrderItem
        from django import forms
        import uuid
        import traceback
        
        class CreateFromOrderForm(forms.Form):
            order = forms.ModelChoiceField(
                queryset=Order.objects.filter(status__in=['pending', 'processing']),
                label='销售订单',
                widget=forms.Select(attrs={'class': 'select2'})
            )
            skip_process_schedule = forms.BooleanField(
                required=False,
                initial=True,
                label='跳过工序排程',
                help_text='选中此项将不自动生成工序排程，您可以稍后手动添加'
            )
        
        if request.method == 'POST':
            form = CreateFromOrderForm(request.POST)
            if form.is_valid():
                order = form.cleaned_data['order']
                skip_process_schedule = form.cleaned_data['skip_process_schedule']
                order_items = OrderItem.objects.filter(order=order)
                
                # 检查该销售订单是否已经有关联的生产单
                if ProductionOrder.objects.filter(sales_order=order).exists():
                    error_msg = f"销售订单 {order.order_number} 已经有关联的生产单，不能重复创建"
                    self.message_user(request, error_msg, level='ERROR')
                    context = {
                        'title': '从销售订单创建生产单',
                        'form': form,
                        'opts': self.model._meta,
                        'error_message': error_msg
                    }
                    return render(request, 'admin/production/create_from_order.html', context)
                
                try:
                    created_orders = []
                    # 为每个订单项创建一个生产单
                    for item in order_items:
                        # 生成唯一的生产单号
                        production_number = f"P{uuid.uuid4().hex[:8].upper()}"
                        
                        # 创建生产单
                        production_order = ProductionOrder.objects.create(
                            order_number=production_number,
                            sales_order=order,
                            product=item.product,
                            planned_quantity=item.quantity,
                            notes=f"从销售订单 {order.order_number} 自动创建"
                        )
                        created_orders.append(production_order)
                        
                        if not skip_process_schedule:
                            try:
                                # 计算工序排程
                                production_order.calculate_process_schedules()
                            except Exception as e:
                                # 如果计算工序排程失败，记录错误但不删除生产单
                                error_msg = f"生产单 {production_number} 计算工序排程失败：{str(e)}"
                                self.message_user(request, error_msg, level='WARNING')
                    
                    # 更新订单状态为生产中
                    if order.status == 'pending':
                        order.status = 'processing'
                        order.save()
                    
                    if skip_process_schedule:
                        self.message_user(request, f'已成功从订单 {order.order_number} 创建 {len(created_orders)} 个生产单，未生成工序排程')
                    else:
                        self.message_user(request, f'已成功从订单 {order.order_number} 创建 {len(created_orders)} 个生产单')
                    return redirect('admin:production_productionorder_changelist')
                except Exception as e:
                    error_msg = f"创建生产单失败：{str(e)}\n{traceback.format_exc()}"
                    self.message_user(request, error_msg, level='ERROR')
                    context = {
                        'title': '从销售订单创建生产单',
                        'form': form,
                        'opts': self.model._meta,
                        'error_message': error_msg
                    }
                    return render(request, 'admin/production/create_from_order.html', context)
        else:
            form = CreateFromOrderForm()
        
        context = {
            'title': '从销售订单创建生产单',
            'form': form,
            'opts': self.model._meta,
        }
        return render(request, 'admin/production/create_from_order.html', context)

    def changelist_view(self, request, extra_context=None):
        """添加创建按钮到列表页"""
        extra_context = extra_context or {}
        extra_context['show_create_from_order'] = True
        return super().changelist_view(request, extra_context)

    def save_model(self, request, obj, form, change):
        """保存模型时自动生成工序排程"""
        is_new = not obj.pk
        
        if not obj.estimated_completion_time:
            # 如果没有设置预计完成时间，默认设置为计划结束日期的结束时间
            obj.estimated_completion_time = timezone.make_aware(
                datetime.combine(obj.end_date, time(23, 59, 59))
            )
        
        super().save_model(request, obj, form, change)
        
        if is_new:
            try:
                obj.calculate_process_schedules()
                messages.success(request, '工序排程已自动生成')
            except Exception as e:
                messages.error(request, f'生成工序排程失败：{str(e)}')

@admin.register(MaterialRequirement)
class MaterialRequirementAdmin(admin.ModelAdmin):
    list_display = ['production_order', 'material', 'required_quantity', 
                   'actual_quantity', 'notes']
    list_filter = ['production_order', 'material']
    search_fields = ['production_order__order_number', 'material__name']
    readonly_fields = ['actual_quantity']

@admin.register(ProductionProgress)
class ProductionProgressAdmin(admin.ModelAdmin):
    list_display = ['production_order', 'record_date', 'quantity', 
                   'accumulated_quantity', 'progress', 'can_edit', 'action_buttons']
    list_filter = ['production_order', 'record_date']
    search_fields = ['production_order__order_number', 'notes']
    readonly_fields = ['created_at', 'accumulated_quantity', 'progress']
    
    def action_buttons(self, obj):
        """操作按钮"""
        if obj.can_edit:
            return format_html(
                '<a class="button" href="{}">撤销</a>',
                reverse('admin:production_productionprogress_cancel', args=[obj.pk])
            )
        return '-'
    action_buttons.short_description = '操作'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:progress_id>/cancel/',
                self.admin_site.admin_view(self.cancel_progress),
                name='production_productionprogress_cancel'
            ),
        ]
        return custom_urls + urls
    
    def cancel_progress(self, request, progress_id):
        """撤销进度记录"""
        progress = get_object_or_404(ProductionProgress, id=progress_id)
        try:
            progress.cancel()
            self.message_user(request, '进度记录已撤销')
        except ValidationError as e:
            self.message_user(request, str(e), level='ERROR')
        except Exception as e:
            self.message_user(request, f'撤销失败：{str(e)}', level='ERROR')
        
        return redirect('admin:production_productionprogress_changelist')

@admin.register(ProductionMaterial)
class ProductionMaterialAdmin(admin.ModelAdmin):
    list_display = ['production_order', 'material_batch', 'quantity_used']
    list_filter = ['production_order', 'material_batch']
    search_fields = ['production_order__order_number', 
                    'material_batch__batch_number']

@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'daily_capacity', 'is_bottleneck', 'sequence']
    list_filter = ['is_bottleneck']
    search_fields = ['name', 'code']
    ordering = ['sequence']

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'model', 'status', 'process_step', 'daily_capacity']
    list_filter = ['status', 'process_step']
    search_fields = ['name', 'code']

@admin.register(ProcessSchedule)
class ProcessScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'production_order',
        'process',
        'planned_start_time',
        'planned_end_time',
        'status',
        'equipment'
    ]
    list_filter = ['status', 'process', 'production_order']
    search_fields = ['production_order__order_number', 'process__name']
    readonly_fields = ['production_order', 'process']

    def get_status_display(self, obj):
        """获取状态显示"""
        return obj.get_status_display()
    get_status_display.short_description = '状态'
