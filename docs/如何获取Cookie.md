# 如何获取富途Cookie

## 🔍 问题确认

即使添加了完整的浏览器请求头，富途API仍然返回：
```json
{"code": -1, "message": "Invalid Method", "data": []}
```

这说明**Cookie已过期或会话失效**，需要重新获取。

---

## 📋 获取Cookie的步骤

### 方法1: 使用浏览器开发者工具（推荐）

#### 步骤1: 打开富途网站并登录

1. 打开浏览器（Chrome、Edge等）
2. 访问: https://www.futunn.com/paper-trade
3. 如果未登录，点击登录按钮
4. 输入账号密码登录

#### 步骤2: 打开开发者工具

- **Windows**: 按 `F12` 或 `Ctrl + Shift + I`
- **Mac**: 按 `Cmd + Option + I`

#### 步骤3: 切换到Network标签

1. 点击开发者工具顶部的 **Network** (网络) 标签
2. 勾选 **Preserve log** (保留日志)
3. 刷新页面 (F5)

#### 步骤4: 找到API请求

1. 在Network标签的过滤框中输入: `common-api`
2. 找到任意一个 `common-api` 请求
3. 点击该请求

#### 步骤5: 复制Cookie

1. 在右侧面板中，点击 **Headers** (标头) 标签
2. 向下滚动找到 **Request Headers** (请求标头)
3. 找到 **cookie:** 这一行
4. 点击 cookie 值，全选并复制（Ctrl+A, Ctrl+C）

**示例**:
```
cookie: cipher_device_id=1742602673871006; device_id=1742602673871006; uid=255983; web_sig=ZwS%2FrGyVKwuWFZEDCRwxsgO1WrgKgwwnH%2FXqYrDDjtBHRBbrd1epG1m3jO%2FdSNZu9TLyG4ZLtGJwJbaac7xpfbyyj2NT8E8rT5h6Xau%2FxydRQ56rt2rTzFDfjK9uCO6Chukr12jvLFyWZm%2FDIttKvQ%3D%3D; ...
```

#### 步骤6: 更新.env文件

1. 打开项目中的 `.env` 文件
2. 找到 `FUTU_COOKIE=` 这一行
3. 将复制的Cookie粘贴到引号中
4. 保存文件

**示例**:
```env
FUTU_COOKIE="cipher_device_id=1742602673871006; device_id=1742602673871006; uid=255983; ..."
```

#### 步骤7: 重启服务

```bash
# 停止当前服务 (Ctrl+C)
# 重新启动
python main.py
```

---

### 方法2: 使用浏览器控制台

#### 步骤1-2: 同上（打开网站并登录）

#### 步骤3: 打开控制台

- 按 `F12` 打开开发者工具
- 切换到 **Console** (控制台) 标签

#### 步骤4: 执行JavaScript代码

在控制台中输入并执行：
```javascript
document.cookie
```

#### 步骤5: 复制输出

控制台会输出完整的Cookie字符串，复制它。

#### 步骤6-7: 同方法1（更新.env并重启）

---

### 方法3: 使用浏览器扩展

#### 推荐扩展

- **EditThisCookie** (Chrome/Edge)
- **Cookie-Editor** (Firefox)

#### 步骤

1. 安装扩展
2. 访问富途网站并登录
3. 点击扩展图标
4. 点击 "Export" 或 "导出"
5. 选择 "Netscape" 或 "Header String" 格式
6. 复制Cookie字符串
7. 更新.env文件

---

## ⚠️ 重要提示

### Cookie的格式

Cookie应该是一个长字符串，包含多个键值对，用分号分隔：

```
key1=value1; key2=value2; key3=value3; ...
```

### 必需的Cookie字段

确保Cookie中包含以下关键字段：
- `uid` - 用户ID
- `web_sig` - Web签名
- `csrfToken` - CSRF令牌
- `futu-csrf` - 富途CSRF令牌

### Cookie的有效期

- Cookie通常有时效性
- 如果长时间未使用，可能需要重新登录
- 建议定期更新Cookie

---

## 🧪 验证Cookie是否有效

### 方法1: 使用curl测试

```bash
curl -H "Cookie: YOUR_COOKIE_HERE" \
  "https://www.futunn.com/paper-trade/common-api?_m=getAccountDetail&account_id=16992013"
```

**成功的响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "account_id": "16992013",
    "net_asset": 1000000.00,
    ...
  }
}
```

**失败的响应**:
```json
{
  "code": -1,
  "message": "Invalid Method",
  "data": []
}
```

### 方法2: 使用Python测试

创建测试文件 `test_cookie.py`:

```python
import httpx
import asyncio

async def test_cookie():
    cookie = "YOUR_COOKIE_HERE"  # 替换为你的Cookie
    
    headers = {
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.futunn.com/paper-trade"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.futunn.com/paper-trade/common-api",
            params={"_m": "getAccountDetail", "account_id": "16992013"},
            headers=headers
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        data = response.json()
        if data.get("code") == 0:
            print("✅ Cookie有效！")
        else:
            print("❌ Cookie无效或已过期")

asyncio.run(test_cookie())
```

运行测试:
```bash
python test_cookie.py
```

---

## 🔧 常见问题

### Q1: Cookie太长，无法完整复制？

**A**: 
- 在Network标签中，右键点击请求
- 选择 "Copy" → "Copy as cURL"
- 这会复制完整的curl命令，包含完整的Cookie
- 从curl命令中提取Cookie部分

### Q2: 复制的Cookie包含换行符？

**A**: 
- 删除所有换行符
- Cookie应该是一行连续的字符串
- 确保没有多余的空格

### Q3: 更新Cookie后仍然报错？

**A**: 
1. 确认Cookie格式正确（无换行、无多余空格）
2. 确认已重启服务
3. 确认账户ID正确
4. 尝试重新登录并获取新Cookie

### Q4: 如何知道Cookie何时过期？

**A**: 
- Cookie通常在几小时到几天后过期
- 如果API返回 "Invalid Method"，通常说明Cookie已过期
- 建议每次使用前重新获取Cookie

---

## 📊 完整示例

### 1. 获取Cookie

在浏览器中:
1. 访问 https://www.futunn.com/paper-trade
2. 登录账户
3. F12 → Network → 刷新页面
4. 找到 common-api 请求
5. 复制 Cookie

### 2. 更新.env

```env
FUTU_COOKIE="cipher_device_id=1742602673871006; device_id=1742602673871006; _gcl_au=1.1.2132210082.1761151492; uid=255983; web_sig=ZwS%2FrGyVKwuWFZEDCRwxsgO1WrgKgwwnH%2FXqYrDDjtBHRBbrd1epG1m3jO%2FdSNZu9TLyG4ZLtGJwJbaac7xpfbyyj2NT8E8rT5h6Xau%2FxydRQ56rt2rTzFDfjK9uCO6Chukr12jvLFyWZm%2FDIttKvQ%3D%3D; csrfToken=XX-LNDkSvKzOHbAbvw3zeEf7; futu-csrf=+6J+BiZiThIfvbfSkt9BiRnQvW4=; ..."
```

### 3. 重启服务

```bash
python main.py
```

### 4. 测试接口

```bash
curl "http://localhost:8000/api/account?market_type=US"
```

---

## 💡 最佳实践

1. **定期更新Cookie**
   - 建议每天或每次使用前更新
   - 避免Cookie过期导致的问题

2. **保护Cookie安全**
   - 不要分享你的Cookie
   - Cookie包含登录凭证
   - 定期更改密码

3. **使用环境变量**
   - 将Cookie存储在.env文件中
   - 不要提交.env到Git仓库
   - 使用.gitignore排除.env

4. **考虑长期方案**
   - 如果频繁遇到Cookie问题
   - 建议切换到富途OpenD API
   - OpenD API不需要Cookie

---

## 🎯 下一步

1. ✅ 按照上述步骤获取新Cookie
2. ✅ 更新.env文件
3. ✅ 重启服务
4. ✅ 测试接口

如果问题仍然存在，建议：
- 检查账户是否正常
- 尝试不同的浏览器
- 考虑使用富途OpenD API

---

**文档更新时间**: 2025-11-01 22:35  
**问题**: Cookie过期  
**解决方案**: 重新获取Cookie
