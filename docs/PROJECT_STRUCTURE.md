# 项目结构

## 📁 目录结构

```
futu-paper-trade-api/
├── 📄 核心代码文件
│   ├── main.py              # FastAPI主程序
│   ├── futu_client.py       # 富途API客户端
│   ├── models.py            # 数据模型
│   └── config.py            # 配置文件
│
├── 📄 配置文件
│   ├── .env                 # 环境变量（包含Cookie和账户ID）
│   ├── .env.example         # 环境变量示例
│   ├── requirements.txt     # Python依赖
│   └── .gitignore          # Git忽略文件
│
├── 📄 启动脚本
│   ├── setup.bat           # 环境安装脚本
│   ├── start.bat           # 快速启动脚本
│   └── run.bat             # 运行脚本
│
├── 📄 项目文档
│   ├── README.md           # 项目说明
│   └── PROJECT_STRUCTURE.md # 本文件
│
├── 📁 docs/                # 文档中心（47个文档）
│   ├── README.md           # 文档索引
│   ├── API_REFERENCE.md    # API接口参考
│   ├── FIELD_MAPPING.md    # 字段映射文档
│   ├── CHANGELOG.md        # 更新日志
│   ├── SUMMARY.md          # 项目总结
│   └── ...                 # 其他文档
│
├── 📁 static/              # 静态文件
│   └── docs.html           # 自定义API文档页面
│
└── 📁 __pycache__/         # Python缓存文件
```

---

## 📄 核心文件说明

### 代码文件

| 文件 | 说明 | 行数 |
|------|------|------|
| `main.py` | FastAPI主程序，定义所有API路由 | ~350行 |
| `futu_client.py` | 富途API客户端，封装所有富途接口调用 | ~850行 |
| `models.py` | Pydantic数据模型，定义请求和响应格式 | ~120行 |
| `config.py` | 配置管理，读取环境变量 | ~50行 |

### 配置文件

| 文件 | 说明 |
|------|------|
| `.env` | 环境变量配置（Cookie、账户ID等） |
| `.env.example` | 环境变量配置示例 |
| `requirements.txt` | Python依赖包列表 |

### 启动脚本

| 文件 | 说明 |
|------|------|
| `setup.bat` | 一键安装Python依赖 |
| `start.bat` | 一键启动API服务 |
| `run.bat` | 运行API服务 |

---

## 📚 文档分类

### API文档（必读）
- `API_REFERENCE.md` - 完整的API接口参考
- `API_CHECK_SUMMARY.md` - API接口检查总结
- `FIELD_MAPPING.md` - 字段映射文档

### 快速开始
- `快速开始指南.md` - 新手入门
- `如何获取Cookie.md` - Cookie获取教程
- `安装指南.md` - 详细安装步骤

### 更新记录
- `CHANGELOG.md` - 更新日志
- `SUMMARY.md` - 项目总结
- `API_UPDATE.md` - API更新说明

### 技术文档
- `富途API响应分析.md` - API响应分析
- `Playwright抓包结果.md` - 抓包结果
- `问题总结.md` - 问题排查

---

## 🚀 快速开始

### 1. 安装依赖
```bash
setup.bat
```

### 2. 配置环境变量
编辑 `.env` 文件，填入：
- `FUTU_COOKIE` - 富途Cookie
- `ACCOUNT_ID_US` - 美股账户ID
- `ACCOUNT_ID_HK` - 港股账户ID
- `ACCOUNT_ID_CN` - A股账户ID

### 3. 启动服务
```bash
start.bat
```

### 4. 访问文档
```
http://localhost:8000/docs
```

---

## 📖 文档查找

### 查看所有文档
访问 `docs/README.md` 查看完整的文档索引

### 在线API文档
访问 `http://localhost:8000/docs` 使用Swagger UI

---

## 🎯 项目特点

✅ **9个API接口**：
- 7个GET接口（查询数据）
- 2个POST接口（交易操作）

✅ **支持3个市场**：
- 美股（US）
- 港股（HK）
- A股（CN）

✅ **完整功能**：
- 账户信息查询
- 持仓列表查询
- 股票行情查询
- 下单交易
- 撤单操作
- 订单历史查询
- 热门新闻
- 热门股票
- K线数据（含北京时间转换）

✅ **规范设计**：
- RESTful API设计
- GET使用Query参数
- POST使用JSON Body
- 完整的错误处理
- 详细的API文档

---

## 📝 维护说明

### 代码文件
- 核心代码在项目根目录
- 不要修改 `__pycache__` 文件夹

### 文档文件
- 所有文档在 `docs/` 文件夹
- 查看 `docs/README.md` 了解文档结构

### 配置文件
- `.env` 包含敏感信息，不要提交到Git
- `.env.example` 是配置模板，可以提交

---

## 🔗 相关链接

- **项目文档**: `docs/README.md`
- **API文档**: `http://localhost:8000/docs`
- **快速开始**: `docs/快速开始指南.md`
- **问题排查**: `docs/故障排除.md`
