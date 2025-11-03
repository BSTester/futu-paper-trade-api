# 市场类型参数映射说明

## 概述

富途API中有两种不同的市场类型参数，它们的映射关系不同，需要注意区分。

---

## 1. API请求参数 `market_type`

用于搜索、行情、交易等API请求的 `market_type` 参数。

### 映射关系

| 市场 | 代码 | market_type 值 |
|------|------|----------------|
| 美股 | US   | 100            |
| 港股 | HK   | 1              |
| A股  | CN   | 3              |
| 日股 | JP   | 4              |

### 使用示例

```python
# config.py 中的配置
MARKET_TYPE = {
    "US": 100,  # 美股
    "HK": 1,    # 港股
    "CN": 3,    # A股
    "JP": 4,    # 日股
}
```

### API示例

```bash
# 美股搜索
https://m-match.futunn.com/trade/search-target-stock?key=AAPL&market_type=100

# 港股搜索
https://m-match.futunn.com/trade/search-target-stock?key=00700&market_type=1

# A股搜索
https://m-match.futunn.com/trade/search-target-stock?key=600000&market_type=3
```

---

## 2. 账户属性参数 `attribute_market`

用于账户列表返回的账户属性标识。

### 映射关系

| 市场 | 代码 | attribute_market 值 |
|------|------|---------------------|
| 港股 | HK   | 1                   |
| 美股 | US   | 2                   |
| A股  | CN   | 3                   |
| 日股 | JP   | 4                   |

### 使用示例

```python
# futu_client.py 中的 _parse_market_type 方法
def _parse_market_type(self, attribute_market: int) -> str:
    """
    解析市场类型
    
    attribute_market映射：
    1 = 港股 (HK)
    2 = 美股 (US)
    3 = A股 (CN)
    4 = 日股 (JP)
    """
    market_map = {
        1: "HK",  # 港股
        2: "US",  # 美股
        3: "CN",  # A股
        4: "JP",  # 日股
    }
    return market_map.get(attribute_market, "")
```

### API示例

```bash
# 获取账户列表
GET /paper-trade/common-api?_m=getAccountList&attribute_market=1

# 返回示例
{
  "data": {
    "account_list": [
      {
        "account_id": "9393",
        "account_name": "港股模拟账户",
        "attribute_market": 1,  # 港股
        "currency": "HKD"
      },
      {
        "account_id": "17198232",
        "account_name": "美股模拟账户",
        "attribute_market": 2,  # 美股
        "currency": "USD"
      }
    ]
  }
}
```

---

## 重要提示

⚠️ **注意区分两种映射**：

1. **API请求参数 `market_type`**：
   - 美股 = 100（特殊值）
   - 港股 = 1
   - A股 = 3

2. **账户属性 `attribute_market`**：
   - 港股 = 1
   - 美股 = 2
   - A股 = 3

这两个参数的映射关系不同，在使用时需要根据具体场景选择正确的映射。

---

## 代码中的使用

### 搜索股票

```python
# 使用 MARKET_TYPE 映射
market_type_code = MARKET_TYPE.get(market_type, 100)
# US -> 100, HK -> 1, CN -> 3
```

### 解析账户类型

```python
# 使用 attribute_market 映射
market_type = self._parse_market_type(attribute_market)
# 1 -> HK, 2 -> US, 3 -> CN
```

---

## 更新历史

- **2025-11-02**: 修正 A股的 `market_type` 从 2 改为 3
- **2025-11-02**: 创建此文档说明两种映射的区别
