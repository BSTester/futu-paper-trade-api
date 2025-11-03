# 日期范围功能

## 更新时间
2025-11-03

## 功能说明

为以下接口增加了两个可选参数，用于指定数据的日期范围：

- `/api/technical-analysis` - 技术分析接口
- `/api/kline` - K线数据接口

- `start_date`: 开始日期（可选）
- `end_date`: 结束日期（可选）

## 参数详情

### start_date（开始日期）

**格式**：
- `YYYY-MM-DD`（如：2025-01-01）
- `YYYY-MM-DD HH:MM:SS`（如：2025-01-01 09:30:00）

**说明**：
- 可选参数，不指定则从最早的数据开始
- 只返回时间戳 >= start_date 的数据
- 适用于所有时间间隔（分钟级、日K、周K等）

### end_date（结束日期）

**格式**：
- `YYYY-MM-DD`（如：2025-10-31）
- `YYYY-MM-DD HH:MM:SS`（如：2025-10-31 16:00:00）

**说明**：
- 可选参数，不指定则到最新的数据为止
- 只返回时间戳 <= end_date 的数据
- 如果只提供日期（YYYY-MM-DD），自动设置为当天的 23:59:59
- 适用于所有时间间隔（分钟级、日K、周K等）

## 使用示例

### 技术分析接口示例

#### 示例1：获取指定月份的数据

```bash
# 获取2025年10月的MACD数据
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&indicator=macd&start_date=2025-10-01&end_date=2025-10-31"
```

#### 示例2：获取最近一周的数据

```bash
# 获取2025-10-25至今的RSI数据
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&indicator=rsi&start_date=2025-10-25"
```

#### 示例3：获取特定交易日的分钟数据

```bash
# 获取2025-11-01交易时段的5分钟K线MACD数据
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=5min&indicator=macd&start_date=2025-11-01 09:30:00&end_date=2025-11-01 16:00:00"
```

#### 示例4：获取所有历史数据（不指定日期）

```bash
# 获取所有可用的日K线数据
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&indicator=macd"
```

### K线数据接口示例

#### 示例1：获取指定月份的K线数据

```bash
# 获取2025年10月的日K线数据
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=daily&start_date=2025-10-01&end_date=2025-10-31"
```

#### 示例2：获取最近一周的K线数据

```bash
# 获取2025-10-25至今的日K线数据
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=daily&start_date=2025-10-25"
```

#### 示例3：获取特定交易日的分钟K线

```bash
# 获取2025-11-01交易时段的5分钟K线数据
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=5min&start_date=2025-11-01 09:30:00&end_date=2025-11-01 16:00:00"
```

#### 示例4：周K线默认行为

```bash
# 周K线不指定日期，默认返回最近1个月
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=weekly"

# 周K线指定更长的日期范围
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=weekly&start_date=2025-01-01"
```

## 响应格式

当指定日期范围时，响应的 `meta` 部分会包含额外的字段：

```json
{
  "meta": {
    "symbol": "AAPL",
    "stock_name": "苹果",
    "security_id": "205189",
    "market_type": "US",
    "interval": "daily",
    "indicator": "macd",
    "indicator_name": "MACD",
    "latest_price": 270.37,
    "data_points": 22,
    "start_date": "2025-10-01 00:00:00 EDT",
    "end_date": "2025-10-31 00:00:00 EDT",
    "requested_start_date": "2025-10-01",
    "requested_end_date": "2025-10-31"
  },
  "data": {
    "2025-10-01": {
      "MACD": "8.5432",
      "MACD_Signal": "6.2341",
      "MACD_Hist": "2.3091"
    },
    ...
  }
}
```

**字段说明**：
- `start_date`: 实际返回数据的开始日期（市场本地时间）
- `end_date`: 实际返回数据的结束日期（市场本地时间）
- `requested_start_date`: 用户请求的开始日期（如果指定）
- `requested_end_date`: 用户请求的结束日期（如果指定）
- `data_points`: 返回的数据点数量

## 错误处理

### 无效的日期格式

```bash
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&start_date=2025/10/01"
```

响应：
```json
{
  "error": "无效的开始日期格式: 2025/10/01，请使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS",
  "symbol": "AAPL"
}
```

### 日期范围内无数据

如果指定的日期范围内没有数据，会返回空的 `data` 对象：

```json
{
  "meta": {
    "symbol": "AAPL",
    "data_points": 0,
    ...
  },
  "data": {}
}
```

## 技术实现

### 1. 日期解析

在 `futu_client.py` 的 `get_technical_analysis` 方法中：

```python
# 解析日期范围（如果提供）
start_timestamp = None
end_timestamp = None

if start_date:
    from datetime import datetime
    try:
        if len(start_date) == 10:  # YYYY-MM-DD
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        else:  # YYYY-MM-DD HH:MM:SS
            start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        start_timestamp = int(start_dt.timestamp())
    except ValueError:
        return {"error": f"无效的开始日期格式: {start_date}"}
```

### 2. 数据过滤

在构建DataFrame时过滤数据：

```python
# 如果指定了日期范围，过滤数据
if start_timestamp and time_val < start_timestamp:
    continue
if end_timestamp and time_val > end_timestamp:
    continue
```

### 3. 元数据记录

在返回结果中记录请求的日期范围：

```python
# 如果指定了日期范围，添加到meta中
if start_date:
    result["meta"]["requested_start_date"] = start_date
if end_date:
    result["meta"]["requested_end_date"] = end_date
```

## 使用场景

### 1. 回测特定时期的策略

```bash
# 回测2025年Q3的交易策略
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&indicator=macd&start_date=2025-07-01&end_date=2025-09-30"
```

### 2. 分析特定事件前后的走势

```bash
# 分析财报发布前后一周的RSI变化
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&indicator=rsi&start_date=2025-10-25&end_date=2025-11-08"
```

### 3. 获取当日盘中数据

```bash
# 获取今日盘中的5分钟K线数据
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=5min&indicator=macd&start_date=2025-11-03 09:30:00&end_date=2025-11-03 16:00:00"
```

### 4. 减少数据传输量

```bash
# 只获取最近30天的数据，减少响应大小
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&indicator=boll&start_date=2025-10-04"
```

## 默认行为

### 默认时间范围限制

为了优化性能和减少数据传输量，**周K及以下时间间隔在不指定日期范围时，默认只返回最近1个月的数据**。

**适用的时间间隔**：
- 分钟级：1min, 5min, 15min, 30min, 60min
- 日K线：daily
- 周K线：weekly

**重要**：这里的"最近1个月"是基于数据的最新日期，而不是当前系统日期。

```bash
# 这些请求会自动限制为最近1个月（基于数据最新日期）
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=weekly&indicator=macd"
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&indicator=macd"
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=5min&indicator=macd"

# 例如：如果数据最新日期是2025-10-31，则返回2025-10-01至2025-10-31的数据
```

如果需要更长的历史数据，请明确指定日期范围：

```bash
# 获取最近3个月的数据
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&indicator=macd&start_date=2025-08-01"

# 获取全年的数据
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&indicator=macd&start_date=2025-01-01"
```

### 不受限制的时间间隔

以下时间间隔在不指定日期范围时，返回所有可用数据：
- 月K线：monthly
- 季K线：quarterly
- 年K线：yearly

## 注意事项

1. **时区处理**：
   - 日期参数使用本地时间（不带时区）
   - 内部会转换为Unix时间戳进行比较
   - 返回的日期会自动转换为市场本地时间

2. **数据可用性**：
   - 富途API返回的历史数据有限制
   - 分钟级数据通常只保留最近几天
   - 日K线数据可以追溯更久

3. **性能优化**：
   - 指定日期范围可以减少数据处理量
   - 对于大量数据的请求，建议使用日期范围
   - 周K线默认限制为1个月，避免返回过多数据

4. **技术指标计算**：
   - 某些指标（如SMA、EMA）需要足够的历史数据
   - 如果日期范围太小，可能导致指标值不准确
   - 建议至少保留50-200个数据点
   - 周K线1个月约4-5个数据点，可能不足以计算某些长期指标

## 测试

运行测试脚本验证功能：

```bash
cd futu-paper-trade-api
python test_date_range.py
```

测试脚本会验证：
- 不指定日期范围
- 指定完整日期范围
- 只指定开始日期
- 无效的日期格式

## 更新日志

- 2025-11-03: 初始版本，添加 start_date 和 end_date 参数
