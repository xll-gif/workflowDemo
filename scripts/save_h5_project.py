#!/usr/bin/env python3
"""
将生成的 H5 代码保存到本地并提交到 GitHub
"""
import os
import json
import subprocess
from pathlib import Path

# 读取生成的文件内容
with open('debug_llm_response.txt', 'r', encoding='utf-8') as f:
    response_data = json.load(f)

# 设置工作目录
workspace_path = os.getenv("COZE_WORKSPACE_PATH", "")
h5_project_dir = os.path.join(workspace_path, "h5-login-app")

print(f"工作目录: {workspace_path}")
print(f"H5 项目目录: {h5_project_dir}")

# 创建项目目录
os.makedirs(h5_project_dir, exist_ok=True)

# 保存文件
generated_files = response_data.get('generated_files', [])
print(f"\n开始保存 {len(generated_files)} 个文件...")

for file_info in generated_files:
    file_path = file_info.get('path', '')
    file_content = file_info.get('content', '')

    if not file_path:
        continue

    # 构建完整路径
    full_path = os.path.join(h5_project_dir, file_path)
    dir_path = os.path.dirname(full_path)

    # 创建目录
    os.makedirs(dir_path, exist_ok=True)

    # 保存文件
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(file_content)

    print(f"  ✓ {file_path}")

print(f"\n✅ 文件保存完成！")
print(f"📁 项目位置: {h5_project_dir}")

# 生成 index.html
index_html = """<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>登录页面</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""

with open(os.path.join(h5_project_dir, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_html)

print("  ✓ index.html")

# 创建 tsconfig.node.json
tsconfig_node = """{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
"""

with open(os.path.join(h5_project_dir, 'tsconfig.node.json'), 'w', encoding='utf-8') as f:
    f.write(tsconfig_node)

print("  ✓ tsconfig.node.json")

# 创建 public 目录和 vite.svg
public_dir = os.path.join(h5_project_dir, 'public')
os.makedirs(public_dir, exist_ok=True)

vite_svg = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" role="img" class="iconify iconify--logos" width="31.88" height="32" preserveAspectRatio="xMidYMid meet" viewBox="0 0 256 257"><defs><linearGradient id="IconifyId1813088fe1fbc01fb466" x1="-.828%" x2="57.636%" y1="7.652%" y2="78.411%"><stop offset="0%" stop-color="#41D1FF"></stop><stop offset="100%" stop-color="#BD34FE"></stop></linearGradient><linearGradient id="IconifyId1813088fe1fbc01fb467" x1="43.376%" x2="50.316%" y1="2.242%" y2="89.03%"><stop offset="0%" stop-color="#FFEA83"></stop><stop offset="8.333%" stop-color="#FFDD35"></stop><stop offset="100%" stop-color="#FFA800"></stop></linearGradient></defs><path fill="url(#IconifyId1813088fe1fbc01fb466)" d="M255.153 37.938L134.897 252.976c-2.483 4.44-8.862 4.466-11.382.048L.875 37.958c-2.746-4.814 1.371-10.646 6.827-9.67l120.385 21.517a6.537 6.537 0 0 0 2.322-.004l117.867-21.483c5.438-.991 9.574 4.796 6.877 9.62Z"></path><path fill="url(#IconifyId1813088fe1fbc01fb467)" d="M185.432.063L96.44 17.501a3.268 3.268 0 0 0-2.634 3.014l-5.474 92.456a3.268 3.268 0 0 0 3.997 3.378l24.777-5.718c2.318-.535 4.413 1.507 3.936 3.838l-7.361 36.047c-.495 2.426 1.782 4.5 4.151 3.78l15.304-4.649c2.372-.72 4.652 1.36 4.15 3.788l-11.698 56.621c-.732 3.542 3.979 5.473 5.943 2.437l1.313-2.028l72.516-144.72c1.215-2.423-.88-5.186-3.54-4.672l-25.505 4.922c-2.396.462-4.435-1.77-3.759-4.114l16.646-57.705c.677-2.35-1.37-4.583-3.769-4.113Z"></path></svg>"""

with open(os.path.join(public_dir, 'vite.svg'), 'w', encoding='utf-8') as f:
    f.write(vite_svg)

print("  ✓ public/vite.svg")

# 创建 src/assets 目录和 logo.png（使用占位图片）
assets_dir = os.path.join(h5_project_dir, 'src', 'assets')
os.makedirs(assets_dir, exist_ok=True)

# 创建一个简单的 SVG logo 代替图片
logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="#1890ff" rx="10"/>
  <text x="50" y="55" font-family="Arial" font-size="40" fill="white" text-anchor="middle" font-weight="bold">Logo</text>
</svg>"""

with open(os.path.join(assets_dir, 'logo.png'), 'w', encoding='utf-8') as f:
    f.write(logo_svg)

print("  ✓ src/assets/logo.png")

# 修改 LoginPage.tsx 中的 logo 导入（使用 svg 替代 png）
login_page_path = os.path.join(h5_project_dir, 'src/components/pages/LoginPage.tsx')
with open(login_page_path, 'r', encoding='utf-8') as f:
    login_page_content = f.read()

# 替换 logo 导入
login_page_content = login_page_content.replace(
    "import logo from '@assets/logo.png';",
    "import logo from '@assets/logo.png?raw';"
)

# 修改 img 标签使用 SVG
login_page_content = login_page_content.replace(
    'src={logo}',
    'src={`data:image/svg+xml;base64,${btoa(logo)}`}'
)

with open(login_page_path, 'w', encoding='utf-8') as f:
    f.write(login_page_content)

print("  ✓ 修改 LoginPage.tsx 的 logo 引用")

# 添加 vite.config.ts 的别名配置
vite_config_path = os.path.join(h5_project_dir, 'vite.config.ts')
with open(vite_config_path, 'r', encoding='utf-8') as f:
    vite_config_content = f.read()

# 添加 assets 别名
vite_config_content = vite_config_content.replace(
    'assets: path.resolve(__dirname, \'./src/assets\')',
    'assets: path.resolve(__dirname, \'./src/assets\'),\n    \'@assets/*\': path.resolve(__dirname, \'./src/assets/*\')'
)

with open(vite_config_path, 'w', encoding='utf-8') as f:
    f.write(vite_config_content)

print("  ✓ 更新 vite.config.ts")

print("\n" + "="*60)
print("✅ H5 项目文件保存完成！")
print("="*60)
print(f"\n📁 项目目录: {h5_project_dir}")
print("\n📝 后续步骤:")
print("  1. cd " + h5_project_dir)
print("  2. npm install")
print("  3. npm run dev")
print("\n项目将在 http://localhost:3000 启动")
