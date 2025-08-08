from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from inventory.models import Product, ProductMovement
from .models import (
    ProductionOrder,
    ProductionMaterial,
    MaterialRequirement,
    ProductionProgress,
    ProcessStep,
    ProcessSchedule,
    Equipment
)
from .serializers import (
    ProductSerializer,
    ProductionOrderSerializer,
    ProductionMaterialSerializer,
    MaterialRequirementSerializer,
    ProductionProgressSerializer,
    ProcessStepSerializer,
    ProcessScheduleSerializer,
    EquipmentSerializer
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # 这些导入只在类型检查时使用，避免运行时的循环导入问题
    from django.db.models.manager import Manager
from inventory.serializers import ProductMovementSerializer
from inventory.models import MaterialBatch
from django.views.generic import TemplateView, DetailView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.utils import timezone
import json

# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['code', 'name', 'is_active']
    search_fields = ['code', 'name', 'specification']
    
    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """获取产品的库存变动历史"""
        product = self.get_object()
        movements = ProductMovement.objects.filter(product=product)
        serializer = ProductMovementSerializer(movements, many=True)
        return Response(serializer.data)

    # @action(detail=True, methods=['get'])
    # def materials(self, request, pk=None):
    #     ...

class ProcessStepViewSet(viewsets.ModelViewSet):
    queryset = ProcessStep.objects.all()  # type: ignore[attr-defined]
    serializer_class = ProcessStepSerializer
    filterset_fields = ['is_bottleneck']
    search_fields = ['name', 'code']
    ordering = ['sequence']

class ProcessScheduleViewSet(viewsets.ModelViewSet):
    queryset = ProcessSchedule.objects.all()  # type: ignore[attr-defined]
    serializer_class = ProcessScheduleSerializer
    filterset_fields = ['status', 'process', 'production_order']
    search_fields = ['production_order__order_number', 'process__name']
    ordering = ['planned_start_time']

class MaterialRequirementViewSet(viewsets.ModelViewSet):
    queryset = MaterialRequirement.objects.all()  # type: ignore[attr-defined]
    serializer_class = MaterialRequirementSerializer
    filterset_fields = ['production_order', 'material']
    search_fields = ['production_order__order_number', 'material__name']

class ProductionMaterialViewSet(viewsets.ModelViewSet):
    queryset = ProductionMaterial.objects.all()  # type: ignore[attr-defined]
    serializer_class = ProductionMaterialSerializer
    filterset_fields = ['production_order', 'material_batch']
    search_fields = ['production_order__order_number']

class ProductionOrderViewSet(viewsets.ModelViewSet):
    queryset = ProductionOrder.objects.all()  # type: ignore[attr-defined]
    serializer_class = ProductionOrderSerializer
    filterset_fields = ['status', 'priority', 'product']
    search_fields = ['order_number', 'notes', 'sales_order__order_number']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def material_ready(self, request, pk=None):
        """备料完成"""
        production_order = self.get_object()
        try:
            production_order.material_ready()
            return Response({'status': 'success', 'message': '备料完成'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def start_production(self, request, pk=None):
        """开始生产"""
        production_order = self.get_object()
        try:
            production_order.start_production()
            return Response({'status': 'success', 'message': '生产已开始'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def record_progress(self, request, pk=None):
        """记录进度"""
        production_order = self.get_object()
        completed_quantity = request.data.get('completed_quantity')
        notes = request.data.get('notes', '')
        
        if not completed_quantity:
            return Response({'error': '请提供完成数量'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 将字符串转换为Decimal类型
            from decimal import Decimal
            completed_quantity = Decimal(str(completed_quantity))
            production_order.record_progress(completed_quantity, notes)
            return Response({'status': 'success', 'message': '进度记录成功'})
        except (ValueError, TypeError) as e:
            return Response({'error': '完成数量格式不正确'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def complete_production(self, request, pk=None):
        """完成生产"""
        production_order = self.get_object()
        completed_quantity = request.data.get('completed_quantity')
        
        if not completed_quantity:
            return Response({'error': '请提供完成数量'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 将字符串转换为Decimal类型
            from decimal import Decimal
            completed_quantity = Decimal(str(completed_quantity))
            production_order.complete_production(completed_quantity)
            return Response({'status': 'success', 'message': '生产完成'})
        except (ValueError, TypeError) as e:
            return Response({'error': '完成数量格式不正确'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel_completion(self, request, pk=None):
        """撤销完成"""
        production_order = self.get_object()
        try:
            production_order.cancel_completion()
            return Response({'status': 'success', 'message': '已撤销完成'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProductionProgressViewSet(viewsets.ModelViewSet):
    queryset = ProductionProgress.objects.all()
    serializer_class = ProductionProgressSerializer
    filterset_fields = ['production_order', 'record_date']
    search_fields = ['production_order__order_number', 'notes']
    ordering = ['-record_date']

    @action(detail=True, methods=['post'])
    def cancel_progress(self, request, pk=None):
        """取消进度记录"""
        progress = self.get_object()
        try:
            progress.cancel()
            return Response({'status': 'success', 'message': '进度记录已取消'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    filterset_fields = ['status', 'process_step']
    search_fields = ['name', 'code', 'model']
    ordering = ['code']

@method_decorator(staff_member_required, name='dispatch')
class CapacityReportView(TemplateView):
    template_name = 'production/capacity_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        process_steps = ProcessStep.objects.all().order_by('sequence')
        
        capacity_data = []
        for step in process_steps:
            schedules = ProcessSchedule.objects.filter(
                process=step,
                planned_start_time__date=timezone.now().date()
            )
            total_work = schedules.aggregate(
                total=Sum('production_order__planned_quantity')
            )['total'] or 0
            
            capacity_data.append({
                'process': step.name,
                'daily_capacity': step.daily_capacity,
                'current_load': total_work,
                'utilization': (total_work / step.daily_capacity * 100) if step.daily_capacity > 0 else 0
            })
        
        context['capacity_data'] = capacity_data
        return context

class ScheduleView(DetailView):
    model = ProcessSchedule
    template_name = 'admin/production/processschedule/schedule_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        process_schedule = self.object
        
        # 获取同一生产订单的所有工序排程
        process_schedules = ProcessSchedule.objects.filter(
            production_order=process_schedule.production_order
        ).order_by('process__sequence')
        
        # 准备工序数据
        process_data = []
        prev_code = None
        
        for schedule in process_schedules:
            # 计算完成百分比
            completed_percent = 0
            if process_schedule.production_order.completed_quantity:
                completed_percent = (
                    process_schedule.production_order.completed_quantity / 
                    process_schedule.production_order.planned_quantity
                ) * 100

            process_data.append({
                'id': schedule.process.code,
                'name': schedule.process.name,
                'start': schedule.planned_start_time.strftime('%Y-%m-%d'),
                'end': schedule.planned_end_time.strftime('%Y-%m-%d'),
                'completed_percent': completed_percent,
                'dependency': prev_code
            })
            prev_code = schedule.process.code

        context['process_data'] = json.dumps(process_data)
        return context
