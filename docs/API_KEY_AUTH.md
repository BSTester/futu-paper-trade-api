# API Key 鉴权说明

## 概述

为了保护API接口安全，系统支持通过API Key进行鉴权。

## 配置

在 `.env` 文件中设置API Key：

```bash
API_KEY=your_secure_api_key_here
```

**注意**：
- 如果不设置 `API_KEY`，则不进行鉴权（所有接口可直接访问）
- 如果设置了 `API_KEY`，则所有业务接口都需要提供正确的API Key才能访问

## 使用方法

### 请求头方式

在HTTP请求头中添加 `X-API-Key` 字段：

```bash
curl -H "X-API-Key: your_secure_api_key_here" \
  http://localhost:8000/api/account?market_type=US
```

### Python 示例

```python
import requests

headers = {
    "X-API-Key": "your_secure_api_key_here"
}

response = requests.get(
    "http://localhost:8000/api/account",
    params={"market_type": "US"},
    headers=headers
)

print(response.json())
```

### JavaScript 示例

```javascript
fetch('http://localhost:8000/api/account?market_type=US', {
  headers: {
    'X-API-Key': 'your_secure_api_key_here'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

## 无需鉴权的接口

以下接口无需API Key即可访问：

- `GET /` - API根路径
- `GET /health` - 健康检查
- `GET /docs` - API文档
- `GET /api-docs` - 自定义API文档
- `GET /openapi.json` - OpenAPI规范

## 需要鉴权的接口

所有业务接口都需要API Key：

- 账户相关：`/api/account`, `/api/positions`
- 交易相关：`/api/trade`, `/api/cancel`, `/api/orders`
- 行情相关：`/api/quote`, `/api/kline`, `/api/technical-analysis`, `/api/hot-stocks`
- 资讯相关：`/api/hot-news`

## 错误响应

如果API Key无效或缺失，将返回 403 错误：

```json
{
  "detail": "Invalid API Key"
}
```

## 安全建议

1. 使用强密码生成器生成API Key
2. 不要在代码中硬编码API Key
3. 使用环境变量管理API Key
4. 定期更换API Key
5. 不要将API Key提交到版本控制系统
