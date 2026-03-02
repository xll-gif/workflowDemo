import React, { useState } from 'react';
import { useForm } from '../../hooks/useForm';
import { login, forgotPassword } from '../../services/api';
import { LoginFormData, ApiError } from '../../types';
import Button from '../ui/Button';
import Input from '../ui/Input';
import logo from '@assets/logo.png';

const LoginPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const initialValues: LoginFormData = {
    email: '',
    password: ''
  };

  const validate = (values: LoginFormData) => {
    const errors: Partial<LoginFormData> = {};
    
    if (!values.email) {
      errors.email = '请输入邮箱';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
      errors.email = '请输入有效的邮箱地址';
    }
    
    if (!values.password) {
      errors.password = '请输入密码';
    } else if (values.password.length < 6) {
      errors.password = '密码长度不能少于6位';
    }
    
    return errors;
  };

  const { values, errors, touched, handleChange, handleBlur, handleSubmit, isValid } = useForm({
    initialValues,
    validate
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await login(data);
      localStorage.setItem('token', response.data.data.token);
      window.location.href = '/dashboard';
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.response?.data?.message || '登录失败，请检查邮箱和密码是否正确');
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = () => {
    if (!values.email) {
      setError('请先输入邮箱地址');
      return;
    }
    forgotPassword({ email: values.email })
      .then(() => {
        alert('重置密码邮件已发送到您的邮箱');
      })
      .catch(() => {
        setError('发送重置邮件失败，请稍后重试');
      });
  };

  return (
    <div className="w-full max-w-md mx-auto flex flex-col items-center space-y-8">
      {/* 品牌Logo */}
      <img 
        src={logo} 
        alt="品牌标识" 
        className="w-24 h-24 object-contain mb-4"
      />
      
      {/* 标题区域 */}
      <div className="text-center space-y-2 w-full">
        <h1 className="text-2xl font-bold text-gray-900">欢迎回来</h1>
        <p className="text-gray-500">请登录您的账户以继续</p>
      </div>

      {/* 登录表单 */}
      <form 
        onSubmit={handleSubmit(onSubmit)} 
        className="w-full space-y-6"
      >
        {/* 邮箱输入框 */}
        <div className="space-y-1">
          <Input
            type="email"
            name="email"
            placeholder="请输入邮箱"
            value={values.email}
            onChange={handleChange}
            onBlur={handleBlur}
            error={touched.email ? errors.email : undefined}
            className="w-full"
          />
        </div>

        {/* 密码输入框 */}
        <div className="space-y-1">
          <Input
            type="password"
            name="password"
            placeholder="请输入密码"
            value={values.password}
            onChange={handleChange}
            onBlur={handleBlur}
            error={touched.password ? errors.password : undefined}
            showPasswordToggle
            className="w-full"
          />
        </div>

        {/* 忘记密码链接 */}
        <div className="flex justify-end">
          <button
            type="button"
            onClick={handleForgotPassword}
            className="text-sm text-blue-500 hover:text-blue-600 transition-colors"
          >
            忘记密码？
          </button>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
            {error}
          </div>
        )}

        {/* 登录按钮 */}
        <Button
          type="submit"
          disabled={!isValid || isLoading}
          loading={isLoading}
          className="w-full h-10"
        >
          登录
        </Button>
      </form>
    </div>
  );
};

export default LoginPage;
