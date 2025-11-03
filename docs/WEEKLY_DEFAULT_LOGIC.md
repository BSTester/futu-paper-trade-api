# 周K线默认限制逻辑说明

## 更新时间
2025-11-03

## 核心逻辑

周K线在不指定日期范围时，默认返回**基于数据最新日期的最近1个月**数据。

## 为什么基于数据最新日期？

### 问题场景

如果基于当前系统日期：

```
当前系统日期: 2025-11-03
数据最新日期: 2025-10-31（周五收盘）

基于系统日期计算: 2025-10-04 至 2025-11-03
实际数据范围: 2025-10-04 至 2025-10-31
结果: 2025-11-01 至 2025-11-03 没有数据（周末和未来）
```

### 正确方案

基于数据最新日期：

```
数据最新日期: 2025-10-31
计算1个月前: 2025-10-01

返回数据范围: 2025-10-01 至 2025-10-31
结果: 返回完整的1个月数据，没有空白期
```

## 实现逻辑

### 步骤1：获取所有数据

```python
# 先从富途API获取所有可用的周K线数据
kline_data = await futu_client.get_kline_data(
    stock_id=security_id,
    kline_type=3,  # 周K线
    market_type=market_type
)
```

### 步骤2：转换为DataFrame

```python
# 将数据转换为DataFrame
df = pd.DataFrame(df_data)
df = df[(df['close'] > 0) & (df['time'].notna())].copy()
```

### 步骤3：应用周K线默认限制

```python
if apply_weekly_default and len(df) > 0:
    # 获取数据中的最新时间戳
    latest_timestamp = df['time'].max()
    
    # 计算1个月前的时间戳（30天）
    one_month_ago_timestamp = latest_timestamp - (30 * 24 * 60 * 60)
    
    # 过滤数据
    df = df[df['time'] >= one_month_ago_timestamp].copy()
    
    # 记录自动设置的日期范围
    start_date = datetime.fromtimestamp(one_month_ago_timestamp).strftime("%Y-%m-%d")
    end_date = datetime.fromtimestamp(latest_timestamp).strftime("%Y-%m-%d")
```

## 示例说明

### 示例1：正常交易日

```
数据最新日期: 2025-10-31 (周五)
计算结果:
  - 最新时间戳: 1730419200
  - 1个月前时间戳: 1727827200
  - 开始日期: 2025-10-01
  - 结束日期: 2025-10-31
  - 返回数据: 约4-5个周K线数据点
```

### 示例2：周末请求

```
当前系统日期: 2025-11-03 (周日)
数据最新日期: 2025-10-31 (周五)

计算结果:
  - 基于数据最新日期: 2025-10-31
  - 开始日期: 2025-10-01
  - 结束日期: 2025-10-31
  - 返回数据: 完整的1个月数据
```

### 示例3：节假日后

```
当前系统日期: 2025-10-10 (假期后第一天)
数据最新日期: 2025-09-30 (假期前最后一天)

计算结果:
  - 基于数据最新日期: 2025-09-30
  - 开始日期: 2025-09-01
  - 结束日期: 2025-09-30
  - 返回数据: 假期前的1个月数据
```

## 优势

### 1. 数据完整性

✅ 总是返回完整的1个月数据  
✅ 没有空白期或未来日期  
✅ 不受周末和节假日影响

### 2. 一致性

✅ 无论何时请求，返回的都是数据中最近的1个月  
✅ 不会因为请求时间不同而返回不同范围的数据  
✅ 便于缓存和重复使用

### 3. 准确性

✅ 反映真实的市场数据范围  
✅ 避免包含不存在的数据点  
✅ 符合用户对"最近1个月"的预期

## 对比

| 方案 | 基于系统日期 | 基于数据最新日期 |
|------|-------------|-----------------|
| 周末请求 | 包含未来日期（无数据） | ✅ 只包含实际数据 |
| 节假日后 | 包含假期日期（无数据） | ✅ 只包含实际数据 |
| 数据完整性 | 可能不足1个月 | ✅ 完整1个月 |
| 一致性 | 随请求时间变化 | ✅ 稳定一致 |
| 缓存友好 | ❌ 难以缓存 | ✅ 易于缓存 |

## 响应示例

### 请求

```bash
GET /api/kline?symbol=AAPL&interval=weekly
```

### 响应

```json
{
  "meta": {
    "symbol": "AAPL",
    "stock_name": "苹果",
    "security_id": "205189",
    "market_type": "US",
    "interval": "weekly",
    "data_points": 4,
    "requested_start_date": "2025-10-01",
    "requested_end_date": "2025-10-31"
  },
  "data": [
    {
      "time": 1727827200,
      "datetime": "2025-10-07",
      "open": 265.30,
      "high": 268.90,
      "low": 264.50,
      "close": 268.15,
      "volume": 42345600
    },
    {
      "time": 1728432000,
      "datetime": "2025-10-14",
      "open": 268.50,
      "high": 271.20,
      "low": 267.80,
      "close": 270.37,
      "volume": 45678900
    },
    {
      "time": 1729036800,
      "datetime": "2025-10-21",
      "open": 270.50,
      "high": 273.80,
      "low": 269.90,
      "close": 272.45,
      "volume": 48901200
    },
    {
      "time": 1729641600,
      "datetime": "2025-10-28",
      "open": 272.80,
      "high": 275.50,
      "low": 271.20,
      "close": 274.90,
      "volume": 51234500
    }
  ]
}
```

注意 `requested_start_date` 和 `requested_end_date` 字段显示了自动计算的日期范围。

## 技术实现细节

### 时间戳计算

```python
# 1个月 = 30天 = 30 * 24 * 60 * 60 秒
one_month_seconds = 30 * 24 * 60 * 60  # 2,592,000 秒

# 计算1个月前的时间戳
one_month_ago_timestamp = latest_timestamp - one_month_seconds
```

### 数据过滤

```python
# 使用pandas过滤
df = df[df['time'] >= one_month_ago_timestamp].copy()
```

### 日期格式化

```python
from datetime import datetime

# 转换时间戳为日期字符串
start_date = datetime.fromtimestamp(one_month_ago_timestamp).strftime("%Y-%m-%d")
end_date = datetime.fromtimestamp(latest_timestamp).strftime("%Y-%m-%d")
```

## 常见问题

### Q1: 为什么是30天而不是1个自然月？

A: 使用30天是为了简化计算和保持一致性。1个自然月的天数不固定（28-31天），使用固定的30天更容易理解和预测。

### Q2: 如果数据不足1个月怎么办？

A: 返回所有可用数据。例如，如果股票刚上市只有2周数据，则返回这2周的数据。

### Q3: 可以修改默认的30天吗？

A: 当前版本固定为30天。如需其他范围，请使用 `start_date` 参数明确指定。

### Q4: 其他时间间隔会应用这个逻辑吗？

A: 不会，只有周K线（`interval=weekly`）应用这个默认限制。

### Q5: 如何获取超过1个月的周K线数据？

A: 明确指定 `start_date` 参数：
```bash
GET /api/kline?symbol=AAPL&interval=weekly&start_date=2025-01-01
```

## 总结

基于数据最新日期的默认限制逻辑确保了：

1. ✅ 返回的数据总是完整的1个月
2. ✅ 不包含未来日期或空白期
3. ✅ 不受请求时间影响，结果一致
4. ✅ 符合用户对"最近1个月"的直观理解
5. ✅ 便于缓存和优化性能

这是一个更合理、更实用的实现方案。
