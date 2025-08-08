import request from './request'

// 生产订单相关接口
export function getProductionOrderList(params?: any) {
  return request({
    url: '/production/production-orders/',
    method: 'get',
    params
  })
}

export function getProductionOrderDetail(id: number) {
  return request({
    url: `/production/production-orders/${id}/`,
    method: 'get'
  })
}

export function createProductionOrder(data: any) {
  return request({
    url: '/production/production-orders/',
    method: 'post',
    data
  })
}

export function updateProductionOrder(id: number, data: any) {
  return request({
    url: `/production/production-orders/${id}/`,
    method: 'put',
    data
  })
}

export function deleteProductionOrder(id: number) {
  return request({
    url: `/production/production-orders/${id}/`,
    method: 'delete'
  })
}

// 生产订单状态变更
export function materialReadyProductionOrder(id: number) {
  return request({
    url: `/production/production-orders/${id}/material_ready/`,
    method: 'post'
  })
}

export function startProductionOrder(id: number) {
  return request({
    url: `/production/production-orders/${id}/start_production/`,
    method: 'post'
  })
}

export function completeProductionOrder(id: number, data: any) {
  return request({
    url: `/production/production-orders/${id}/complete_production/`,
    method: 'post',
    data
  })
}

export function recordProductionProgress(id: number, data: any) {
  return request({
    url: `/production/production-orders/${id}/record_progress/`,
    method: 'post',
    data
  })
}

export function cancelProductionProgress(id: number, progressId: number) {
  return request({
    url: `/production/production-orders/${id}/cancel_progress/`,
    method: 'post',
    data: { progress_id: progressId }
  })
}

// 工序步骤相关接口
export function getProcessStepList(params?: any) {
  return request({
    url: '/production/process-steps/',
    method: 'get',
    params
  })
}

export function getProcessStepDetail(id: number) {
  return request({
    url: `/production/process-steps/${id}/`,
    method: 'get'
  })
}

export function createProcessStep(data: any) {
  return request({
    url: '/production/process-steps/',
    method: 'post',
    data
  })
}

export function updateProcessStep(id: number, data: any) {
  return request({
    url: `/production/process-steps/${id}/`,
    method: 'put',
    data
  })
}

export function deleteProcessStep(id: number) {
  return request({
    url: `/production/process-steps/${id}/`,
    method: 'delete'
  })
}

// 设备管理相关接口
export function getEquipmentList(params?: any) {
  return request({
    url: '/production/equipments/',
    method: 'get',
    params
  })
}

export function getEquipmentDetail(id: number) {
  return request({
    url: `/production/equipments/${id}/`,
    method: 'get'
  })
}

export function createEquipment(data: any) {
  return request({
    url: '/production/equipments/',
    method: 'post',
    data
  })
}

export function updateEquipment(id: number, data: any) {
  return request({
    url: `/production/equipments/${id}/`,
    method: 'put',
    data
  })
}

export function deleteEquipment(id: number) {
  return request({
    url: `/production/equipments/${id}/`,
    method: 'delete'
  })
}

// 工序排程相关接口
export function getProcessScheduleList(params?: any) {
  return request({
    url: '/production/process-schedules/',
    method: 'get',
    params
  })
}

export function createProcessSchedule(data: any) {
  return request({
    url: '/production/process-schedules/',
    method: 'post',
    data
  })
}

export function updateProcessSchedule(id: number, data: any) {
  return request({
    url: `/production/process-schedules/${id}/`,
    method: 'put',
    data
  })
}

export function deleteProcessSchedule(id: number) {
  return request({
    url: `/production/process-schedules/${id}/`,
    method: 'delete'
  })
}

// 材料需求相关接口
export function getMaterialRequirementList(params?: any) {
  return request({
    url: '/production/material-requirements/',
    method: 'get',
    params
  })
}

export function createMaterialRequirement(data: any) {
  return request({
    url: '/production/material-requirements/',
    method: 'post',
    data
  })
}

export function updateMaterialRequirement(id: number, data: any) {
  return request({
    url: `/production/material-requirements/${id}/`,
    method: 'put',
    data
  })
}

export function deleteMaterialRequirement(id: number) {
  return request({
    url: `/production/material-requirements/${id}/`,
    method: 'delete'
  })
}

// 生产用料相关接口
export function getProductionMaterialList(params?: any) {
  return request({
    url: '/production/production-materials/',
    method: 'get',
    params
  })
}

export function createProductionMaterial(data: any) {
  return request({
    url: '/production/production-materials/',
    method: 'post',
    data
  })
}

export function updateProductionMaterial(id: number, data: any) {
  return request({
    url: `/production/production-materials/${id}/`,
    method: 'put',
    data
  })
}

export function deleteProductionMaterial(id: number) {
  return request({
    url: `/production/production-materials/${id}/`,
    method: 'delete'
  })
}

// 生产进度相关接口
export function getProductionProgressList(params?: any) {
  return request({
    url: '/production/production-progress/',
    method: 'get',
    params
  })
}

export function createProductionProgress(data: any) {
  return request({
    url: '/production/production-progress/',
    method: 'post',
    data
  })
}

export function updateProductionProgress(id: number, data: any) {
  return request({
    url: `/production/production-progress/${id}/`,
    method: 'put',
    data
  })
}

export function deleteProductionProgress(id: number) {
  return request({
    url: `/production/production-progress/${id}/`,
    method: 'delete'
  })
}

export function cancelProgress(id: number) {
  return request({
    url: `/production/production-progress/${id}/cancel_progress/`,
    method: 'post'
  })
} 