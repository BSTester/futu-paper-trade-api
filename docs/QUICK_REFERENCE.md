# 日期范围功能快速参考

## 🎯 核心功能

两个接口现在支持日期范围过滤：
- `/api/technical-analysis` - 技术分析
- `/api/kline` - K线数据

## 📝 参数

| 参数 | 类型 | 必填 | 格式 | 说明 |
|------|------|------|------|------|
| `start_date` | string | 否 | `YYYY-MM-DD` 或 `YYYY-MM-DD HH:MM:SS` | 开始日期 |
| `end_date` | string | 否 | `YYYY-MM-DD` 或 `YYYY-MM-DD HH:MM:SS` | 结束日期 |
| `format` | string | 否 | `json` 或 `csv` | 返回格式（默认json） |

## ⚡ 快速示例

### 基础用法

```bash
# 获取指定月份的数据
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=daily&start_date=2025-10-01&end_date=2025-10-31"

# 只指定开始日期（到最新）
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=daily&start_date=2025-10-01"

# 分钟级数据（精确到秒）
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=5min&start_date=2025-11-01 09:30:00&end_date=2025-11-01 16:00:00"
```

### 技术分析

```bash
# 获取指定日期范围的MACD
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&indicator=macd&start_date=2025-10-01&end_date=2025-10-31"

# 获取最近一周的RSI
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&indicator=rsi&start_date=2025-10-25"

# CSV格式输出
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&indicator=macd&format=csv"
```

### K线数据

```bash
# 获取指定日期范围的K线
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=daily&start_date=2025-10-01&end_date=2025-10-31"

# CSV格式输出
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=daily&format=csv"

# CSV格式指定日期范围
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=daily&start_date=2025-10-01&end_date=2025-10-31&format=csv"
```

## ⚠️ 重要：默认时间范围限制

**周K及以下时间间隔不指定日期时，默认只返回最近1个月！**

**适用范围**：1min, 5min, 15min, 30min, 60min, daily, weekly

**重要**：基于数据的最新日期，而不是当前系统日期。

```bash
# ⚠️ 这些请求现在只返回最近1个月（基于数据最新日期）
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=weekly"
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=daily"
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=5min"

# ✅ 要获取更长历史，明确指定日期
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=daily&start_date=2025-01-01"
```

## 📊 时间间隔对比

| 时间间隔 | 不指定日期的默认行为 |
|---------|-------------------|
| `1min, 5min, 15min, 30min, 60min` | ⚠️ **仅返回最近1个月** |
| `daily` | ⚠️ **仅返回最近1个月** |
| `weekly` | ⚠️ **仅返回最近1个月** |
| `monthly` | 返回所有可用数据 |
| `quarterly` | 返回所有可用数据 |
| `yearly` | 返回所有可用数据 |

## 🔄 迁移检查清单

如果你的代码使用周K线：

- [ ] 检查是否依赖所有历史数据
- [ ] 如果是，添加 `start_date` 参数
- [ ] 测试更新后的代码
- [ ] 更新文档和注释

## 📦 响应格式

新增字段（当指定日期范围时）：

```json
{
  "meta": {
    "requested_start_date": "2025-10-01",
    "requested_end_date": "2025-10-31",
    ...
  }
}
```

## 🧪 测试

```bash
# 测试技术分析接口
python test_date_range.py

# 测试K线接口
python test_kline_date_range.py
```

## ❌ 错误处理

### 无效日期格式

```bash
# ❌ 错误
curl "http://localhost:8000/api/kline?symbol=AAPL&start_date=2025/10/01"

# ✅ 正确
curl "http://localhost:8000/api/kline?symbol=AAPL&start_date=2025-10-01"
```

响应：
```json
{
  "detail": "无效的开始日期格式: 2025/10/01，请使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS"
}
```

## 💡 最佳实践

1. **明确指定日期范围**：不要依赖默认行为
2. **使用合适的时间间隔**：根据分析需求选择
3. **分批请求大量数据**：避免一次请求过多数据
4. **缓存结果**：历史数据不会改变，可以缓存

## 📚 完整文档

- [UPDATE_2025-11-03.md](./docs/UPDATE_2025-11-03.md) - 完整更新说明
- [DATE_RANGE_FEATURE.md](./docs/DATE_RANGE_FEATURE.md) - 功能详细说明
- [WEEKLY_DEFAULT_RANGE.md](./docs/WEEKLY_DEFAULT_RANGE.md) - 周K线限制说明
- [API_REFERENCE.md](./docs/API_REFERENCE.md) - API参考文档

## 🆘 常见问题

**Q: 为什么周K线有默认限制？**
A: 优化性能，减少不必要的数据传输。

**Q: 如何获取周K线的所有历史数据？**
A: 明确指定 `start_date` 参数。

**Q: 其他时间间隔会受影响吗？**
A: 不会，只有周K线有默认限制。

**Q: 可以跨年查询吗？**
A: 可以，完全支持任意日期范围。
