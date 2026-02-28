import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Input from '../ui/Input';
import Button from '../ui/Button';
import useForm from '../../hooks/useForm';
import { login, forgotPassword } from '../../services/api';
import { LoginRequest } from '../../types';
import logo from '@assets/logo.png?raw';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const { values, errors, handleChange, validateForm } = useForm<LoginRequest>({
    initialValues: {
      email: '',
      password: ''
    },
    validations: {
      email: (value) => {
        if (!value) return '请输入邮箱';
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return '请输入有效的邮箱地址';
        return '';
      },
      password: (value) => {
        if (!value) return '请输入密码';
        if (value.length < 6) return '密码长度不能少于6位';
        return '';
      }
    }
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) return;

    setLoading(true);
    try {
      const response = await login(values);
      localStorage.setItem('token', response.token);
      localStorage.setItem('user', JSON.stringify(response.user));
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.message || '登录失败，请检查邮箱和密码是否正确');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async () => {
    if (!values.email) {
      setError('请先输入邮箱地址');
      return;
    }

    const emailError = errors.email;
    if (emailError) {
      setError(emailError);
      return;
    }

    setLoading(true);
    try {
      await forgotPassword({ email: values.email });
      alert('重置密码邮件已发送到您的邮箱，请查收');
    } catch (err: any) {
      setError(err.response?.data?.message || '发送失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-8">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <img src={`data:image/svg+xml;base64,${btoa(logo)}`} alt="Logo" className="w-[100px] h-[100px] object-contain" />
        </div>

        {/* 标题 */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">欢迎回来</h1>
          <p className="text-gray-500">登录您的账户继续使用服务</p>
        </div>

        {/* 表单 */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            type="email"
            placeholder="请输入邮箱"
            value={values.email}
            onChange={(e) => handleChange('email', e.target.value)}
            error={errors.email}
            className="w-full"
            disabled={loading}
            autoComplete="username"
          />

          <Input
            type={showPassword ? 'text' : 'password'}
            placeholder="请输入密码"
            value={values.password}
            onChange={(e) => handleChange('password', e.target.value)}
            error={errors.password}
            className="w-full"
            disabled={loading}
            autoComplete="current-password"
            suffix={
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="text-gray-400 hover:text-gray-600 focus:outline-none"
              >
                {showPassword ? '👁️' : '🙈'}
              </button>
            }
          />

          {/* 错误提示 */}
          {error && (
            <div className="text-red-500 text-sm text-center p-2 bg-red-50 rounded">
              {error}
            </div>
          )}

          {/* 忘记密码链接 */}
          <div className="text-right">
            <button
              type="button"
              onClick={handleForgotPassword}
              className="text-sm text-blue-500 hover:text-blue-600 focus:outline-none"
              disabled={loading}
            >
              忘记密码？
            </button>
          </div>

          {/* 登录按钮 */}
          <Button
            type="submit"
            className="w-full h-10"
            loading={loading}
            disabled={loading}
          >
            登录
          </Button>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;