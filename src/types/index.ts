// 登录表单数据类型
export interface LoginFormData {
  email: string;
  password: string;
}

// 登录成功响应
export interface LoginResponse {
  token: string;
  user: {
    id: string;
    email: string;
    name: string;
  };
}

// 忘记密码请求参数
export interface ForgotPasswordParams {
  email: string;
}

// API 错误类型
export interface ApiError<T = any> {
  response?: {
    data: T;
    status: number;
    headers: any;
  };
  message: string;
}

// API 通用响应类型
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}
