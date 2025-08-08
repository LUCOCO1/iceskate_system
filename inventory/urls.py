from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'materials', views.MaterialViewSet)
router.register(r'movements', views.MaterialMovementViewSet)
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'purchases', views.MaterialPurchaseViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'product-movements', views.ProductMovementViewSet)
router.register(r'batches', views.MaterialBatchViewSet)
router.register(r'inventories', views.InventoryViewSet)
router.register(r'outbounds', views.ProductOutboundViewSet)
router.register(r'outbound-items', views.ProductOutboundItemViewSet)

app_name = 'inventory'

urlpatterns = [
    path('', include(router.urls)),
    path('purchase/<int:pk>/print/', views.print_purchase, name='print-purchase'),
    path('outbound/<int:pk>/print/', views.print_outbound, name='print-outbound'),
] 