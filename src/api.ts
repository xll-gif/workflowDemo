import axios from 'axios'

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 添加 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// API 接口定义
export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  code: number
  message: string
  data: {
    token: string
    refreshToken: string
    user: {
      id: number
      name: string
      email: string
      avatar: string
    }
    expiresIn: number
  }
}

export interface ForgotPasswordRequest {
  email: string
}

export interface ForgotPasswordResponse {
  code: number
  message: string
  data: {
    email: string
  }
}

// API 方法
export const authApi = {
  // 用户登录
  login(data: LoginRequest): Promise<LoginResponse> {
    return request.post('/auth/login', data)
  },

  // 忘记密码
  forgotPassword(data: ForgotPasswordRequest): Promise<ForgotPasswordResponse> {
    return request.post('/auth/forgot-password', data)
  }
}

export default request
