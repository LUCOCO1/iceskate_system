// 材料类型
export interface Material {
  id: number
  name: string
  code: string
  specification: string
  dimensions?: string
  supply_method?: string
  unit: string
  stock: number
  min_stock: number
  warning_stock: number
  max_stock: number
  last_purchase_price?: number
  notes: string
  is_active: boolean
  stock_status?: string
}

// 材料变动记录类型
export interface MaterialMovement {
  id: number
  material: number
  material_name: string
  movement_type: 'in' | 'out' | 'adjust'
  movement_type_display: string
  quantity: number
  unit: string
  movement_date: string
  reference_number: string
  purchase?: number
  notes: string
  operator?: number
  location: string
  batch?: number
  source_info?: string
}

// 供应商类型
export interface Supplier {
  id: number
  name: string
  code: string
  contact: string
  phone: string
  address: string
  is_active: boolean
  notes: string
}

// 采购单类型
export interface MaterialPurchase {
  id: number
  purchase_number: string
  supplier: number
  supplier_name?: string
  purchase_date: string
  delivery_date?: string
  status: 'draft' | 'pending' | 'received' | 'completed' | 'cancelled'
  status_display?: string
  notes?: string
  created_at: string
  updated_at: string
  items?: PurchaseItem[]
}

// 采购单明细类型
export interface PurchaseItem {
  id: number
  purchase: number
  material: number
  material_name?: string
  material_specification?: string
  control_number: string
  specification: string
  quantity: number
  received_quantity: number
  unit: string
  material_type: string
  notes?: string
}

// 材料批次类型
export interface MaterialBatch {
  id: number
  material: number
  material_name?: string
  batch_number: string
  purchase?: number
  production_date?: string
  expiry_date?: string
  quantity: number
  remaining_quantity: number
  unit: string
  location?: string
  notes?: string
  created_at: string
}

// 库存盘点类型
export interface Inventory {
  id: number
  inventory_number: string
  inventory_date: string
  status: 'draft' | 'completed'
  status_display?: string
  notes?: string
  created_by: number
  created_by_username?: string
  created_at: string
  updated_at: string
  items?: InventoryItem[]
}

// 盘点明细类型
export interface InventoryItem {
  id: number
  inventory: number
  material: number
  material_name?: string
  system_quantity: number
  actual_quantity: number
  difference: number
  notes?: string
}

// 产品类型
export interface Product {
  id: number
  name: string
  code: string
  specification: string
  unit: string
  unit_weight?: number | string
  stock: number
  min_stock: number
  warning_stock: number
  max_stock: number
  customers: number[]
  customer_names: string[]
  customers_display: string
  stock_status: string
  notes: string
  is_active: boolean
}

// 产品变动记录类型
export interface ProductMovement {
  id: number
  product: number
  product_name: string
  movement_type: 'in' | 'out'
  movement_type_display: string
  quantity: number
  unit: string
  movement_date: string
  reference_number: string
  notes: string
  created_at: string
}

// 产品出库单类型
export interface ProductOutbound {
  id: number
  outbound_number: string
  outbound_date: string
  order?: number
  order_number?: string  // 关联订单号（只读）
  status: 'draft' | 'confirmed' | 'cancelled'
  status_display?: string  // 状态显示（只读）
  notes?: string
  created_by?: number
  created_by_name?: string  // 创建人姓名（只读）
  created_at: string
  items?: ProductOutboundItem[]
}

// 产品出库单明细类型
export interface ProductOutboundItem {
  id: number
  outbound: number
  product: number
  product_name?: string  // 产品名称（只读）
  product_code?: string  // 产品编码（只读）
  quantity: number
  unit: string
  notes?: string
}

// 客户类型
export interface Customer {
  id: number
  name: string
  code: string
  contact?: string
  phone?: string
  address?: string
  email?: string
  is_active: boolean
  notes?: string
}

// 库存详情类型（用于库存详情页面）
export interface InventoryDetail {
  id: number
  inventory_type: string
  material_id: number
  material_name: string
  material_code: string
  product_id: number
  product_name: string
  product_code: string
  specification: string
  quantity: number
  unit: string
  location: string
  min_stock: number
  max_stock: number
  last_update_time: string
  notes?: string
}

// 库存变动记录类型
export interface InventoryMovement {
  id: number
  inventory_id: number
  movement_type: 'in' | 'out' | 'transfer' | 'adjust'
  quantity_change: number
  after_quantity: number
  movement_date: string
  reference_number?: string
  location?: string
  operator?: string
  notes?: string
} 