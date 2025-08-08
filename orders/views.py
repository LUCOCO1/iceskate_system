from django.shortcuts import render
from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, Customer, OrderItem
from .serializers import OrderSerializer, CustomerSerializer, OrderItemSerializer
from services.pdf_service import OrderPDFService
from inventory.models import Product
from inventory.models import ProductMovement

# Create your views here.

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filterset_fields = ['code', 'name', 'is_active']
    search_fields = ['code', 'name', 'contact']

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filterset_fields = ['customer']  # 移除status，使用自定义过滤
    search_fields = ['order_number', 'notes']
    
    def get_queryset(self):
        """重写获取查询集方法以支持status多值过滤"""
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status', None)
        
        if status_param:
            try:
                # 支持逗号分隔的多个状态值
                if ',' in status_param:
                    status_list = [s.strip() for s in status_param.split(',') if s.strip()]
                    if status_list:
                        queryset = queryset.filter(status__in=status_list)
                else:
                    queryset = queryset.filter(status=status_param.strip())
            except Exception as e:
                # 如果过滤出错，记录错误但不影响其他查询
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Status filtering error: {e}, status_param: {status_param}")
        
        return queryset

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    filterset_fields = ['order', 'product']

    @action(detail=True, methods=['get'])
    def print_order(self, request, pk=None):
        """打印订单"""
        order = self.get_object()
        pdf_service = OrderPDFService()
        pdf_file = pdf_service.generate_order_pdf(order)
        
        return FileResponse(
            open(pdf_file, 'rb'),
            as_attachment=True,
            filename=f"order_{order.order_number}.pdf"
        )
