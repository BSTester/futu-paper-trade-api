"""富途模拟交易API服务主程序"""
from fastapi import FastAPI, HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict, Any
import os
from futu_client import FutuClient
from models import (
    AccountInfo, Position, StockQuote, TradeRequest, 
    TradeResponse, SearchStockRequest, StockSearchResult,
    CancelOrderRequest
)
from config import API_HOST, API_PORT, API_KEY


def convert_to_csv_text(data: Dict[str, Any]) -> str:
    """
    将技术分析数据转换为CSV文本格式
    
    Args:
        data: 技术分析数据字典
        
    Returns:
        CSV格式的字符串
    """
    if not data:
        return ""
    
    lines = []
    
    # 获取所有指标名称（从第一条数据中）
    first_date = next(iter(data.keys()))
    indicator_names = list(data[first_date].keys())
    
    # 添加CSV表头
    header = ["Date"] + indicator_names
    lines.append(",".join(header))
    
    # 添加数据行
    for date, values in data.items():
        row = [date] + [values.get(name, "") for name in indicator_names]
        lines.append(",".join(str(v) for v in row))
    
    return "\n".join(lines)


def convert_kline_to_csv_text(data: List[Dict[str, Any]]) -> str:
    """
    将K线数据转换为CSV文本格式
    
    Args:
        data: K线数据列表
        
    Returns:
        CSV格式的字符串
    """
    if not data:
        return ""
    
    lines = []
    
    # 添加CSV表头
    header = ["datetime", "time", "open", "high", "low", "close", "volume"]
    lines.append(",".join(header))
    
    # 添加数据行
    for item in data:
        row = [
            item.get("datetime", ""),
            str(item.get("time", "")),
            str(item.get("open", "")),
            str(item.get("high", "")),
            str(item.get("low", "")),
            str(item.get("close", "")),
            str(item.get("volume", ""))
        ]
        lines.append(",".join(row))
    
    return "\n".join(lines)

app = FastAPI(
    title="富途模拟交易API",
    description="支持美股、港股、A股的模拟交易API服务",
    version="1.0.0",
    # 配置文档URL
    docs_url="/docs",  # Swagger UI（使用默认CDN）
    redoc_url=None,  # 禁用 ReDoc（避免CDN访问问题）
    openapi_url="/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化富途客户端
futu_client = FutuClient()

# API Key 校验
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """验证API Key"""
    # 如果未配置API_KEY，则不进行校验
    if not API_KEY:
        return True
    
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key"
        )
    return True


@app.get("/", tags=["系统"])
async def root():
    """API根路径（无需API Key）"""
    return {
        "name": "富途模拟交易API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "api_docs": "/api-docs",
        "openapi": "/openapi.json",
        "auth": "API Key required" if API_KEY else "No authentication"
    }


@app.get("/api-docs", response_class=HTMLResponse, tags=["系统"])
async def api_docs():
    """自定义API文档页面（使用国内CDN）"""
    html_file = os.path.join(os.path.dirname(__file__), "static", "docs.html")
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return """
        <html>
        <head><title>API文档</title></head>
        <body>
            <h1>富途模拟交易API</h1>
            <p>请访问 <a href="/docs">/docs</a> 查看Swagger UI文档</p>
        </body>
        </html>
        """


@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查（无需API Key）"""
    return {"status": "healthy"}


@app.get("/api/account", tags=["账户"])
async def get_account(market_type: str, authenticated: bool = Security(verify_api_key)):
    """
    获取账户信息
    
    - **market_type**: 市场类型（必填，US/HK/CN）
    
    返回账户的详细信息，包括资产净值、现金、持仓市值、盈亏等
    
    **注意**: 如果返回"未登录"错误，说明Cookie已过期，需要重新获取
    """
    try:
        info = await futu_client.get_account_info(market_type=market_type)
        # 检查是否有错误
        if "error" in info:
            return info
        return info
    except Exception as e:
        return {
            "error": "系统错误",
            "message": str(e),
            "code": 500
        }


@app.get("/api/positions", tags=["持仓"])
async def get_positions(market_type: str, authenticated: bool = Security(verify_api_key)):
    """
    获取持仓列表
    
    - **market_type**: 市场类型（必填，US/HK/CN）
    
    返回账户的所有股票持仓信息
    
    **注意**: 如果返回"未登录"错误，说明Cookie已过期，需要重新获取
    """
    try:
        result = await futu_client.get_positions(market_type=market_type)
        # 检查是否有错误
        if "error" in result:
            return result
        return result
    except Exception as e:
        return {
            "error": "系统错误",
            "message": str(e),
            "code": 500,
            "positions": []
        }


@app.get("/api/quote", tags=["行情"])
async def get_quote(stock_code: str, authenticated: bool = Security(verify_api_key)):
    """
    获取指定股票行情（自动判断市场类型）
    
    - **stock_code**: 股票代码，如 AAPL, 00700, 600519
    
    返回股票的实时行情数据
    
    **自动判断规则**：
    - 5位数字（如00700）→ 港股
    - 6位数字（如600519）→ A股
    - 包含字母（如AAPL）→ 美股
    
    **注意**: 返回的字段中，open_price、high_price、low_price、volume 只在有值时才会出现
    """
    try:
        # 自动判断市场类型
        market_type = futu_client._detect_market_type(stock_code)
        
        # 搜索股票获取security_id
        stocks = await futu_client.search_stock(stock_code, market_type)
        if not stocks:
            raise HTTPException(status_code=404, detail=f"未找到股票: {stock_code}")
        
        security_id = stocks[0].security_id
        quotes = await futu_client.get_stock_quote([security_id], market_type)
        return quotes
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行情失败: {str(e)}")


@app.post("/api/trade", response_model=TradeResponse, tags=["交易"])
async def trade(trade_request: TradeRequest, authenticated: bool = Security(verify_api_key)):
    """
    交易接口（买入/卖出）- 使用JSON body传递参数
    
    请求体参数：
    - **stock_code**: 股票代码（必填，自动判断市场类型）
      - 美股: AAPL, TSLA, NVDA
      - 港股: 00700, 09988
      - A股: 600519, 000001
    - **side**: 交易方向（必填，BUY=买入, SELL=卖出）
    - **quantity**: 数量（必填）
    - **price**: 价格（限价单必填，市价单可选）
    - **order_type**: 订单类型（LIMIT=限价单, MARKET=市价单，默认LIMIT）
    
    **自动判断规则**：
    - 5位数字（如00700）→ 港股
    - 6位数字（如600519, 688xxx）→ A股
    - 包含字母（如AAPL）→ 美股
    
    **示例 - 买入**:
    ```json
    {
      "stock_code": "AAPL",
      "side": "BUY",
      "quantity": 10,
      "price": 180.50,
      "order_type": "LIMIT"
    }
    ```
    
    **示例 - 卖出**:
    ```json
    {
      "stock_code": "AAPL",
      "side": "SELL",
      "quantity": 10,
      "price": 185.00,
      "order_type": "LIMIT"
    }
    ```
    """
    try:
        response = await futu_client.place_order(trade_request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"交易失败: {str(e)}")


@app.post("/api/cancel", response_model=TradeResponse, tags=["交易"])
async def cancel(request: CancelOrderRequest, authenticated: bool = Security(verify_api_key)):
    """
    撤单接口 - 使用JSON body传递参数
    
    请求体参数：
    - **order_id**: 订单ID（必填）
    - **stock_code**: 股票代码（必填，用于自动判断市场类型）
    
    **自动判断规则**：
    - 5位数字（如00700）→ 港股
    - 6位数字（如600519）→ A股
    - 包含字母（如AAPL）→ 美股
    
    **示例**:
    ```json
    {
      "order_id": "123456789",
      "stock_code": "AAPL"
    }
    ```
    """
    try:
        response = await futu_client.cancel_order(
            request.order_id, 
            request.stock_code
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"撤单失败: {str(e)}")


@app.get("/api/orders", tags=["交易"])
async def get_orders(market_type: str, filter_status: int = 0, authenticated: bool = Security(verify_api_key)):
    """
    查询订单
    
    - **market_type**: 市场类型（必填，US/HK/CN）
    - **filter_status**: 过滤状态（可选）
      - 0: 全部订单（默认）
      - 1: 已成交
      - 2: 等待成交
      - 3: 已撤单
    
    **示例**:
    ```
    GET /api/orders?market_type=US
    GET /api/orders?market_type=US&filter_status=1
    ```
    """
    try:
        orders = await futu_client.get_order_history(
            market_type=market_type,
            filter_status=filter_status
        )
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取订单失败: {str(e)}")


@app.get("/api/hot-news", tags=["资讯"])
async def get_hot_news(lang: str = "zh-cn", authenticated: bool = Security(verify_api_key)):
    """
    获取热门新闻
    
    - **lang**: 语言（可选，zh-cn/zh-hk/en-us，默认zh-cn）
    
    返回热门股票新闻列表
    
    **示例**:
    ```
    GET /api/hot-news
    GET /api/hot-news?lang=en-us
    ```
    """
    try:
        news = await futu_client.get_hot_news(lang=lang)
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门新闻失败: {str(e)}")


@app.get("/api/hot-stocks", tags=["行情"])
async def get_hot_stocks_list(market_type: str = "US", count: int = 10, authenticated: bool = Security(verify_api_key)):
    """
    获取热门股票列表
    
    - **market_type**: 市场类型（可选，US/HK/CN，默认US）
    - **count**: 返回数量（可选，默认10）
    
    返回指定市场的热门股票列表
    
    **示例**:
    ```
    GET /api/hot-stocks
    GET /api/hot-stocks?market_type=HK&count=20
    ```
    """
    try:
        stocks = await futu_client.get_hot_stocks_list(
            market_type=market_type,
            count=count
        )
        return stocks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门股票失败: {str(e)}")


@app.get("/api/technical-analysis", tags=["行情"])
async def get_technical_analysis(
    symbol: str,
    interval: str = "daily",
    indicator: str = "macd",
    format: str = "json",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    authenticated: bool = Security(verify_api_key)
):
    """
    获取技术分析指标（返回时间序列数据，自动判断市场类型）
    
    - **symbol**: 股票代码（必填）
    - **interval**: 时间间隔（可选，默认daily）
      - 分钟级: 1min, 5min, 15min, 30min, 60min
      - 日线及以上: daily, weekly, monthly, quarterly, yearly
    - **indicator**: 技术指标（可选，默认macd）
      - 可选指标：close_50_sma, close_200_sma, close_10_ema, macd, rsi, boll, atr, vwma
    - **format**: 返回格式（可选，默认json）
      - json: JSON格式
      - csv: CSV格式
    - **start_date**: 开始日期（可选，格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS）
    - **end_date**: 结束日期（可选，格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS）
    
    返回技术分析指标的时间序列数据，可用于绘制曲线图
    
    **自动判断规则**：
    - 5位数字（如00700）→ 港股
    - 6位数字（如600519）→ A股
    - 包含字母（如AAPL）→ 美股
    
    **特殊指标说明**：
    - **macd**: 返回 MACD, MACD_Signal, MACD_Hist 三个值
    - **boll**: 返回 Boll_Upper, Boll_Middle, Boll_Lower 三个值
    - 其他指标返回单个值
    
    **日期范围说明**：
    - 如果不指定日期范围，返回所有可用数据
    - **周K线特殊处理**：如果不指定日期范围，默认返回最近1个月的数据
    - 如果指定日期范围，只返回该范围内的数据
    - 日期格式支持：YYYY-MM-DD（如 2025-01-01）或 YYYY-MM-DD HH:MM:SS（如 2025-01-01 09:30:00）
    
    **示例**:
    ```
    GET /api/technical-analysis?symbol=AAPL
    GET /api/technical-analysis?symbol=AAPL&interval=daily&indicator=macd
    GET /api/technical-analysis?symbol=AAPL&interval=5min&indicator=rsi
    GET /api/technical-analysis?symbol=AAPL&interval=60min&indicator=boll
    GET /api/technical-analysis?symbol=AAPL&format=csv
    GET /api/technical-analysis?symbol=AAPL&start_date=2025-01-01&end_date=2025-10-31
    GET /api/technical-analysis?symbol=AAPL&interval=daily&indicator=macd&start_date=2025-01-01
    GET /api/technical-analysis?symbol=AAPL&interval=5min&start_date=2025-11-01 09:30:00&end_date=2025-11-01 16:00:00
    ```
    
    **CSV格式返回示例**:
    ```json
    {
      "meta": {
        "symbol": "AAPL",
        "stock_name": "苹果",
        "market_type": "US",
        "interval": "daily",
        "indicator": "macd",
        "data_points": 200
      },
      "data": "Date,MACD,MACD_Signal,MACD_Hist\n2025-10-31,9.4638,6.9336,2.5302\n2025-10-30,8.7040,6.3011,2.4029",
      "format": "csv"
    }
    ```
    """
    try:
        # 验证格式参数
        format_lower = format.lower()
        if format_lower not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail=f"不支持的格式: {format}，支持的格式: json, csv")
        
        # 获取技术分析
        result = await futu_client.get_technical_analysis(
            symbol=symbol,
            interval=interval,
            indicator=indicator,
            start_date=start_date,
            end_date=end_date
        )
        
        # 检查是否有错误
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        # 根据格式返回数据
        if format_lower == "csv":
            # 转换data字段为CSV文本
            csv_content = convert_to_csv_text(result.get("data", {}))
            
            # 返回JSON，但data字段为CSV文本
            return {
                "meta": result.get("meta", {}),
                "data": csv_content,
                "format": "csv"
            }
        else:
            # 返回JSON格式
            return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取技术分析失败: {str(e)}")


@app.get("/api/kline", tags=["行情"])
async def get_kline(
    symbol: str,
    interval: str = "daily",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "json",
    authenticated: bool = Security(verify_api_key)
):
    """
    获取K线数据（自动判断市场类型）
    
    - **symbol**: 股票代码（必填）
    - **interval**: 时间间隔（可选，默认daily）
      - 分钟级: 1min, 5min, 15min, 30min, 60min
      - 日线及以上: daily, weekly, monthly, quarterly, yearly
      - 注意：周K及以下时间间隔不指定日期时默认返回最近1个月数据（基于数据最新日期）
    - **start_date**: 开始日期（可选，格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS）
    - **end_date**: 结束日期（可选，格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS）
    - **format**: 返回格式（可选，默认json）
      - json: JSON格式
      - csv: CSV格式
    
    返回股票的K线OHLCV数据（时间已自动转换为市场本地时间）
    
    **自动判断规则**：
    - 5位数字（如00700）→ 港股
    - 6位数字（如600519）→ A股
    - 包含字母（如AAPL）→ 美股
    
    **时区说明**：
    - 美股（US）：美国东部时间 EST/EDT (UTC-5/-4，自动处理夏令时)
    - 港股（HK）：香港时间 HKT (UTC+8)
    - A股（CN）：中国标准时间 CST (UTC+8)
    
    **日期范围说明**：
    - 如果不指定日期范围，返回所有可用数据
    - **周K线特殊处理**：如果不指定日期范围，默认返回最近1个月的数据
    - 如果指定日期范围，只返回该范围内的数据
    - 日期格式支持：YYYY-MM-DD（如 2025-01-01）或 YYYY-MM-DD HH:MM:SS（如 2025-01-01 09:30:00）
    
    **示例**:
    ```
    GET /api/kline?symbol=AAPL
    GET /api/kline?symbol=AAPL&interval=daily
    GET /api/kline?symbol=AAPL&interval=5min
    GET /api/kline?symbol=00700&interval=weekly
    GET /api/kline?symbol=AAPL&start_date=2025-10-01&end_date=2025-10-31
    GET /api/kline?symbol=AAPL&interval=5min&start_date=2025-11-01 09:30:00&end_date=2025-11-01 16:00:00
    GET /api/kline?symbol=AAPL&interval=daily&format=csv
    ```
    
    **CSV格式返回示例**:
    ```json
    {
      "meta": {
        "symbol": "AAPL",
        "stock_name": "苹果",
        "market_type": "US",
        "interval": "daily",
        "data_points": 200
      },
      "data": "datetime,time,open,high,low,close,volume\n2025-10-31,1730419200,268.50,271.20,267.80,270.37,45678900\n...",
      "format": "csv"
    }
    ```
    """
    try:
        # 验证格式参数
        format_lower = format.lower()
        if format_lower not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail=f"不支持的格式: {format}，支持的格式: json, csv")
        
        # 映射interval到kline_type
        interval_mapping = {
            "1min": (1, "1min"),
            "5min": (1, "5min"),
            "15min": (1, "15min"),
            "30min": (1, "30min"),
            "60min": (1, "1h"),
            "daily": (2, None),
            "weekly": (3, None),
            "monthly": (4, None),
            "yearly": (5, None),
            "quarterly": (11, None)
        }
        
        if interval not in interval_mapping:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的时间间隔: {interval}，支持的间隔: {list(interval_mapping.keys())}"
            )
        
        kline_type, resample_interval = interval_mapping[interval]
        
        # 记录是否需要应用默认1个月限制（周K及以下时间间隔，且未指定日期范围）
        # 周K及以下包括：weekly, daily, 60min, 30min, 15min, 5min, 1min
        short_intervals = ["weekly", "daily", "60min", "30min", "15min", "5min", "1min"]
        apply_default_range = interval in short_intervals and not start_date and not end_date
        
        # 解析日期范围（如果提供）
        start_timestamp = None
        end_timestamp = None
        
        if start_date:
            from datetime import datetime
            try:
                # 清理日期字符串（处理URL编码的+号）
                start_date = start_date.strip().replace('+', ' ')
                
                if len(start_date) == 10:  # YYYY-MM-DD
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                else:  # YYYY-MM-DD HH:MM:SS
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                start_timestamp = int(start_dt.timestamp())
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"无效的开始日期格式: {start_date}，请使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS。错误: {str(e)}"
                )
        
        if end_date:
            from datetime import datetime, timedelta
            try:
                # 清理日期字符串（处理URL编码的+号）
                end_date = end_date.strip().replace('+', ' ')
                
                if len(end_date) == 10:  # YYYY-MM-DD
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                    # 如果只提供日期，设置为当天的23:59:59
                    end_dt = end_dt + timedelta(days=1) - timedelta(seconds=1)
                else:  # YYYY-MM-DD HH:MM:SS
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:MM:%S")
                end_timestamp = int(end_dt.timestamp())
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"无效的结束日期格式: {end_date}，请使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS。错误: {str(e)}"
                )
        
        # 自动判断市场类型
        market_type = futu_client._detect_market_type(symbol)
        
        # 搜索股票获取security_id
        stocks = await futu_client.search_stock(symbol, market_type)
        if not stocks:
            raise HTTPException(status_code=404, detail=f"未找到股票: {symbol}")
        
        security_id = stocks[0].security_id
        stock_name = stocks[0].stock_name
        
        # 获取K线数据
        kline_data = await futu_client.get_kline_data(
            stock_id=security_id,
            kline_type=kline_type,
            market_type=market_type
        )
        
        # 提取K线列表
        kline_list = kline_data.get("minus", {}).get("list", [])
        
        if not kline_list:
            # 尝试其他路径
            if "data" in kline_data:
                kline_list = kline_data["data"].get("list", [])
            if not kline_list and "list" in kline_data:
                kline_list = kline_data["list"]
        
        if not kline_list:
            raise HTTPException(status_code=404, detail="无K线数据")
        
        # 先转换为DataFrame进行处理
        import pandas as pd
        df_data = []
        for item in kline_list:
            # 时间
            time_val = item.get("time") or item.get("k")
            if not time_val:
                continue
            
            # 如果指定了日期范围，过滤数据
            if start_timestamp and time_val < start_timestamp:
                continue
            if end_timestamp and time_val > end_timestamp:
                continue
            
            # 价格数据 - 收盘价
            close_price = item.get("cc_price") or item.get("c")
            if close_price is None:
                price_raw = item.get("price", 0)
                close_price = price_raw / 10000 if price_raw else 0
            else:
                close_price = float(close_price)
            
            # 如果没有收盘价，跳过这条数据
            if close_price == 0:
                continue
            
            # 开盘价
            open_price = item.get("cc_open") or item.get("o")
            if open_price is None:
                open_raw = item.get("open", 0)
                open_price = open_raw / 10000 if open_raw else 0
            else:
                open_price = float(open_price)
            
            # 如果开盘价为0，使用收盘价
            if open_price == 0:
                open_price = close_price
            
            # 最高价
            high_price = item.get("cc_high") or item.get("h")
            if high_price is None:
                high_raw = item.get("high", 0)
                high_price = high_raw / 10000 if high_raw else 0
            else:
                high_price = float(high_price)
            
            # 如果最高价为0，使用收盘价
            if high_price == 0:
                high_price = close_price
            
            # 最低价
            low_price = item.get("cc_low") or item.get("l")
            if low_price is None:
                low_raw = item.get("low", 0)
                low_price = low_raw / 10000 if low_raw else 0
            else:
                low_price = float(low_price)
            
            # 如果最低价为0，使用收盘价
            if low_price == 0:
                low_price = close_price
            
            volume = item.get("volume") or item.get("v", 0)
            
            df_data.append({
                "time": time_val,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume
            })
        
        # 创建DataFrame
        df = pd.DataFrame(df_data)
        
        # 确保数据类型正确
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(int)
        
        # 过滤无效数据
        df = df[(df['close'] > 0) & (df['time'].notna())].copy()
        
        # 如果是周K及以下时间间隔且未指定日期范围，基于数据最新日期限制为最近1个月
        if apply_default_range and len(df) > 0:
            from datetime import datetime, timedelta
            # 获取数据中的最新时间戳
            latest_timestamp = df['time'].max()
            # 计算1个月前的时间戳（30天）
            one_month_ago_timestamp = latest_timestamp - (30 * 24 * 60 * 60)
            # 过滤数据
            df = df[df['time'] >= one_month_ago_timestamp].copy()
            # 记录自动设置的日期范围
            start_date = datetime.fromtimestamp(one_month_ago_timestamp).strftime("%Y-%m-%d")
            end_date = datetime.fromtimestamp(latest_timestamp).strftime("%Y-%m-%d")
        
        # 如果需要重采样（分钟级数据）
        if resample_interval:
            from technical_indicators import resample_kline_data
            df = resample_kline_data(df, resample_interval)
        
        # 格式化输出数据
        formatted_data = []
        date_only_intervals = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        
        for _, row in df.iterrows():
            time_val = int(row['time'])
            
            # 转换时间为本地时间
            if interval in date_only_intervals:
                from datetime import datetime
                local_time = datetime.fromtimestamp(time_val).strftime('%Y-%m-%d')
            else:
                local_time = futu_client._convert_timestamp_to_local_time(time_val, market_type)
            
            formatted_data.append({
                "time": time_val,
                "datetime": local_time,
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": int(row['volume'])
            })
        
        # 根据格式返回数据
        if format_lower == "csv":
            # 转换data为CSV文本
            csv_content = convert_kline_to_csv_text(formatted_data)
            
            result = {
                "meta": {
                    "symbol": symbol,
                    "stock_name": stock_name,
                    "security_id": security_id,
                    "market_type": market_type,
                    "interval": interval,
                    "data_points": len(formatted_data)
                },
                "data": csv_content,
                "format": "csv"
            }
        else:
            # JSON格式
            result = {
                "meta": {
                    "symbol": symbol,
                    "stock_name": stock_name,
                    "security_id": security_id,
                    "market_type": market_type,
                    "interval": interval,
                    "data_points": len(formatted_data)
                },
                "data": formatted_data
            }
        
        # 如果指定了日期范围，添加到meta中
        if start_date:
            result["meta"]["requested_start_date"] = start_date
        if end_date:
            result["meta"]["requested_end_date"] = end_date
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取K线数据失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print(f"🚀 富途模拟交易API服务启动中...")
    print(f"📍 服务地址: http://{API_HOST}:{API_PORT}")
    print(f"📖 API文档: http://{API_HOST}:{API_PORT}/docs")
    uvicorn.run(app, host=API_HOST, port=API_PORT)
