from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CapacityReportView

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'process-steps', views.ProcessStepViewSet)
router.register(r'process-schedules', views.ProcessScheduleViewSet)
router.register(r'material-requirements', views.MaterialRequirementViewSet)
router.register(r'production-materials', views.ProductionMaterialViewSet)
router.register(r'production-orders', views.ProductionOrderViewSet)
router.register(r'production-progress', views.ProductionProgressViewSet)
router.register(r'equipments', views.EquipmentViewSet)

app_name = 'production'

urlpatterns = [
    path('', include(router.urls)),
    path('capacity-report/', CapacityReportView.as_view(), name='capacity_report'),
    # 暂时注释掉这两个URL，因为视图函数还未实现
    # path('production-order/<int:pk>/', views.production_order_detail, name='production_order_detail'),
    # path('process-schedule/<int:pk>/', views.process_schedule_detail, name='process_schedule_detail'),
] 