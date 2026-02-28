import { rest } from 'msw'

// Mock 数据生成工具
const generateId = () => Math.random().toString(36).substr(2, 9)

// 导出 handlers
export const handlers = [
  // 用户登录
  rest.post('/api/auth/login', async (req, res, ctx) => {
    // 模拟延迟
    await new Promise(resolve => setTimeout(resolve, 500))

    const { email, password } = await req.json()

    // 模拟验证
    if (!email || !password) {
      return res(
        ctx.status(400),
        ctx.json({
          code: 400,
          message: '请输入邮箱和密码',
          data: null
        })
      )
    }

    // 模拟登录成功
    return res(
      ctx.status(200),
      ctx.json({
        code: 200,
        message: '登录成功',
        data: {
          token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
          refreshToken: 'refresh_token_here',
          user: {
            id: 1,
            name: '张三',
            email: email,
            avatar: 'https://example.com/avatar.jpg'
          },
          expiresIn: 7200
        }
      })
    )
  }),

  // 忘记密码
  rest.post('/api/auth/forgot-password', async (req, res, ctx) => {
    // 模拟延迟
    await new Promise(resolve => setTimeout(resolve, 500))

    const { email } = await req.json()

    if (!email) {
      return res(
        ctx.status(400),
        ctx.json({
          code: 400,
          message: '请输入邮箱',
          data: null
        })
      )
    }

    return res(
      ctx.status(200),
      ctx.json({
        code: 200,
        message: '重置密码邮件已发送',
        data: {
          email: email
        }
      })
    )
  })
]
