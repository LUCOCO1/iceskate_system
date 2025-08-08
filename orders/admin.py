from django.contrib import admin
from django import forms
from django.urls import reverse
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customer, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'color', 'material', 'quantity', 'unit', 'notes']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'contact', 'phone', 'is_active')
    search_fields = ('code', 'name', 'contact')
    list_filter = ('is_active',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_order_number', 'customer', 'order_date', 'delivery_date', 'status')
    list_filter = ('status', 'order_date')
    search_fields = ('order_number', 'customer_order_number', 'customer__name')
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('基本信息', {
            'fields': (
                'order_number', 'customer', 'customer_order_number',
                'order_date', 'delivery_date', 'status'
            )
        }),
        ('其他信息', {
            'fields': ('notes', 'created_by', 'created_at', 'updated_at')
        }),
    )

    def action_buttons(self, obj):
        """显示操作按钮"""
        buttons = []
        
        # 打印按钮
        print_url = reverse('orders:print-order', args=[obj.pk])
        buttons.append(f'<a class="button" href="{print_url}">打印</a>')
        
        # 根据当前状态显示不同的操作按钮
        if obj.status == 'pending':
            buttons.append(self._get_status_button(obj, 'processing', '开始生产'))
        elif obj.status == 'processing':
            buttons.append(self._get_status_button(obj, 'completed', '生产完成'))
        elif obj.status == 'completed':
            buttons.append(self._get_status_button(obj, 'shipped', '发货'))
            
        return format_html(' '.join(buttons))
    
    def _get_status_button(self, obj, new_status, text):
        """生成状态变更按钮"""
        url = reverse('admin:orders_order_changelist')
        return f'<a class="button" href="{url}?id={obj.id}&new_status={new_status}">{text}</a>'
    
    action_buttons.short_description = '操作'
    
    def changelist_view(self, request, extra_context=None):
        """处理状态变更请求"""
        if 'id' in request.GET and 'new_status' in request.GET:
            order_id = request.GET.get('id')
            new_status = request.GET.get('new_status')
            try:
                order = Order.objects.get(id=order_id)
                order.status = new_status
                order.save()
                self.message_user(request, f'订单 {order.order_number} 状态已更新为 {new_status}')
            except Order.DoesNotExist:
                self.message_user(request, '订单不存在', level='ERROR')
                
        return super().changelist_view(request, extra_context)

    def save_model(self, request, obj, form, change):
        if not change:  # 新建订单时
            obj.created_by = request.user  # 自动设置创建人
        super().save_model(request, obj, form, change)
