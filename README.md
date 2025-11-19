# 富途模拟交易API

基于富途牛牛Web端的模拟交易API服务，支持美股、港股、A股的行情查询和模拟交易。

## 一键部署

[![Deploy to Leapcell](https://img.shields.io/badge/Deploy%20to-Leapcell-7C3AED?style=for-the-badge&logo=icloud&logoColor=white)](https://leapcell.io/new/clone?repositoryUrl=https://github.com/BSTester/futu-paper-trade-api)
[![Deploy to Render](https://img.shields.io/badge/Deploy%20to-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com/deploy?repo=https://github.com/BSTester/futu-paper-trade-api)

> **使用说明**：点击按钮即可开始部署，系统会自动从 GitHub 导入项目并配置。

详细部署指南：
- [Leapcell 部署文档](docs/LEAPCELL_DEPLOYMENT.md)
- [Render 部署文档](docs/RENDER_DEPLOYMENT.md)
- [完整部署指南](DEPLOY.md)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
# 富途Cookie（必填）
FUTU_COOKIE=your_cookie_here
FUTU_CSRF_TOKEN=your_csrf_token_here

# API Key（可选，用于接口鉴权）
API_KEY=your_secure_api_key_here

# API服务配置
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. 启动服务

```bash
python main.py
```

或使用启动脚本：

```bash
# Windows
start.bat

# Docker
docker-compose up -d
```

### 4. 访问API文档

- Swagger UI: http://localhost:8000/docs
- API文档: http://localhost:8000/api-docs

## 主要功能

- ✅ 账户信息查询
- ✅ 持仓查询
- ✅ 实时行情
- ✅ K线数据
- ✅ 技术指标分析
- ✅ 买入/卖出交易
- ✅ 订单查询与撤单
- ✅ 热门股票和新闻
- ✅ API Key 鉴权

## 部署指南

### 部署到 Leapcell

[Leapcell](https://leapcell.io/) 是一个现代化的应用部署平台，支持从 GitHub 仓库直接部署。

#### 方式一：一键部署（推荐）

点击上方的 "Deploy on Leapcell" 按钮，系统会自动：
- 从 GitHub 导入项目
- 读取 `leapcell.json` 配置文件
- 自动配置构建和启动命令
- 提示你填写必需的环境变量

你只需要：
1. 点击部署按钮
2. 授权 GitHub 访问
3. 填写环境变量（`FUTU_COOKIE` 和 `FUTU_CSRF_TOKEN`）
4. 点击部署

#### 方式二：手动部署

1. 访问 [Leapcell](https://leapcell.io/) 并登录
2. 点击 "New Project" 创建新项目
3. 选择 "Import from GitHub" 并授权访问你的仓库
4. 选择本项目的仓库
5. Leapcell 会自动检测 `leapcell.json` 配置文件
6. 填写必需的环境变量
7. 点击 "Deploy" 开始部署

#### 环境变量配置

**必填项：**
- `FUTU_COOKIE` - 从富途牛牛Web端获取的Cookie
- `FUTU_CSRF_TOKEN` - 从富途牛牛Web端获取的CSRF Token

**账户配置（根据需要配置）：**
- `ACCOUNT_ID_HK` - 港股账户ID（如需交易港股）
- `ACCOUNT_ID_US` - 美股模拟账户ID（如需交易美股）
- `ACCOUNT_ID_CN` - A股账户ID（如需交易A股）
- `ACCOUNT_ID_US_COMPETITION` - 美股比赛账户ID（可选，如配置则优先使用比赛账户）

**可选项：**
- `API_KEY` - API接口鉴权密钥（建议设置）
- `API_HOST` - 默认 `0.0.0.0`
- `API_PORT` - 默认 `8000`

> **账户ID获取方法**：登录富途牛牛Web端，在账户页面可以看到账户ID

#### 验证部署

部署完成后，访问以下地址验证：

- 健康检查: `https://your-app.leapcell.app/health`
- API文档: `https://your-app.leapcell.app/docs`
- 自定义文档: `https://your-app.leapcell.app/api-docs`

#### 更新 Cookie

Cookie 会定期过期，需要更新：

1. 在 Leapcell 项目设置中找到环境变量
2. 更新 `FUTU_COOKIE` 和 `FUTU_CSRF_TOKEN`
3. 保存后会自动重新部署

### 部署到 Render

[Render](https://render.com/) 是一个现代化的云平台，提供免费套餐和自动 HTTPS。

#### 方式一：一键部署（推荐）

点击上方的 "Deploy to Render" 按钮，系统会自动：
- 从 GitHub 导入项目
- 读取 `render.yaml` 配置文件
- 自动配置构建和启动命令
- 自动生成 API Key

你只需要：
1. 点击部署按钮
2. 授权 GitHub 访问
3. 填写必需的环境变量（`FUTU_COOKIE` 和 `FUTU_CSRF_TOKEN`）
4. 点击 "Apply" 开始部署

#### 方式二：手动部署

1. 访问 [Render](https://render.com/) 并登录
2. 点击 "New +" → "Web Service"
3. 连接 GitHub 仓库
4. Render 会自动检测 `render.yaml` 配置
5. 填写环境变量
6. 点击 "Create Web Service"

#### 环境变量配置

**必填项：**
- `FUTU_COOKIE` - 从富途牛牛Web端获取的Cookie
- `FUTU_CSRF_TOKEN` - 从富途牛牛Web端获取的CSRF Token

**账户配置（根据需要配置）：**
- `ACCOUNT_ID_HK` - 港股账户ID
- `ACCOUNT_ID_US` - 美股模拟账户ID
- `ACCOUNT_ID_CN` - A股账户ID
- `ACCOUNT_ID_US_COMPETITION` - 美股比赛账户ID（可选）

**自动生成：**
- `API_KEY` - Render 会自动生成随机密钥

#### 验证部署

部署完成后，访问以下地址验证：

- 健康检查: `https://your-app.onrender.com/health`
- API文档: `https://your-app.onrender.com/docs`
- 自定义文档: `https://your-app.onrender.com/api-docs`

#### 注意事项

- **免费套餐限制**：15分钟无请求后会自动休眠，下次请求时需要等待唤醒（约30秒）
- **自动部署**：推送到 GitHub 主分支会自动触发部署
- **HTTPS**：Render 自动提供免费的 HTTPS 证书

详细说明请查看：[Render 部署文档](docs/RENDER_DEPLOYMENT.md)

### 部署到 Railway

详细的 Railway 部署说明请参考：[docs/RAILWAY_DEPLOYMENT.md](docs/RAILWAY_DEPLOYMENT.md)

### Docker 部署

```bash
# 构建镜像
docker build -t futu-trading-api .

# 运行容器
docker run -d -p 8000:8000 --env-file .env futu-trading-api

# 或使用 docker-compose
docker-compose up -d
```

## 技术栈

- FastAPI - Web框架
- httpx - HTTP客户端
- pandas - 数据处理
- pandas-ta - 技术指标计算

## 许可证

MIT License
