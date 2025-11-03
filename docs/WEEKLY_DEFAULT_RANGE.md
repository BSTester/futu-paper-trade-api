# 周K线默认时间范围限制

## 更新时间
2025-11-03

## 变更说明

为了优化性能和减少不必要的数据传输，**周K线（weekly）在不指定日期范围时，现在默认只返回最近1个月的数据**。

## 原因

1. **数据量控制**：周K线数据跨度大，不限制可能返回数年的数据
2. **性能优化**：减少数据处理和网络传输时间
3. **实用性**：大多数技术分析场景只需要近期数据

## 重要说明

**"最近1个月"是基于数据的最新日期计算，而不是当前系统日期。**

这意味着：
- 如果数据最新日期是2025-10-31，则返回2025-10-01至2025-10-31的数据
- 如果数据最新日期是2025-09-30，则返回2025-09-01至2025-09-30的数据
- 这样可以确保返回的是数据中最近的1个月，而不是系统时间的最近1个月

## 影响范围

**仅影响周K线（interval=weekly）且不指定日期范围的请求**

### 受影响的请求

```bash
# 这个请求现在默认返回最近1个月
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=weekly&indicator=macd"
```

### 不受影响的请求

```bash
# 明确指定日期范围 - 不受影响
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=weekly&indicator=macd&start_date=2025-01-01"

# 其他时间间隔 - 不受影响
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&indicator=macd"
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=monthly&indicator=macd"
```

## 如何获取更长的历史数据

如果需要更长时间范围的周K线数据，请明确指定日期范围：

### 获取最近3个月

```bash
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=weekly&indicator=macd&start_date=2025-08-01"
```

### 获取全年数据

```bash
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=weekly&indicator=macd&start_date=2025-01-01"
```

### 获取所有历史数据

```bash
# 只指定结束日期，从最早的数据开始
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=weekly&indicator=macd&end_date=2025-11-03"
```

## 响应示例

### 默认行为（最近1个月）

请求：
```bash
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=weekly&indicator=macd"
```

响应：
```json
{
  "meta": {
    "symbol": "AAPL",
    "stock_name": "苹果",
    "interval": "weekly",
    "indicator": "macd",
    "data_points": 4,
    "start_date": "2025-10-04",
    "end_date": "2025-11-03",
    "requested_start_date": "2025-10-04",
    "requested_end_date": "2025-11-03"
  },
  "data": {
    "2025-10-07": {...},
    "2025-10-14": {...},
    "2025-10-21": {...},
    "2025-10-28": {...}
  }
}
```

注意 `requested_start_date` 和 `requested_end_date` 字段显示了自动设置的日期范围。

## 技术实现

在 `futu_client.py` 的 `get_technical_analysis` 方法中：

```python
# 如果是周K线且没有指定日期范围，设置默认为最近1个月
if interval == "weekly" and not start_date and not end_date:
    from datetime import datetime, timedelta
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=30)
    start_date = start_dt.strftime("%Y-%m-%d")
    end_date = end_dt.strftime("%Y-%m-%d")
```

## 其他时间间隔

其他时间间隔保持原有行为：

| 时间间隔 | 默认行为 |
|---------|---------|
| 1min, 5min, 15min, 30min, 60min | 返回所有可用数据（通常几天） |
| daily | 返回所有可用数据 |
| **weekly** | **默认最近1个月** ⭐ |
| monthly | 返回所有可用数据 |
| quarterly | 返回所有可用数据 |
| yearly | 返回所有可用数据 |

## 注意事项

1. **技术指标计算**：
   - 1个月的周K线约4-5个数据点
   - 某些长期指标（如200周SMA）需要更多数据
   - 如果指标需要更多历史数据，请明确指定日期范围

2. **向后兼容**：
   - 如果你的代码依赖获取所有周K线数据，需要更新为明确指定日期范围
   - 建议在代码中明确指定需要的日期范围，而不是依赖默认行为

3. **性能提升**：
   - 默认限制可以显著减少响应时间
   - 对于需要大量历史数据的场景，建议分批请求

## 迁移指南

如果你的现有代码受到影响，请按以下方式更新：

### 之前的代码

```python
# 获取周K线数据（之前返回所有历史数据）
response = requests.get(
    "http://localhost:8000/api/technical-analysis",
    params={
        "symbol": "AAPL",
        "interval": "weekly",
        "indicator": "macd"
    }
)
```

### 更新后的代码

```python
# 明确指定需要的日期范围
response = requests.get(
    "http://localhost:8000/api/technical-analysis",
    params={
        "symbol": "AAPL",
        "interval": "weekly",
        "indicator": "macd",
        "start_date": "2025-01-01"  # 明确指定开始日期
    }
)
```

## 测试

运行测试脚本验证新行为：

```bash
cd futu-paper-trade-api
python test_date_range.py
```

测试脚本会验证：
- 周K线的默认1个月限制
- 周K线指定更长日期范围的行为
- 其他时间间隔不受影响
