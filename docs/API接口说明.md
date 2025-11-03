# API接口详细说明

## 基础信息

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`
- **认证方式**: Cookie（在配置文件中设置）

## 接口列表

### 1. 系统接口

#### 1.1 根路径
```http
GET /
```

**响应示例**:
```json
{
  "name": "富途模拟交易API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

#### 1.2 健康检查
```http
GET /health
```

**响应示例**:
```json
{
  "status": "healthy"
}
```

---

### 2. 账户接口

#### 2.1 获取账户列表
```http
GET /api/accounts
```

**功能**: 获取用户所有的模拟交易账户ID

**响应示例**:
```json
["16992013", "16992014"]
```

#### 2.2 获取账户详情
```http
GET /api/account/info?account_id=16992013
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| account_id | string | 否 | 账户ID，不传则使用默认账户 |

**响应示例**:
```json
{
  "account_id": "16992013",
  "net_asset": 100303.41,
  "cash": 89488.61,
  "market_value": 10814.80,
  "buying_power": 189792.02,
  "profit_loss": 304.40,
  "profit_loss_ratio": 0.0030,
  "today_profit_loss": 0.00,
  "today_profit_loss_ratio": 0.00,
  "margin": 4325.92,
  "available_funds": 95977.49
}
```

**字段说明**:
- `net_asset`: 资产净值（美元）
- `cash`: 现金余额
- `market_value`: 持仓市值
- `buying_power`: 最大购买力
- `profit_loss`: 持仓盈亏金额
- `profit_loss_ratio`: 持仓盈亏比例
- `today_profit_loss`: 今日盈亏金额
- `today_profit_loss_ratio`: 今日盈亏比例
- `margin`: 维持保证金
- `available_funds`: 剩余流动性

---

### 3. 持仓接口

#### 3.1 获取持仓列表
```http
GET /api/positions?account_id=16992013
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| account_id | string | 否 | 账户ID |

**响应示例**:
```json
[
  {
    "security_id": "202597",
    "stock_code": "NVDA",
    "stock_name": "英伟达",
    "market_type": "US",
    "quantity": 50,
    "available_quantity": 50,
    "cost_price": 200.50,
    "current_price": 202.49,
    "market_value": 10124.50,
    "profit_loss": 99.50,
    "profit_loss_ratio": 0.0099
  }
]
```

**字段说明**:
- `security_id`: 证券ID（内部使用）
- `stock_code`: 股票代码
- `stock_name`: 股票名称
- `market_type`: 市场类型
- `quantity`: 持仓数量
- `available_quantity`: 可卖数量
- `cost_price`: 成本价
- `current_price`: 当前价
- `market_value`: 持仓市值
- `profit_loss`: 盈亏金额
- `profit_loss_ratio`: 盈亏比例

---

### 4. 行情接口

#### 4.1 搜索股票
```http
POST /api/stock/search
Content-Type: application/json

{
  "keyword": "NVDA",
  "market_type": "US"
}
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 股票代码或名称 |
| market_type | string | 否 | 市场类型: US/HK/CN |

**响应示例**:
```json
[
  {
    "security_id": "202597",
    "stock_code": "NVDA",
    "stock_name": "英伟达",
    "market_type": "US",
    "security_type": "STOCK"
  }
]
```

**搜索示例**:
- 美股: `NVDA`, `AAPL`, `TSLA`, `Apple`
- 港股: `00700`, `09988`, `腾讯`, `阿里巴巴`
- A股: `600519`, `000001`, `茅台`, `平安银行`

#### 4.2 获取股票行情
```http
GET /api/stock/quote?security_ids=202597,202598&market_type=US
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| security_ids | string | 是 | 证券ID列表，逗号分隔 |
| market_type | string | 否 | 市场类型，默认US |

**响应示例**:
```json
[
  {
    "security_id": "202597",
    "stock_code": "NVDA",
    "stock_name": "英伟达",
    "current_price": 202.49,
    "change": 0.40,
    "change_ratio": 0.0020,
    "open_price": 202.10,
    "high_price": 203.50,
    "low_price": 201.50,
    "volume": 10716270
  }
]
```

#### 4.3 获取热门股票
```http
GET /api/stock/hot?market_type=US&count=10
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| market_type | string | 否 | 市场类型，默认US |
| count | int | 否 | 返回数量，默认10 |

**响应示例**:
```json
[
  {
    "security_id": "202597",
    "stock_code": "NVDA",
    "stock_name": "英伟达",
    "market_type": "US",
    "security_type": "STOCK"
  }
]
```

---

### 5. 交易接口

#### 5.1 下单交易（完整接口）
```http
POST /api/trade
Content-Type: application/json

{
  "stock_code": "NVDA",
  "market_type": "US",
  "side": "BUY",
  "order_type": "LIMIT",
  "price": 202.50,
  "quantity": 10,
  "security_type": "STOCK"
}
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| stock_code | string | 是 | 股票代码 |
| market_type | string | 是 | 市场类型: US/HK/CN |
| side | string | 是 | 交易方向: BUY/SELL |
| order_type | string | 是 | 订单类型: LIMIT/MARKET |
| price | float | 否 | 价格（限价单必填） |
| quantity | int | 是 | 数量（必须>0） |
| security_type | string | 否 | 证券类型，默认STOCK |

**响应示例**:
```json
{
  "success": true,
  "message": "下单成功",
  "order_id": "123456789",
  "data": {
    "stock_code": "NVDA",
    "stock_name": "英伟达",
    "side": "BUY",
    "price": 202.50,
    "quantity": 10,
    "security_id": "202597"
  }
}
```

#### 5.2 快速买入
```http
POST /api/trade/buy?stock_code=NVDA&market_type=US&quantity=10&price=202.50&order_type=LIMIT
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| stock_code | string | 是 | 股票代码 |
| market_type | string | 是 | 市场类型 |
| quantity | int | 是 | 买入数量 |
| price | float | 否 | 价格（限价单必填） |
| order_type | string | 否 | 订单类型，默认LIMIT |

**响应格式**: 同5.1

#### 5.3 快速卖出
```http
POST /api/trade/sell?stock_code=NVDA&market_type=US&quantity=10&price=203.00&order_type=LIMIT
```

**参数**: 同5.2

**响应格式**: 同5.1

---

## 市场类型说明

| 市场 | 代码 | 说明 | 股票代码示例 |
|------|------|------|-------------|
| 美股 | US | 美国股市 | NVDA, AAPL, TSLA, MSFT |
| 港股 | HK | 香港股市 | 00700, 09988, 01810, 03690 |
| A股 | CN | 中国A股 | 600519, 000001, 000858, 601318 |

## 订单类型说明

### LIMIT（限价单）
- 需要指定价格
- 按指定价格或更优价格成交
- 可能不会立即成交
- 适合对价格有明确要求的交易

**示例**:
```json
{
  "order_type": "LIMIT",
  "price": 202.50
}
```

### MARKET（市价单）
- 不需要指定价格
- 按当前市场价格立即成交
- 成交速度快
- 适合快速建仓或平仓

**示例**:
```json
{
  "order_type": "MARKET"
}
```

## 交易方向说明

- **BUY**: 买入（做多）
- **SELL**: 卖出（平仓或做空）

## 证券类型说明

- **STOCK**: 股票（默认）
- **ETF**: 交易所交易基金
- **OPTION**: 期权

## 错误响应

所有接口在出错时返回HTTP错误状态码和错误信息：

```json
{
  "detail": "错误描述信息"
}
```

常见错误码：
- `400`: 请求参数错误
- `401`: 认证失败（Cookie无效）
- `404`: 资源不存在
- `500`: 服务器内部错误

## 使用限制

1. **请求频率**: 建议控制在每秒10次以内
2. **Cookie有效期**: Cookie会过期，需要定期更新
3. **交易时间**: 遵循各市场的交易时间
4. **最小交易单位**: 
   - 美股: 1股
   - 港股: 通常100股（一手）
   - A股: 100股（一手）

## 完整交易流程示例

### 1. 查询账户信息
```bash
curl http://localhost:8000/api/account/info
```

### 2. 搜索要买的股票
```bash
curl -X POST http://localhost:8000/api/stock/search \
  -H "Content-Type: application/json" \
  -d '{"keyword":"NVDA","market_type":"US"}'
```

### 3. 获取实时行情
```bash
curl "http://localhost:8000/api/stock/quote?security_ids=202597&market_type=US"
```

### 4. 下单买入
```bash
curl -X POST "http://localhost:8000/api/trade/buy?stock_code=NVDA&market_type=US&quantity=10&price=202.50&order_type=LIMIT"
```

### 5. 查看持仓
```bash
curl http://localhost:8000/api/positions
```

### 6. 卖出股票
```bash
curl -X POST "http://localhost:8000/api/trade/sell?stock_code=NVDA&market_type=US&quantity=10&price=205.00&order_type=LIMIT"
```

## 注意事项

⚠️ **重要提示**:
1. 本API仅用于模拟交易，不涉及真实资金
2. Cookie需要从浏览器登录后获取
3. 请合理控制请求频率
4. 模拟交易结果不代表真实交易结果
5. 建议先在测试环境充分测试后再使用
