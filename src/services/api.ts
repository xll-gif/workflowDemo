import axios from 'axios';
import { LoginFormData, LoginResponse, ForgotPasswordParams, ApiResponse } from '../types';

// 创建 Axios 实例
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 登录 API
export const login = (data: LoginFormData) => {
  return apiClient.post<ApiResponse<LoginResponse>>('/auth/login', data);
};

// 忘记密码 API
export const forgotPassword = (data: ForgotPasswordParams) => {
  return apiClient.post<ApiResponse>('/auth/forgot-password', data);
};

export default apiClient;
