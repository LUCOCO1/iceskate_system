import request from './request'

// 材料相关接口
export function getMaterialList(params?: any) {
  return request({
    url: '/inventory/materials/',
    method: 'get',
    params
  })
}

export function getMaterialDetail(id: number) {
  return request({
    url: `/inventory/materials/${id}/`,
    method: 'get'
  })
}

export function createMaterial(data: any) {
  return request({
    url: '/inventory/materials/',
    method: 'post',
    data
  })
}

export function updateMaterial(id: number, data: any) {
  return request({
    url: `/inventory/materials/${id}/`,
    method: 'put',
    data
  })
}

export function deleteMaterial(id: number) {
  return request({
    url: `/inventory/materials/${id}/`,
    method: 'delete'
  })
}

// 产品相关接口
export function getProductList(params?: any) {
  return request({
    url: '/inventory/products/',
    method: 'get',
    params
  })
}

export function getProductDetail(id: number) {
  return request({
    url: `/inventory/products/${id}/`,
    method: 'get'
  })
}

export function createProduct(data: any) {
  return request({
    url: '/inventory/products/',
    method: 'post',
    data
  })
}

export function updateProduct(id: number, data: any) {
  return request({
    url: `/inventory/products/${id}/`,
    method: 'put',
    data
  })
}

export function deleteProduct(id: number) {
  return request({
    url: `/inventory/products/${id}/`,
    method: 'delete'
  })
}

// 供应商相关接口
export function getSupplierList(params?: any) {
  return request({
    url: '/inventory/suppliers/',
    method: 'get',
    params
  })
}

export function getSupplierDetail(id: number) {
  return request({
    url: `/inventory/suppliers/${id}/`,
    method: 'get'
  })
}

export function createSupplier(data: any) {
  return request({
    url: '/inventory/suppliers/',
    method: 'post',
    data
  })
}

export function updateSupplier(id: number, data: any) {
  return request({
    url: `/inventory/suppliers/${id}/`,
    method: 'put',
    data
  })
}

export function deleteSupplier(id: number) {
  return request({
    url: `/inventory/suppliers/${id}/`,
    method: 'delete'
  })
}

// 材料变动记录接口
export function getMaterialMovementList(params?: any) {
  return request({
    url: '/inventory/movements/',
    method: 'get',
    params
  })
}

export function createMaterialMovement(data: any) {
  return request({
    url: '/inventory/movements/',
    method: 'post',
    data
  })
}

export function deleteMaterialMovement(id: number) {
  return request({
    url: `/inventory/movements/${id}/`,
    method: 'delete'
  })
}

// 产品变动记录接口
export function getProductMovementList(params?: any) {
  return request({
    url: '/inventory/product-movements/',
    method: 'get',
    params
  })
}

export function createProductMovement(data: any) {
  return request({
    url: '/inventory/product-movements/',
    method: 'post',
    data
  })
}

// 库存盘点相关接口
export function getInventoryList(params?: any) {
  return request({
    url: '/inventory/inventories/',
    method: 'get',
    params
  })
}

export function getInventoryDetail(id: number, type?: string) {
  return request({
    url: `/inventory/inventories/${id}/`,
    method: 'get',
    params: type ? { type } : undefined
  })
}

export function getInventoryMovementHistory(params: any) {
  return request({
    url: '/inventory/movements/',
    method: 'get',
    params
  })
}

export function createInventory(data: any) {
  return request({
    url: '/inventory/inventories/',
    method: 'post',
    data
  })
}

export function updateInventory(id: number, data: any) {
  return request({
    url: `/inventory/inventories/${id}/`,
    method: 'put',
    data
  })
}

export function deleteInventory(id: number) {
  return request({
    url: `/inventory/inventories/${id}/`,
    method: 'delete'
  })
}

// 材料采购单接口
export function getPurchaseList(params?: any) {
  return request({
    url: '/inventory/purchases/',
    method: 'get',
    params
  })
}

export function getPurchaseDetail(id: number) {
  return request({
    url: `/inventory/purchases/${id}/`,
    method: 'get'
  })
}

export function createPurchase(data: any) {
  return request({
    url: '/inventory/purchases/',
    method: 'post',
    data
  })
}

export function updatePurchase(id: number, data: any) {
  return request({
    url: `/inventory/purchases/${id}/`,
    method: 'put',
    data
  })
}

export function deletePurchase(id: number) {
  return request({
    url: `/inventory/purchases/${id}/`,
    method: 'delete'
  })
}

// 产品出库单接口
export function getProductOutboundList(params?: any) {
  return request({
    url: '/inventory/outbounds/',
    method: 'get',
    params
  })
}

export function getProductOutboundDetail(id: number) {
  return request({
    url: `/inventory/outbounds/${id}/`,
    method: 'get'
  })
}

export function createProductOutbound(data: any) {
  return request({
    url: '/inventory/outbounds/',
    method: 'post',
    data
  })
}

export function updateProductOutbound(id: number, data: any) {
  return request({
    url: `/inventory/outbounds/${id}/`,
    method: 'put',
    data
  })
}

export function deleteProductOutbound(id: number) {
  return request({
    url: `/inventory/outbounds/${id}/`,
    method: 'delete'
  })
}

// 客户相关接口
export function getCustomerList(params?: any) {
  return request({
    url: '/orders/customers/',
    method: 'get',
    params
  })
}

// 别名导出，用于兼容现有代码
export const getOutboundList = getProductOutboundList
export const getOutboundDetail = getProductOutboundDetail
export const createOutbound = createProductOutbound
export const updateOutbound = updateProductOutbound
export const deleteOutbound = deleteProductOutbound

// 确认入库
export function confirmPurchase(id: number) {
  return request({
    url: `/inventory/purchases/${id}/receive/`,
    method: 'post'
  })
}

// 取消入库
export function cancelPurchaseReceive(id: number) {
  return request({
    url: `/inventory/purchases/${id}/cancel_receive/`,
    method: 'post'
  })
}

// 确认出库
export function confirmOutbound(id: number) {
  return request({
    url: `/inventory/outbounds/${id}/confirm/`,
    method: 'post'
  })
}

// 取消出库
export function cancelOutbound(id: number) {
  return request({
    url: `/inventory/outbounds/${id}/cancel/`,
    method: 'post'
  })
}

// 材料批次相关接口
export function getMaterialBatchList(params?: any) {
  return request({
    url: '/inventory/batches/',
    method: 'get',
    params
  })
}

export function getMaterialBatchDetail(id: number) {
  return request({
    url: `/inventory/batches/${id}/`,
    method: 'get'
  })
}

export function createMaterialBatch(data: any) {
  return request({
    url: '/inventory/batches/',
    method: 'post',
    data
  })
}

export function updateMaterialBatch(id: number, data: any) {
  return request({
    url: `/inventory/batches/${id}/`,
    method: 'put',
    data
  })
}

export function deleteMaterialBatch(id: number) {
  return request({
    url: `/inventory/batches/${id}/`,
    method: 'delete'
  })
}

// 材料需求计算接口
export function calculateMaterialRequirements(data: any) {
  return request({
    url: '/inventory/products/calculate_material_requirements/',
    method: 'post',
    data
  })
} 