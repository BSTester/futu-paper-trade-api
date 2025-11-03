# Playwright 抓包结果

## 🔍 实际的API调用

通过 Playwright 访问富途模拟交易页面，捕获到以下实际的API请求：

---

## ✅ 发现的API端点

### 1. 账户列表
```
GET https://www.futunn.com/paper-trade/common-api?_m=getAccountList&attribute_market=1
状态: 200 OK
```

### 2. 账户详情
```
GET https://www.futunn.com/paper-trade/common-api?_m=getAccountDetail&account_id=16992013
状态: 200 OK
```

### 3. 持仓列表
```
GET https://www.futunn.com/paper-trade/common-api?_m=getIntegratedPosList&account_id=16992013
状态: 200 OK
```

### 4. 股票行情
```
GET https://www.futunn.com/paper-trade/common-api?_m=batchGetSecurityQuote&security_ids=["202597"]&market_type=100&pre_after_price_switch=true
状态: 200 OK
```

### 5. K线数据
```
GET https://www.futunn.com/paper-trade/api-quote-kline?stockId=202597&type=1&symbol=1&security=1&req_section=1
状态: 200 OK
```

### 6. 热门股票
```
GET https://m-match.futunn.com/stock/get-hot-list?market_type=100&stock_type=1&count=10
状态: 200 OK
```

### 7. 风险交易金额
```
GET https://www.futunn.com/paper-trade/common-api?_m=getRiskTradeAmount&account_id=16992013&order_info=...
状态: 200 OK
```

---

## 🎯 重要发现

### 方法名是正确的！

我们代码中使用的方法名和浏览器实际调用的**完全一致**：

| 功能 | 我们的代码 | 浏览器实际调用 | 状态 |
|------|-----------|---------------|------|
| 账户列表 | `getAccountList` | `getAccountList` | ✅ 一致 |
| 账户详情 | `getAccountDetail` | `getAccountDetail` | ✅ 一致 |
| 持仓列表 | `getIntegratedPosList` | `getIntegratedPosList` | ✅ 一致 |
| 股票行情 | `batchGetSecurityQuote` | `batchGetSecurityQuote` | ✅ 一致 |

### 那为什么我们的请求返回 "Invalid Method"？

可能的原因：

1. **Cookie 格式问题**
   - 浏览器的Cookie可能包含额外的字段
   - Cookie可能需要特定的格式

2. **请求头不完整**
   - 可能缺少某些必需的请求头
   - User-Agent、Referer等可能需要特定值

3. **参数格式问题**
   - 参数的编码方式可能不对
   - 某些参数可能需要特定格式

---

## 🔍 详细对比

### 我们的请求
```python
URL: https://www.futunn.com/paper-trade/common-api
Method: GET
Params: {'_m': 'getAccountDetail', 'account_id': '16992013'}
Headers: {
    "Cookie": "...",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.futunn.com/paper-trade"
}
```

**响应**:
```json
{"code": -1, "message": "Invalid Method", "data": []}
```

### 浏览器的请求
```
URL: https://www.futunn.com/paper-trade/common-api?_m=getAccountDetail&account_id=16992013
Method: GET
状态: 200 OK
```

**响应**: 成功（从页面显示可以看出）

---

## 💡 可能的问题

### 1. Cookie 问题

浏览器登录后的Cookie可能包含：
- `uid` - 用户ID
- `web_sig` - 签名
- `ci_sig` - 另一个签名
- `csrfToken` - CSRF令牌
- `futu-csrf` - 富途CSRF令牌
- 其他会话相关的Cookie

我们的Cookie可能：
- ❌ 已过期
- ❌ 缺少某些必需的字段
- ❌ 格式不正确

### 2. 请求头问题

可能需要的额外请求头：
- `X-Requested-With`
- `Origin`
- `Sec-Fetch-*` 系列
- 其他自定义头

### 3. 参数编码问题

注意到浏览器的请求中：
```
security_ids=["202597"]
```

这是一个JSON数组的字符串表示，可能需要特定的编码方式。

---

## 🔧 解决方案

### 方案1: 更新Cookie（推荐）

1. **重新获取Cookie**
   - 在浏览器中登录富途
   - 打开开发者工具
   - 复制完整的Cookie字符串
   - 更新 `.env` 文件

2. **确保Cookie完整**
   - 包含所有字段
   - 特别注意 `uid`, `web_sig`, `csrfToken` 等

### 方案2: 完善请求头

在 `futu_client.py` 中添加更多请求头：

```python
self.headers = {
    "Cookie": self.cookie,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.futunn.com/paper-trade",
    "Origin": "https://www.futunn.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "X-Requested-With": "XMLHttpRequest"
}
```

### 方案3: 使用Playwright自动化

直接使用Playwright来调用API：

```python
from playwright.async_api import async_playwright

async def get_account_with_playwright():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        
        # 设置Cookie
        await context.add_cookies([...])
        
        page = await context.new_page()
        await page.goto("https://www.futunn.com/paper-trade")
        
        # 等待API响应
        async with page.expect_response("**/common-api?_m=getAccountDetail*") as response_info:
            response = await response_info.value
            data = await response.json()
            return data
```

---

## 📊 测试建议

### 1. 验证Cookie有效性

```bash
curl -H "Cookie: YOUR_COOKIE_HERE" \
  "https://www.futunn.com/paper-trade/common-api?_m=getAccountList&attribute_market=1"
```

如果返回正常数据，说明Cookie有效。

### 2. 对比请求头

使用浏览器开发者工具：
1. 找到成功的请求
2. 右键 → Copy → Copy as cURL
3. 对比我们的请求和浏览器的请求

### 3. 检查响应

如果Cookie有效但仍返回错误，可能是：
- 请求头不完整
- 参数格式不对
- 需要额外的验证

---

## 🎯 下一步行动

### 立即可做

1. ✅ 确认方法名正确
2. ✅ 确认API端点正确
3. ⏳ 更新Cookie
4. ⏳ 完善请求头

### 需要测试

1. 重新获取Cookie并测试
2. 添加更多请求头并测试
3. 使用curl直接测试API

### 长期方案

考虑使用富途OpenD API，避免这些Web API的问题。

---

**抓包完成时间**: 2025-11-01 22:05  
**方法名状态**: ✅ 正确  
**问题根源**: ⚠️ Cookie或请求头问题  
**建议**: 重新获取Cookie并完善请求头
