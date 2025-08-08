from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q, F
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
from .serializers import (
    MaterialSerializer,
    MaterialMovementSerializer,
    SupplierSerializer,
    MaterialPurchaseSerializer,
    PurchaseItemSerializer,
    MaterialBatchSerializer,
    InventorySerializer,
    InventoryItemSerializer,
    ProductSerializer,
    ProductMovementSerializer,
    ProductOutboundSerializer,
    ProductOutboundItemSerializer
)
from django.http import FileResponse
from services.material_pdf_service import MaterialPurchasePDFService
import os
from django.template.response import TemplateResponse
from django.core.exceptions import ValidationError
from orders.models import Customer
from orders.serializers import CustomerSerializer

# Create your views here.

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    filterset_fields = ['code', 'name']
    search_fields = ['code', 'name', 'specification']
    
    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """获取材料的库存变动历史"""
        material = self.get_object()
        movements = MaterialMovement.objects.filter(material=material)
        serializer = MaterialMovementSerializer(movements, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def purchases(self, request, pk=None):
        """获取材料的采购历史"""
        material = self.get_object()
        purchases = MaterialPurchase.objects.filter(material=material)
        serializer = MaterialPurchaseSerializer(purchases, many=True)
        return Response(serializer.data)

class MaterialMovementViewSet(viewsets.ModelViewSet):
    queryset = MaterialMovement.objects.all()
    serializer_class = MaterialMovementSerializer
    filterset_fields = ['material', 'movement_type']
    search_fields = ['reference_number', 'notes']

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filterset_fields = ['code', 'name', 'is_active']
    search_fields = ['code', 'name', 'contact']

class MaterialPurchaseViewSet(viewsets.ModelViewSet):
    queryset = MaterialPurchase.objects.all()
    serializer_class = MaterialPurchaseSerializer
    filterset_fields = ['status', 'supplier']
    search_fields = ['purchase_number', 'notes']
    
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """确认入库"""
        purchase = self.get_object()
        
        try:
            # 调用模型中的入库方法
            purchase.receive_materials()
            return Response({'status': 'success', 'message': '入库操作成功'})
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'入库失败：{str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def cancel_receive(self, request, pk=None):
        """撤销入库"""
        purchase = self.get_object()
        
        try:
            # 调用模型中的撤销入库方法
            purchase.cancel_inbound()
            return Response({'status': 'success', 'message': '撤销入库操作成功'})
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'撤销入库失败：{str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """获取采购单相关的库存变动记录"""
        purchase = self.get_object()
        movements = MaterialMovement.objects.filter(purchase=purchase)
        serializer = MaterialMovementSerializer(movements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def print(self, request, pk=None):
        """打印采购单"""
        purchase = self.get_object()
        service = MaterialPurchasePDFService()
        pdf_path = service.generate_purchase_pdf(purchase)
        
        return FileResponse(
            open(pdf_path, 'rb'),
            as_attachment=True,
            filename=f'purchase_{purchase.purchase_number}.pdf'
        )

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['code', 'name', 'is_active']
    search_fields = ['code', 'name', 'specification']
    
    def get_queryset(self):
        """支持按客户筛选产品"""
        queryset = super().get_queryset()
        customer_id = self.request.query_params.get('customer', None)
        if customer_id:
            queryset = queryset.filter(customers=customer_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def customers(self, request):
        """获取客户列表"""
        customers = Customer.objects.filter(is_active=True)
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """获取产品的库存变动历史"""
        product = self.get_object()
        movements = ProductMovement.objects.filter(product=product)
        serializer = ProductMovementSerializer(movements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stock_warning(self, request):
        """获取库存预警产品列表"""
        # 获取库存低于预警值或高于最大库存的产品
        warning_products = Product.objects.filter(
            Q(stock__lte=F('warning_stock')) |  # 库存低于预警值
            Q(stock__gte=F('max_stock'))  # 库存高于最大值
        ).filter(is_active=True)  # 只查询启用的产品

        serializer = self.get_serializer(warning_products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """获取低库存产品列表"""
        low_stock_products = Product.objects.filter(
            stock__lte=F('min_stock'),
            is_active=True
        )
        serializer = self.get_serializer(low_stock_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def calculate_material_requirements(self, request):
        """根据订单数量计算材料需求"""
        from .material_requirements import MaterialRequirementCalculator
        
        try:
            data = request.data
            order_items = data.get('order_items', [])
            order_id = data.get('order_id')
            
            # 如果提供了订单ID，直接从订单计算
            if order_id:
                result = MaterialRequirementCalculator.calculate_from_order(order_id)
            else:
                # 否则从订单明细数据计算
                result = MaterialRequirementCalculator.calculate_from_order_items(order_items)
            
            if not result['success']:
                return Response(
                    {'errors': result['errors']}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            return Response(result)
            
        except Exception as e:
            return Response(
                {'error': f'计算材料需求失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProductMovementViewSet(viewsets.ModelViewSet):
    queryset = ProductMovement.objects.all()
    serializer_class = ProductMovementSerializer
    filterset_fields = ['product', 'movement_type']
    search_fields = ['reference_number', 'notes']

class MaterialBatchViewSet(viewsets.ModelViewSet):
    queryset = MaterialBatch.objects.all()
    serializer_class = MaterialBatchSerializer
    filterset_fields = ['material', 'batch_number']
    search_fields = ['batch_number']

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    filterset_fields = ['status', 'inventory_date']
    search_fields = ['inventory_number']
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """确认盘点"""
        inventory = self.get_object()
        if inventory.status == 'draft':
            inventory.status = 'confirmed'
            inventory.save()
            
            # 更新材料库存
            for item in inventory.items.all():
                material = item.material
                material.stock = item.actual_quantity
                material.save()
            
            return Response({'status': 'success'})
        return Response(
            {'status': 'error', 'message': '只能确认草稿状态的盘点单'},
            status=status.HTTP_400_BAD_REQUEST
        )

def print_purchase(request, pk):
    """
    打印采购单视图
    """
    purchase = get_object_or_404(MaterialPurchase, pk=pk)
    
    context = {
        'purchase': purchase,
        'items': purchase.items.all(),
        'title': f'采购单：{purchase.purchase_number}'
    }
    
    return TemplateResponse(
        request,
        'inventory/print_purchase.html',
        context
    )

class ProductOutboundViewSet(viewsets.ModelViewSet):
    queryset = ProductOutbound.objects.all()
    serializer_class = ProductOutboundSerializer
    filterset_fields = ['status', 'outbound_date', 'order']
    search_fields = ['outbound_number', 'notes']
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """确认出库"""
        outbound = self.get_object()
        try:
            outbound.confirm_outbound()
            return Response({'status': 'success', 'message': '出库确认成功'})
        except Exception as e:
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消出库"""
        outbound = self.get_object()
        try:
            outbound.cancel_outbound()
            return Response({'status': 'success', 'message': '出库取消成功'})
        except Exception as e:
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def print(self, request, pk=None):
        """打印出库单"""
        outbound = self.get_object()
        return Response({
            'print_url': outbound.get_print_url()
        })

class ProductOutboundItemViewSet(viewsets.ModelViewSet):
    queryset = ProductOutboundItem.objects.all()
    serializer_class = ProductOutboundItemSerializer
    filterset_fields = ['outbound', 'product']

def print_outbound(request, pk):
    """打印出库单"""
    outbound = get_object_or_404(ProductOutbound, pk=pk)
    return TemplateResponse(request, 'inventory/print_outbound.html', {
        'outbound': outbound
    })
