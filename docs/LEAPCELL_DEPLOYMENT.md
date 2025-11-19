# Leapcell 部署指南

本文档详细介绍如何将富途模拟交易API部署到 [Leapcell](https://leapcell.io/)。

## 什么是 Leapcell？

Leapcell 是一个现代化的应用部署平台，特点：
- 🚀 从 GitHub 一键部署
- 🔧 自动检测配置文件
- 🌐 自动提供 HTTPS 域名
- 📊 实时日志和监控
- 💰 按使用量计费

## 部署方式

### 方式一：一键部署（推荐）

1. **点击部署按钮**
   
   在项目 README 中点击 "Deploy on Leapcell" 按钮

2. **授权 GitHub**
   
   首次使用需要授权 Leapcell 访问你的 GitHub 仓库

3. **选择仓库**
   
   选择富途模拟交易API的仓库

4. **配置环境变量**
   
   系统会自动读取 `leapcell.json` 配置，你需要填写：
   
   **必填项：**
   - `FUTU_COOKIE` - 富途牛牛Web端的Cookie
   - `FUTU_CSRF_TOKEN` - 富途牛牛Web端的CSRF Token
   
   **账户配置（根据需要配置）：**
   - `ACCOUNT_ID_HK` - 港股账户ID（如需交易港股）
   - `ACCOUNT_ID_US` - 美股模拟账户ID（如需交易美股）
   - `ACCOUNT_ID_CN` - A股账户ID（如需交易A股）
   - `ACCOUNT_ID_US_COMPETITION` - 美股比赛账户ID（可选，如配置则优先使用）
   
   **可选项：**
   - `API_KEY` - API鉴权密钥（建议设置）

5. **开始部署**
   
   点击 "Deploy" 按钮，等待构建完成

6. **访问应用**
   
   部署成功后，Leapcell 会提供一个公网地址，如：
   `https://your-app.leapcell.app`

### 方式二：手动部署

1. **登录 Leapcell**
   
   访问 https://leapcell.io/ 并登录

2. **创建新项目**
   
   点击 "New Project" 按钮

3. **导入 GitHub 仓库**
   
   - 选择 "Import from GitHub"
   - 授权访问（如果是首次使用）
   - 选择富途模拟交易API仓库

4. **自动配置检测**
   
   Leapcell 会自动检测项目根目录的 `leapcell.json` 文件，并应用以下配置：
   
   ```json
   {
     "build": {
       "command": "pip install -r requirements.txt"
     },
     "start": {
       "command": "uvicorn main:app --host 0.0.0.0 --port $PORT"
     }
   }
   ```

5. **配置环境变量**
   
   在环境变量设置页面添加：
   
   | 变量名 | 说明 | 是否必填 |
   |--------|------|----------|
   | FUTU_COOKIE | 富途Cookie | 是 |
   | FUTU_CSRF_TOKEN | CSRF Token | 是 |
   | ACCOUNT_ID_HK | 港股账户ID | 否（如需交易港股则必填） |
   | ACCOUNT_ID_US | 美股模拟账户ID | 否（如需交易美股则必填） |
   | ACCOUNT_ID_CN | A股账户ID | 否（如需交易A股则必填） |
   | ACCOUNT_ID_US_COMPETITION | 美股比赛账户ID | 否（可选，优先使用） |
   | API_KEY | API鉴权密钥 | 否（建议设置） |
   | API_HOST | 监听地址 | 否（默认0.0.0.0） |
   | API_PORT | 监听端口 | 否（默认8000） |

6. **部署应用**
   
   点击 "Deploy" 开始部署

## 获取富途 Cookie 和 CSRF Token

### 步骤：

1. **打开富途牛牛Web端**
   
   访问 https://www.futunn.com/ 并登录

2. **打开开发者工具**
   
   - Chrome/Edge: 按 `F12` 或右键 → 检查
   - Firefox: 按 `F12` 或右键 → 检查元素

3. **切换到 Network 标签**
   
   在开发者工具中选择 "Network" (网络) 标签

4. **刷新页面**
   
   按 `F5` 刷新页面，观察网络请求

5. **查找请求**
   
   找到任意一个发往 `*.futunn.com` 的请求

6. **复制 Cookie**
   
   - 点击该请求
   - 在 "Headers" (请求头) 中找到 `Cookie`
   - 复制完整的 Cookie 值

7. **复制 CSRF Token**
   
   - 在同一个请求的 Headers 中找到 `x-csrf-token`
   - 复制该值

### 示例：

```
Cookie: _ga=GA1.2.xxx; _gid=GA1.2.xxx; ...
x-csrf-token: abc123def456...
```

## 验证部署

部署成功后，访问以下端点验证：

### 1. 健康检查

```bash
curl https://your-app.leapcell.app/health
```

预期响应：
```json
{
  "status": "healthy"
}
```

### 2. API 文档

浏览器访问：
- Swagger UI: `https://your-app.leapcell.app/docs`
- 自定义文档: `https://your-app.leapcell.app/api-docs`

### 3. 测试接口

```bash
# 获取账户信息（需要API Key）
curl -H "X-API-Key: your_api_key" \
  "https://your-app.leapcell.app/api/account?market_type=US"
```

## 常见问题

### 1. 部署失败：找不到依赖

**问题**：构建时提示找不到某些 Python 包

**解决**：
- 检查 `requirements.txt` 是否完整
- 确保 Python 版本兼容（建议 3.9+）
- 查看 Leapcell 构建日志获取详细错误信息

### 2. 应用启动失败

**问题**：部署成功但应用无法访问

**解决**：
- 检查环境变量是否正确设置
- 确保 `FUTU_COOKIE` 和 `FUTU_CSRF_TOKEN` 有效
- 查看应用日志：Leapcell 控制台 → Logs

### 3. Cookie 过期

**问题**：接口返回"未登录"错误

**解决**：
1. 重新从富途Web端获取 Cookie 和 CSRF Token
2. 在 Leapcell 控制台更新环境变量
3. 保存后会自动重新部署

### 4. 端口配置问题

**问题**：应用无法正常访问

**解决**：
- 确保启动命令使用 `$PORT` 环境变量
- Leapcell 会自动分配端口，不要硬编码端口号
- 正确的启动命令：`uvicorn main:app --host 0.0.0.0 --port $PORT`

### 5. API Key 鉴权失败

**问题**：接口返回 403 错误

**解决**：
- 检查请求头是否包含 `X-API-Key`
- 确认 API Key 与环境变量中设置的一致
- 如果不需要鉴权，可以不设置 `API_KEY` 环境变量

## 更新部署

### 自动部署

Leapcell 支持自动部署：

1. 在项目设置中启用 "Auto Deploy"
2. 每次推送到 GitHub 主分支时自动部署
3. 适合持续开发和更新

### 手动部署

1. 在 Leapcell 控制台找到你的项目
2. 点击 "Redeploy" 按钮
3. 等待构建完成

## 监控和日志

### 查看日志

1. 登录 Leapcell 控制台
2. 选择你的项目
3. 点击 "Logs" 标签
4. 实时查看应用日志

### 监控指标

Leapcell 提供以下监控指标：
- CPU 使用率
- 内存使用率
- 网络流量
- 请求数量
- 响应时间

## 成本优化

### 建议：

1. **使用休眠功能**
   - 如果应用不常用，可以启用自动休眠
   - 无请求时自动休眠，有请求时自动唤醒

2. **合理设置资源**
   - 根据实际使用情况调整 CPU 和内存配置
   - 避免过度配置

3. **监控使用量**
   - 定期查看使用统计
   - 优化高频接口的性能

## 安全建议

1. **设置强 API Key**
   ```bash
   # 生成随机 API Key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **定期更新 Cookie**
   - Cookie 会过期，建议每周检查
   - 设置提醒定期更新

3. **限制访问来源**
   - 如果只在特定场景使用，可以配置 IP 白名单
   - 使用 Leapcell 的访问控制功能

4. **启用 HTTPS**
   - Leapcell 默认提供 HTTPS
   - 确保所有请求都使用 HTTPS

## 技术支持

- Leapcell 文档: https://docs.leapcell.io/
- Leapcell 社区: https://community.leapcell.io/
- 项目 Issues: https://github.com/BSTester/futu-paper-trade-api/issues

## 总结

使用 Leapcell 部署富途模拟交易API非常简单：

1. ✅ 一键部署，无需复杂配置
2. ✅ 自动 HTTPS，安全可靠
3. ✅ 实时日志，便于调试
4. ✅ 自动扩展，按需付费
5. ✅ 持续部署，开发便捷

现在就开始部署吧！🚀
