# 更新日志 - 2025-11-03

## 新增功能

### 1. 日期范围过滤

为以下接口添加了 `start_date` 和 `end_date` 参数：

- ✅ `/api/technical-analysis` - 技术分析接口
- ✅ `/api/kline` - K线数据接口

**参数说明**：
- `start_date` (可选): 开始日期，格式 `YYYY-MM-DD` 或 `YYYY-MM-DD HH:MM:SS`
- `end_date` (可选): 结束日期，格式 `YYYY-MM-DD` 或 `YYYY-MM-DD HH:MM:SS`

**示例**：
```bash
# 获取指定月份的数据
GET /api/kline?symbol=AAPL&interval=daily&start_date=2025-10-01&end_date=2025-10-31

# 获取指定时间段的分钟数据
GET /api/kline?symbol=AAPL&interval=5min&start_date=2025-11-01 09:30:00&end_date=2025-11-01 16:00:00
```

### 2. CSV格式输出

为以下接口添加了 `format` 参数，支持CSV格式输出：

- ✅ `/api/technical-analysis` - 技术分析接口
- ✅ `/api/kline` - K线数据接口

**参数说明**：
- `format` (可选): 返回格式，默认 `json`
  - `json`: JSON格式（默认）
  - `csv`: CSV格式

**示例**：
```bash
# K线数据CSV格式
GET /api/kline?symbol=AAPL&interval=daily&format=csv

# 技术分析CSV格式
GET /api/technical-analysis?symbol=AAPL&interval=daily&indicator=macd&format=csv

# CSV格式指定日期范围
GET /api/kline?symbol=AAPL&interval=daily&start_date=2025-10-01&end_date=2025-10-31&format=csv
```

**CSV响应格式**：
```json
{
  "meta": {
    "symbol": "AAPL",
    "stock_name": "苹果",
    "data_points": 22
  },
  "data": "datetime,time,open,high,low,close,volume\n2025-10-31,1730419200,268.50,271.20,267.80,270.37,45678900\n...",
  "format": "csv"
}
```

### 周K线默认限制

**重要变更**：周K及以下时间间隔在不指定日期范围时，默认只返回最近1个月的数据。

**适用范围**：
- 分钟级：1min, 5min, 15min, 30min, 60min
- 日K线：daily
- 周K线：weekly

**重要说明**：这里的"最近1个月"是基于数据的最新日期，而不是当前系统日期。

**原因**：
- 优化性能
- 减少数据传输量
- 大多数场景只需要近期数据

**影响范围**：
- ⚠️ `/api/kline?interval=weekly` - 默认返回最近1个月
- ⚠️ `/api/kline?interval=daily` - 默认返回最近1个月
- ⚠️ `/api/kline?interval=5min` - 默认返回最近1个月
- ⚠️ `/api/technical-analysis?interval=weekly` - 默认返回最近1个月
- ⚠️ `/api/technical-analysis?interval=daily` - 默认返回最近1个月
- ⚠️ `/api/technical-analysis?interval=5min` - 默认返回最近1个月

**不受影响的时间间隔**：
- ✅ `interval=monthly` - 返回所有数据
- ✅ `interval=quarterly` - 返回所有数据
- ✅ `interval=yearly` - 返回所有数据

**如何获取更长的历史数据**：
```bash
# 明确指定开始日期
GET /api/kline?symbol=AAPL&interval=weekly&start_date=2025-01-01
```

## 向后兼容性

### ✅ 完全兼容
- 日K线及其他时间间隔（除周K线外）
- 明确指定日期范围的请求
- 所有其他API接口

### ⚠️ 需要注意
- 周K线不指定日期范围的请求（现在默认返回最近1个月）

### 迁移方案

如果你的代码依赖周K线的所有历史数据：

**之前**：
```python
response = requests.get("/api/kline", params={"symbol": "AAPL", "interval": "weekly"})
```

**现在**：
```python
response = requests.get("/api/kline", params={
    "symbol": "AAPL", 
    "interval": "weekly",
    "start_date": "2025-01-01"  # 明确指定开始日期
})
```

## 文档更新

- ✅ `docs/API_REFERENCE.md` - 更新API参考文档
- ✅ `docs/DATE_RANGE_FEATURE.md` - 日期范围功能详细说明
- ✅ `docs/WEEKLY_DEFAULT_RANGE.md` - 周K线默认限制说明
- ✅ `docs/UPDATE_2025-11-03.md` - 完整更新说明
- ✅ `main.py` - 更新API文档字符串

## 测试

新增测试脚本：
- ✅ `test_date_range.py` - 测试技术分析接口的日期范围功能
- ✅ `test_kline_date_range.py` - 测试K线接口的日期范围功能

运行测试：
```bash
python test_date_range.py
python test_kline_date_range.py
```

## 使用示例

### 技术分析接口

```bash
# 默认行为（日K线返回所有数据）
GET /api/technical-analysis?symbol=AAPL&interval=daily&indicator=macd

# 周K线默认返回最近1个月
GET /api/technical-analysis?symbol=AAPL&interval=weekly&indicator=macd

# 指定日期范围
GET /api/technical-analysis?symbol=AAPL&interval=daily&indicator=macd&start_date=2025-10-01&end_date=2025-10-31

# 只指定开始日期
GET /api/technical-analysis?symbol=AAPL&interval=daily&indicator=rsi&start_date=2025-10-15
```

### K线数据接口

```bash
# 默认行为（日K线返回所有数据）
GET /api/kline?symbol=AAPL&interval=daily

# 周K线默认返回最近1个月
GET /api/kline?symbol=AAPL&interval=weekly

# 指定日期范围
GET /api/kline?symbol=AAPL&interval=daily&start_date=2025-10-01&end_date=2025-10-31

# 分钟级数据指定时间范围
GET /api/kline?symbol=AAPL&interval=5min&start_date=2025-11-01 09:30:00&end_date=2025-11-01 16:00:00

# CSV格式输出
GET /api/kline?symbol=AAPL&interval=daily&format=csv

# CSV格式指定日期范围
GET /api/kline?symbol=AAPL&interval=daily&start_date=2025-10-01&end_date=2025-10-31&format=csv
```

## 响应格式

新增字段（当指定日期范围时）：

```json
{
  "meta": {
    "symbol": "AAPL",
    "data_points": 22,
    "requested_start_date": "2025-10-01",
    "requested_end_date": "2025-10-31"
  },
  "data": [...]
}
```

## 性能优化

- ⚡ 周K线默认限制减少了不必要的数据传输
- ⚡ 日期范围过滤在数据处理早期阶段进行，提高效率
- ⚡ 减少了服务器负载和响应时间

## 下一步

建议在生产环境部署前：
1. 运行测试脚本验证功能
2. 检查现有代码是否依赖周K线的所有历史数据
3. 更新客户端代码以明确指定日期范围（如果需要）

## 相关链接

- [完整更新说明](./docs/UPDATE_2025-11-03.md)
- [日期范围功能文档](./docs/DATE_RANGE_FEATURE.md)
- [周K线默认限制说明](./docs/WEEKLY_DEFAULT_RANGE.md)
- [API参考文档](./docs/API_REFERENCE.md)
