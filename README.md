# 富途模拟交易API

基于富途牛牛Web端的模拟交易API服务，支持美股、港股、A股的行情查询和模拟交易。

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

## 技术栈

- FastAPI - Web框架
- httpx - HTTP客户端
- pandas - 数据处理
- pandas-ta - 技术指标计算

## 许可证

MIT License
