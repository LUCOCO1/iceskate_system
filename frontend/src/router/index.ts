import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

// 布局组件
const Layout = () => import('../layouts/MainLayout.vue')

// 路由配置
const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '仪表盘', icon: 'Odometer' }
      }
    ]
  },
  {
    path: '/inventory',
    component: Layout,
    redirect: '/inventory/products',
    meta: { title: '库存管理', icon: 'Box' },
    children: [
      // 产品
      {
        path: 'products',
        name: 'Products',
        component: () => import('../views/inventory/ProductList.vue'),
        meta: { title: '产品' }
      },
      // 产品出库单
      {
        path: 'outbounds',
        name: 'ProductOutbounds',
        component: () => import('../views/inventory/OutboundList.vue'),
        meta: { title: '产品出库单' }
      },
      {
        path: 'outbound-create',
        name: 'OutboundCreate',
        component: () => import('../views/inventory/OutboundForm.vue'),
        meta: { title: '新建出库单', hidden: true }
      },
      {
        path: 'outbound-edit/:id',
        name: 'OutboundEdit',
        component: () => import('../views/inventory/OutboundForm.vue'),
        meta: { title: '编辑出库单', hidden: true }
      },
      // 产品变动
      {
        path: 'product-movements',
        name: 'ProductMovements',
        component: () => import('../views/inventory/ProductMovementList.vue'),
        meta: { title: '产品变动' }
      },
      // 供应商
      {
        path: 'suppliers',
        name: 'Suppliers',
        component: () => import('../views/inventory/SupplierList.vue'),
        meta: { title: '供应商' }
      },
      {
        path: 'outbound-detail/:id',
        name: 'OutboundDetail',
        component: () => import('../views/inventory/OutboundDetail.vue'),
        meta: { title: '出库单详情', hidden: true }
      },
      // 库存盘点
      {
        path: 'inventories',
        name: 'Inventories',
        component: () => import('../views/inventory/InventoryList.vue'),
        meta: { title: '库存盘点' }
      },
      {
        path: 'inventory-create',
        name: 'InventoryCreate',
        component: () => import('../views/inventory/InventoryForm.vue'),
        meta: { title: '新建盘点单', hidden: true }
      },
      // 材料
      {
        path: 'materials',
        name: 'Materials',
        component: () => import('../views/inventory/MaterialList.vue'),
        meta: { title: '材料' }
      },
      // 材料变动
      {
        path: 'material-movements',
        name: 'MaterialMovements',
        component: () => import('../views/inventory/MaterialMovementList.vue'),
        meta: { title: '材料变动' }
      },
      // 材料批次 (需要创建新组件)
      {
        path: 'material-batches',
        name: 'MaterialBatches',
        component: () => import('../views/inventory/MaterialBatchList.vue'),
        meta: { title: '材料批次' }
      },
      // 采购单
      {
        path: 'purchases',
        name: 'Purchases',
        component: () => import('../views/inventory/PurchaseList.vue'),
        meta: { title: '采购单' }
      },
      {
        path: 'purchase-create',
        name: 'PurchaseCreate',
        component: () => import('../views/inventory/PurchaseForm.vue'),
        meta: { title: '新建采购单', hidden: true }
      },
      {
        path: 'purchase-edit/:id',
        name: 'PurchaseEdit',
        component: () => import('../views/inventory/PurchaseForm.vue'),
        meta: { title: '编辑采购单', hidden: true }
      }
    ]
  },
  {
    path: '/production',
    component: Layout,
    redirect: '/production/process-steps',
    meta: { title: '生产管理', icon: 'SetUp' },
    children: [
      // 工序
      {
        path: 'process-steps',
        name: 'ProcessSteps',
        component: () => import('../views/production/ProcessStepList.vue'),
        meta: { title: '工序' }
      },
      // 工序排程
      {
        path: 'process-schedules',
        name: 'ProcessSchedules',
        component: () => import('../views/production/ProcessScheduleList.vue'),
        meta: { title: '工序排程' }
      },
      // 材料需求
      {
        path: 'material-requirements',
        name: 'MaterialRequirements',
        component: () => import('../views/production/MaterialRequirementList.vue'),
        meta: { title: '材料需求' }
      },
      // 生产用料
      {
        path: 'production-materials',
        name: 'ProductionMaterials',
        component: () => import('../views/production/ProductionMaterialList.vue'),
        meta: { title: '生产用料' }
      },
      // 生产订单
      {
        path: 'production-orders',
        name: 'ProductionOrders',
        component: () => import('../views/production/ProductionOrderList.vue'),
        meta: { title: '生产订单' }
      },
      {
        path: 'production-order-create',
        name: 'ProductionOrderCreate',
        component: () => import('../views/production/ProductionOrderForm.vue'),
        meta: { title: '新建生产订单', hidden: true }
      },
      {
        path: 'production-order-edit/:id',
        name: 'ProductionOrderEdit',
        component: () => import('../views/production/ProductionOrderForm.vue'),
        meta: { title: '编辑生产订单', hidden: true }
      },
      {
        path: 'production-order-detail/:id',
        name: 'ProductionOrderDetail',
        component: () => import('../views/production/ProductionOrderDetail.vue'),
        meta: { title: '生产订单详情', hidden: true }
      },
      // 生产进度
      {
        path: 'production-progress',
        name: 'ProductionProgress',
        component: () => import('../views/production/ProductionProgressList.vue'),
        meta: { title: '生产进度' }
      },
      // 设备
      {
        path: 'equipments',
        name: 'Equipments',
        component: () => import('../views/production/EquipmentList.vue'),
        meta: { title: '设备' }
      }
    ]
  },
  {
    path: '/orders',
    component: Layout,
    redirect: '/orders/orders',
    meta: { title: '订单管理', icon: 'Document' },
    children: [
      // 订单
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('../views/orders/OrderList.vue'),
        meta: { title: '订单' }
      },
      {
        path: 'create',
        name: 'OrderCreate',
        component: () => import('../views/orders/OrderForm.vue'),
        meta: { title: '新建订单', hidden: true }
      },
      {
        path: ':id/edit',
        name: 'OrderEdit',
        component: () => import('../views/orders/OrderForm.vue'),
        meta: { title: '编辑订单', hidden: true }
      },
      // 客户管理
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('../views/orders/CustomerList.vue'),
        meta: { title: '客户管理' }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/test',
    name: 'Test',
    component: () => import('../views/TestPage.vue'),
    meta: { title: 'API测试' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 冰刀系统` : '冰刀系统'
  
  // 检查登录状态 (允许测试页面无需登录访问)
  const isAuthenticated = localStorage.getItem('token')
  if (to.path !== '/login' && to.path !== '/test' && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router 