# Railway.app 部署指南

## 📋 部署步骤

### 1. 准备工作

确保你的代码已经推送到 GitHub 仓库。

### 2. 注册 Railway 账号

1. 访问 [Railway.app](https://railway.app/)
2. 使用 GitHub 账号登录
3. 授权 Railway 访问你的 GitHub 仓库

### 3. 创建新项目

1. 点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 选择你的仓库（futu-paper-trade-api）
4. Railway 会自动检测到 Python 项目并开始构建

### 4. 配置环境变量

在 Railway 项目面板中：

1. 点击你的服务
2. 进入 "Variables" 标签
3. 添加以下环境变量：

```
FUTU_COOKIE=你的富途Cookie
ACCOUNT_ID_HK=你的港股账户ID
ACCOUNT_ID_US=你的美股账户ID
ACCOUNT_ID_CN=你的A股账户ID
ACCOUNT_ID_US_COMPETITION=你的美股比赛账户ID（可选，如果有则优先使用）
API_KEY=你的API密钥
API_HOST=0.0.0.0
```

**注意**：
- 不要设置 `API_PORT`，Railway 会自动提供 `$PORT` 环境变量
- `FUTU_COOKIE` 需要从浏览器获取最新的 Cookie

### 5. 生成公网域名

1. 在服务设置中找到 "Networking" 或 "Settings"
2. 点击 "Generate Domain"
3. Railway 会自动分配一个 `.railway.app` 域名
4. 例如：`https://your-app-name.railway.app`

### 6. 访问你的 API

部署成功后，你可以通过以下地址访问：

- **API 根路径**：`https://your-app-name.railway.app/`
- **API 文档**：`https://your-app-name.railway.app/docs`
- **健康检查**：`https://your-app-name.railway.app/health`

### 7. 测试 API

使用 curl 或 Postman 测试：

```bash
# 健康检查（无需 API Key）
curl https://your-app-name.railway.app/health

# 获取账户信息（需要 API Key）
curl -H "X-API-Key: 你的API密钥" \
  "https://your-app-name.railway.app/api/account?market_type=US"
```

## 🔧 配置说明

### railway.json
- 定义构建和部署配置
- 使用 Nixpacks 自动检测 Python 环境
- 启动命令会自动使用 Railway 提供的 `$PORT`

### Procfile
- 备用启动配置
- 定义 web 进程启动命令

### runtime.txt
- 指定 Python 版本为 3.11

### .railwayignore
- 排除不需要部署的文件
- 减小部署包大小

## 💰 费用说明

**免费额度**：
- 每月 $5 credit
- 约 500 小时运行时间
- 512MB RAM
- 1GB 磁盘空间

**注意**：
- 如果超出免费额度，服务会暂停
- 可以升级到 Hobby Plan（$5/月）获得更多资源

## 🔄 自动部署

Railway 支持自动部署：
- 每次推送到 GitHub 主分支时自动重新部署
- 可以在 Railway 设置中配置部署分支

## 📊 监控和日志

在 Railway 面板中可以：
- 查看实时日志
- 监控 CPU 和内存使用
- 查看部署历史
- 设置告警

## ⚠️ 重要提示

1. **Cookie 过期**：富途 Cookie 会定期过期，需要手动更新环境变量
2. **API Key 安全**：不要在代码中硬编码 API Key，使用环境变量
3. **请求限制**：注意富途 API 的请求频率限制
4. **冷启动**：免费版可能有冷启动延迟（首次请求较慢）

## 🐛 故障排查

### 部署失败
- 检查 Railway 日志查看错误信息
- 确保 requirements.txt 中的依赖版本兼容
- 检查 Python 版本是否正确

### 服务无法访问
- 确认服务状态为 "Active"
- 检查环境变量是否正确配置
- 查看日志是否有启动错误

### Cookie 过期
- 重新从浏览器获取 Cookie
- 在 Railway 环境变量中更新 `FUTU_COOKIE`
- 服务会自动重启

## 📚 相关链接

- [Railway 文档](https://docs.railway.app/)
- [Railway 定价](https://railway.app/pricing)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
