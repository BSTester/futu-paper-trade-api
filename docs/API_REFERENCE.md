# 富途模拟交易API接口文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **文档地址**: `http://localhost:8000/docs`

## 接口列表

### 1. GET 请求接口（使用Query参数）

#### 1.1 获取账户信息
```
GET /api/account?market_type=US
```

**Query参数**：
- `market_type` (必填): 市场类型 (US/HK/CN)

**响应示例**：
```json
{
  "account_id": "17198232",
  "net_asset": 100000.0,
  "cash": 100000.0,
  "market_value": 0.0,
  "buying_power": 200000.0,
  "profit_loss": 0.0,
  "profit_loss_ratio": 0.0,
  "today_profit_loss": 0.0,
  "today_profit_loss_ratio": 0.0,
  "margin": 0.0,
  "available_funds": 100000.0
}
```

**测试命令**：
```bash
curl "http://localhost:8000/api/account?market_type=US"
```

---

#### 1.2 获取持仓列表
```
GET /api/positions?market_type=US
```

**Query参数**：
- `market_type` (必填): 市场类型 (US/HK/CN)

**响应示例**：
```json
{
  "positions": [
    {
      "security_id": "205189",
      "stock_code": "AAPL",
      "stock_name": "苹果",
      "market_type": "US",
      "quantity": 100,
      "available_quantity": 100,
      "cost_price": 150.0,
      "current_price": 155.0,
      "market_value": 15500.0,
      "profit_loss": 500.0,
      "profit_loss_ratio": 3.33
    }
  ],
  "count": 1
}
```

**测试命令**：
```bash
curl "http://localhost:8000/api/positions?market_type=US"
```

---

#### 1.3 获取股票行情
```
GET /api/quote?stock_code=AAPL
```

**Query参数**：
- `stock_code` (必填): 股票代码

**自动判断市场类型**：
- 5位数字（如00700）→ 港股
- 6位数字（如600519）→ A股
- 包含字母（如AAPL）→ 美股

**响应示例**：
```json
[
  {
    "security_id": "205189",
    "stock_code": "AAPL.US",
    "stock_name": "苹果",
    "current_price": 270.37,
    "change": -1.03,
    "change_ratio": -0.38
  }
]
```

**注意**: `open_price`, `high_price`, `low_price`, `volume` 只在有值时才会出现

**测试命令**：
```bash
# 美股
curl "http://localhost:8000/api/quote?stock_code=AAPL"

# 港股
curl "http://localhost:8000/api/quote?stock_code=00700"

# A股
curl "http://localhost:8000/api/quote?stock_code=600000"
```

---

#### 1.4 获取订单历史
```
GET /api/orders?market_type=US&filter_status=0
```

**Query参数**：
- `market_type` (必填): 市场类型 (US/HK/CN)
- `filter_status` (可选): 过滤状态
  - 0: 全部订单（默认）
  - 1: 已成交
  - 2: 等待成交
  - 3: 已撤单

**测试命令**：
```bash
curl "http://localhost:8000/api/orders?market_type=US"
curl "http://localhost:8000/api/orders?market_type=US&filter_status=1"
```

---

#### 1.5 获取热门新闻
```
GET /api/hot-news?lang=zh-cn
```

**Query参数**：
- `lang` (可选): 语言 (zh-cn/zh-hk/en-us，默认zh-cn)

**测试命令**：
```bash
curl "http://localhost:8000/api/hot-news"
curl "http://localhost:8000/api/hot-news?lang=en-us"
```

---

#### 1.6 获取热门股票
```
GET /api/hot-stocks?market_type=US&count=10
```

**Query参数**：
- `market_type` (可选): 市场类型 (US/HK/CN，默认US)
- `count` (可选): 返回数量（默认10）

**测试命令**：
```bash
curl "http://localhost:8000/api/hot-stocks"
curl "http://localhost:8000/api/hot-stocks?market_type=HK&count=20"
```

---

#### 1.7 获取技术分析指标
```
GET /api/technical-analysis?symbol=AAPL&interval=daily
```

**Query参数**：
- `symbol` (必填): 股票代码
- `interval` (可选): 时间间隔（默认daily）
  - 分钟级: 1min, 5min, 15min, 30min, 60min
  - 日线及以上: daily, weekly, monthly
- `indicator` (可选): 技术指标（默认macd）
  - 可选指标：close_50_sma, close_200_sma, close_10_ema, macd, rsi, boll, atr, vwma
- `format` (可选): 返回格式（默认json）
  - json: JSON格式
  - csv: CSV格式
- `start_date` (可选): 开始日期（格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS）
- `end_date` (可选): 结束日期（格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS）

**自动判断市场类型**：
- 5位数字（如00700）→ 港股
- 6位数字（如600519）→ A股
- 包含字母（如AAPL）→ 美股

**日期范围说明**：
- 如果不指定日期范围，月K及以上返回所有可用数据
- **周K及以下时间间隔**：如果不指定日期范围，默认返回最近1个月的数据（基于数据最新日期）
  - 适用于：1min, 5min, 15min, 30min, 60min, daily, weekly
- 如果指定日期范围，只返回该范围内的数据
- 日期格式支持：YYYY-MM-DD（如 2025-01-01）或 YYYY-MM-DD HH:MM:SS（如 2025-01-01 09:30:00）

**响应示例（返回时间序列数据）**：
```json
{
  "symbol": "AAPL",
  "stock_name": "苹果",
  "security_id": "205189",
  "market_type": "US",
  "interval": "daily",
  "latest_price": 270.37,
  "data_points": 200,
  "price_data": [
    {
      "time": 1730419200,
      "open": 268.50,
      "high": 271.20,
      "low": 267.80,
      "close": 270.37,
      "volume": 45678900
    }
  ],
  "indicators": {
    "rsi": {
      "name": "RSI",
      "description": "RSI: Measures momentum to flag overbought/oversold conditions...",
      "data": [
        {"time": 1730419200, "value": 65.32},
        {"time": 1730505600, "value": 66.15}
      ]
    },
    "macd": {
      "name": "MACD",
      "description": "MACD: Computes momentum via differences of EMAs...",
      "data": [
        {"time": 1730419200, "value": 2.15},
        {"time": 1730505600, "value": 2.35}
      ]
    },
    "close_50_sma": {
      "name": "50 SMA",
      "description": "50 SMA: A medium-term trend indicator...",
      "data": [
        {"time": 1730419200, "value": 268.50},
        {"time": 1730505600, "value": 268.75}
      ]
    }
  }
}
```

**数据说明**：
- `price_data`: 价格OHLCV时间序列数据
- `indicators`: 各技术指标的时间序列数据
- 每个指标包含 `data` 数组，每个元素包含 `time`（Unix时间戳）和 `value`（指标值）
- 可用于绘制价格曲线和指标曲线

**测试命令**：
```bash
# 日K线技术分析
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily"

# 5分钟K线技术分析
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=5min"

# 1小时K线技术分析
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=60min"

# 周K线技术分析
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=weekly"

# 获取特定指标
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&indicator=rsi"

# 指定日期范围（日K线）
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&start_date=2025-01-01&end_date=2025-10-31"

# 指定日期范围（分钟级）
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=5min&start_date=2025-11-01 09:30:00&end_date=2025-11-01 16:00:00"

# 只指定开始日期
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&start_date=2025-10-01"

# 港股日K线
curl "http://localhost:8000/api/technical-analysis?symbol=00700&interval=daily"

# A股5分钟K线
curl "http://localhost:8000/api/technical-analysis?symbol=600000&interval=5min"

# CSV格式输出
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&format=csv"
```

**时间间隔说明**：
- **1min, 5min, 15min, 30min, 60min**: 分钟级K线，适合短线交易
- **daily**: 日K线，适合中短期分析
- **weekly**: 周K线，适合中期趋势分析
- **monthly**: 月K线，适合长期趋势分析

---

#### 1.8 获取K线数据
```
GET /api/kline?symbol=AAPL&interval=daily
```

**Query参数**：
- `symbol` (必填): 股票代码
- `interval` (可选): 时间间隔（默认daily）
  - 分钟级: 1min, 5min, 15min, 30min, 60min
  - 日线及以上: daily, weekly, monthly, quarterly, yearly
  - 注意：weekly 不指定日期时默认返回最近1个月数据
- `start_date` (可选): 开始日期（格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS）
- `end_date` (可选): 结束日期（格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS）
- `format` (可选): 返回格式（默认json）
  - json: JSON格式
  - csv: CSV格式

**自动判断市场类型**：
- 5位数字（如00700）→ 港股
- 6位数字（如600519）→ A股
- 包含字母（如AAPL）→ 美股

**日期范围说明**：
- 如果不指定日期范围，月K及以上返回所有可用数据
- **周K及以下时间间隔**：如果不指定日期范围，默认返回最近1个月的数据（基于数据最新日期）
  - 适用于：1min, 5min, 15min, 30min, 60min, daily, weekly
- 如果指定日期范围，只返回该范围内的数据
- 日期格式支持：YYYY-MM-DD（如 2025-01-01）或 YYYY-MM-DD HH:MM:SS（如 2025-01-01 09:30:00）

**响应特点**：
- 所有时间戳已转换为市场本地时间
  - 美股（US）：美国东部时间 EST/EDT (UTC-5/-4，自动处理夏令时)
  - 港股（HK）：香港时间 HKT (UTC+8)
  - A股（CN）：中国标准时间 CST (UTC+8)
- 时间格式：`YYYY-MM-DD HH:MM:SS 时区名称`（分钟级）或 `YYYY-MM-DD`（日K及以上）
- 原始Unix时间戳仍然保留
- 美股会根据日期自动显示 EST（冬令时）或 EDT（夏令时）

**测试命令**：
```bash
# 日K线
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=daily"

# 5分钟K线
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=5min"

# 周K线（默认最近1个月）
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=weekly"

# 指定日期范围（日K线）
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=daily&start_date=2025-10-01&end_date=2025-10-31"

# 指定日期范围（分钟级）
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=5min&start_date=2025-11-01 09:30:00&end_date=2025-11-01 16:00:00"

# CSV格式输出
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=daily&format=csv"

# CSV格式指定日期范围
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=daily&start_date=2025-10-01&end_date=2025-10-31&format=csv"

# 港股周K线
curl "http://localhost:8000/api/kline?symbol=00700&interval=weekly"

# A股日K线
curl "http://localhost:8000/api/kline?symbol=600519&interval=daily"
```

**响应示例（美股 - 夏令时）**：
```json
{
  "minus": {
    "list": [
      {
        "time": 1761897660,
        "local_time": "2025-10-31 04:01:00 EDT",
        "price": 278500,
        "cc_price": 278.5,
        "volume": 7751
      }
    ],
    "time_section": [
      {
        "begin": 1761897660,
        "begin_local_time": "2025-10-31 04:01:00 EDT",
        "end": 1761917400,
        "end_local_time": "2025-10-31 09:30:00 EDT"
      }
    ],
    "server_time": 1762017476,
    "server_local_time": "2025-11-01 13:24:17 EDT"
  }
}
```

**响应示例（美股 - 冬令时）**：
```json
{
  "minus": {
    "list": [
      {
        "time": 1735660800,
        "local_time": "2024-12-31 09:00:00 EST",
        "price": 278500,
        "cc_price": 278.5,
        "volume": 7751
      }
    ]
  }
}
```

**响应示例（港股/A股）**：
```json
{
  "minus": {
    "list": [
      {
        "time": 1761897660,
        "local_time": "2025-10-31 16:01:00 HKT",
        "price": 278500,
        "cc_price": 278.5,
        "volume": 7751
      }
    ]
  }
}
```

**自动判断市场类型**：
- 5位数字（如00700）→ 港股
- 6位数字（如600519）→ A股
- 包含字母（如AAPL）→ 美股

**测试命令**：
```bash
# 分时K线
curl "http://localhost:8000/api/kline?stock_code=AAPL&kline_type=1"

# 日K线
curl "http://localhost:8000/api/kline?stock_code=AAPL&kline_type=2"

# 周K线
curl "http://localhost:8000/api/kline?stock_code=AAPL&kline_type=3"

# 月K线
curl "http://localhost:8000/api/kline?stock_code=AAPL&kline_type=4"

# 年K线
curl "http://localhost:8000/api/kline?stock_code=AAPL&kline_type=5"

# 季K线
curl "http://localhost:8000/api/kline?stock_code=AAPL&kline_type=11"
```

---

### 2. POST 请求接口（使用JSON Body）

#### 2.1 下单交易
```
POST /api/trade
Content-Type: application/json
```

**JSON Body**：
```json
{
  "stock_code": "AAPL",
  "market_type": "US",
  "side": "BUY",
  "quantity": 10,
  "price": 180.50,
  "order_type": "LIMIT"
}
```

**参数说明**：
- `stock_code` (必填): 股票代码
- `market_type` (必填): 市场类型 (US/HK/CN)
- `side` (必填): 交易方向 (BUY/SELL)
- `quantity` (必填): 数量
- `price` (可选): 价格（限价单必填）
- `order_type` (可选): 订单类型 (LIMIT/MARKET，默认LIMIT)
- `security_type` (可选): 证券类型（默认STOCK）

**响应示例**：
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
    "quantity": 10
  }
}
```

**测试命令**：
```bash
# 买入
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

# 卖出
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

**PowerShell测试**：
```powershell
# 买入
$body = @{
    stock_code = "AAPL"
    market_type = "US"
    side = "BUY"
    quantity = 10
    price = 180.50
    order_type = "LIMIT"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/trade" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

---

#### 2.2 撤单
```
POST /api/cancel
Content-Type: application/json
```

**JSON Body**：
```json
{
  "order_id": "123456789",
  "market_type": "US"
}
```

**参数说明**：
- `order_id` (必填): 订单ID
- `market_type` (必填): 市场类型 (US/HK/CN)

**响应示例**：
```json
{
  "success": true,
  "message": "撤单成功",
  "order_id": "123456789",
  "data": {
    "account_id": "17198232",
    "order_id": "123456789",
    "market_type": "US"
  }
}
```

**测试命令**：
```bash
curl -X POST "http://localhost:8000/api/cancel" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "123456789",
    "market_type": "US"
  }'
```

**PowerShell测试**：
```powershell
$body = @{
    order_id = "123456789"
    market_type = "US"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/cancel" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

---

## 接口分类总结

### GET 请求（Query参数）
1. ✅ `/api/account` - 获取账户信息（需指定market_type）
2. ✅ `/api/positions` - 获取持仓列表（需指定market_type）
3. ✅ `/api/quote` - 获取股票行情（自动判断市场）
4. ✅ `/api/orders` - 获取订单历史（需指定market_type）
5. ✅ `/api/hot-news` - 获取热门新闻
6. ✅ `/api/hot-stocks` - 获取热门股票
7. ✅ `/api/technical-analysis` - 获取技术分析指标（自动判断市场）
8. ✅ `/api/kline` - 获取K线数据（自动判断市场）

### POST 请求（JSON Body）
1. ✅ `/api/trade` - 下单交易
2. ✅ `/api/cancel` - 撤单

---

## 错误响应格式

### Cookie过期
```json
{
  "error": "未登录",
  "message": "你还未登录",
  "code": 1002,
  "hint": "Cookie已过期，请从浏览器重新获取Cookie并更新到.env文件中"
}
```

### 参数错误
```json
{
  "error": "必须提供market_type参数来指定市场类型",
  "code": 400
}
```

### 资源未找到
```json
{
  "detail": "未找到股票: INVALID"
}
```

---

## 注意事项

1. **GET请求**：所有参数通过URL Query参数传递
2. **POST请求**：所有参数通过JSON Body传递
3. **需要登录的接口**：`/api/account`, `/api/positions`, `/api/trade`, `/api/cancel`, `/api/orders`
4. **不需要登录的接口**：`/api/quote`, `/api/hot-news`, `/api/hot-stocks`, `/api/kline`
5. **时间转换**：K线接口返回的所有时间已自动转换为北京时间（UTC+8）
6. **字段优化**：股票行情接口只返回有值的字段，避免显示无意义的0值

---

## 快速测试

访问 Swagger UI 文档进行交互式测试：
```
http://localhost:8000/docs
```

在文档中可以：
- 查看所有接口的详细说明
- 直接在浏览器中测试接口
- 查看请求和响应的数据模型
- 复制curl命令
