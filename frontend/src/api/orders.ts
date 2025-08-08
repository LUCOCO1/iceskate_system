import request from './request'

// 订单相关接口
export function getOrderList(params?: any) {
  return request({
    url: '/orders/orders/',
    method: 'get',
    params
  })
}

export function getOrderDetail(id: number) {
  return request({
    url: `/orders/orders/${id}/`,
    method: 'get'
  })
}

export function createOrder(data: any) {
  return request({
    url: '/orders/orders/',
    method: 'post',
    data
  })
}

export function updateOrder(id: number, data: any) {
  return request({
    url: `/orders/orders/${id}/`,
    method: 'put',
    data
  })
}

export function deleteOrder(id: number) {
  return request({
    url: `/orders/orders/${id}/`,
    method: 'delete'
  })
}

// 订单状态变更
export function confirmOrder(id: number) {
  return request({
    url: `/orders/orders/${id}/confirm/`,
    method: 'post'
  })
}

export function completeOrder(id: number) {
  return request({
    url: `/orders/orders/${id}/complete/`,
    method: 'post'
  })
}

export function cancelOrder(id: number) {
  return request({
    url: `/orders/orders/${id}/cancel/`,
    method: 'post'
  })
}

// 订单项接口
export function getOrderItemList(params?: any) {
  return request({
    url: '/orders/order-items/',
    method: 'get',
    params
  })
}

// 客户接口
export function getCustomerList(params?: any) {
  return request({
    url: '/orders/customers/',
    method: 'get',
    params
  })
}

export function getCustomerDetail(id: number) {
  return request({
    url: `/orders/customers/${id}/`,
    method: 'get'
  })
}

export function createCustomer(data: any) {
  return request({
    url: '/orders/customers/',
    method: 'post',
    data
  })
}

export function updateCustomer(id: number, data: any) {
  return request({
    url: `/orders/customers/${id}/`,
    method: 'put',
    data
  })
}

export function deleteCustomer(id: number) {
  return request({
    url: `/orders/customers/${id}/`,
    method: 'delete'
  })
} 