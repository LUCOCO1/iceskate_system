from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication
from django.db.models import Count, Q
from datetime import datetime, timedelta
from production.models import ProductionOrder
from inventory.models import Material, Product
from orders.models import Order

# Create your views here.

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': '请提供用户名和密码'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response({'error': '用户名或密码不正确'}, status=status.HTTP_401_UNAUTHORIZED)
    
    login(request, user)
    
    # 获取或创建Token
    token, created = Token.objects.get_or_create(user=user)
    
    # 准备用户信息
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'isAdmin': user.is_staff
    }
    
    return Response({
        'token': token.key,
        'user': user_data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def user_info(request):
    user = request.user
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'isAdmin': user.is_staff
    }
    return Response(user_data)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def logout_view(request):
    # 删除用户的Token
    Token.objects.filter(user=request.user).delete()
    # 登出
    logout(request)
    return Response({'message': '成功登出'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def dashboard_stats(request):
    """获取Dashboard统计数据"""
    try:
        # 生产订单数量
        production_orders_count = ProductionOrder.objects.count()
        
        # 待处理采购订单数量（这里可以根据实际需求调整）
        pending_purchases_count = ProductionOrder.objects.filter(status='pending').count()
        
        # 库存预警数量（假设库存低于10的为预警）
        low_stock_materials = Material.objects.filter(current_stock__lt=10).count()
        low_stock_products = Product.objects.filter(current_stock__lt=10).count()
        inventory_warnings = low_stock_materials + low_stock_products
        
        # 今日完成的订单数量
        today = datetime.now().date()
        today_completed = ProductionOrder.objects.filter(
            status='completed',
            actual_end_date__date=today
        ).count()
        
        return Response([
            production_orders_count,
            pending_purchases_count,
            inventory_warnings,
            today_completed
        ])
    except Exception as e:
        return Response([0, 0, 0, 0])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])  
def dashboard_production(request):
    """获取Dashboard生产数据"""
    time_range = request.GET.get('time_range', 'week')
    
    try:
        if time_range == 'week':
            # 获取本周的生产数据（模拟数据）
            planned_data = [150, 230, 224, 218, 135, 147, 260]
            actual_data = [120, 210, 190, 240, 110, 130, 200]
            labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        else:
            # 获取本月的生产数据（模拟数据）
            planned_data = [1200, 1800, 1650, 2100, 1900, 2200, 2400]
            actual_data = [1100, 1650, 1500, 2000, 1800, 2100, 2200]
            labels = ['1日', '5日', '10日', '15日', '20日', '25日', '30日']
            
        return Response({
            'planned': planned_data,
            'actual': actual_data,
            'labels': labels
        })
    except Exception as e:
        # 返回默认数据
        return Response({
            'planned': [150, 230, 224, 218, 135, 147, 260],
            'actual': [120, 210, 190, 240, 110, 130, 200],
            'labels': ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def dashboard_inventory(request):
    """获取Dashboard库存数据"""
    inventory_type = request.GET.get('type', 'material')
    
    try:
        if inventory_type == 'material':
            # 获取材料库存数据
            materials = Material.objects.all()[:5]  # 取前5个材料
            data = []
            for material in materials:
                data.append({
                    'value': material.current_stock or 0,
                    'name': material.name
                })
            # 如果材料不足5个，填充默认数据
            if len(data) < 5:
                default_materials = [
                    {'value': 35, 'name': '钢板'},
                    {'value': 20, 'name': '轴承'},
                    {'value': 15, 'name': '螺丝'},
                    {'value': 25, 'name': '包装材料'},
                    {'value': 5, 'name': '其他'}
                ]
                data = default_materials[:5]
        else:
            # 获取产品库存数据
            products = Product.objects.all()[:4]  # 取前4个产品
            data = []
            for product in products:
                data.append({
                    'value': product.current_stock or 0,
                    'name': product.name
                })
            # 如果产品不足4个，填充默认数据
            if len(data) < 4:
                default_products = [
                    {'value': 40, 'name': '成品A'},
                    {'value': 30, 'name': '成品B'},
                    {'value': 20, 'name': '成品C'},
                    {'value': 10, 'name': '其他产品'}
                ]
                data = default_products[:4]
                
        return Response({'data': data})
    except Exception as e:
        # 返回默认数据
        if inventory_type == 'material':
            default_data = [
                {'value': 35, 'name': '钢板'},
                {'value': 20, 'name': '轴承'},
                {'value': 15, 'name': '螺丝'},
                {'value': 25, 'name': '包装材料'},
                {'value': 5, 'name': '其他'}
            ]
        else:
            default_data = [
                {'value': 40, 'name': '成品A'},
                {'value': 30, 'name': '成品B'},
                {'value': 20, 'name': '成品C'},
                {'value': 10, 'name': '其他产品'}
            ]
        return Response({'data': default_data})
