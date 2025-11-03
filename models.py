"""数据模型"""
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class MarketType(str, Enum):
    """市场类型"""
    US = "US"  # 美股
    HK = "HK"  # 港股
    CN = "CN"  # A股


class OrderSide(str, Enum):
    """订单方向"""
    BUY = "BUY"    # 买入
    SELL = "SELL"  # 卖出


class OrderType(str, Enum):
    """订单类型"""
    LIMIT = "LIMIT"    # 限价单
    MARKET = "MARKET"  # 市价单


class SecurityType(str, Enum):
    """证券类型"""
    STOCK = "STOCK"  # 股票
    ETF = "ETF"      # ETF
    OPTION = "OPTION"  # 期权


class AccountInfo(BaseModel):
    """账户信息"""
    account_id: str = Field(..., description="账户ID")
    net_asset: float = Field(..., description="资产净值")
    cash: float = Field(..., description="现金")
    market_value: float = Field(..., description="持仓市值")
    buying_power: float = Field(..., description="最大购买力")
    profit_loss: float = Field(..., description="持仓盈亏")
    profit_loss_ratio: float = Field(..., description="持仓盈亏比例")
    today_profit_loss: float = Field(..., description="今日盈亏")
    today_profit_loss_ratio: float = Field(..., description="今日盈亏比例")
    margin: float = Field(..., description="维持保证金")
    available_funds: float = Field(..., description="剩余流动性")


class Position(BaseModel):
    """持仓信息"""
    security_id: str = Field(..., description="证券ID")
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    market_type: str = Field(..., description="市场类型")
    quantity: int = Field(..., description="持仓数量")
    available_quantity: int = Field(..., description="可卖数量")
    cost_price: float = Field(..., description="成本价")
    current_price: float = Field(..., description="当前价")
    market_value: float = Field(..., description="市值")
    profit_loss: float = Field(..., description="盈亏金额")
    profit_loss_ratio: float = Field(..., description="盈亏比例")


class StockQuote(BaseModel):
    """股票行情"""
    security_id: str = Field(..., description="证券ID")
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    current_price: float = Field(..., description="当前价")
    change: float = Field(..., description="涨跌额")
    change_ratio: float = Field(..., description="涨跌幅")
    open_price: Optional[float] = Field(None, description="开盘价（可能为空）")
    high_price: Optional[float] = Field(None, description="最高价（可能为空）")
    low_price: Optional[float] = Field(None, description="最低价（可能为空）")
    volume: Optional[int] = Field(None, description="成交量（可能为空）")


class TradeRequest(BaseModel):
    """交易请求"""
    stock_code: str = Field(..., description="股票代码，如 NVDA, 00700, 600519")
    side: OrderSide = Field(..., description="交易方向: BUY/SELL")
    order_type: OrderType = Field(OrderType.LIMIT, description="订单类型: LIMIT/MARKET")
    price: Optional[float] = Field(None, description="价格（限价单必填）")
    quantity: int = Field(..., description="数量", gt=0)


class TradeResponse(BaseModel):
    """交易响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    order_id: Optional[str] = Field(None, description="订单ID")
    data: Optional[dict] = Field(None, description="详细数据")


class SearchStockRequest(BaseModel):
    """搜索股票请求"""
    keyword: str = Field(..., description="股票代码或名称")
    market_type: Optional[MarketType] = Field(None, description="市场类型")


class StockSearchResult(BaseModel):
    """股票搜索结果"""
    security_id: str = Field(..., description="证券ID")
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    market_type: str = Field(..., description="市场类型")
    security_type: str = Field(..., description="证券类型")


class CancelOrderRequest(BaseModel):
    """撤单请求"""
    order_id: str = Field(..., description="订单ID")
    stock_code: str = Field(..., description="股票代码（用于自动判断市场类型）")
