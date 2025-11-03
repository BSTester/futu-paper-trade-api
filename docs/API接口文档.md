# 富途模拟交易API - 接口文档

## 📋 接口总览

本API提供了6个核心接口，涵盖账户、持仓、行情、交易的完整功能。

| 方法 | 端点 | 功能 | 标签 |
|------|------|------|------|
| GET | /api/account | 获取账户信息 | 账户 |
| GET | /api/positions | 获取持仓列表 | 持仓 |
| GET | /api/quote | 获取股票行情 | 行情 |
| POST | /api/trade | 交易（买入/卖出） | 交易 |
| POST | /api/cancel | 撤单 | 交易 |
| GET | /api/orders | 查询订单 | 交易 |

## 🔧 接口详情

### 1. 获取账户信息

**端点**: `GET /api/account`

**参数**:
- `market_type` (必填): 市场类型
  - `US` - 美股
  - `HK` - 港股
  - `CN` - A股

**请求示例**:
```bash
curl "http://localhost:8000/api/account?market_type=US"
```

**响应示例**:
```json
{
  "account_id": "16992013",
  "net_asset": 1000000.00,
  "cash": 500000.00,
  "market_value": 500000.00,
  "buying_power": 500000.00,
  "profit_loss": 50000.00,
  "profit_loss_ratio": 5.0,
  "today_profit_loss": 1000.00,
  "today_profit_loss_ratio": 0.1,
  "margin": 0.00,
  "available_funds": 500000.00
}
```

---

### 2. 获取持仓列表

**端点**: `GET /api/positions`

**参数**:
- `market_type` (必填): 市场类型 (US/HK/CN)

**请求示例**:
```bash
curl "http://localhost:8000/api/positions?market_type=US"
```

**响应示例**:
```json
[
  {
    "security_id": "202597",
    "stock_code": "AAPL",
    "stock_name": "苹果",
    "market_type": "US",
    "quantity": 100,
    "available_quantity": 100,
    "cost_price": 180.50,
    "current_price": 185.00,
    "market_value": 18500.00,
    "profit_loss": 450.00,
    "profit_loss_ratio": 2.49
  }
]
```

---

### 3. 获取股票行情

**端点**: `GET /api/quote`

**参数**:
- `stock_code` (必填): 股票代码
  - 美股: AAPL, TSLA, NVDA
  - 港股: 00700, 09988
  - A股: 600519, 000001
- `market_type` (必填): 市场类型 (US/HK/CN)

**请求示例**:
```bash
curl "http://localhost:8000/api/quote?stock_code=AAPL&market_type=US"
```

**响应示例**:
```json
[
  {
    "security_id": "202597",
    "stock_code": "AAPL",
    "stock_name": "苹果",
    "current_price": 185.00,
    "change": 2.50,
    "change_ratio": 1.37,
    "open_price": 183.00,
    "high_price": 186.00,
    "low_price": 182.50,
    "volume": 50000000
  }
]
```

---

### 4. 交易接口（买入/卖出）

**端点**: `POST /api/trade`

**参数**:
- `stock_code` (必填): 股票代码
- `market_type` (必填): 市场类型 (US/HK/CN)
- `side` (必填): 交易方向
  - `BUY` - 买入
  - `SELL` - 卖出
- `quantity` (必填): 数量
- `price` (可选): 价格（限价单必填）
- `order_type` (可选): 订单类型，默认 LIMIT
  - `LIMIT` - 限价单
  - `MARKET` - 市价单

**请求示例 - 买入**:
```bash
curl -X POST "http://localhost:8000/api/trade" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "AAPL",
    "market_type": "US",
    "side": "BUY",
    "quantity": 10,
    "price": 180.50,
    "order_type": "LIMIT"
  }'
```

**请求示例 - 卖出**:
```bash
curl -X POST "http://localhost:8000/api/trade" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "AAPL",
    "market_type": "US",
    "side": "SELL",
    "quantity": 10,
    "price": 185.00,
    "order_type": "LIMIT"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": "订单已提交",
  "order_id": "123456789",
  "data": {
    "stock_code": "AAPL",
    "stock_name": "苹果",
    "side": "BUY",
    "price": 180.50,
    "quantity": 10,
    "security_id": "202597",
    "account_id": "16992013",
    "market_type": "US"
  }
}
```

---

### 5. 撤单接口

**端点**: `POST /api/cancel`

**参数**:
- `order_id` (必填): 订单ID
- `market_type` (必填): 市场类型 (US/HK/CN)

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/cancel" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "123456789",
    "market_type": "US"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": "撤单成功",
  "order_id": "123456789",
  "data": {
    "account_id": "16992013",
    "order_id": "123456789",
    "market_type": "US"
  }
}
```

---

### 6. 查询订单

**端点**: `GET /api/orders`

**参数**:
- `market_type` (必填): 市场类型 (US/HK/CN)
- `filter_status` (可选): 过滤状态，默认 0
  - `0` - 全部订单
  - `1` - 已成交
  - `2` - 等待成交
  - `3` - 已撤单

**请求示例**:
```bash
# 查询所有订单
curl "http://localhost:8000/api/orders?market_type=US"

# 查询已成交订单
curl "http://localhost:8000/api/orders?market_type=US&filter_status=1"
```

**响应示例**:
```json
{
  "order_list": [
    {
      "order_id": "123456789",
      "stock_code": "AAPL",
      "stock_name": "苹果",
      "side": "B",
      "order_type": "LIMIT",
      "price": 180.50,
      "quantity": 10,
      "filled_quantity": 10,
      "status": "已成交",
      "create_time": 1730419200,
      "update_time": 1730419300
    }
  ],
  "total": 1
}
```

---

## 🌐 系统接口

### 健康检查

**端点**: `GET /health`

**响应**:
```json
{
  "status": "healthy"
}
```

### API信息

**端点**: `GET /`

**响应**:
```json
{
  "name": "富途模拟交易API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "api_docs": "/api-docs",
  "openapi": "/openapi.json"
}
```

---

## 📖 使用说明

### 市场类型

所有接口都需要指定市场类型：

- `US` - 美股
- `HK` - 港股
- `CN` - A股

### 股票代码格式

不同市场的股票代码格式：

- **美股**: 直接使用代码，如 `AAPL`, `TSLA`, `NVDA`
- **港股**: 5位数字，如 `00700` (腾讯), `09988` (阿里)
- **A股**: 6位数字，如 `600519` (茅台), `000001` (平安)

### 交易方向

- `BUY` - 买入
- `SELL` - 卖出

### 订单类型

- `LIMIT` - 限价单（需要指定价格）
- `MARKET` - 市价单（按当前市价成交）

### 订单状态

- `0` - 全部订单
- `1` - 已成交
- `2` - 等待成交
- `3` - 已撤单

---

## 🔐 认证配置

API需要配置有效的Cookie才能访问富途接口。

### 配置步骤

1. 编辑 `.env` 文件
2. 设置 `FUTU_COOKIE` 变量
3. 配置对应市场的账户ID：
   - `ACCOUNT_ID_US` - 美股账户
   - `ACCOUNT_ID_HK` - 港股账户
   - `ACCOUNT_ID_CN` - A股账户

### 获取Cookie

1. 浏览器访问 https://www.futunn.com/paper-trade
2. 登录账户
3. 打开开发者工具 (F12)
4. 切换到 Application/Storage → Cookies
5. 复制所有Cookie值

---

## 🧪 测试工具

### Swagger UI

访问 http://localhost:8000/docs 使用交互式文档测试接口。

### 测试脚本

```bash
# 测试所有接口
python test_simplified_api.py
```

### curl 示例

```bash
# 1. 获取账户信息
curl "http://localhost:8000/api/account?market_type=US"

# 2. 获取持仓
curl "http://localhost:8000/api/positions?market_type=US"

# 3. 获取行情
curl "http://localhost:8000/api/quote?stock_code=AAPL&market_type=US"

# 4. 买入股票
curl -X POST "http://localhost:8000/api/trade" \
  -H "Content-Type: application/json" \
  -d '{"stock_code":"AAPL","market_type":"US","side":"BUY","quantity":10,"price":180.50}'

# 5. 查询订单
curl "http://localhost:8000/api/orders?market_type=US"

# 6. 撤单
curl -X POST "http://localhost:8000/api/cancel" \
  -H "Content-Type: application/json" \
  -d '{"order_id":"123456789","market_type":"US"}'
```

---

## ⚠️ 注意事项

1. **Cookie有效期**: Cookie会过期，需要定期更新
2. **订单ID**: 撤单需要有效的订单ID，从下单响应中获取
3. **市场时间**: 只能在对应市场的交易时间内交易
4. **账户配置**: 确保配置了对应市场的账户ID
5. **价格精度**: 不同市场对价格精度有不同要求

---

## 📚 相关文档

- [快速开始指南](docs/快速开始指南.md)
- [配置说明](docs/环境变量配置说明.md)
- [故障排除](docs/故障排除.md)

---

## 🎯 接口设计原则

1. **简洁性**: 每个功能只有一个接口，避免重复
2. **一致性**: 所有接口都使用统一的参数格式
3. **明确性**: 参数命名清晰，功能明确
4. **完整性**: 涵盖交易的完整流程

---

**文档版本**: 1.0  
**更新时间**: 2025-11-01  
**服务地址**: http://localhost:8000  
**文档地址**: http://localhost:8000/docs
