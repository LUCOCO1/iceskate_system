// 材料批次相关类型定义

export interface MaterialBatch {
  id: number
  batch_number: string
  material: number
  material_name: string
  purchase: number
  production_date: string
  expiry_date: string | null
  initial_quantity: number
  remaining_quantity: number
  status: 'normal' | 'expired' | 'depleted'
  created_at: string
}

export interface MaterialBatchQuery {
  page?: number
  page_size?: number
  batch_number?: string
  material?: number | string
  status?: string
}

export interface MaterialBatchForm {
  material: number | null
  batch_number: string
  production_date: string
  expiry_date: string
  initial_quantity: number
  notes: string
}

export interface MaterialBatchResponse {
  count: number
  next: string | null
  previous: string | null
  results: MaterialBatch[]
}

export interface MaterialBatchDetail extends MaterialBatch {
  material_detail: {
    id: number
    name: string
    code: string
    specification: string
    unit: string
  }
  purchase_detail: {
    id: number
    purchase_number: string
    supplier_name: string
    purchase_date: string
  }
  movements: Array<{
    id: number
    movement_type: 'in' | 'out'
    quantity: number
    movement_date: string
    reference_number: string
    notes: string
  }>
}

export interface BatchStatistics {
  total_batches: number
  normal_batches: number
  expired_batches: number
  depleted_batches: number
  total_quantity: number
  remaining_quantity: number
  expiring_soon: number
} 