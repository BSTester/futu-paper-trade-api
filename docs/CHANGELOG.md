# 更新日志

## 2025-11-02

### K线时区优化（支持夏令时）

**重要更新**：时间转换改为使用市场本地时区，并自动处理美股夏令时

**时区映射**：
- 美股（US）→ 美国东部时间 EST/EDT (UTC-5/-4，自动处理夏令时)
- 港股（HK）→ 香港时间 HKT (UTC+8)
- A股（CN）→ 中国标准时间 CST (UTC+8)

**夏令时处理**：
- 使用 Python 的 `zoneinfo` (Python 3.9+) 或 `pytz` 库
- 自动判断时间戳是否在夏令时期间
- 夏令时显示 EDT (UTC-4)
- 冬令时显示 EST (UTC-5)

**字段变更**：
- `beijing_time` → `local_time`
- `begin_beijing_time` → `begin_local_time`
- `end_beijing_time` → `end_local_time`
- `server_beijing_time` → `server_local_time`

**时间格式**：`YYYY-MM-DD HH:MM:SS 时区名称`

**示例**：
```json
// 夏令时期间
{
  "time": 1761897660,
  "local_time": "2025-10-31 04:01:00 EDT"  // 美股夏令时
}

// 冬令时期间
{
  "time": 1735660800,
  "local_time": "2024-12-31 09:00:00 EST"  // 美股冬令时
}
```

---

### K线类型完善

**新增功能**：支持所有K线类型，并自动设置正确的symbol参数

**支持的K线类型**：
- 1: 分时（Minute）- symbol=1
- 2: 日K（Day）- symbol=3
- 3: 周K（Week）- symbol=4
- 4: 月K（Month）- symbol=5
- 5: 年K（Year）- symbol=7
- 11: 季K（Quarter）- symbol=6

**实现方式**：
- 用户只需指定 `kline_type` 参数
- API会根据 `kline_type` 自动设置正确的 `symbol` 参数
- 无需用户手动计算参数映射关系

**示例**：
```bash
# 日K线
curl "http://localhost:8000/api/kline?stock_code=AAPL&market_type=US&kline_type=2"

# 周K线
curl "http://localhost:8000/api/kline?stock_code=AAPL&market_type=US&kline_type=3"

# 季K线
curl "http://localhost:8000/api/kline?stock_code=AAPL&market_type=US&kline_type=11"
```

详见 [KLINE_PARAMS.md](KLINE_PARAMS.md)

---

## 2025-11-01

### K线数据时间转换

**新增功能**：K线接口返回的时间戳自动转换为北京时间（UTC+8）

**修改内容**：
1. 添加 `_convert_timestamp_to_beijing_time()` 方法，将Unix时间戳转换为北京时间字符串
2. 修改 `get_kline_data()` 方法，自动转换所有时间字段

**转换的字段**：
- `minus.list[].time` → 添加 `beijing_time` 字段
- `minus.time_section[].begin` → 添加 `begin_beijing_time` 字段
- `minus.time_section[].end` → 添加 `end_beijing_time` 字段
- `minus.server_time` → 添加 `server_beijing_time` 字段

**示例**：
```json
{
  "minus": {
    "list": [
      {
        "time": 1761897660,
        "beijing_time": "2025-10-31 16:01:00",
        "price": 278500,
        "cc_price": 278.5,
        "volume": 7751
      }
    ],
    "time_section": [
      {
        "begin": 1761897660,
        "begin_beijing_time": "2025-10-31 16:01:00",
        "end": 1761917400,
        "end_beijing_time": "2025-10-31 21:30:00"
      }
    ],
    "server_time": 1762013691,
    "server_beijing_time": "2025-11-02 00:14:51"
  }
}
```

### 优化股票行情接口

**问题**：股票行情接口返回的某些字段（`open_price`, `high_price`, `low_price`, `volume`）在富途API中可能为0或不存在，但仍然显示在响应中。

**修复**：
1. 修改 `get_stock_quote()` 方法，只返回有值的字段
2. 修改 `StockQuote` 模型，将这些字段设为可选
3. 移除 `/api/quote` 路由的响应模型验证，改为返回动态字典

**修复前**：
```json
{
  "security_id": "205189",
  "stock_code": "AAPL.US",
  "stock_name": "苹果",
  "current_price": 270.37,
  "change": -1.03,
  "change_ratio": -0.38,
  "open_price": 0.0,      // ❌ 显示无意义的0值
  "high_price": 0.0,      // ❌ 显示无意义的0值
  "low_price": 0.0,       // ❌ 显示无意义的0值
  "volume": 0             // ❌ 显示无意义的0值
}
```

**修复后**：
```json
{
  "security_id": "205189",
  "stock_code": "AAPL.US",
  "stock_name": "苹果",
  "current_price": 270.37,
  "change": -1.03,
  "change_ratio": -0.38
  // ✅ 没有值的字段不显示
}
```

**如果有值时的响应**：
```json
{
  "security_id": "205189",
  "stock_code": "AAPL.US",
  "stock_name": "苹果",
  "current_price": 270.37,
  "change": -1.03,
  "change_ratio": -0.38,
  "open_price": 271.4,    // ✅ 有值时才显示
  "high_price": 275.2,    // ✅ 有值时才显示
  "low_price": 269.8,     // ✅ 有值时才显示
  "volume": 1234567       // ✅ 有值时才显示
}
```

### 修正账户信息和持仓列表字段映射

**问题**：富途API返回的字段名与代码中使用的字段名不匹配，导致返回的数据全部为0。

**修复**：
1. 修正账户信息接口的10个字段映射
2. 修正持仓列表接口的字段名（从 `position_list` 改为 `positions`）

详见 `README_FIXES.md` 和 `FIELD_MAPPING.md`

### 优化错误处理

**问题**：当Cookie过期时，接口返回500错误，不友好。

**修复**：返回友好的JSON错误信息，包含提示如何更新Cookie。

**Cookie过期时的响应**：
```json
{
  "error": "未登录",
  "message": "你还未登录",
  "code": 1002,
  "hint": "Cookie已过期，请从浏览器重新获取Cookie并更新到.env文件中"
}
```

## 测试结果

✅ 所有接口测试通过：
- 账户信息：正确返回真实数据
- 持仓列表：正确返回持仓数据
- 股票行情：只返回有值的字段
- 热门新闻：正常工作
- 热门股票：正常工作
- K线数据：正常工作

## 修改的文件

1. `futu_client.py`
   - 修正 `get_account_info()` 字段映射
   - 修正 `get_positions()` 字段映射
   - 优化 `get_stock_quote()` 只返回有值的字段
   - 优化错误处理

2. `models.py`
   - 修改 `StockQuote` 模型，将部分字段设为可选

3. `main.py`
   - 移除 `/api/quote` 的响应模型验证
   - 优化 `/api/account` 和 `/api/positions` 的错误处理

## 相关文档

- `README_FIXES.md` - 详细的修复说明
- `FIELD_MAPPING.md` - 字段映射文档
- `test_all_apis.ps1` - 完整测试脚本
- `test_simple.ps1` - 简化测试脚本
