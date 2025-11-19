# Render 部署指南

本文档详细介绍如何将富途模拟交易API部署到 [Render](https://render.com/)。

## 什么是 Render？

Render 是一个现代化的云平台，特点：
- 🆓 提供免费套餐
- 🚀 从 GitHub 一键部署
- 🔒 自动 HTTPS 证书
- 🔄 自动部署（Git push 触发）
- 📊 实时日志和监控
- 🌐 全球 CDN

## 免费套餐说明

Render 的免费套餐包括：
- ✅ 750小时/月的运行时间
- ✅ 自动 HTTPS
- ✅ 自动部署
- ⚠️ 15分钟无请求后自动休眠
- ⚠️ 唤醒需要约30秒

**适用场景**：
- 个人项目
- 测试和开发
- 低频使用的API服务

## 部署方式

### 方式一：一键部署（推荐）

1. **点击部署按钮**
   
   在项目 README 中点击 "Deploy to Render" 按钮

2. **授权 GitHub**
   
   首次使用需要授权 Render 访问你的 GitHub 仓库

3. **选择仓库**
   
   选择富途模拟交易API的仓库

4. **自动配置**
   
   Render 会自动读取 `render.yaml` 配置文件，包括：
   
   ```yaml
   services:
     - type: web
       name: futu-trading-api
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

5. **配置环境变量**
   
   填写必需的环境变量：
   
   **必填项：**
   - `FUTU_COOKIE` - 富途牛牛Web端的Cookie
   - `FUTU_CSRF_TOKEN` - 富途牛牛Web端的CSRF Token
   
   **账户配置（根据需要配置）：**
   - `ACCOUNT_ID_HK` - 港股账户ID
   - `ACCOUNT_ID_US` - 美股模拟账户ID
   - `ACCOUNT_ID_CN` - A股账户ID
   - `ACCOUNT_ID_US_COMPETITION` - 美股比赛账户ID（可选）
   
   **自动生成：**
   - `API_KEY` - 会自动生成随机密钥

6. **开始部署**
   
   点击 "Apply" 按钮，等待构建完成

7. **访问应用**
   
   部署成功后，Render 会提供一个公网地址，如：
   `https://your-app.onrender.com`

### 方式二：手动部署

1. **登录 Render**
   
   访问 https://render.com/ 并登录

2. **创建新服务**
   
   点击 "New +" → "Web Service"

3. **连接 GitHub**
   
   - 点击 "Connect a repository"
   - 授权访问（如果是首次使用）
   - 选择富途模拟交易API仓库

4. **配置服务**
   
   Render 会自动检测 `render.yaml`，或手动配置：
   
   | 配置项 | 值 |
   |--------|-----|
   | Name | futu-trading-api |
   | Region | Oregon (US West) |
   | Branch | main |
   | Runtime | Python 3 |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
   | Plan | Free |

5. **配置环境变量**
   
   在 "Environment" 部分添加：
   
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
   | PYTHON_VERSION | Python版本 | 否（默认3.11） |

6. **创建服务**
   
   点击 "Create Web Service" 开始部署

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
curl https://your-app.onrender.com/health
```

预期响应：
```json
{
  "status": "healthy"
}
```

### 2. API 文档

浏览器访问：
- Swagger UI: `https://your-app.onrender.com/docs`
- 自定义文档: `https://your-app.onrender.com/api-docs`

### 3. 测试接口

```bash
# 获取账户信息（需要API Key）
curl -H "X-API-Key: your_api_key" \
  "https://your-app.onrender.com/api/account?market_type=US"
```

## 常见问题

### 1. 服务休眠问题

**问题**：15分钟无请求后服务会休眠，下次请求需要等待30秒唤醒

**解决方案**：

#### 方案A：使用定时任务保持活跃（推荐）

使用外部服务定期访问你的API：

1. **UptimeRobot**（免费）
   - 访问 https://uptimerobot.com/
   - 创建 HTTP(s) 监控
   - URL: `https://your-app.onrender.com/health`
   - 监控间隔: 5分钟

2. **Cron-job.org**（免费）
   - 访问 https://cron-job.org/
   - 创建新任务
   - URL: `https://your-app.onrender.com/health`
   - 执行间隔: 每10分钟

#### 方案B：升级到付费套餐

- 付费套餐不会自动休眠
- 价格：$7/月起
- 适合生产环境

### 2. 构建失败

**问题**：部署时构建失败

**解决**：
- 检查 `requirements.txt` 是否完整
- 确保 Python 版本兼容（建议 3.9+）
- 查看构建日志获取详细错误信息
- 尝试在本地运行 `pip install -r requirements.txt` 验证依赖

### 3. 启动失败

**问题**：构建成功但服务无法启动

**解决**：
- 检查环境变量是否正确设置
- 确保 `FUTU_COOKIE` 和 `FUTU_CSRF_TOKEN` 有效
- 查看应用日志：Render Dashboard → Logs
- 确认启动命令使用了 `$PORT` 环境变量

### 4. Cookie 过期

**问题**：接口返回"未登录"错误

**解决**：
1. 重新从富途Web端获取 Cookie 和 CSRF Token
2. 在 Render Dashboard 更新环境变量
3. 保存后会自动重新部署

### 5. 端口配置问题

**问题**：应用无法正常访问

**解决**：
- Render 会自动分配端口到 `$PORT` 环境变量
- 确保启动命令使用 `$PORT`：
  ```bash
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```
- 不要硬编码端口号

### 6. 自定义域名

**问题**：想使用自己的域名

**解决**：
1. 在 Render Dashboard 找到你的服务
2. 点击 "Settings" → "Custom Domain"
3. 添加你的域名
4. 在域名提供商处添加 CNAME 记录
5. 等待 DNS 生效（通常几分钟）

## 自动部署

Render 支持自动部署：

### 配置自动部署

1. 在 Render Dashboard 找到你的服务
2. 默认已启用自动部署
3. 每次推送到 GitHub 主分支时自动部署

### 禁用自动部署

1. Settings → "Build & Deploy"
2. 关闭 "Auto-Deploy"
3. 需要手动点击 "Manual Deploy" 部署

### 部署分支

可以配置部署特定分支：

1. Settings → "Build & Deploy"
2. 修改 "Branch" 设置
3. 例如：`main`, `production`, `develop`

## 监控和日志

### 查看日志

1. 登录 Render Dashboard
2. 选择你的服务
3. 点击 "Logs" 标签
4. 实时查看应用日志

### 日志类型

- **Build Logs**: 构建过程日志
- **Deploy Logs**: 部署过程日志
- **Runtime Logs**: 应用运行日志

### 监控指标

Render 提供以下监控：
- CPU 使用率
- 内存使用率
- 请求数量
- 响应时间
- 错误率

## 环境管理

### 多环境部署

可以为不同环境创建多个服务：

1. **开发环境**
   - Branch: `develop`
   - 使用测试 Cookie

2. **生产环境**
   - Branch: `main`
   - 使用生产 Cookie

### 环境变量管理

1. 在 Dashboard 中管理环境变量
2. 支持加密存储
3. 修改后自动重新部署

## 性能优化

### 1. 使用持久化磁盘（付费功能）

```yaml
services:
  - type: web
    name: futu-trading-api
    disk:
      name: data
      mountPath: /data
      sizeGB: 1
```

### 2. 配置健康检查

```yaml
services:
  - type: web
    name: futu-trading-api
    healthCheckPath: /health
```

### 3. 设置资源限制

付费套餐可以配置：
- CPU 核心数
- 内存大小
- 并发连接数

## 安全建议

### 1. 设置强 API Key

```bash
# 生成随机 API Key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

在 Render 环境变量中设置生成的 Key。

### 2. 定期更新 Cookie

- Cookie 会过期，建议每周检查
- 设置日历提醒定期更新

### 3. 使用环境变量

- 不要在代码中硬编码敏感信息
- 所有密钥都通过环境变量配置

### 4. 启用 HTTPS

- Render 默认提供免费 HTTPS
- 确保所有请求都使用 HTTPS

### 5. 限制访问

如果只在特定场景使用：
- 设置强 API Key
- 考虑使用 IP 白名单（需要自己实现）

## 成本说明

### 免费套餐

- ✅ 750小时/月运行时间
- ✅ 100GB 带宽/月
- ✅ 自动 HTTPS
- ⚠️ 15分钟无请求后休眠

### 付费套餐

| 套餐 | 价格 | 特点 |
|------|------|------|
| Starter | $7/月 | 不休眠，512MB RAM |
| Standard | $25/月 | 2GB RAM，更好性能 |
| Pro | $85/月 | 4GB RAM，高性能 |

### 选择建议

- **个人测试**：免费套餐 + UptimeRobot 保活
- **小型项目**：Starter 套餐
- **生产环境**：Standard 或 Pro 套餐

## 迁移和备份

### 导出配置

Render 配置已保存在 `render.yaml` 中，可以：
1. 提交到 Git 仓库
2. 随时重新部署
3. 迁移到其他账号

### 数据备份

如果使用持久化磁盘：
1. 定期下载数据
2. 使用 Render 的快照功能（付费）

## 故障排查

### 查看详细日志

```bash
# 使用 Render CLI
render logs -s your-service-name -f
```

### 常见错误

1. **Port already in use**
   - 确保使用 `$PORT` 环境变量

2. **Module not found**
   - 检查 `requirements.txt`
   - 确认依赖版本兼容

3. **Connection timeout**
   - 检查 Cookie 是否有效
   - 确认网络连接正常

## 技术支持

- Render 文档: https://render.com/docs
- Render 社区: https://community.render.com/
- 项目 Issues: https://github.com/BSTester/futu-paper-trade-api/issues

## 总结

使用 Render 部署富途模拟交易API的优势：

1. ✅ 完全免费（免费套餐）
2. ✅ 一键部署，配置简单
3. ✅ 自动 HTTPS，安全可靠
4. ✅ 自动部署，开发便捷
5. ✅ 实时日志，便于调试
6. ⚠️ 免费套餐会休眠（可用保活服务解决）

**适合场景**：
- 个人项目和测试
- 低频使用的API服务
- 预算有限的小型项目

现在就开始部署吧！🚀
