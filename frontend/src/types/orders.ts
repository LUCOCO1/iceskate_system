// 客户类型
export interface Customer {
  id: number
  code: string
  name: string
  contact: string
  phone: string
  address: string
  email: string
  notes: string
  is_active: boolean
}

// 客户表单类型
export interface CustomerForm {
  code: string
  name: string
  contact: string
  phone: string
  address: string
  email: string
  notes: string
  is_active: boolean
}

// 订单明细类型
export interface OrderItem {
  id: number
  order: number
  product: number
  product_name?: string
  color: string
  material: string
  quantity: number
  unit: string
  notes: string
}

// 订单明细表单类型
export interface OrderItemForm {
  product: number | null
  product_name?: string
  color: string
  material: string
  quantity: number
  unit: string
  notes: string
}

// 订单类型
export interface Order {
  id: number
  order_number: string
  customer: number
  customer_name?: string
  order_date: string
  delivery_date: string
  status: 'pending' | 'processing' | 'completed' | 'shipped' | 'cancelled'
  status_display?: string
  notes: string
  customer_order_number: string
  created_by: number
  created_at: string
  updated_at: string
  items?: OrderItem[]
}

// 订单表单类型
export interface OrderForm {
  customer: number | null
  order_date: string
  delivery_date: string
  status: 'pending' | 'processing' | 'completed' | 'shipped' | 'cancelled'
  notes: string
  customer_order_number: string
  items: OrderItemForm[]
}

// 订单状态选项
export const ORDER_STATUS_OPTIONS = [
  { value: 'pending', label: '待处理', color: 'info' },
  { value: 'processing', label: '生产中', color: 'primary' },
  { value: 'completed', label: '已完成', color: 'success' },
  { value: 'shipped', label: '已发货', color: 'warning' },
  { value: 'cancelled', label: '已取消', color: 'danger' }
]

// 获取状态标签类型
export function getStatusTagType(status: string): string {
  const option = ORDER_STATUS_OPTIONS.find(opt => opt.value === status)
  return option?.color || 'info'
}

// 获取状态标签文本
export function getStatusLabel(status: string): string {
  const option = ORDER_STATUS_OPTIONS.find(opt => opt.value === status)
  return option?.label || '未知'
} 