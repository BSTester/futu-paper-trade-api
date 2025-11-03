# Docker 部署指南

## 快速开始

### 1. 准备环境变量

确保 `.env` 文件已配置：

```env
# 富途Cookie（必填）
FUTU_COOKIE=your_cookie_here

# 账户配置（按需配置）
ACCOUNT_ID_US=17198232
ACCOUNT_ID_HK=9393
ACCOUNT_ID_CN=12345
```

### 2. 构建并启动服务

```bash
# 构建镜像并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 访问服务

- API服务：http://localhost:8000
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

---

## Docker 命令详解

### 构建镜像

```bash
# 构建镜像
docker-compose build

# 强制重新构建（不使用缓存）
docker-compose build --no-cache
```

### 启动服务

```bash
# 启动服务（后台运行）
docker-compose up -d

# 启动服务（前台运行，查看日志）
docker-compose up

# 启动并重新构建
docker-compose up -d --build
```

### 查看状态

```bash
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs

# 实时查看日志
docker-compose logs -f

# 查看最近100行日志
docker-compose logs --tail=100
```

### 停止和删除

```bash
# 停止服务
docker-compose stop

# 停止并删除容器
docker-compose down

# 停止并删除容器、网络、镜像
docker-compose down --rmi all

# 停止并删除容器、卷
docker-compose down -v
```

### 重启服务

```bash
# 重启服务
docker-compose restart

# 重启特定服务
docker-compose restart futu-api
```

---

## 环境变量配置

### 方式1：使用 .env 文件（推荐）

在项目根目录创建 `.env` 文件：

```env
FUTU_COOKIE=your_cookie_here
ACCOUNT_ID_US=17198232
ACCOUNT_ID_HK=9393
ACCOUNT_ID_CN=12345
API_HOST=0.0.0.0
API_PORT=8000
```

### 方式2：在 docker-compose.yml 中配置

编辑 `docker-compose.yml`，在 `environment` 部分直接设置：

```yaml
environment:
  - FUTU_COOKIE=your_cookie_here
  - ACCOUNT_ID_US=17198232
```

### 方式3：使用环境变量文件

创建 `.env.docker` 文件，然后在 docker-compose.yml 中引用：

```yaml
services:
  futu-api:
    env_file:
      - .env.docker
```

---

## 端口配置

### 修改端口

编辑 `docker-compose.yml`：

```yaml
ports:
  - "9000:8000"  # 将主机的9000端口映射到容器的8000端口
```

然后访问：http://localhost:9000

---

## 数据持久化

### 挂载日志目录

编辑 `docker-compose.yml`，添加卷挂载：

```yaml
volumes:
  - ./.env:/app/.env:ro
  - ./logs:/app/logs  # 挂载日志目录
```

---

## 健康检查

容器内置健康检查，每30秒检查一次服务状态：

```bash
# 查看健康状态
docker-compose ps

# 输出示例
NAME                    STATUS
futu-paper-trade-api    Up 2 minutes (healthy)
```

---

## 故障排查

### 查看容器日志

```bash
# 查看所有日志
docker-compose logs

# 查看最近的日志
docker-compose logs --tail=50 -f
```

### 进入容器调试

```bash
# 进入容器
docker-compose exec futu-api bash

# 或使用sh（如果bash不可用）
docker-compose exec futu-api sh

# 在容器内查看进程
ps aux

# 在容器内测试API
curl http://localhost:8000/health
```

### 检查环境变量

```bash
# 查看容器的环境变量
docker-compose exec futu-api env | grep FUTU
```

### 重新构建

```bash
# 停止并删除容器
docker-compose down

# 重新构建并启动
docker-compose up -d --build
```

---

## 生产环境部署

### 1. 使用外部网络

```yaml
networks:
  futu-network:
    external: true
```

### 2. 限制资源

```yaml
services:
  futu-api:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### 3. 添加反向代理

使用 Nginx 或 Traefik 作为反向代理：

```yaml
services:
  futu-api:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.futu-api.rule=Host(`api.example.com`)"
```

---

## 更新服务

### 更新代码

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建并启动
docker-compose up -d --build

# 3. 查看日志确认启动成功
docker-compose logs -f
```

### 更新依赖

```bash
# 1. 修改 requirements.txt

# 2. 重新构建镜像
docker-compose build --no-cache

# 3. 重启服务
docker-compose up -d
```

---

## 常见问题

### Q1: 容器启动失败？
A: 检查日志：`docker-compose logs`

### Q2: 端口被占用？
A: 修改 docker-compose.yml 中的端口映射

### Q3: Cookie过期？
A: 更新 .env 文件中的 FUTU_COOKIE，然后重启：`docker-compose restart`

### Q4: 如何备份数据？
A: 
```bash
# 导出容器
docker export futu-paper-trade-api > backup.tar

# 备份.env文件
cp .env .env.backup
```

---

## 监控和日志

### 查看资源使用

```bash
# 查看容器资源使用情况
docker stats futu-paper-trade-api
```

### 日志管理

```bash
# 清理日志
docker-compose logs --no-log-prefix > logs.txt
truncate -s 0 $(docker inspect --format='{{.LogPath}}' futu-paper-trade-api)
```

---

## 安全建议

1. **不要将 .env 文件提交到 Git**
   - 已在 .gitignore 中配置

2. **使用环境变量而不是硬编码**
   - Cookie 和账户ID 都通过环境变量配置

3. **限制容器权限**
   - 容器以非root用户运行（可选配置）

4. **定期更新镜像**
   - 定期重新构建以获取安全更新

---

## 多环境部署

### 开发环境

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### 生产环境

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

创建 `docker-compose.prod.yml`：

```yaml
version: '3.8'

services:
  futu-api:
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```
