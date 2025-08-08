import request from './request'

export function getUserList(params?: any) {
  return request({
    url: '/api/system/users/',
    method: 'get',
    params
  })
}

export function getUserDetail(id: number) {
  return request({
    url: `/api/system/users/${id}/`,
    method: 'get'
  })
}

export function updateUserProfile(data: any) {
  return request({
    url: '/api/system/users/profile/',
    method: 'put',
    data
  })
}

export function changePassword(data: any) {
  return request({
    url: '/api/auth/change-password/',
    method: 'post',
    data
  })
}

export function getDashboardStats() {
  return request({
    url: '/api/system/dashboard-stats/',
    method: 'get'
  })
}

export function getDashboardProduction(timeRange: string = 'week') {
  return request({
    url: '/api/system/dashboard-production/',
    method: 'get',
    params: { time_range: timeRange }
  })
}

export function getDashboardInventory(type: string = 'material') {
  return request({
    url: '/api/system/dashboard-inventory/',
    method: 'get',
    params: { type }
  })
} 