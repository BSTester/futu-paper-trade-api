# 时区处理说明

## 概述

K线接口会根据股票所在市场自动转换时间为对应的本地时区，并正确处理美股的夏令时。

---

## 支持的时区

### 美股（US）- 美国东部时间

**时区名称**：
- **EDT（Eastern Daylight Time）**：夏令时，UTC-4
- **EST（Eastern Standard Time）**：冬令时，UTC-5

**夏令时规则**：
- 开始：每年3月第二个周日 02:00 → 03:00
- 结束：每年11月第一个周日 02:00 → 01:00
- 系统自动判断并显示正确的时区名称

**示例**：
```json
// 2025年10月31日（夏令时期间）
{
  "time": 1761897660,
  "local_time": "2025-10-31 04:01:00 EDT"
}

// 2024年12月31日（冬令时期间）
{
  "time": 1735660800,
  "local_time": "2024-12-31 09:00:00 EST"
}
```

---

### 港股（HK）- 香港时间

**时区名称**：HKT（Hong Kong Time）

**UTC偏移**：UTC+8（全年固定，无夏令时）

**示例**：
```json
{
  "time": 1761897660,
  "local_time": "2025-10-31 16:01:00 HKT"
}
```

---

### A股（CN）- 中国标准时间

**时区名称**：CST（China Standard Time）

**UTC偏移**：UTC+8（全年固定，无夏令时）

**示例**：
```json
{
  "time": 1761897660,
  "local_time": "2025-10-31 16:01:00 CST"
}
```

---

## 技术实现

### 时区库

系统按以下优先级使用时区库：

1. **zoneinfo**（Python 3.9+）- 首选
   - Python 标准库
   - 使用 IANA 时区数据库
   - 自动处理夏令时

2. **pytz** - 后备方案
   - 第三方库（已添加到 requirements.txt）
   - 支持 Python 3.6+
   - 完整的时区支持

3. **固定偏移** - 最后方案
   - 使用 datetime.timezone
   - 不处理夏令时（仅用于紧急情况）

### 时区标识符

| 市场 | IANA时区标识符 | 说明 |
|------|---------------|------|
| 美股 | America/New_York | 纽约时间，自动处理EST/EDT |
| 港股 | Asia/Hong_Kong | 香港时间 |
| A股 | Asia/Shanghai | 上海时间 |

---

## API使用

### 请求示例

```bash
# 美股K线（自动使用EST/EDT）
curl "http://localhost:8000/api/kline?stock_code=AAPL&market_type=US&kline_type=1"

# 港股K线（使用HKT）
curl "http://localhost:8000/api/kline?stock_code=00700&market_type=HK&kline_type=1"

# A股K线（使用CST）
curl "http://localhost:8000/api/kline?stock_code=600519&market_type=CN&kline_type=1"
```

### 响应字段

| 字段 | 说明 | 示例 |
|------|------|------|
| time | Unix时间戳（秒） | 1761897660 |
| local_time | 市场本地时间（含时区） | "2025-10-31 04:01:00 EDT" |

---

## 夏令时转换时间表（美股）

### 2024-2025年

| 日期 | 事件 | 时间变化 | 时区 |
|------|------|---------|------|
| 2024-03-10 | 夏令时开始 | 02:00 → 03:00 | EST → EDT |
| 2024-11-03 | 夏令时结束 | 02:00 → 01:00 | EDT → EST |
| 2025-03-09 | 夏令时开始 | 02:00 → 03:00 | EST → EDT |
| 2025-11-02 | 夏令时结束 | 02:00 → 01:00 | EDT → EST |

### 2026年

| 日期 | 事件 | 时间变化 | 时区 |
|------|------|---------|------|
| 2026-03-08 | 夏令时开始 | 02:00 → 03:00 | EST → EDT |
| 2026-11-01 | 夏令时结束 | 02:00 → 01:00 | EDT → EST |

---

## 常见问题

### Q: 为什么美股有时显示EST，有时显示EDT？

A: 这是正常的。美国东部时间有夏令时（EDT）和冬令时（EST）之分：
- 3月-11月：夏令时（EDT），UTC-4
- 11月-次年3月：冬令时（EST），UTC-5

系统会根据时间戳自动判断并显示正确的时区。

### Q: 港股和A股有夏令时吗？

A: 没有。香港和中国大陆都不实行夏令时，全年使用固定的UTC+8时区。

### Q: 如何验证时区转换是否正确？

A: 可以使用在线时区转换工具验证：
- https://www.timeanddate.com/worldclock/converter.html
- 输入Unix时间戳和目标时区进行对比

### Q: 原始Unix时间戳还保留吗？

A: 是的。响应中同时包含：
- `time`: 原始Unix时间戳
- `local_time`: 转换后的本地时间

这样既方便阅读，又保留了原始数据。

---

## 相关文档

- [API_REFERENCE.md](API_REFERENCE.md) - 完整API参考
- [KLINE_PARAMS.md](KLINE_PARAMS.md) - K线参数说明
- [CHANGELOG.md](CHANGELOG.md) - 更新日志
