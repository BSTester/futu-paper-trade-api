# 快速部署指南

本项目支持多种部署方式，选择最适合你的方式：

## 🚀 一键部署（推荐）

### Leapcell

最简单的部署方式，只需点击按钮：

1. 点击 README 中的 "Deploy on Leapcell" 按钮
2. 将 URL 中的 `YOUR_USERNAME/YOUR_REPO_NAME` 替换为你的 GitHub 仓库地址
3. 填写必需的环境变量（`FUTU_COOKIE` 和 `FUTU_CSRF_TOKEN`）
4. 点击部署

**优势**：
- ✅ 零配置，自动检测 `leapcell.json`
- ✅ 自动 HTTPS 域名
- ✅ 实时日志和监控
- ✅ 按使用量付费

**详细文档**：[docs/LEAPCELL_DEPLOYMENT.md](docs/LEAPCELL_DEPLOYMENT.md)

---

### Render

适合个人项目和测试环境：

1. 点击 README 中的 "Deploy to Render" 按钮
2. 授权 GitHub 访问
3. 填写环境变量（`FUTU_COOKIE` 和 `FUTU_CSRF_TOKEN`）
4. 点击 "Apply" 开始部署

**优势**：
- ✅ 完全免费（免费套餐）
- ✅ 自动 HTTPS 证书
- ✅ 自动部署（Git push 触发）
- ✅ 简单易用
- ⚠️ 免费套餐15分钟无请求后休眠

**详细文档**：[docs/RENDER_DEPLOYMENT.md](docs/RENDER_DEPLOYMENT.md)

---

### Railway

适合需要更多自定义配置的场景：

1. 点击 README 中的 "Deploy on Railway" 按钮
2. 连接 GitHub 仓库
3. 配置环境变量
4. 部署

**优势**：
- ✅ 丰富的配置选项
- ✅ 支持数据库等附加服务
- ✅ 免费额度较高

**详细文档**：[docs/RAILWAY_DEPLOYMENT.md](docs/RAILWAY_DEPLOYMENT.md)

---

## 🐳 Docker 部署

适合有 Docker 环境的服务器：

```bash
# 1. 克隆项目
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写 FUTU_COOKIE 和 FUTU_CSRF_TOKEN

# 3. 使用 Docker Compose 启动
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 访问服务
# http://localhost:8000
```

**优势**：
- ✅ 环境隔离
- ✅ 易于迁移
- ✅ 便于管理

---

## 💻 本地部署

适合开发和测试：

```bash
# 1. 克隆项目
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 4. 启动服务
python main.py

# 5. 访问服务
# http://localhost:8000
```

**Windows 用户**：
```bash
# 使用启动脚本
start.bat
```

---

## 🔧 环境变量说明

所有部署方式都需要配置以下环境变量：

### 必填项

| 变量名 | 说明 | 获取方式 |
|--------|------|----------|
| `FUTU_COOKIE` | 富途牛牛Web端Cookie | 从浏览器开发者工具获取 |
| `FUTU_CSRF_TOKEN` | CSRF Token | 从浏览器开发者工具获取 |

### 账户配置（根据需要配置）

| 变量名 | 说明 | 获取方式 |
|--------|------|----------|
| `ACCOUNT_ID_HK` | 港股账户ID | 登录富途Web端，在账户页面查看 |
| `ACCOUNT_ID_US` | 美股模拟账户ID | 登录富途Web端，在账户页面查看 |
| `ACCOUNT_ID_CN` | A股账户ID | 登录富途Web端，在账户页面查看 |
| `ACCOUNT_ID_US_COMPETITION` | 美股比赛账户ID（可选） | 登录富途Web端，在账户页面查看 |

> **说明**：
> - 如果配置了美股比赛账户，则美股交易会优先使用比赛账户
> - 如果未配置美股比赛账户，则美股交易使用模拟账户
> - 只需配置你要交易的市场对应的账户ID

### 可选项

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `API_KEY` | API接口鉴权密钥 | 无（不鉴权） |
| `API_HOST` | 服务监听地址 | `0.0.0.0` |
| `API_PORT` | 服务监听端口 | `8000` |

### 如何获取 Cookie 和 CSRF Token？

详细步骤请查看：[docs/LEAPCELL_DEPLOYMENT.md#获取富途-cookie-和-csrf-token](docs/LEAPCELL_DEPLOYMENT.md#获取富途-cookie-和-csrf-token)

---

## 📊 部署后验证

无论使用哪种部署方式，都可以通过以下方式验证：

### 1. 健康检查

```bash
curl https://your-domain.com/health
```

预期响应：
```json
{
  "status": "healthy"
}
```

### 2. 访问 API 文档

浏览器访问：
- Swagger UI: `https://your-domain.com/docs`
- 自定义文档: `https://your-domain.com/api-docs`

### 3. 测试接口

```bash
# 如果设置了 API_KEY
curl -H "X-API-Key: your_api_key" \
  "https://your-domain.com/api/account?market_type=US"

# 如果没有设置 API_KEY
curl "https://your-domain.com/api/account?market_type=US"
```

---

## ⚠️ 常见问题

### Cookie 过期怎么办？

Cookie 会定期过期，需要重新获取并更新：

1. 从富途Web端重新获取 Cookie 和 CSRF Token
2. 更新部署平台的环境变量
3. 重新部署（大多数平台会自动重启）

### 如何设置 API Key？

```bash
# 生成随机 API Key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 将生成的 Key 设置为环境变量 API_KEY
```

### 部署失败怎么办？

1. 查看部署日志，找到具体错误信息
2. 检查环境变量是否正确设置
3. 确认 `requirements.txt` 中的依赖是否完整
4. 查看对应平台的部署文档

---

## 📊 部署平台对比

| 特性 | Leapcell | Render | Railway | Docker |
|------|----------|--------|---------|--------|
| 免费套餐 | ✅ | ✅ | ✅ | ✅ |
| 一键部署 | ✅ | ✅ | ✅ | ❌ |
| 自动 HTTPS | ✅ | ✅ | ✅ | ❌ |
| 自动部署 | ✅ | ✅ | ✅ | ❌ |
| 休眠限制 | ❌ | ⚠️ 15分钟 | ⚠️ 取决于套餐 | ❌ |
| 配置难度 | 简单 | 简单 | 中等 | 中等 |
| 适用场景 | 生产环境 | 个人项目 | 全场景 | 自建服务器 |

**推荐选择**：
- 🥇 **生产环境**：Leapcell（稳定不休眠）
- 🥈 **个人测试**：Render（完全免费 + 保活服务）
- 🥉 **开发环境**：本地 Docker（完全控制）

## 📚 更多资源

- [部署平台对比指南](docs/DEPLOYMENT_COMPARISON.md) - **帮助你选择最适合的平台**
- [Leapcell 部署详细指南](docs/LEAPCELL_DEPLOYMENT.md)
- [Render 部署详细指南](docs/RENDER_DEPLOYMENT.md)
- [Railway 部署详细指南](docs/RAILWAY_DEPLOYMENT.md)
- [API 使用文档](http://localhost:8000/api-docs)
- [项目 README](README.md)

---

## 🆘 需要帮助？

- 提交 Issue: https://github.com/BSTester/futu-paper-trade-api/issues
- 查看文档: [docs/](docs/)
- 项目地址: https://github.com/BSTester/futu-paper-trade-api

---

**祝你部署顺利！🎉**
