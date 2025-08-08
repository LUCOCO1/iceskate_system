from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('login/', csrf_exempt(views.login_view), name='login'),
    path('user/', views.user_info, name='user_info'),
    path('logout/', csrf_exempt(views.logout_view), name='logout'),
    path('dashboard-stats/', views.dashboard_stats, name='dashboard_stats'),
    path('dashboard-production/', views.dashboard_production, name='dashboard_production'),
    path('dashboard-inventory/', views.dashboard_inventory, name='dashboard_inventory'),
] 