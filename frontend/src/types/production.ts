// 生产订单类型
export interface ProductionOrder {
  id: number
  order_number: string
  sales_order?: number
  product: number
  product_name: string
  planned_quantity: number
  completed_quantity: number
  start_date: string
  end_date: string
  actual_start_date?: string
  actual_end_date?: string
  status: 'pending' | 'material_ready' | 'in_production' | 'completed'
  priority: 'high' | 'medium' | 'low'
  progress: number
  responsible_person: string
  notes?: string
  created_at: string
  updated_at: string
  estimated_completion_time?: string
  actual_production_cost?: number
  quality_check_status: 'pending' | 'passed' | 'failed'
  material_requirements?: MaterialRequirement[]
  progress_records?: ProductionProgress[]
  process_schedules?: ProcessSchedule[]
}

// 表单用的材料需求类型
export interface MaterialRequirementForm {
  material_name: string
  material_specification: string
  required_quantity: number
  notes: string
}

// 生产订单表单类型
export interface ProductionOrderForm {
  sales_order?: number
  product?: number
  product_name: string
  planned_quantity: number
  start_date: string
  end_date: string
  priority: 'high' | 'medium' | 'low'
  responsible_person: string
  notes: string
  material_requirements: MaterialRequirementForm[]
}

// 材料需求清单类型
export interface MaterialRequirement {
  id: number
  production_order: number
  material: number
  material_name?: string
  material_specification?: string
  required_quantity: number
  actual_quantity: number
  notes?: string
}

// 生产进度记录类型
export interface ProductionProgress {
  id: number
  production_order: number
  record_date: string
  quantity: number
  accumulated_quantity: number
  progress: number
  notes?: string
  created_at: string
  can_edit: boolean
  actual_efficiency: number
  delay_reason?: string
  quality_issues?: number
}

// 生产用料记录类型
export interface ProductionMaterial {
  id: number
  production_order: number
  material_batch: number
  material_name?: string
  batch_number?: string
  quantity_used: number
  unit: string
  usage_date: string
  notes?: string
}

// 工序步骤类型
export interface ProcessStep {
  id: number
  name: string
  code: string
  daily_capacity: number
  is_bottleneck: boolean
  sequence: number
  notes?: string
}

// 工序排程类型
export interface ProcessSchedule {
  id: number
  production_order: number
  process: number
  process_name?: string
  planned_start_time: string
  planned_end_time: string
  actual_start_time?: string
  actual_end_time?: string
  status: 'pending' | 'in_progress' | 'completed' | 'delayed'
  equipment?: number
  equipment_name?: string
  operator?: number
  operator_name?: string
  notes?: string
}

// 设备类型
export interface Equipment {
  id: number
  name: string
  code: string
  model: string
  status: 'normal' | 'maintenance' | 'malfunction' | 'scrapped'
  process_step: number
  process_step_name?: string
  daily_capacity: number
  purchase_date: string
  last_maintenance?: string
  next_maintenance?: string
  notes?: string
} 