from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
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
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse
import pandas as pd
from django.template.response import TemplateResponse
from django.core.exceptions import ValidationError

class MaterialMovementInline(admin.TabularInline):
    model = MaterialMovement
    extra = 0
    readonly_fields = ['movement_date']
    can_delete = False

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    fields = ['control_number', 'material', 'specification', 'quantity', 
              'unit', 'material_type', 'notes']

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'specification', 'unit', 'stock')
    search_fields = ('code', 'name', 'specification')
    inlines = [MaterialMovementInline]

@admin.register(MaterialMovement)
class MaterialMovementAdmin(admin.ModelAdmin):
    list_display = ('material', 'movement_type', 'quantity', 'unit', 'movement_date', 'reference_number', 'purchase', 'batch')
    list_filter = ('movement_type', 'material', 'movement_date')
    search_fields = ('reference_number', 'notes', 'purchase__purchase_number')
    readonly_fields = ('movement_date',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'contact', 'phone', 'is_active')
    search_fields = ('code', 'name', 'contact')
    list_filter = ('is_active',)

@admin.register(MaterialPurchase)
class MaterialPurchaseAdmin(admin.ModelAdmin):
    list_display = ('purchase_number', 'supplier', 'status', 'total_quantity', 'received_quantity', 'action_buttons')
    list_filter = ('status', 'supplier')
    search_fields = ('purchase_number', 'supplier__name')
    inlines = [PurchaseItemInline]
    readonly_fields = ['created_at', 'updated_at']

    def total_quantity(self, obj):
        """总数量"""
        return sum(item.quantity for item in obj.items.all())
    total_quantity.short_description = '总数量'
    
    def received_quantity(self, obj):
        """已入库数量"""
        return sum(item.received_quantity for item in obj.items.all())
    received_quantity.short_description = '已入库数量'

    def action_buttons(self, obj):
        """显示操作按钮"""
        buttons = []
        
        # 打印按钮
        print_url = reverse('inventory:print-purchase', args=[obj.pk])
        buttons.append(f'<a class="button" href="{print_url}">打印</a>')
        
        # 根据当前状态显示不同的操作按钮
        if obj.status == 'draft':
            buttons.append(self._get_status_button(obj, 'pending', '确认'))
        elif obj.status == 'pending':
            buttons.append(self._get_status_button(obj, 'received', '确认入库'))
        elif obj.status == 'received':
            buttons.append(self._get_status_button(obj, 'pending', '撤销入库'))
            buttons.append(self._get_status_button(obj, 'completed', '完成'))
        
        return format_html(' '.join(buttons))
    
    def _get_status_button(self, obj, new_status, text):
        """生成状态变更按钮"""
        url = reverse('admin:inventory_materialpurchase_changelist')
        return f'<a class="button" href="{url}?id={obj.id}&new_status={new_status}">{text}</a>'
    
    action_buttons.short_description = '操作'
    
    def changelist_view(self, request, extra_context=None):
        """处理状态变更请求"""
        if 'id' in request.GET and 'new_status' in request.GET:
            purchase_id = request.GET.get('id')
            new_status = request.GET.get('new_status')
            try:
                purchase = MaterialPurchase.objects.get(id=purchase_id)
                old_status = purchase.status
                
                if new_status == 'received':
                    purchase.receive_materials()
                elif new_status == 'pending' and old_status == 'received':
                    purchase.cancel_receive()
                else:
                    purchase.status = new_status
                    purchase.save()
                
                message = f'采购单 {purchase.purchase_number} '
                if new_status == 'received':
                    message += '已确认入库'
                elif new_status == 'pending' and old_status == 'received':
                    message += '已撤销入库'
                elif new_status == 'pending':
                    message += '已确认'
                elif new_status == 'completed':
                    message += '已完成'
                
                self.message_user(request, message)
            except ValidationError as e:
                self.message_user(request, f'操作失败：{str(e)}', level=messages.ERROR)
            except Exception as e:
                self.message_user(request, f'操作失败：{str(e)}', level=messages.ERROR)
        
        return super().changelist_view(request, extra_context)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'specification', 'unit_weight', 'stock', 'get_stock_status', 'get_customers_display', 'is_active')
    list_filter = ('is_active', 'customers')
    search_fields = ('code', 'name', 'specification')
    filter_horizontal = ('customers',)
    
    def get_customers_display(self, obj):
        """显示关联的客户"""
        customers = obj.customers.all()
        if customers.exists():
            customer_names = [customer.name for customer in customers[:3]]  # 最多显示3个客户
            display_text = ', '.join(customer_names)
            if customers.count() > 3:
                display_text += f' 等{customers.count()}个客户'
            return display_text
        return '暂无关联客户'
    
    get_customers_display.short_description = '关联客户'
    
    def get_stock_status(self, obj):
        if obj.stock <= obj.min_stock:
            return format_html('<span style="color: red;">低库存</span>')
        elif obj.stock <= obj.warning_stock:
            return format_html('<span style="color: orange;">库存预警</span>')
        elif obj.stock >= obj.max_stock:
            return format_html('<span style="color: blue;">库存过高</span>')
        return "正常"
    
    get_stock_status.short_description = '库存状态'

    fieldsets = (
        ('基本信息', {
            'fields': ('code', 'name', 'specification', 'unit', 'unit_weight', 'is_active')
        }),
        ('库存信息', {
            'fields': ('stock', 'min_stock', 'warning_stock', 'max_stock')
        }),
        ('客户关联', {
            'fields': ('customers',),
            'description': '选择与该产品关联的客户。可以多选客户，方便后续按客户筛选产品。'
        }),
        ('其他', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-products/', 
                 self.admin_site.admin_view(self.import_products), 
                 name='import-products'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_import_button'] = True
        return super().changelist_view(request, extra_context)
    
    def import_products(self, request):
        if request.method == "POST":
            try:
                excel_file = request.FILES["excel_file"]
                if not excel_file.name.endswith('.xlsx'):
                    messages.error(request, '请上传 Excel 文件(.xlsx)')
                    return redirect("..")
                
                # 读取Excel文件
                df = pd.read_excel(excel_file)
                
                # 验证必要的列是否存在
                required_columns = ['产品编码', '产品名称', '规格', '单位']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    messages.error(request, f'Excel中缺少必要的列: {", ".join(missing_columns)}')
                    return redirect("..")
                
                success_count = 0
                error_count = 0
                error_messages = []
                
                # 开始导入数据
                for index, row in df.iterrows():
                    try:
                        # 检查产品编码是否已存在
                        product, created = Product.objects.get_or_create(
                            code=row['产品编码'],
                            defaults={
                                'name': row['产品名称'],
                                'specification': row['规格'],
                                'unit': row['单位'],
                                'stock': 0,
                                'min_stock': 0,
                                'warning_stock': 0,
                                'max_stock': 0,
                                'is_active': True
                            }
                        )
                        
                        if not created:
                            # 更新现有产品
                            product.name = row['产品名称']
                            product.specification = row['规格']
                            product.unit = row['单位']
                            product.save()
                        
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        error_messages.append(f'第 {index + 2} 行: {str(e)}')
                
                if success_count > 0:
                    messages.success(request, f'成功导入 {success_count} 个产品')
                if error_count > 0:
                    messages.error(request, f'导入失败 {error_count} 个产品')
                    for msg in error_messages:
                        messages.error(request, msg)
                
                return redirect("..")
            except Exception as e:
                messages.error(request, f'导入失败: {str(e)}')
                return redirect("..")
        
        # GET 请求显示上传表单
        return TemplateResponse(
            request,
            "admin/inventory/product/import_products.html",
            context={
                'title': '导入产品',
                'opts': self.model._meta,
            }
        )

@admin.register(ProductMovement)
class ProductMovementAdmin(admin.ModelAdmin):
    list_display = [
        'product',
        'movement_type',
        'quantity',
        'unit',
        'movement_date',
        'reference_number',
        'notes'
    ]
    list_filter = [
        'movement_type',
        'movement_date',
        'product',
    ]
    search_fields = [
        'product__name',
        'product__code',
        'reference_number',
        'notes'
    ]
    date_hierarchy = 'movement_date'
    readonly_fields = ['movement_date', 'created_at']

    def get_movement_type_display(self, obj):
        """自定义变动类型显示"""
        return obj.get_movement_type_display()
    get_movement_type_display.short_description = '变动类型'

@admin.register(MaterialBatch)
class MaterialBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_number', 'material', 'purchase', 'production_date', 
                   'initial_quantity', 'remaining_quantity', 'status')
    list_filter = ('material', 'status', 'production_date')
    search_fields = ('batch_number', 'material__name', 'purchase__purchase_number')
    readonly_fields = ('created_at',)

class InventoryItemInline(admin.TabularInline):
    model = InventoryItem
    extra = 1

class InventoryAdmin(admin.ModelAdmin):
    list_display = ('inventory_number', 'inventory_date', 'status', 'created_by')
    list_filter = ('status', 'inventory_date')
    search_fields = ('inventory_number',)
    inlines = [InventoryItemInline]
    readonly_fields = ['created_at']

class ProductOutboundItemInline(admin.TabularInline):
    model = ProductOutboundItem
    extra = 1
    fields = ['product', 'quantity', 'unit', 'notes']
    autocomplete_fields = ['product']

@admin.register(ProductOutbound)
class ProductOutboundAdmin(admin.ModelAdmin):
    list_display = ['outbound_number', 'outbound_date', 'order', 'status', 'action_buttons']
    list_filter = ['status', 'outbound_date']
    search_fields = ['outbound_number', 'notes', 'order__order_number']
    readonly_fields = ['outbound_number', 'created_at', 'created_by']
    inlines = [ProductOutboundItemInline]
    autocomplete_fields = ['order']
    fields = ['outbound_number', 'outbound_date', 'order', 'status', 'notes', 'created_at', 'created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:  # 只在创建时设置创建人
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def action_buttons(self, obj):
        """根据状态显示不同的操作按钮"""
        buttons = []
        
        if obj.status == 'draft':
            # 确认按钮
            confirm_url = reverse('admin:confirm_outbound', args=[obj.pk])
            buttons.append(
                f'<a class="button" href="{confirm_url}">确认出库</a>'
            )
        
        if obj.status == 'confirmed':
            # 取消按钮
            cancel_url = reverse('admin:cancel_outbound', args=[obj.pk])
            buttons.append(
                f'<a class="button" href="{cancel_url}">取消出库</a>'
            )
        
        # 打印按钮
        print_url = reverse('inventory:print-outbound', args=[obj.pk])
        buttons.append(
            f'<a class="button" href="{print_url}" target="_blank">打印</a>'
        )
        
        return format_html(' '.join(buttons))
    
    action_buttons.short_description = '操作'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:outbound_id>/confirm/',
                self.admin_site.admin_view(self.confirm_outbound),
                name='confirm_outbound'
            ),
            path(
                '<int:outbound_id>/cancel/',
                self.admin_site.admin_view(self.cancel_outbound),
                name='cancel_outbound'
            ),
        ]
        return custom_urls + urls
    
    def confirm_outbound(self, request, outbound_id):
        """确认出库"""
        outbound = ProductOutbound.objects.get(pk=outbound_id)
        try:
            outbound.confirm_outbound()
            self.message_user(request, '出库单确认成功')
        except ValidationError as e:
            self.message_user(request, f'出库单确认失败：{str(e)}', level=messages.ERROR)
        except Exception as e:
            self.message_user(request, f'出库单确认失败：{str(e)}', level=messages.ERROR)
        
        return redirect('admin:inventory_productoutbound_changelist')
    
    def cancel_outbound(self, request, outbound_id):
        """取消出库"""
        outbound = ProductOutbound.objects.get(pk=outbound_id)
        try:
            outbound.cancel_outbound()
            self.message_user(request, '出库单取消成功')
        except ValidationError as e:
            self.message_user(request, f'出库单取消失败：{str(e)}', level=messages.ERROR)
        except Exception as e:
            self.message_user(request, f'出库单取消失败：{str(e)}', level=messages.ERROR)
        
        return redirect('admin:inventory_productoutbound_changelist')

@admin.register(ProductOutboundItem)
class ProductOutboundItemAdmin(admin.ModelAdmin):
    list_display = ['outbound', 'product', 'quantity', 'unit']
    list_filter = ['outbound', 'product']
    search_fields = ['outbound__outbound_number', 'product__name', 'product__code']
    autocomplete_fields = ['outbound', 'product']

class Media:
    css = {
        'all': ('admin/css/custom.css',)
    }

admin.site.register(Inventory, InventoryAdmin)
