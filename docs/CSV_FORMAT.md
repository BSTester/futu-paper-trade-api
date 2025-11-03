# CSV格式输出功能

## 更新时间
2025-11-03

## 概述

技术分析接口和K线数据接口现在支持CSV格式输出，方便数据导出和分析。

## 支持的接口

- `/api/technical-analysis` - 技术分析接口
- `/api/kline` - K线数据接口

## 使用方法

### 参数

添加 `format=csv` 参数到请求URL：

```bash
# K线数据CSV格式
GET /api/kline?symbol=AAPL&interval=daily&format=csv

# 技术分析CSV格式
GET /api/technical-analysis?symbol=AAPL&interval=daily&indicator=macd&format=csv
```

### 支持的格式值

| 格式 | 说明 | 默认 |
|------|------|------|
| `json` | JSON格式 | ✅ |
| `csv` | CSV格式 | |

## 响应格式

### JSON包装的CSV

CSV数据以JSON格式包装返回，便于程序处理：

```json
{
  "meta": {
    "symbol": "AAPL",
    "stock_name": "苹果",
    "market_type": "US",
    "interval": "daily",
    "data_points": 22
  },
  "data": "datetime,time,open,high,low,close,volume\n2025-10-31,1730419200,268.50,271.20,267.80,270.37,45678900\n...",
  "format": "csv"
}
```

### 字段说明

- `meta`: 元数据信息（与JSON格式相同）
- `data`: CSV格式的文本数据
- `format`: 标识返回格式为 "csv"

## K线数据CSV格式

### CSV表头

```csv
datetime,time,open,high,low,close,volume
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `datetime` | string | 本地时间（YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS） |
| `time` | integer | Unix时间戳（秒） |
| `open` | float | 开盘价 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `close` | float | 收盘价 |
| `volume` | integer | 成交量 |

### 示例数据

```csv
datetime,time,open,high,low,close,volume
2025-10-31,1730419200,268.50,271.20,267.80,270.37,45678900
2025-10-30,1730332800,265.30,268.90,264.50,268.15,42345600
2025-10-29,1730246400,263.80,266.50,262.90,265.70,38901200
```

## 技术分析CSV格式

### CSV表头（根据指标不同而变化）

#### MACD指标
```csv
Date,MACD,MACD_Signal,MACD_Hist
```

#### RSI指标
```csv
Date,RSI
```

#### 布林带指标
```csv
Date,Boll_Upper,Boll_Middle,Boll_Lower
```

### 示例数据

#### MACD
```csv
Date,MACD,MACD_Signal,MACD_Hist
2025-10-31,9.4638,6.9336,2.5302
2025-10-30,8.7040,6.3011,2.4029
2025-10-29,7.9856,5.7123,2.2733
```

#### RSI
```csv
Date,RSI
2025-10-31,65.32
2025-10-30,64.18
2025-10-29,62.95
```

## 使用示例

### 示例1：获取K线CSV数据

```bash
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=daily&format=csv"
```

响应：
```json
{
  "meta": {
    "symbol": "AAPL",
    "stock_name": "苹果",
    "security_id": "205189",
    "market_type": "US",
    "interval": "daily",
    "data_points": 200
  },
  "data": "datetime,time,open,high,low,close,volume\n2025-10-31,1730419200,268.50,271.20,267.80,270.37,45678900\n...",
  "format": "csv"
}
```

### 示例2：获取技术分析CSV数据

```bash
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&indicator=macd&format=csv"
```

响应：
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
    "data_points": 200
  },
  "data": "Date,MACD,MACD_Signal,MACD_Hist\n2025-10-31,9.4638,6.9336,2.5302\n...",
  "format": "csv"
}
```

### 示例3：结合日期范围使用

```bash
# K线数据指定日期范围
curl "http://localhost:8000/api/kline?symbol=AAPL&interval=daily&start_date=2025-10-01&end_date=2025-10-31&format=csv"

# 技术分析指定日期范围
curl "http://localhost:8000/api/technical-analysis?symbol=AAPL&interval=daily&indicator=rsi&start_date=2025-10-01&end_date=2025-10-31&format=csv"
```

## 程序化使用

### Python示例

```python
import requests
import csv
from io import StringIO

# 获取CSV格式的K线数据
response = requests.get(
    "http://localhost:8000/api/kline",
    params={
        "symbol": "AAPL",
        "interval": "daily",
        "format": "csv"
    }
)

data = response.json()

# 解析CSV数据
csv_text = data['data']
csv_reader = csv.DictReader(StringIO(csv_text))

# 处理数据
for row in csv_reader:
    print(f"日期: {row['datetime']}, 收盘价: {row['close']}")
```

### JavaScript示例

```javascript
// 获取CSV格式的K线数据
fetch('http://localhost:8000/api/kline?symbol=AAPL&interval=daily&format=csv')
  .then(response => response.json())
  .then(data => {
    // 解析CSV数据
    const csvText = data.data;
    const lines = csvText.split('\n');
    const headers = lines[0].split(',');
    
    // 处理数据
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',');
      const row = {};
      headers.forEach((header, index) => {
        row[header] = values[index];
      });
      console.log(`日期: ${row.datetime}, 收盘价: ${row.close}`);
    }
  });
```

### 保存为CSV文件

```python
import requests

# 获取CSV数据
response = requests.get(
    "http://localhost:8000/api/kline",
    params={
        "symbol": "AAPL",
        "interval": "daily",
        "format": "csv"
    }
)

data = response.json()

# 保存到文件
with open('aapl_kline.csv', 'w', encoding='utf-8') as f:
    f.write(data['data'])

print("CSV文件已保存: aapl_kline.csv")
```

## 错误处理

### 无效的格式参数

请求：
```bash
curl "http://localhost:8000/api/kline?symbol=AAPL&format=xml"
```

响应（HTTP 400）：
```json
{
  "detail": "不支持的格式: xml，支持的格式: json, csv"
}
```

## 性能考虑

### CSV vs JSON

| 方面 | CSV | JSON |
|------|-----|------|
| 文件大小 | 较小（约30-40%减少） | 较大 |
| 解析速度 | 快 | 中等 |
| 可读性 | 高（表格形式） | 中等 |
| 程序处理 | 需要CSV解析器 | 原生支持 |
| 适用场景 | 数据导出、Excel分析 | API集成、Web应用 |

### 建议

1. **数据导出和分析**：使用CSV格式
2. **API集成**：使用JSON格式（默认）
3. **大量数据**：使用CSV格式减少传输量
4. **实时处理**：使用JSON格式便于解析

## 与Excel集成

### 方法1：直接保存CSV文件

```python
import requests

response = requests.get(
    "http://localhost:8000/api/kline",
    params={"symbol": "AAPL", "interval": "daily", "format": "csv"}
)

with open('aapl_data.csv', 'w', encoding='utf-8') as f:
    f.write(response.json()['data'])
```

然后在Excel中打开 `aapl_data.csv` 文件。

### 方法2：使用pandas

```python
import requests
import pandas as pd
from io import StringIO

response = requests.get(
    "http://localhost:8000/api/kline",
    params={"symbol": "AAPL", "interval": "daily", "format": "csv"}
)

csv_text = response.json()['data']
df = pd.read_csv(StringIO(csv_text))

# 保存为Excel
df.to_excel('aapl_data.xlsx', index=False)

# 或进行数据分析
print(df.describe())
```

## 常见问题

### Q1: CSV格式是否支持所有参数？

A: 是的，CSV格式支持所有参数（symbol、interval、start_date、end_date等）。

### Q2: CSV数据的编码是什么？

A: UTF-8编码，支持中文和其他Unicode字符。

### Q3: 如何在Excel中正确打开CSV文件？

A: 
1. 保存CSV文件
2. 在Excel中选择"数据" -> "从文本/CSV"
3. 选择文件并确认编码为UTF-8
4. 点击"加载"

### Q4: CSV格式的时间是本地时间吗？

A: 是的，datetime字段已转换为市场本地时间。time字段是Unix时间戳。

### Q5: 可以只获取CSV文本而不要JSON包装吗？

A: 当前版本CSV数据以JSON包装返回，便于程序处理。如需纯CSV，可以提取data字段。

## 最佳实践

1. **数据导出**：使用CSV格式，便于Excel分析
2. **批量下载**：结合日期范围参数，分批下载大量数据
3. **数据备份**：定期导出CSV格式数据作为备份
4. **数据分析**：使用pandas等工具处理CSV数据
5. **文件命名**：使用有意义的文件名，如 `AAPL_daily_2025-10.csv`

## 总结

CSV格式输出功能提供了灵活的数据导出方式，适合：
- 数据分析和可视化
- Excel报表制作
- 数据备份和归档
- 与其他系统集成

结合日期范围参数，可以精确控制导出的数据范围，满足各种数据分析需求。
