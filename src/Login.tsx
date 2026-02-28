import { useState } from 'react'
import { authApi } from './api'
import './Login.css'

interface LoginForm {
  email: string
  password: string
}

export default function Login() {
  const [formData, setFormData] = useState<LoginForm>({
    email: '',
    password: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  const validateForm = (): boolean => {
    if (!formData.email) {
      setError('请输入邮箱')
      return false
    }

    // 邮箱格式验证
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(formData.email)) {
      setError('请输入有效的邮箱地址')
      return false
    }

    if (!formData.password) {
      setError('请输入密码')
      return false
    }

    // 密码长度验证
    if (formData.password.length < 6) {
      setError('密码长度不能少于 6 位')
      return false
    }

    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // 表单验证
    if (!validateForm()) {
      return
    }

    setLoading(true)

    try {
      // 调用登录接口
      const response = await authApi.login({
        email: formData.email,
        password: formData.password
      })

      if (response.code === 200) {
        // 登录成功
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('refreshToken', response.data.refreshToken)
        localStorage.setItem('user', JSON.stringify(response.data.user))

        alert('登录成功！即将跳转...')

        // 跳转到首页（模拟）
        setTimeout(() => {
          console.log('跳转到首页')
          // window.location.href = '/home'
        }, 1000)
      } else {
        setError(response.message || '登录失败，请重试')
      }
    } catch (err: any) {
      console.error('Login error:', err)
      if (err.response?.data?.message) {
        setError(err.response.data.message)
      } else {
        setError('网络错误，请稍后重试')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleForgotPassword = () => {
    alert('跳转到忘记密码页面')
    // window.location.href = '/forgot-password'
  }

  return (
    <div className="login-page">
      <div className="login-container">
        {/* Logo */}
        <div className="login-logo">
          <img
            src="https://coze-coding-project.tos.coze.site/demo/login/logo.png"
            alt="Logo"
            className="logo-image"
          />
        </div>

        {/* 标题 */}
        <h1 className="login-title">欢迎回来</h1>
        <p className="login-subtitle">请登录您的账户</p>

        {/* 登录表单 */}
        <form className="login-form" onSubmit={handleSubmit}>
          {/* 错误提示 */}
          {error && <div className="error-message">{error}</div>}

          {/* 邮箱输入框 */}
          <div className="form-group">
            <div className="input-wrapper">
              <img
                src="https://coze-coding-project.tos.coze.site/demo/login/icon-email.png"
                alt="Email"
                className="input-icon"
              />
              <input
                type="email"
                className="form-input"
                placeholder="请输入邮箱"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                disabled={loading}
              />
            </div>
          </div>

          {/* 密码输入框 */}
          <div className="form-group">
            <div className="input-wrapper">
              <img
                src="https://coze-coding-project.tos.coze.site/demo/login/icon-lock.png"
                alt="Lock"
                className="input-icon"
              />
              <input
                type={showPassword ? 'text' : 'password'}
                className="form-input"
                placeholder="请输入密码"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                disabled={loading}
              />
              <button
                type="button"
                className="eye-button"
                onClick={() => setShowPassword(!showPassword)}
                disabled={loading}
              >
                <img
                  src="https://coze-coding-project.tos.coze.site/demo/login/icon-eye.png"
                  alt={showPassword ? 'Hide' : 'Show'}
                  className="eye-icon"
                />
              </button>
            </div>
          </div>

          {/* 登录按钮 */}
          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading ? '登录中...' : '登录'}
          </button>

          {/* 忘记密码 */}
          <div className="forgot-password">
            <button
              type="button"
              className="forgot-password-link"
              onClick={handleForgotPassword}
              disabled={loading}
            >
              忘记密码？
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
