# 富途API字段映射文档

## 更新时间
2025-11-01

## 账户信息接口 (`/api/account`)

### 富途API返回字段 → 我们的API返回字段

| 富途字段 | 我们的字段 | 说明 | 示例值 |
|---------|-----------|------|--------|
| `account_id` | `account_id` | 账户ID | "17198232" |
| `asset_value` | `net_asset` | 资产净值 | 100000.0 |
| `balance` | `cash` | 现金/余额 | 100000.0 |
| `stock_value` | `market_value` | 持仓市值 | 0.0 |
| `power` | `buying_power` | 购买力 | 200000.0 |
| `profit` | `profit_loss` | 盈亏 | 0.0 |
| `profit_ratio` | `profit_loss_ratio` | 盈亏比例 | 0.0 |
| `today_profit` | `today_profit_loss` | 今日盈亏 | 0.0 |
| `today_profit_ratio` | `today_profit_loss_ratio` | 今日盈亏比例 | 0.0 |
| `maintenance_margin` | `margin` | 维持保证金 | "0" |
| `excess_liquidity` | `available_funds` | 可用资金 | "100000" |

### 富途API原始响应示例
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "support_currency": [],
    "account_id": 17198232,
    "account_title": "第二届全球模拟交易大赛",
    "account_type": 2,
    "market_type": 100,
    "is_traded": false,
    "sort": 102,
    "is_display": true,
    "relate_match_id": 239,
    "act_id": 1,
    "signup_type": 3,
    "balance": 100000,
    "power": 200000,
    "asset_value": 100000,
    "stock_value": 0,
    "profit": 0,
    "profit_ratio": 0,
    "today_profit": 0,
    "today_profit_ratio": 0,
    "today_profit_direction": "flat",
    "is_public": true,
    "total_position_profit": 0,
    "maintenance_margin": "0",
    "excess_liquidity": "100000"
  }
}
```

### 我们的API返回示例
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

---

## 持仓列表接口 (`/api/positions`)

### 富途API返回字段 → 我们的API返回字段

| 富途字段 | 我们的字段 | 说明 | 类型 |
|---------|-----------|------|------|
| `security_id` | `security_id` | 证券ID | string |
| `stock_code` | `stock_code` | 股票代码 | string |
| `stock_name` | `stock_name` | 股票名称 | string |
| `market_type` | `market_type` | 市场类型 | string |
| `quantity` | `quantity` | 持仓数量 | int |
| `available_quantity` | `available_quantity` | 可用数量 | int |
| `cost_price` | `cost_price` | 成本价 | float |
| `current_price` | `current_price` | 当前价 | float |
| `market_value` | `market_value` | 市值 | float |
| `profit_loss` | `profit_loss` | 盈亏 | float |
| `profit_loss_ratio` | `profit_loss_ratio` | 盈亏比例 | float |

### 富途API原始响应示例（空持仓）
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "positions": [],
    "pos_count": "0"
  }
}
```

### 富途API原始响应示例（有持仓）
```json
{
  "code": 0,
  "message": "成功",
  "data": {
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
    "pos_count": "1"
  }
}
```

### 我们的API返回示例
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

---

## 股票行情接口 (`/api/quote`)

### 富途API返回字段 → 我们的API返回字段

| 富途字段 | 我们的字段 | 说明 |
|---------|-----------|------|
| `security_id` | `security_id` | 证券ID |
| `display_code` / `stock_code` | `stock_code` | 股票代码 |
| `display_name` / `security_name` / `stock_name` | `stock_name` | 股票名称 |
| `price` / `current_price` | `current_price` | 当前价格 |
| `change` | `change` | 涨跌额 |
| `change_ratio` | `change_ratio` | 涨跌幅（%） |
| `open_price` | `open_price` | 开盘价 |
| `high_price` | `high_price` | 最高价 |
| `low_price` | `low_price` | 最低价 |
| `volume` | `volume` | 成交量 |

### 富途API原始响应示例
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "leg_quote": [
      {
        "futu_symbol": "AAPL",
        "display_code": "AAPL.US",
        "display_name": "苹果",
        "security_id": "205189",
        "bid": {
          "price": "269.980",
          "shares_number": "200",
          "direction": "down"
        },
        "ask": {
          "price": "270.000",
          "shares_number": "200",
          "direction": "down"
        },
        "bid_ratio": "50.00",
        "ask_ratio": "50.00",
        "price": "270.370",
        "leg_security_type": 1,
        "spread_code": 45,
        "price_direct": "down",
        "change": "-1.030",
        "change_ratio": "-0.38%",
        "is_delay": 0,
        "lot_size": 1,
        "security_name": "苹果"
      }
    ]
  }
}
```

### 我们的API返回示例
```json
[
  {
    "security_id": "205189",
    "stock_code": "AAPL.US",
    "stock_name": "苹果",
    "current_price": 270.37,
    "change": -1.03,
    "change_ratio": -0.38,
    "open_price": 0.0,
    "high_price": 0.0,
    "low_price": 0.0,
    "volume": 0
  }
]
```

---

## 热门新闻接口 (`/api/hot-news`)

### 富途API原始响应示例
```json
{
  "code": 0,
  "message": "成功",
  "data": [
    {
      "audioInfos": [
        {
          "language": "Cantonese",
          "audioDuration": 42,
          "audioUrl": "https://newsspeech.futunn.com/..."
        }
      ],
      "newsId": "19572778",
      "title": "新闻标题",
      "content": "新闻内容",
      "publishTime": 1730462400
    }
  ]
}
```

### 我们的API返回
直接返回 `data` 数组，不做字段转换。

---

## 热门股票接口 (`/api/hot-stocks`)

### 富途API原始响应示例
```json
{
  "code": 0,
  "message": "成功",
  "data": [
    {
      "security_id": "82252918909550",
      "code": "META",
      "market_label": "us",
      "security_name": "Meta Platforms",
      "change": "-18.120",
      "change_ratio": "-2.72%",
      "price": "648.350",
      "price_direct": "down",
      "is_delay": 1,
      "nominal_price": "648.350",
      "market_status": 99
    }
  ]
}
```

### 我们的API返回
直接返回 `data` 数组，不做字段转换。

---

## K线数据接口 (`/api/kline`)

### 富途API原始响应示例
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "stockId": "205189",
    "symbol": "AAPL.US",
    "marketCode": 11,
    "marketType": 2,
    "instrumentType": 3,
    "lotSize": 1,
    "fixed": 3,
    "priceLastClose": "271.400",
    "minus": {
      "stockId": "205189",
      "list": [
        {
          "time": 1761897660,
          "price": 278500,
          "cc_price": 278.5,
          "volume": 7751,
          "turnover": 2152915.09,
          "ratio": "2.62",
          "change_price": 7.1
        }
      ]
    }
  }
}
```

### 我们的API返回
直接返回 `data` 对象，不做字段转换。

---

## 错误响应格式

### 未登录错误（Cookie过期）
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
  "error": "未找到US市场的模拟账户，请在.env文件中配置ACCOUNT_ID_US",
  "code": 404
}
```

### 系统错误
```json
{
  "error": "系统错误",
  "message": "具体错误信息",
  "code": 500
}
```

---

## 测试命令

```bash
# 测试账户信息
curl "http://localhost:8000/api/account?market_type=US"

# 测试持仓列表
curl "http://localhost:8000/api/positions?market_type=US"

# 测试股票行情
curl "http://localhost:8000/api/quote?stock_code=AAPL&market_type=US"

# 测试热门新闻
curl "http://localhost:8000/api/hot-news?lang=zh-cn"

# 测试热门股票
curl "http://localhost:8000/api/hot-stocks?market_type=US&count=10"

# 测试K线数据
curl "http://localhost:8000/api/kline?stock_code=AAPL&market_type=US&kline_type=1"
```
