# 🚀 如何将 H5 项目推送到 GitHub

## 方法一：使用推送脚本（推荐）

1. **创建 GitHub 仓库**

   在 GitHub 上创建一个新的仓库，例如：`https://github.com/你的用户名/h5-login-app.git`

2. **运行推送脚本**

   ```bash
   cd /workspace/projects/h5-login-app
   ./push_to_github.sh https://github.com/你的用户名/h5-login-app.git
   ```

## 方法二：手动推送

1. **添加远程仓库**

   ```bash
   cd /workspace/projects/h5-login-app
   git remote add origin https://github.com/你的用户名/h5-login-app.git
   ```

2. **推送到 GitHub**

   ```bash
   git push -u origin master
   ```

## 🎉 推送成功后

你可以在 GitHub 上查看你的项目，并使用以下方式部署：

### 使用 GitHub Pages

1. 进入仓库的 **Settings** 页面
2. 找到 **Pages** 设置
3. 选择 **Source** 为 `gh-pages` 分支（需要先创建）或 `main` 分支的 `/docs` 目录
4. 保存后，GitHub 会自动部署你的应用

### 使用 Vercel（推荐）

1. 访问 [Vercel](https://vercel.com)
2. 导入你的 GitHub 仓库
3. Vercel 会自动检测项目配置（已有 `vercel.json`）
4. 点击 **Deploy** 即可

### 使用 Netlify

1. 访问 [Netlify](https://netlify.com)
2. 导入你的 GitHub 仓库
3. 构建命令：`npm run build`
4. 发布目录：`dist`
5. 点击 **Deploy site**

## 📦 项目本地预览

如果你想在本地预览项目：

```bash
cd /workspace/projects/h5-login-app
npm run dev
```

项目将在 http://localhost:3000 启动

## 🔧 注意事项

- 如果推送时提示认证错误，请配置 GitHub Token
- 建议使用 SSH 方式推送（需要配置 SSH 密钥）
- 确保你的 GitHub 仓库是公开的，或者你有访问权限

## 📝 部署后的访问

部署成功后，你会获得一个访问 URL，例如：

- Vercel: `https://h5-login-app.vercel.app`
- GitHub Pages: `https://你的用户名.github.io/h5-login-app`
- Netlify: `https://h5-login-app.netlify.app`

直接访问这个 URL 即可查看你的登录页面！

---

**祝部署成功！** 🎊
