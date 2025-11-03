# 富途模拟交易API分析报告

## 页面概况
- 页面URL: https://www.futunn.com/paper-trade
- 功能: 模拟股票交易平台
- 当前账户: 第二届全球模拟交易大赛

## 账户信息展示
从页面可以看到以下账户数据：
- **资产净值**: 100,303.41 美元
- **总排名**: 10916
- **今日盈亏**: 0.00
- **今日盈亏比例**: 0.00%
- **持仓盈亏**: +304.40
- **持仓市值**: 10,814.80
- **最大购买力**: 189,792.02
- **维持保证金**: 4,325.92
- **现金**: 89,488.61
- **剩余流动性**: 95,977.49

## 核心API接口

### 1. 获取账户列表
```
GET https://www.futunn.com/paper-trade/common-api?_m=getAccountList&attribute_market=1
```
**功能**: 获取用户的模拟交易账户列表
**返回**: 账户ID列表

### 2. 获取账户详情
```
GET https://www.futunn.com/paper-trade/common-api?_m=getAccountDetail&account_id=16992013
```
**功能**: 获取指定账户的详细信息
**参数**: 
- `account_id`: 账户ID (示例: 16992013)
**返回数据包含**:
- 资产净值
- 现金余额
- 购买力
- 保证金信息
- 盈亏数据

### 3. 获取持仓列表
```
GET https://www.futunn.com/paper-trade/common-api?_m=getIntegratedPosList&account_id=16992013
```
**功能**: 获取账户的股票持仓信息
**参数**:
- `account_id`: 账户ID
**返回数据包含**:
- 持仓股票代码
- 持仓数量
- 成本价
- 当前价
- 盈亏金额和比例
- 持仓市值

### 4. 获取股票行情
```
GET https://www.futunn.com/paper-trade/common-api?_m=batchGetSecurityQuote&security_ids=["202597"]&market_type=100&pre_after_price_switch=true
```
**功能**: 批量获取股票实时行情
**参数**:
- `security_ids`: 股票ID数组 (示例: ["202597"] 对应 NVDA)
- `market_type`: 市场类型 (100 = 美股)
- `pre_after_price_switch`: 是否包含盘前盘后价格

### 5. 获取比赛排名
```
GET https://m-match.futunn.com/match/maccount-rank?mid=239&num=100
```
**功能**: 获取模拟交易比赛的排名信息
**参数**:
- `mid`: 比赛ID (239 = 第二届全球模拟交易大赛)
- `num`: 返回排名数量

### 6. 获取K线数据
```
GET https://www.futunn.com/paper-trade/api-quote-kline?stockId=202597&type=1&symbol=1&security=1&req_section=1
```
**功能**: 获取股票K线图数据
**参数**:
- `stockId`: 股票ID
- `type`: K线类型 (1=分时, 其他值对应日K/周K等)

### 7. 风险交易金额计算
```
GET https://www.futunn.com/paper-trade/common-api?_m=getRiskTradeAmount&account_id=16992013&order_info={...}
```
**功能**: 计算下单前的风险评估和所需金额
**参数**:
- `account_id`: 账户ID
- `order_info`: 订单信息JSON (包含价格、数量、方向等)

### 8. 获取热门股票榜单
```
GET https://m-match.futunn.com/stock/get-hot-list?market_type=100&stock_type=1&count=10
```
**功能**: 获取热门股票列表
**参数**:
- `market_type`: 市场类型 (100 = 美股)
- `stock_type`: 股票类型 (1 = 股票)
- `count`: 返回数量

## API特点分析

### ✅ 可以通过接口获取的数据
1. **账户信息**: 完全可以通过API获取
   - 资产净值、现金、购买力等所有财务数据
   - 账户ID: 16992013

2. **持仓信息**: 完全可以通过API获取
   - 持仓股票列表
   - 每只股票的数量、成本、市值、盈亏

3. **实时行情**: 可以获取
   - 股票实时价格
   - K线数据
   - 盘前盘后价格

4. **比赛排名**: 可以获取
   - 当前排名
   - 排行榜数据

### 🔒 认证要求
从网络请求可以看出：
- 这些API需要登录认证
- 使用Cookie进行身份验证
- 需要有效的session才能访问

### 📝 数据格式
- 所有API返回JSON格式数据
- 使用RESTful风格的查询参数
- 支持批量查询（如批量获取股票行情）

## 实际应用建议

### 方案1: 使用富途OpenAPI
从你的工作区可以看到 `Futu_OpenD` 程序，这是富途官方提供的OpenAPI网关：
- 更稳定、更规范的API接口
- 支持实盘和模拟盘
- 有完整的Python SDK (futu-api)
- 官方文档: https://openapi.futunn.com/

### 方案2: 直接调用Web API
如果要直接使用上述发现的Web API：
1. 需要先登录获取Cookie
2. 在请求头中携带Cookie
3. 注意API可能会变动，不如官方OpenAPI稳定

## 示例代码（使用官方OpenAPI）

```python
from futu import *

# 连接OpenD
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 获取账户信息
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)

# 查询账户资金
ret, data = trd_ctx.accinfo_query()
if ret == RET_OK:
    print(data)

# 查询持仓
ret, data = trd_ctx.position_list_query()
if ret == RET_OK:
    print(data)

trd_ctx.close()
quote_ctx.close()
```

## 总结
✅ **模拟股票账户信息和持仓信息完全可以通过接口获取**

推荐使用富途官方的OpenAPI（你已经下载了OpenD程序），这样更稳定可靠。如果一定要用Web API，需要处理登录认证和Cookie管理。
