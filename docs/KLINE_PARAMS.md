# K线接口参数映射文档

## 富途API K线参数

### 接口地址
```
GET https://www.futunn.com/paper-trade/api-quote-kline
```

### 参数说明

| 参数 | 说明 | 类型 | 必填 |
|------|------|------|------|
| stockId | 股票ID（security_id） | string | 是 |
| type | K线类型 | int | 是 |
| symbol | 符号类型（根据type自动设置） | int | 是 |
| security | 证券类型 | int | 是 |
| req_section | 请求区段 | int | 是 |

---

## K线类型映射表

### 完整映射关系

| kline_type | 名称 | symbol | 富途API示例 |
|------------|------|--------|-------------|
| 1 | 分时（Minute） | 1 | `type=1&symbol=1` |
| 2 | 日K（Day） | 3 | `type=2&symbol=3` |
| 3 | 周K（Week） | 4 | `type=3&symbol=4` |
| 4 | 月K（Month） | 5 | `type=4&symbol=5` |
| 5 | 年K（Year） | 7 | `type=5&symbol=7` |
| 11 | 季K（Quarter） | 6 | `type=11&symbol=6` |

### 富途API原始请求示例

```bash
# 分时
https://www.futunn.com/paper-trade/api-quote-kline?stockId=202597&type=1&symbol=1&security=1&req_section=1

# 日K
https://www.futunn.com/paper-trade/api-quote-kline?stockId=202597&type=2&symbol=3&security=1&req_section=1

# 周K
https://www.futunn.com/paper-trade/api-quote-kline?stockId=202597&type=3&symbol=4&security=1&req_section=1

# 月K
https://www.futunn.com/paper-trade/api-quote-kline?stockId=202597&type=4&symbol=5&security=1&req_section=1

# 年K
https://www.futunn.com/paper-trade/api-quote-kline?stockId=202597&type=5&symbol=7&security=1&req_section=1

# 季K
https://www.futunn.com/paper-trade/api-quote-kline?stockId=202597&type=11&symbol=6&security=1&req_section=1
```

---

## 我们的API实现

### 自动参数映射

我们的API会根据 `kline_type` 自动设置正确的 `symbol` 参数，用户无需手动指定。

### 使用方法

```bash
# 只需指定 kline_type，symbol 会自动设置
GET /api/kline?stock_code=AAPL&market_type=US&kline_type=1
```

### 代码实现

```python
# 在 futu_client.py 中的自动映射逻辑
symbol_mapping = {
    1: 1,   # 分时 -> symbol=1
    2: 3,   # 日K -> symbol=3
    3: 4,   # 周K -> symbol=4
    4: 5,   # 月K -> symbol=5
    5: 7,   # 年K -> symbol=7
    11: 6,  # 季K -> symbol=6
}
symbol = symbol_mapping.get(kline_type, 1)
```

---

## 响应数据格式

### 时间转换

所有时间戳都会自动转换为市场本地时间：

**美股示例（EDT夏令时）**：
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

**美股示例（EST冬令时）**：
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

**港股/A股示例（HKT/CST时区）**：
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

### 数据字段说明

| 字段 | 说明 | 类型 |
|------|------|------|
| time | Unix时间戳（秒） | int |
| local_time | 市场本地时间字符串（含时区） | string |
| price | 价格（整数，需除以100） | int |
| cc_price | 价格（浮点数） | float |
| volume | 成交量 | int |
| turnover | 成交额 | float |
| ratio | 涨跌幅 | string |
| change_price | 涨跌额 | float |

### 时区说明

| 市场 | 时区 | UTC偏移 | 夏令时 | 示例 |
|------|------|---------|--------|------|
| 美股（US） | EST/EDT | UTC-5/-4 | 自动处理 | `2025-10-31 04:01:00 EDT` |
| 港股（HK） | HKT | UTC+8 | 无 | `2025-10-31 16:01:00 HKT` |
| A股（CN） | CST | UTC+8 | 无 | `2025-10-31 16:01:00 CST` |

**美股夏令时说明**：
- **EDT（Eastern Daylight Time）**：夏令时，UTC-4，通常3月第二个周日至11月第一个周日
- **EST（Eastern Standard Time）**：冬令时，UTC-5，通常11月第一个周日至次年3月第二个周日
- 系统会根据时间戳自动判断并显示正确的时区名称

---

## 测试示例

### PowerShell测试

```powershell
# 测试所有K线类型
$types = @(1, 2, 3, 4, 5, 11)
foreach ($type in $types) {
    $url = "http://localhost:8000/api/kline?stock_code=AAPL&market_type=US&kline_type=$type"
    $response = Invoke-WebRequest -Uri $url
    $data = $response.Content | ConvertFrom-Json
    Write-Host "Type $type : $($data.minus.list.Count) data points"
}
```

### Curl测试

```bash
# 测试分时K线
curl "http://localhost:8000/api/kline?stock_code=AAPL&market_type=US&kline_type=1"

# 测试日K线
curl "http://localhost:8000/api/kline?stock_code=AAPL&market_type=US&kline_type=2"

# 测试周K线
curl "http://localhost:8000/api/kline?stock_code=AAPL&market_type=US&kline_type=3"
```

---

## 注意事项

1. **参数自动映射**：用户只需指定 `kline_type`，`symbol` 参数会自动设置
2. **时区自动转换**：时间会根据市场自动转换为对应时区
   - 美股 → 美国东部时间（EST/EDT，自动处理夏令时）
   - 港股 → 香港时间（HKT）
   - A股 → 中国标准时间（CST）
3. **夏令时处理**：美股会自动判断并显示 EST 或 EDT
4. **时间格式**：`YYYY-MM-DD HH:MM:SS 时区名称`
5. **原始时间保留**：原始Unix时间戳仍然保留在响应中
6. **数据点数量**：不同K线类型返回的数据点数量不同
7. **市场支持**：支持美股（US）、港股（HK）、A股（CN）三个市场

---

## 相关文档

- [API_REFERENCE.md](API_REFERENCE.md) - 完整API参考
- [FIELD_MAPPING.md](FIELD_MAPPING.md) - 字段映射文档
- [CHANGELOG.md](CHANGELOG.md) - 更新日志
