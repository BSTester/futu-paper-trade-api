# API更新说明

## 更新时间
2025-11-01

## 更新内容

### 1. 修正字段映射
修正了账户信息和持仓列表接口的字段映射，确保与富途API返回的实际字段名一致。

**账户信息字段映射**：
- `balance` → `cash` (现金)
- `power` → `buying_power` (购买力)
- `asset_value` → `net_asset` (资产净值)
- `stock_value` → `market_value` (持仓市值)
- `profit` → `profit_loss` (盈亏)
- `profit_ratio` → `profit_loss_ratio` (盈亏比例)
- `today_profit` → `today_profit_loss` (今日盈亏)
- `today_profit_ratio` → `today_profit_loss_ratio` (今日盈亏比例)
- `maintenance_margin` → `margin` (维持保证金)
- `excess_liquidity` → `available_funds` (可用资金)

**持仓列表字段映射**：
- 修正了从 `position_list` 到 `positions` 的字段名

### 2. 优化错误处理
修改了需要登录的API接口，当Cookie过期时返回友好的错误信息，而不是抛出500错误。

### 2. 受影响的接口

#### `/api/account` - 获取账户信息
**之前**: Cookie过期时返回500错误
**现在**: 返回200状态码，包含详细的错误信息

**Cookie过期时的响应示例**:
```json
{
  "error": "未登录",
  "message": "你还未登录",
  "code": 1002,
  "hint": "Cookie已过期，请从浏览器重新获取Cookie并更新到.env文件中"
}
```

**正常响应示例**:
```json
{
  "account_id": "16992013",
  "net_asset": 1000000.0,
  "cash": 950000.0,
  "market_value": 50000.0,
  "buying_power": 950000.0,
  "profit_loss": 5000.0,
  "profit_loss_ratio": 0.5,
  "today_profit_loss": 1000.0,
  "today_profit_loss_ratio": 0.1,
  "margin": 0.0,
  "available_funds": 950000.0
}
```

#### `/api/positions` - 获取持仓列表
**之前**: Cookie过期时返回500错误
**现在**: 返回200状态码，包含详细的错误信息

**Cookie过期时的响应示例**:
```json
{
  "error": "未登录",
  "message": "你还未登录",
  "code": 1002,
  "hint": "Cookie已过期，请从浏览器重新获取Cookie并更新到.env文件中",
  "positions": []
}
```

**正常响应示例**:
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

### 3. 不需要登录的接口（正常工作）

以下接口不需要Cookie，始终正常工作：

- ✅ `/api/quote` - 获取股票行情
- ✅ `/api/hot-news` - 获取热门新闻
- ✅ `/api/hot-stocks` - 获取热门股票
- ✅ `/api/kline` - 获取K线数据

### 4. 如何更新Cookie

当看到"未登录"错误时，需要：

1. 打开浏览器，访问 https://www.futunn.com/paper-trade
2. 登录你的富途账户
3. 打开浏览器开发者工具（F12）
4. 切换到 Network 标签
5. 刷新页面，找到任意请求
6. 在请求头中复制完整的 Cookie 值
7. 更新 `.env` 文件中的 `FUTU_COOKIE` 值
8. 重启API服务

### 5. 测试命令

```bash
# 测试账户信息（需要有效Cookie）
curl "http://localhost:8000/api/account?market_type=US"

# 测试持仓列表（需要有效Cookie）
curl "http://localhost:8000/api/positions?market_type=US"

# 测试股票行情（不需要Cookie）
curl "http://localhost:8000/api/quote?stock_code=AAPL&market_type=US"

# 测试热门新闻（不需要Cookie）
curl "http://localhost:8000/api/hot-news?lang=zh-cn"

# 测试热门股票（不需要Cookie）
curl "http://localhost:8000/api/hot-stocks?market_type=US&count=10"
```

## 技术细节

### 修改的文件
1. `futu_client.py` - 修改了 `get_account_info()` 和 `get_positions()` 方法
2. `main.py` - 修改了 `/api/account` 和 `/api/positions` 路由

### 错误码说明
- `1002`: 未登录（Cookie过期）
- `400`: 参数错误
- `404`: 未找到资源
- `500`: 系统错误
