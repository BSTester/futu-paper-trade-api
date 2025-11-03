# 技术指标使用指南

## 概述

技术分析接口支持多种时间周期和技术指标，帮助您分析股票走势和做出交易决策。

---

## 时间周期

### 1. 日K及以上周期

直接使用 `kline_type` 参数：

| kline_type | 周期 | 说明 |
|------------|------|------|
| 2 | 日K | 默认，适合中短期分析 |
| 3 | 周K | 适合中期趋势分析 |
| 4 | 月K | 适合长期趋势分析 |
| 5 | 年K | 适合超长期分析 |
| 11 | 季K | 适合季度分析 |

**示例**：
```bash
# 日K线分析
curl "http://localhost:8000/api/technical-analysis?stock_code=AAPL&kline_type=2"

# 周K线分析
curl "http://localhost:8000/api/technical-analysis?stock_code=AAPL&kline_type=3"
```

---

### 2. 分时周期

使用 `kline_type=1` 配合 `interval` 参数：

#### 分钟级（取2个交易日数据）

| interval | 周期 | 数据量 | 适用场景 |
|----------|------|--------|----------|
| 1min | 1分钟 | ~780条 | 超短线交易、盘中波动 |
| 3min | 3分钟 | ~260条 | 短线交易 |
| 5min | 5分钟 | ~156条 | 短线交易、日内波段 |
| 15min | 15分钟 | ~52条 | 日内趋势 |
| 30min | 30分钟 | ~26条 | 日内趋势、短期波段 |

#### 小时级（取7个交易日数据）

| interval | 周期 | 数据量 | 适用场景 |
|----------|------|--------|----------|
| 1h | 1小时 | ~45条 | 短期趋势 |
| 2h | 2小时 | ~22条 | 短期趋势 |
| 4h | 4小时 | ~11条 | 中短期趋势 |

**示例**：
```bash
# 5分钟K线分析
curl "http://localhost:8000/api/technical-analysis?stock_code=AAPL&kline_type=1&interval=5min"

# 1小时K线分析
curl "http://localhost:8000/api/technical-analysis?stock_code=AAPL&kline_type=1&interval=1h"
```

---

## 支持的技术指标

### 1. 移动平均线（MA）

#### close_50_sma - 50日简单移动平均线
- **用法**：识别中期趋势方向，作为动态支撑/阻力
- **技巧**：滞后于价格，需结合更快指标获得及时信号
- **信号**：
  - 价格在50日线上方 → 多头趋势
  - 价格在50日线下方 → 空头趋势
  - 价格突破50日线 → 趋势可能转变

#### close_200_sma - 200日简单移动平均线
- **用法**：确认整体市场趋势，黄金/死亡交叉设置
- **技巧**：反应缓慢，最适合战略趋势确认
- **信号**：
  - 50日线上穿200日线 → 黄金交叉（看涨）
  - 50日线下穿200日线 → 死亡交叉（看跌）

#### close_10_ema - 10日指数移动平均线
- **用法**：捕捉动量快速变化和潜在入场点
- **技巧**：在震荡市场容易产生噪音，需与更长周期平均线结合
- **信号**：
  - 价格突破10日EMA → 短期趋势变化
  - 10日EMA方向 → 短期动量方向

---

### 2. MACD指标

#### macd - MACD线
- **计算**：12日EMA - 26日EMA
- **用法**：寻找交叉和背离作为趋势变化信号
- **信号**：
  - MACD > 0 → 短期动量强于长期
  - MACD < 0 → 短期动量弱于长期

#### macds - MACD信号线
- **计算**：MACD的9日EMA
- **用法**：与MACD线交叉触发交易
- **信号**：
  - MACD上穿信号线 → 买入信号
  - MACD下穿信号线 → 卖出信号

#### macdh - MACD柱状图
- **计算**：MACD - 信号线
- **用法**：可视化动量强度，早期发现背离
- **信号**：
  - 柱状图扩大 → 动量增强
  - 柱状图缩小 → 动量减弱
  - 柱状图变色 → 趋势可能转变

---

### 3. 动量指标

#### rsi - 相对强弱指标
- **范围**：0-100
- **用法**：标记超买/超卖状况，观察背离信号
- **信号**：
  - RSI > 70 → 超买，可能回调
  - RSI < 30 → 超卖，可能反弹
  - RSI背离 → 趋势可能反转
- **技巧**：在强趋势中RSI可能保持极值，需与趋势分析交叉检查

---

### 4. 波动性指标

#### boll - 布林带中轨
- **计算**：20日SMA
- **用法**：作为价格运动的动态基准
- **技巧**：与上下轨结合使用

#### boll_ub - 布林带上轨
- **计算**：中轨 + 2倍标准差
- **用法**：信号潜在超买状况和突破区域
- **信号**：
  - 价格触及上轨 → 可能超买
  - 价格突破上轨 → 强势突破
- **技巧**：价格可能在强趋势中沿着带运行

#### boll_lb - 布林带下轨
- **计算**：中轨 - 2倍标准差
- **用法**：表示潜在超卖状况
- **信号**：
  - 价格触及下轨 → 可能超卖
  - 价格跌破下轨 → 弱势突破
- **技巧**：使用额外分析避免假反转信号

#### atr - 平均真实范围
- **用法**：测量波动性，设置止损水平
- **应用**：
  - 止损距离 = 当前价格 ± (2-3倍ATR)
  - 仓位大小 = 风险金额 / ATR
- **技巧**：这是反应性指标，作为风险管理策略的一部分

---

### 5. 成交量指标

#### vwma - 成交量加权移动平均线
- **用法**：通过整合价格与成交量确认趋势
- **技巧**：注意成交量突增造成的偏斜结果
- **信号**：
  - 价格在VWMA上方 → 买盘主导
  - 价格在VWMA下方 → 卖盘主导

#### mfi - 资金流量指数
- **范围**：0-100
- **用法**：使用价格和成交量测量买卖压力
- **信号**：
  - MFI > 80 → 超买
  - MFI < 20 → 超卖
  - MFI背离 → 潜在反转
- **技巧**：与RSI或MACD一起使用确认信号

---

## 使用建议

### 1. 选择合适的时间周期

| 交易风格 | 推荐周期 | 推荐指标 |
|----------|----------|----------|
| 超短线（日内） | 1min, 3min, 5min | RSI, MACD, VWMA |
| 短线（1-5天） | 15min, 30min, 1h | RSI, MACD, 布林带 |
| 波段（1-4周） | 4h, 日K | MACD, 布林带, 50SMA |
| 中线（1-3月） | 日K, 周K | 50SMA, 200SMA, MACD |
| 长线（3月以上） | 周K, 月K | 200SMA, 趋势线 |

### 2. 指标组合策略

#### 趋势跟踪策略
```bash
# 使用移动平均线和MACD
curl "http://localhost:8000/api/technical-analysis?stock_code=AAPL&kline_type=2&indicators=close_50_sma,close_200_sma,macd,macds"
```

#### 超买超卖策略
```bash
# 使用RSI和布林带
curl "http://localhost:8000/api/technical-analysis?stock_code=AAPL&kline_type=2&indicators=rsi,boll,boll_ub,boll_lb"
```

#### 成交量确认策略
```bash
# 使用MACD和MFI
curl "http://localhost:8000/api/technical-analysis?stock_code=AAPL&kline_type=2&indicators=macd,macds,mfi,vwma"
```

#### 日内交易策略
```bash
# 5分钟K线，使用快速指标
curl "http://localhost:8000/api/technical-analysis?stock_code=AAPL&kline_type=1&interval=5min&indicators=rsi,macd,close_10_ema"
```

### 3. 注意事项

1. **不要单独使用一个指标**：多个指标相互确认可以提高准确性
2. **注意背离信号**：价格与指标的背离往往预示趋势反转
3. **考虑市场环境**：趋势市场和震荡市场适用不同的指标
4. **设置止损**：使用ATR等指标设置合理的止损位
5. **数据量要求**：
   - RSI需要至少14个数据点
   - MACD需要至少26个数据点
   - 布林带需要至少20个数据点
   - 200日SMA需要至少200个数据点

---

## 完整示例

### 示例1：日K线全面分析
```bash
curl "http://localhost:8000/api/technical-analysis?stock_code=AAPL&kline_type=2"
```

### 示例2：5分钟K线短线分析
```bash
curl "http://localhost:8000/api/technical-analysis?stock_code=AAPL&kline_type=1&interval=5min&indicators=rsi,macd,macds,macdh,close_10_ema"
```

### 示例3：1小时K线波段分析
```bash
curl "http://localhost:8000/api/technical-analysis?stock_code=AAPL&kline_type=1&interval=1h&indicators=rsi,macd,boll,boll_ub,boll_lb,close_50_sma"
```

### 示例4：周K线趋势分析
```bash
curl "http://localhost:8000/api/technical-analysis?stock_code=AAPL&kline_type=3&indicators=close_50_sma,close_200_sma,macd,macds"
```

---

## 响应数据解读

```json
{
  "stock_code": "AAPL",
  "stock_name": "苹果",
  "market_type": "US",
  "kline_type": 1,
  "interval": "5min",
  "latest_price": 270.37,
  "data_points": 156,
  "indicators": {
    "rsi": {
      "name": "RSI",
      "description": "...",
      "value": 65.32  // 当前RSI值，65表示偏强但未超买
    },
    "macd": {
      "name": "MACD",
      "value": 2.15  // 正值表示短期动量强于长期
    },
    "macds": {
      "name": "MACD Signal",
      "value": 1.85  // MACD > Signal，看涨信号
    },
    "close_10_ema": {
      "name": "10 EMA",
      "value": 269.50  // 当前价格270.37 > 10EMA，短期上涨趋势
    }
  }
}
```

**分析**：
- RSI=65.32：动量偏强，但未超买（<70）
- MACD=2.15 > Signal=1.85：短期看涨
- 价格270.37 > 10EMA=269.50：短期上涨趋势
- **结论**：短期多头趋势，可考虑持有或轻仓做多

---

## 常见问题

### Q1: 为什么有些指标返回null？
A: 数据点不足以计算该指标。例如200日SMA需要至少200个数据点。

### Q2: 分时数据如何选择时间间隔？
A: 
- 日内交易：1min, 3min, 5min
- 短线波段：15min, 30min, 1h
- 短期趋势：2h, 4h

### Q3: 如何判断趋势强度？
A: 结合多个指标：
- MACD柱状图扩大 → 趋势增强
- RSI持续在50以上 → 上涨趋势
- 价格在所有均线上方 → 强势上涨

### Q4: 数据更新频率？
A: 实时获取富途API数据，分时数据延迟约1-2分钟。
