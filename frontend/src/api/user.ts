import request from './request'

interface LoginResponse {
  token: string;
  user: {
    id: number;
    username: string;
    email: string;
    isAdmin: boolean;
  };
}

// 用户登录
export function login(data: { username: string; password: string }): Promise<LoginResponse> {
  return request({
    url: '/auth/login/',
    method: 'post',
    data
  })
}

// 获取用户信息
export function getUserInfo() {
  return request({
    url: '/auth/user/',
    method: 'get'
  })
}

// 退出登录
export function logout() {
  return request({
    url: '/auth/logout/',
    method: 'post'
  })
} 