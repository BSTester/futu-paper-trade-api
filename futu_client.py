"""富途API客户端"""
import httpx
import pandas as pd
from typing import Optional, List, Dict, Any
from config import (
    FUTU_COOKIE, FUTU_CSRF_TOKEN, FUTU_BASE_URL, FUTU_MATCH_URL,
    MARKET_TYPE, ORDER_SIDE, ORDER_TYPE, PERIOD_TYPE, SECURITY_TYPE,
    ACCOUNT_MAPPING
)
from models import (
    AccountInfo, Position, StockQuote, TradeRequest, 
    TradeResponse, StockSearchResult
)
from technical_indicators import calculate_indicators_series, SUPPORTED_INDICATORS
from kline_cache import get_kline_cache


class FutuClient:
    """富途API客户端"""
    
    def __init__(self, cookie: str = None, csrf_token: str = None):
        self.cookie = cookie or FUTU_COOKIE
        self.csrf_token = csrf_token or FUTU_CSRF_TOKEN
        # 使用从浏览器捕获的完整请求头（基础请求头）
        self.base_headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Cookie": self.cookie,
            "Host": "www.futunn.com",
            "Pragma": "no-cache",
            "Priority": "u=1, i",
            "Referer": "https://www.futunn.com/paper-trade",
            "Sec-Ch-Ua": '"Chromium";v="141", "Not A;Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            # 富途API必需的固定请求头
            "x-paper-trading-location": "CN",
            "x-futu-client-lang": "0",
            "futu-x-csrf-token": self.csrf_token
        }
        # 使用环境变量配置的账户映射
        self._account_mapping = ACCOUNT_MAPPING
    
    def _normalize_stock_code(self, stock_code: str) -> str:
        """
        标准化股票代码，去除市场后缀（用于请求富途接口）
        
        Args:
            stock_code: 原始股票代码（可能包含后缀，如 00700.HK, 600519.SH）
            
        Returns:
            纯数字或字母的股票代码（如 00700, 600519, AAPL）
        """
        stock_code = stock_code.upper().strip()
        
        # 如果包含点号，去除后缀
        if '.' in stock_code:
            code_part, _ = stock_code.split('.', 1)
            return code_part
        
        return stock_code
    
    def _detect_market_type(self, stock_code: str) -> str:
        """
        根据股票代码自动判断市场类型（更严谨的判断逻辑）
        
        Args:
            stock_code: 股票代码
            
        Returns:
            市场类型 (US/HK/CN)
        """
        stock_code = stock_code.upper().strip()
        
        # 检查是否有明确的后缀
        if '.' in stock_code:
            code_part, suffix = stock_code.split('.', 1)
            suffix = suffix.upper()
            
            # 根据后缀直接判断
            if suffix in ['HK', 'HKEX']:
                return "HK"
            elif suffix in ['US', 'NASDAQ', 'NYSE']:
                return "US"
            elif suffix in ['CN', 'SH', 'SZ', 'SS']:
                return "CN"
        else:
            code_part = stock_code
        
        # 港股：5位数字
        # 规则：00001-99999
        # 常见：00001-09999（主板）, 80000-89999（GEM）
        if code_part.isdigit() and len(code_part) == 5:
            return "HK"
        
        # A股：6位数字
        # 上海：60xxxx（主板）, 688xxx（科创板）, 689xxx（科创板）
        # 深圳：00xxxx（主板）, 30xxxx（创业板）, 002xxx（中小板）
        if code_part.isdigit() and len(code_part) == 6:
            first_two = code_part[:2]
            first_three = code_part[:3]
            # 验证是否符合A股编码规则
            if first_two in ['60', '68', '00', '30'] or first_three in ['688', '689', '002']:
                return "CN"
        
        # 美股：包含字母
        # 规则：1-5个字母，可能包含点号（如 BRK.B）
        # 常见：AAPL, TSLA, MSFT, BRK.B, BRK.A
        if any(c.isalpha() for c in code_part):
            # 验证是否符合美股代码规则（1-5个字母）
            letters_only = ''.join(c for c in code_part if c.isalpha())
            if 1 <= len(letters_only) <= 5:
                return "US"
        
        # 默认返回美股（兜底）
        return "US"
        
    async def _request(self, method: str, url: str, api_method: str = None, **kwargs) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法 (GET/POST)
            url: 请求URL
            api_method: 富途API方法名（用于设置x-paper-trading-method请求头）
            **kwargs: 其他请求参数
        """
        # 构建请求头（每次请求都复制基础请求头）
        headers = self.base_headers.copy()
        
        # 根据URL动态设置Host请求头
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        headers["Host"] = parsed_url.netloc
        
        # 如果提供了api_method，设置x-paper-trading-method请求头
        if api_method:
            headers["x-paper-trading-method"] = api_method
        # 如果没有提供api_method，尝试从params中的_m参数获取
        elif 'params' in kwargs and '_m' in kwargs['params']:
            headers["x-paper-trading-method"] = kwargs['params']['_m']
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method, url, headers=headers, timeout=30.0, **kwargs
            )
            response.raise_for_status()
            
            content = response.text
            if not content:
                raise ValueError(f"API返回空响应: {url}")
            
            return response.json()
    
    async def get_account_list(self) -> List[Dict[str, Any]]:
        """
        获取账户列表
        
        返回格式：
        [
            {
                "account_id": "9393",
                "account_name": "港股模拟账户",
                "market_type": "HK",
                "currency": "HKD"
            },
            ...
        ]
        """
        url = f"{FUTU_BASE_URL}/paper-trade/common-api"
        params = {
            "_m": "getAccountList",
            "attribute_market": 1
        }
        data = await self._request("GET", url, params=params)
        
        # 处理不同的响应格式
        if isinstance(data, list):
            # 如果直接返回列表
            account_list = data
        elif isinstance(data, dict):
            # 如果返回字典，尝试获取account_list
            account_list = data.get("data", {}).get("account_list", [])
            if not account_list and "account_list" in data:
                account_list = data.get("account_list", [])
        else:
            account_list = []
        
        accounts = []
        for acc in account_list:
            market_type = self._parse_market_type(acc.get("attribute_market", 0))
            account_info = {
                "account_id": str(acc.get("account_id", "")),
                "account_name": acc.get("account_name", ""),
                "market_type": market_type,
                "currency": acc.get("currency", ""),
                "attribute_market": acc.get("attribute_market", 0)
            }
            accounts.append(account_info)
        
        return accounts
    
    def _parse_market_type(self, attribute_market: int) -> str:
        """
        解析市场类型
        
        attribute_market映射：
        1 = 港股 (HK)
        2 = 美股 (US)
        3 = A股 (CN)
        4 = 日股 (JP)
        """
        market_map = {
            1: "HK",  # 港股
            2: "US",  # 美股
            3: "CN",  # A股（沪深）
            4: "JP",  # 日股
        }
        return market_map.get(attribute_market, "")
    
    def get_account_id_by_market(self, market_type: str) -> Optional[str]:
        """
        根据市场类型获取对应的账户ID（从环境变量配置）
        
        Args:
            market_type: 市场类型 (US/HK/CN/JP)
            
        Returns:
            账户ID，如果未找到则返回None
        """
        return self._account_mapping.get(market_type)
    
    async def get_account_info(self, account_id: str = None, market_type: str = None) -> Dict[str, Any]:
        """
        获取账户详情
        
        Args:
            account_id: 账户ID（可选，如果不提供则根据market_type自动匹配）
            market_type: 市场类型（必须提供，US/HK/CN）
            
        Returns:
            账户信息字典，如果未登录则返回错误信息
        """
        # 如果没有提供account_id，根据market_type自动获取
        if not account_id:
            if not market_type:
                return {"error": "必须提供market_type参数来指定市场类型", "code": 400}
            account_id = self.get_account_id_by_market(market_type)
            if not account_id:
                return {"error": f"未找到{market_type}市场的模拟账户，请在.env文件中配置ACCOUNT_ID_{market_type}", "code": 404}
        
        url = f"{FUTU_BASE_URL}/paper-trade/common-api"
        params = {
            "_m": "getAccountDetail",
            "account_id": account_id
        }
        data = await self._request("GET", url, params=params)
        
        # 检查是否未登录
        if isinstance(data, dict) and data.get("code") == 1002:
            return {
                "error": "未登录",
                "message": data.get("message", "你还未登录"),
                "code": 1002,
                "hint": "Cookie已过期，请从浏览器重新获取Cookie并更新到.env文件中"
            }
        
        # 处理不同的响应格式
        if isinstance(data, dict):
            account_data = data.get("data", {})
            if not account_data or not isinstance(account_data, dict):
                return {
                    "error": "获取账户信息失败",
                    "message": data.get("message", "未知错误"),
                    "code": data.get("code", -1)
                }
        else:
            account_data = {}
        
        # 富途API字段映射
        # balance -> cash (现金/余额)
        # power -> buying_power (购买力)
        # asset_value -> net_asset (资产净值)
        # stock_value -> market_value (持仓市值)
        # profit -> profit_loss (盈亏)
        # profit_ratio -> profit_loss_ratio (盈亏比例)
        # today_profit -> today_profit_loss (今日盈亏)
        # today_profit_ratio -> today_profit_loss_ratio (今日盈亏比例)
        # maintenance_margin -> margin (维持保证金)
        # excess_liquidity -> available_funds (可用资金)
        
        return {
            "account_id": account_id,
            "net_asset": float(account_data.get("asset_value", 0)),
            "cash": float(account_data.get("balance", 0)),
            "market_value": float(account_data.get("stock_value", 0)),
            "buying_power": float(account_data.get("power", 0)),
            "profit_loss": float(account_data.get("profit", 0)),
            "profit_loss_ratio": float(account_data.get("profit_ratio", 0)),
            "today_profit_loss": float(account_data.get("today_profit", 0)),
            "today_profit_loss_ratio": float(account_data.get("today_profit_ratio", 0)),
            "margin": float(account_data.get("maintenance_margin", 0)),
            "available_funds": float(account_data.get("excess_liquidity", 0))
        }
    
    async def get_positions(self, account_id: str = None, market_type: str = None) -> Dict[str, Any]:
        """
        获取持仓列表
        
        Args:
            account_id: 账户ID（可选，如果不提供则根据market_type自动匹配）
            market_type: 市场类型（必须提供，US/HK/CN）
            
        Returns:
            持仓列表或错误信息
        """
        # 如果没有提供account_id，根据market_type自动获取
        if not account_id:
            if not market_type:
                return {"error": "必须提供market_type参数来指定市场类型", "code": 400, "positions": []}
            account_id = self.get_account_id_by_market(market_type)
            if not account_id:
                return {"error": f"未找到{market_type}市场的模拟账户，请在.env文件中配置ACCOUNT_ID_{market_type}", "code": 404, "positions": []}
        
        url = f"{FUTU_BASE_URL}/paper-trade/common-api"
        
        # 根据市场类型选择不同的接口
        # 美股使用 getIntegratedPosList，港股和A股使用 getPosList
        if market_type == "US":
            api_method = "getIntegratedPosList"
        else:
            # HK 或 CN 市场
            api_method = "getPosList"
        
        params = {
            "_m": api_method,
            "account_id": account_id
        }
        data = await self._request("GET", url, api_method=api_method, params=params)
        
        # 检查是否未登录
        if isinstance(data, dict) and data.get("code") == 1002:
            return {
                "error": "未登录",
                "message": data.get("message", "你还未登录"),
                "code": 1002,
                "hint": "Cookie已过期，请从浏览器重新获取Cookie并更新到.env文件中",
                "positions": []
            }
        
        # 处理响应数据
        positions_data = data.get("data", {})
        if not isinstance(positions_data, dict):
            return {"positions": [], "count": 0}
        
        # 格式化持仓数据
        positions = []
        
        if market_type == "US":
            # 美股接口返回格式: {"code":0,"message":"成功","data":{"positions":[{"positions":[...]}],"pos_count":"1"}}
            # 注意：data.positions 是一个数组，每个元素包含一个 positions 数组
            outer_positions = positions_data.get("positions", [])
            
            # 提取所有持仓数据（从嵌套结构中）
            all_positions = []
            for outer_pos in outer_positions:
                if isinstance(outer_pos, dict) and "positions" in outer_pos:
                    inner_positions = outer_pos.get("positions", [])
                    all_positions.extend(inner_positions)
            
            # 格式化持仓数据
            for pos in all_positions:
                quantity = int(pos.get("quantity", 0))
                
                positions.append({
                    "security_id": str(pos.get("security_id", "")),
                    "stock_code": pos.get("stock_code") or pos.get("futu_symbol", ""),
                    "stock_name": pos.get("stock_name", ""),
                    "market_type": pos.get("market_type_code", ""),
                    "quantity": quantity,
                    "available_quantity": quantity,  # 通常可用数量等于持仓数量
                    "cost_price": float(pos.get("cost_price", 0)),
                    "current_price": float(pos.get("price", 0)),
                    "market_value": float(pos.get("market_value", 0)),
                    "profit_loss": float(pos.get("profit", 0)),
                    "profit_loss_ratio": float(pos.get("profit_ratio", 0)),
                    "pos_rate": float(pos.get("pos_rate", 0))  # 持仓占比
                })
        else:
            # 港股/A股接口返回格式: {"code":0,"message":"成功","data":{"positions":[...],"pos_count":"1"}}
            # positions直接是持仓数组
            all_positions = positions_data.get("positions", [])
            
            for pos in all_positions:
                # 港股/A股字段映射
                # quantity: 持仓数量（可能是字符串或整数）
                # power: 可用数量
                # cost_price: 成本价
                # price: 当前价格
                # market_value: 市值
                # profit: 盈亏金额
                # profit_ratio: 盈亏比例
                # pos_rate: 持仓占比
                # stock_code: 股票代码（如 601088.SH）
                # stock_name: 股票名称
                # market_type_code: 市场类型代码
                
                quantity_str = pos.get("quantity", "0")
                quantity = int(quantity_str) if isinstance(quantity_str, str) else int(quantity_str or 0)
                
                power_str = pos.get("power", "0")
                available_quantity = int(power_str) if isinstance(power_str, str) else int(power_str or 0)
                
                positions.append({
                    "security_id": str(pos.get("security_id", "")),
                    "stock_code": pos.get("stock_code", ""),
                    "stock_name": pos.get("stock_name", ""),
                    "market_type": pos.get("market_type_code", ""),
                    "quantity": quantity,
                    "available_quantity": available_quantity,
                    "cost_price": float(pos.get("cost_price", 0)),
                    "current_price": float(pos.get("price", 0)),
                    "market_value": float(pos.get("market_value", 0)),
                    "profit_loss": float(pos.get("profit", 0)),
                    "profit_loss_ratio": float(pos.get("profit_ratio", 0)),
                    "pos_rate": float(pos.get("pos_rate", 0))  # 持仓占比
                })
        
        return {"positions": positions, "count": len(positions)}
    
    async def search_stock(self, keyword: str, market_type: str = None) -> List[StockSearchResult]:
        """
        搜索股票
        
        Args:
            keyword: 搜索关键词（股票代码或名称）
            market_type: 市场类型 (US/HK/CN)，如果不提供则默认为US
            
        Returns:
            股票搜索结果列表
        """
        # 标准化股票代码（去除后缀，如 00700.HK -> 00700）
        normalized_keyword = self._normalize_stock_code(keyword)
        
        # 根据市场类型设置不同的 supported_securities 参数
        if market_type == "CN":
            # A股：只支持ETF
            supported_securities = '{"etf":true,"warrant":false,"short_sale":false,"option":false,"financing":false}'
        elif market_type == "HK":
            # 港股：支持ETF和窝轮
            supported_securities = '{"etf":true,"warrant":true,"short_sale":false,"option":false,"financing":false}'
        else:
            # 美股（默认）：支持ETF、融券、期权、融资
            supported_securities = '{"etf":true,"warrant":false,"short_sale":true,"option":true,"financing":true}'
        
        url = f"{FUTU_MATCH_URL}/trade/search-target-stock"
        params = {
            "key": normalized_keyword,
            "market_type": MARKET_TYPE.get(market_type, 100) if market_type else 100,
            "supported_securities": supported_securities
        }
        
        data = await self._request("GET", url, params=params)
        
        # 处理不同的响应格式
        if isinstance(data, list):
            results = data
        elif isinstance(data, dict):
            # 新接口返回格式: {"code":0,"message":"成功","data":[...]}
            if "data" in data and isinstance(data["data"], list):
                results = data["data"]
            # 旧格式: {"data":{"list":[...]}}
            elif "data" in data and isinstance(data["data"], dict):
                results = data["data"].get("list", [])
            # 直接包含list: {"list":[...]}
            elif "list" in data:
                results = data["list"]
            else:
                results = []
        else:
            results = []
        
        stocks = []
        for item in results:
            stocks.append(StockSearchResult(
                security_id=str(item.get("security_id", "")),
                stock_code=item.get("code_name", item.get("stock_code", "")),
                stock_name=item.get("sc_name", item.get("stock_name", "")),
                market_type=item.get("market_type", ""),
                security_type=str(item.get("instrument_type", item.get("security_type", "")))
            ))
        return stocks
    
    async def get_stock_quote(self, security_ids: List[str], market_type: str = "US") -> List[Dict[str, Any]]:
        """获取股票行情"""
        import json
        url = f"{FUTU_BASE_URL}/paper-trade/common-api"
        params = {
            "_m": "batchGetSecurityQuote",
            "security_ids": json.dumps(security_ids),  # 使用JSON格式而不是Python的str()
            "market_type": MARKET_TYPE.get(market_type, 100),
            "pre_after_price_switch": "true"
        }
        data = await self._request("GET", url, params=params)
        # 尝试不同的字段名
        quotes_data = data.get("data", {}).get("leg_quote", [])
        if not quotes_data:
            quotes_data = data.get("data", {}).get("quote_list", [])
        
        quotes = []
        for quote in quotes_data:
            # 处理change_ratio字段（可能是"-0.38%"格式）
            change_ratio_str = quote.get("change_ratio", "0")
            if isinstance(change_ratio_str, str) and '%' in change_ratio_str:
                change_ratio = float(change_ratio_str.replace('%', ''))
            else:
                change_ratio = float(change_ratio_str) if change_ratio_str else 0
            
            # 处理change字段（可能是"-1.030"格式）
            change_str = quote.get("change", "0")
            if isinstance(change_str, str):
                change = float(change_str) if change_str else 0
            else:
                change = float(change_str)
            
            # 构建返回数据，只包含有值的字段
            quote_dict = {
                "security_id": str(quote.get("security_id", "")),
                "stock_code": quote.get("display_code", quote.get("stock_code", "")),
                "stock_name": quote.get("display_name", quote.get("security_name", quote.get("stock_name", ""))),
                "current_price": float(quote.get("price", quote.get("current_price", 0))),
                "change": change,
                "change_ratio": change_ratio
            }
            
            # 只添加非零的可选字段
            open_price = float(quote.get("open_price", 0))
            if open_price > 0:
                quote_dict["open_price"] = open_price
                
            high_price = float(quote.get("high_price", 0))
            if high_price > 0:
                quote_dict["high_price"] = high_price
                
            low_price = float(quote.get("low_price", 0))
            if low_price > 0:
                quote_dict["low_price"] = low_price
                
            volume = int(quote.get("volume", 0))
            if volume > 0:
                quote_dict["volume"] = volume
            
            quotes.append(quote_dict)
        return quotes
    
    async def place_order(self, trade_request: TradeRequest) -> TradeResponse:
        """
        下单交易（支持所有市场，自动选择正确的接口）
        
        Args:
            trade_request: 交易请求对象
            
        Returns:
            TradeResponse: 交易响应对象
        """
        # 1. 自动判断市场类型
        market_type = self._detect_market_type(trade_request.stock_code)
        
        # 2. 根据市场类型获取对应的账户ID（从环境变量配置）
        account_id = self.get_account_id_by_market(market_type)
        
        if not account_id:
            return TradeResponse(
                success=False,
                message=f"未找到{market_type}市场的模拟账户，请先在富途牛牛中开通该市场的模拟交易账户"
            )
        
        # 3. 搜索股票获取security_id（使用标准化的股票代码）
        normalized_code = self._normalize_stock_code(trade_request.stock_code)
        stocks = await self.search_stock(
            normalized_code, 
            market_type
        )
        
        if not stocks:
            return TradeResponse(
                success=False,
                message=f"未找到股票: {trade_request.stock_code}"
            )
        
        stock = stocks[0]
        security_id = stock.security_id
        
        # 4. 获取当前价格（如果是市价单）
        order_type = trade_request.order_type.value if hasattr(trade_request.order_type, 'value') else trade_request.order_type
        if order_type == "MARKET":
            quotes = await self.get_stock_quote(
                [security_id], 
                market_type
            )
            if quotes:
                # quotes 是字典列表，不是对象
                trade_request.price = quotes[0]["current_price"]
        
        if not trade_request.price:
            return TradeResponse(
                success=False,
                message="价格不能为空"
            )
        
        # 5. 根据市场类型选择接口和构建订单数据
        side = trade_request.side.value if hasattr(trade_request.side, 'value') else trade_request.side
        
        # 所有市场统一使用：B=买入, A=卖出
        side_code = ORDER_SIDE[side]
        
        url = f"{FUTU_BASE_URL}/paper-trade/common-api"
        
        if market_type == "US":
            # 美股使用 inputIntegratedOrder 接口
            params = {"_m": "inputIntegratedOrder"}
            
            # 订单类型：1=限价单, 2=碎股单, 3=市价单
            order_type_code = ORDER_TYPE[order_type]
            
            # 时段类型：REGULAR=仅盘中（市价单只能盘中）, EXTENDED=全时段（限价单可以全时段）
            period_type_code = PERIOD_TYPE["REGULAR"] if order_type == "MARKET" else PERIOD_TYPE["EXTENDED"]
            
            order_data = {
                "account_id": str(account_id),
                "market_type": 100,
                "price": str(trade_request.price),
                "side": side_code,
                "quantity": trade_request.quantity,
                "order_type": order_type_code,
                "security_id": str(security_id),
                "period_type": period_type_code
            }
        else:
            # A股/港股使用 inputOrder 接口
            params = {"_m": "inputOrder"}
            
            market_type_code = MARKET_TYPE.get(market_type, 3)
            
            order_data = {
                "account_id": str(account_id),
                "security_id": str(security_id),
                "market_type": market_type_code,
                "side": side_code,
                "order_type": ORDER_TYPE[order_type],
                "price": str(trade_request.price),
                "quantity": trade_request.quantity,
                "security_type": 1  # 默认为股票类型
            }
        
        # 6. 提交订单
        try:
            data = await self._request("POST", url, params=params, json=order_data)
            
            if data.get("code") == 0:
                return TradeResponse(
                    success=True,
                    message="订单已提交",
                    order_id=str(data.get("data", {}).get("order_id", "")),
                    data={
                        "stock_code": trade_request.stock_code,
                        "stock_name": stock.stock_name,
                        "side": side,
                        "price": trade_request.price,
                        "quantity": trade_request.quantity,
                        "security_id": security_id,
                        "account_id": account_id,
                        "market_type": market_type
                    }
                )
            else:
                return TradeResponse(
                    success=False,
                    message=data.get("message", "下单失败"),
                    data=data
                )
        except Exception as e:
            return TradeResponse(
                success=False,
                message=f"下单异常: {str(e)}"
            )
    
    async def get_hot_stocks(self, market_type: str = "US", count: int = 10) -> List[StockSearchResult]:
        """获取热门股票"""
        url = f"{FUTU_MATCH_URL}/stock/get-hot-list"
        params = {
            "market_type": MARKET_TYPE.get(market_type, 100),
            "stock_type": 1,
            "count": count
        }
        data = await self._request("GET", url, params=params)
        stocks_data = data.get("data", {}).get("list", [])
        
        stocks = []
        for item in stocks_data:
            stocks.append(StockSearchResult(
                security_id=str(item.get("security_id", "")),
                stock_code=item.get("stock_code", ""),
                stock_name=item.get("stock_name", ""),
                market_type=market_type,
                security_type="STOCK"
            ))
        return stocks

    async def cancel_order(self, order_id: str, stock_code: str) -> TradeResponse:
        """
        撤销订单（支持所有市场，自动选择正确的接口）
        
        Args:
            order_id: 订单ID
            stock_code: 股票代码（用于自动判断市场类型）
            
        Returns:
            TradeResponse: 撤单响应对象
        """
        # 标准化股票代码并自动判断市场类型
        normalized_code = self._normalize_stock_code(stock_code)
        market_type = self._detect_market_type(normalized_code)
        
        # 根据市场类型获取账户ID
        account_id = self.get_account_id_by_market(market_type)
        if not account_id:
            return TradeResponse(
                success=False,
                message=f"未找到{market_type}市场的模拟账户"
            )
        
        # 根据市场类型选择接口
        url = f"{FUTU_BASE_URL}/paper-trade/common-api"
        
        if market_type == "US":
            # 美股使用 cancelIntegratedOrder 接口
            params = {"_m": "cancelIntegratedOrder"}
            
            cancel_data = {
                "account_id": str(account_id),
                "market_type": 100,
                "order_id": str(order_id)
            }
        else:
            # A股/港股使用 cancelOrder 接口
            params = {"_m": "cancelOrder"}
            
            cancel_data = {
                "account_id": str(account_id),
                "order_id": str(order_id)
            }
        
        try:
            data = await self._request("POST", url, params=params, json=cancel_data)
            
            if data.get("code") == 0:
                return TradeResponse(
                    success=True,
                    message="撤单成功",
                    order_id=order_id,
                    data={
                        "account_id": account_id,
                        "order_id": order_id,
                        "market_type": market_type
                    }
                )
            else:
                return TradeResponse(
                    success=False,
                    message=data.get("message", "撤单失败"),
                    data=data
                )
        except Exception as e:
            return TradeResponse(
                success=False,
                message=f"撤单异常: {str(e)}"
            )
    
    async def get_order_history(
        self, 
        account_id: str = None, 
        market_type: str = None,
        filter_status: int = 0,
        side: str = "",
        start_time: int = None,
        end_time: int = None
    ) -> Dict[str, Any]:
        """
        获取订单历史
        
        Args:
            account_id: 账户ID（可选，如果不提供则根据market_type自动匹配）
            market_type: 市场类型（如果不提供account_id则必须提供，US/HK/CN）
            filter_status: 过滤状态 (0=全部, 1=已成交, 2=等待成交, 3=已撤单)
            side: 方向 (空=全部, B=买入, S=卖出)
            start_time: 开始时间 (Unix时间戳)
            end_time: 结束时间 (Unix时间戳)
            
        Returns:
            订单历史数据
        """
        # 如果没有提供account_id，根据market_type自动获取
        if not account_id:
            if not market_type:
                raise ValueError("必须提供account_id或market_type参数")
            account_id = self.get_account_id_by_market(market_type)
            if not account_id:
                raise ValueError(f"未找到{market_type}市场的模拟账户")
        
        # 如果没有提供时间范围，使用当天
        if not start_time or not end_time:
            import time
            from datetime import datetime, timedelta
            
            # 获取当天0点的时间戳
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            start_time = int(today.timestamp())
            end_time = int((today + timedelta(days=1)).timestamp()) - 1
        
        url = f"{FUTU_BASE_URL}/paper-trade/common-api"
        params = {
            "_m": "getTradeHistoryOrders",
            "account_id": account_id,
            "last_id": 0,
            "filter_status": filter_status,
            "side": side,
            "start_time": start_time,
            "end_time": end_time
        }
        
        data = await self._request("GET", url, params=params)
        return data.get("data", {})

    async def get_hot_news(self, lang: str = "zh-cn") -> List[Dict[str, Any]]:
        """
        获取热门新闻
        
        Args:
            lang: 语言 (zh-cn/zh-hk/en-us)
            
        Returns:
            新闻列表
        """
        url = f"{FUTU_BASE_URL}/search-stock/hot-news"
        params = {
            "lang": lang
        }
        
        data = await self._request("GET", url, params=params)
        
        # 处理响应格式: {"code":0,"message":"成功","data":[...]}
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # 直接返回data数组
            if "data" in data and isinstance(data["data"], list):
                return data["data"]
            # 或者data.list格式
            return data.get("data", {}).get("list", [])
        return []
    
    async def get_hot_stocks_list(self, market_type: str = "US", stock_type: int = 1, count: int = 10) -> List[Dict[str, Any]]:
        """
        获取热门股票列表
        
        Args:
            market_type: 市场类型 (US/HK/CN)
            stock_type: 股票类型 (1=股票)
            count: 返回数量
            
        Returns:
            热门股票列表
        """
        url = f"{FUTU_MATCH_URL}/stock/get-hot-list"
        params = {
            "market_type": MARKET_TYPE.get(market_type, 100),
            "stock_type": stock_type,
            "count": count
        }
        
        data = await self._request("GET", url, params=params)
        
        # 处理响应格式: {"code":0,"message":"成功","data":[...]}
        if isinstance(data, dict):
            # 检查是否有错误
            if data.get("code") != 0:
                return []
            # 直接返回data数组
            if "data" in data and isinstance(data["data"], list):
                return data["data"]
            # 或者data.list格式
            return data.get("data", {}).get("list", [])
        return []
    
    def _convert_timestamp_to_local_time(self, timestamp: int, market_type: str = "US") -> str:
        """
        将Unix时间戳转换为市场本地时间字符串
        
        Args:
            timestamp: Unix时间戳（秒）
            market_type: 市场类型 (US/HK/CN)
            
        Returns:
            本地时间字符串，格式：YYYY-MM-DD HH:MM:SS (时区名称)
        """
        from datetime import datetime
        
        try:
            # 优先使用 zoneinfo (Python 3.9+)
            from zoneinfo import ZoneInfo
            
            # 创建UTC时间
            utc_time = datetime.fromtimestamp(timestamp, tz=ZoneInfo("UTC"))
            
            # 根据市场类型设置时区
            if market_type == "US":
                # 美国东部时间 (自动处理EST/EDT夏令时)
                local_time = utc_time.astimezone(ZoneInfo("America/New_York"))
                # 根据是否夏令时显示不同的时区名称
                tz_name = local_time.strftime("%Z")  # 自动显示EST或EDT
            elif market_type == "HK":
                # 香港时间
                local_time = utc_time.astimezone(ZoneInfo("Asia/Hong_Kong"))
                tz_name = "HKT"
            elif market_type == "CN":
                # 中国标准时间
                local_time = utc_time.astimezone(ZoneInfo("Asia/Shanghai"))
                tz_name = "CST"
            else:
                # 默认使用UTC+8
                local_time = utc_time.astimezone(ZoneInfo("Asia/Shanghai"))
                tz_name = "UTC+8"
                
        except ImportError:
            # 如果 zoneinfo 不可用，尝试使用 pytz
            try:
                import pytz
                
                # 创建UTC时间
                utc_time = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
                
                # 根据市场类型设置时区
                if market_type == "US":
                    # 美国东部时间 (自动处理EST/EDT夏令时)
                    eastern = pytz.timezone('America/New_York')
                    local_time = utc_time.astimezone(eastern)
                    tz_name = local_time.strftime("%Z")  # 自动显示EST或EDT
                elif market_type == "HK":
                    # 香港时间
                    hk_tz = pytz.timezone('Asia/Hong_Kong')
                    local_time = utc_time.astimezone(hk_tz)
                    tz_name = "HKT"
                elif market_type == "CN":
                    # 中国标准时间
                    cn_tz = pytz.timezone('Asia/Shanghai')
                    local_time = utc_time.astimezone(cn_tz)
                    tz_name = "CST"
                else:
                    # 默认使用UTC+8
                    cn_tz = pytz.timezone('Asia/Shanghai')
                    local_time = utc_time.astimezone(cn_tz)
                    tz_name = "UTC+8"
                    
            except ImportError:
                # 如果都不可用，使用简单的固定偏移（不推荐，但作为后备方案）
                from datetime import timezone, timedelta
                
                utc_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                
                if market_type == "US":
                    # 使用固定的UTC-5 (EST)，不处理夏令时
                    local_tz = timezone(timedelta(hours=-5))
                    tz_name = "EST"
                elif market_type in ["HK", "CN"]:
                    local_tz = timezone(timedelta(hours=8))
                    tz_name = "HKT" if market_type == "HK" else "CST"
                else:
                    local_tz = timezone(timedelta(hours=8))
                    tz_name = "UTC+8"
                
                local_time = utc_time.astimezone(local_tz)
        
        # 格式化为字符串（包含时区信息）
        return f"{local_time.strftime('%Y-%m-%d %H:%M:%S')} {tz_name}"
    
    async def get_kline_data(
        self, 
        stock_id: str, 
        kline_type: int = 1,
        market_type: str = "US",
        symbol: int = None,
        security: int = 1,
        req_section: int = 1
    ) -> Dict[str, Any]:
        """
        获取K线数据（带缓存）
        
        缓存策略：
        - 日K及以上级别（daily/weekly/monthly/quarterly/yearly）使用缓存
        - 分钟级数据不缓存，每次都从API获取
        - 缓存有效期：当天，每天0点自动失效
        
        Args:
            stock_id: 股票ID (security_id)
            kline_type: K线类型
                - 1: 分时（不缓存）
                - 2: 日K（缓存）
                - 3: 周K（缓存）
                - 4: 月K（缓存）
                - 5: 年K（缓存）
                - 11: 季K（缓存）
            market_type: 市场类型 (US/HK/CN)，用于时区转换
            symbol: 符号类型（可选，会根据kline_type自动设置）
            security: 证券类型（默认1）
            req_section: 请求区段（默认1）
            
        Returns:
            K线数据（时间已转换为市场本地时间）
        """
        # 尝试从缓存获取（只缓存日K及以上级别）
        cache = get_kline_cache()
        cached_data = cache.get(stock_id, kline_type, market_type)
        if cached_data is not None:
            return cached_data
        
        # 根据K线类型自动设置symbol参数
        # 参考富途API的实际参数映射
        if symbol is None:
            symbol_mapping = {
                1: 1,   # 分时 -> symbol=1
                2: 3,   # 日K -> symbol=3
                3: 4,   # 周K -> symbol=4
                4: 5,   # 月K -> symbol=5
                5: 7,   # 年K -> symbol=7
                11: 6,  # 季K -> symbol=6
            }
            symbol = symbol_mapping.get(kline_type, 1)
        
        url = f"{FUTU_BASE_URL}/paper-trade/api-quote-kline"
        params = {
            "stockId": stock_id,
            "type": kline_type,
            "symbol": symbol,
            "security": security,
            "req_section": req_section
        }
        
        data = await self._request("GET", url, params=params)
        
        # 处理响应格式
        if isinstance(data, dict):
            kline_data = data.get("data", {})
            
            # 转换K线数据中的时间戳
            if isinstance(kline_data, dict):
                # 处理minus对象
                if "minus" in kline_data and isinstance(kline_data["minus"], dict):
                    minus_data = kline_data["minus"]
                    
                    # 处理minus.list中的时间戳
                    kline_list = minus_data.get("list", [])
                    for item in kline_list:
                        if "time" in item:
                            # 添加本地时间字段
                            item["local_time"] = self._convert_timestamp_to_local_time(item["time"], market_type)
                    
                    # 处理minus.time_section中的时间戳
                    if "time_section" in minus_data and isinstance(minus_data["time_section"], list):
                        for section in minus_data["time_section"]:
                            if "begin" in section:
                                section["begin_local_time"] = self._convert_timestamp_to_local_time(section["begin"], market_type)
                            if "end" in section:
                                section["end_local_time"] = self._convert_timestamp_to_local_time(section["end"], market_type)
                    
                    # 处理minus.server_time
                    if "server_time" in minus_data:
                        minus_data["server_local_time"] = self._convert_timestamp_to_local_time(minus_data["server_time"], market_type)
            
            # 缓存数据（只缓存日K及以上级别）
            cache.set(stock_id, kline_type, market_type, kline_data)
            
            return kline_data
        return {}

    async def get_technical_analysis(
        self,
        symbol: str,
        interval: str = "daily",
        indicator: str = "macd",
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        获取技术分析指标（返回时间序列数据）
        
        Args:
            symbol: 股票代码（自动判断市场类型）
            interval: 时间间隔
                - 分钟级: 1min, 5min, 15min, 30min, 60min
                - 日线及以上: daily, weekly, monthly, quarterly, yearly
            indicator: 要计算的指标（每次只返回一个指标）
                可选指标：close_50_sma, close_200_sma, close_10_ema, macd,
                         rsi, boll, atr, vwma
                RSI说明：返回4个周期的RSI值 - RSI(6)/RSI(12)/RSI(14)/RSI(24)
            start_date: 开始日期（可选，格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS）
            end_date: 结束日期（可选，格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS）
        
        Returns:
            包含技术指标时间序列的字典
        """
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
            return {
                "error": f"不支持的时间间隔: {interval}",
                "supported_intervals": list(interval_mapping.keys())
            }
        
        kline_type, resample_interval = interval_mapping[interval]
        
        # 记录是否需要应用默认1个月限制（周K及以下时间间隔，且未指定日期范围）
        # 周K及以下包括：weekly, daily, 60min, 30min, 15min, 5min, 1min
        short_intervals = ["weekly", "daily", "60min", "30min", "15min", "5min", "1min"]
        apply_default_range = interval in short_intervals and not start_date and not end_date
        
        # 标准化股票代码并自动判断市场类型
        normalized_symbol = self._normalize_stock_code(symbol)
        market_type = self._detect_market_type(normalized_symbol)
        
        # 搜索股票获取security_id（使用标准化的代码）
        stocks = await self.search_stock(normalized_symbol, market_type)
        if not stocks:
            return {
                "error": f"未找到股票: {symbol}",
                "symbol": symbol,
                "market_type": market_type
            }
        
        stock = stocks[0]
        security_id = stock.security_id
        
        # 获取K线数据
        kline_data = await self.get_kline_data(
            stock_id=security_id,
            kline_type=kline_type,
            market_type=market_type
        )
        
        # 提取K线列表
        # 尝试不同的数据路径
        kline_list = kline_data.get("minus", {}).get("list", [])
        
        # 如果 minus.list 为空，尝试其他路径
        if not kline_list:
            # 尝试直接从 data 获取
            if "data" in kline_data:
                kline_list = kline_data["data"].get("list", [])
            # 尝试从根级别获取
            if not kline_list and "list" in kline_data:
                kline_list = kline_data["list"]
        
        if not kline_list:
            return {
                "error": "未获取到K线数据",
                "symbol": symbol,
                "stock_name": stock.stock_name,
                "market_type": market_type,
                "interval": interval,
                "message": "可能原因：1) 该股票在指定日期范围内没有交易数据 2) 股票代码不正确 3) 市场休市",
                "upstream_response": kline_data
            }
        
        # 解析日期范围（如果提供）
        start_timestamp = None
        end_timestamp = None
        
        if start_date:
            from datetime import datetime
            try:
                # 清理日期字符串
                start_date = start_date.strip()
                
                # 只接受日期格式 YYYY-MM-DD
                if len(start_date) != 10:
                    return {
                        "error": f"日期格式错误: {start_date}，请只使用日期格式 YYYY-MM-DD（如 2025-11-01）",
                        "symbol": symbol
                    }
                
                # 根据市场类型使用对应的时区
                try:
                    from zoneinfo import ZoneInfo
                    if market_type == "US":
                        tz = ZoneInfo("America/New_York")
                    elif market_type == "HK":
                        tz = ZoneInfo("Asia/Hong_Kong")
                    elif market_type == "CN":
                        tz = ZoneInfo("Asia/Shanghai")
                    else:
                        tz = ZoneInfo("Asia/Shanghai")
                    
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=tz)
                except ImportError:
                    # 如果 zoneinfo 不可用，使用 pytz
                    import pytz
                    if market_type == "US":
                        tz = pytz.timezone("America/New_York")
                    elif market_type == "HK":
                        tz = pytz.timezone("Asia/Hong_Kong")
                    elif market_type == "CN":
                        tz = pytz.timezone("Asia/Shanghai")
                    else:
                        tz = pytz.timezone("Asia/Shanghai")
                    
                    start_dt = tz.localize(datetime.strptime(start_date, "%Y-%m-%d"))
                
                start_timestamp = int(start_dt.timestamp())
            except ValueError as e:
                return {
                    "error": f"无效的开始日期格式: {start_date}，请使用 YYYY-MM-DD",
                    "detail": str(e),
                    "symbol": symbol
                }
        
        if end_date:
            from datetime import datetime, timedelta
            try:
                # 清理日期字符串
                end_date = end_date.strip()
                
                # 只接受日期格式 YYYY-MM-DD
                if len(end_date) != 10:
                    return {
                        "error": f"日期格式错误: {end_date}，请只使用日期格式 YYYY-MM-DD（如 2025-11-01）",
                        "symbol": symbol
                    }
                
                # 根据市场类型使用对应的时区
                try:
                    from zoneinfo import ZoneInfo
                    if market_type == "US":
                        tz = ZoneInfo("America/New_York")
                    elif market_type == "HK":
                        tz = ZoneInfo("Asia/Hong_Kong")
                    elif market_type == "CN":
                        tz = ZoneInfo("Asia/Shanghai")
                    else:
                        tz = ZoneInfo("Asia/Shanghai")
                    
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=tz)
                except ImportError:
                    # 如果 zoneinfo 不可用，使用 pytz
                    import pytz
                    if market_type == "US":
                        tz = pytz.timezone("America/New_York")
                    elif market_type == "HK":
                        tz = pytz.timezone("Asia/Hong_Kong")
                    elif market_type == "CN":
                        tz = pytz.timezone("Asia/Shanghai")
                    else:
                        tz = pytz.timezone("Asia/Shanghai")
                    
                    end_dt = tz.localize(datetime.strptime(end_date, "%Y-%m-%d"))
                
                # 设置为当天的23:59:59
                end_dt = end_dt + timedelta(days=1) - timedelta(seconds=1)
                end_timestamp = int(end_dt.timestamp())
            except ValueError as e:
                return {
                    "error": f"无效的结束日期格式: {end_date}，请使用 YYYY-MM-DD",
                    "detail": str(e),
                    "symbol": symbol
                }
        
        # 转换为DataFrame
        # 注意：不要在这里过滤日期范围！需要用所有历史数据计算技术指标
        # 日期范围过滤应该在计算完指标后，只过滤返回结果
        df_data = []
        for item in kline_list:
            # 判断数据格式：日K及以上使用 k/o/c/h/l/v，分时使用 time/price/open/high/low/volume
            
            # 时间字段
            time_val = item.get("time") or item.get("k")
            
            # 收盘价
            close_price = item.get("cc_price")
            if close_price is None:
                # 尝试 c 字段（日K格式）
                close_price = item.get("c")
                if close_price is not None:
                    # 检查是否需要除以10000（如果值过大，说明是原始值）
                    close_price = float(close_price)
                    # 如果价格大于100000，很可能需要除以10000
                    if close_price > 100000:
                        close_price = close_price / 10000
                else:
                    # 尝试 price 字段（分时格式）
                    price_raw = item.get("price", 0)
                    close_price = price_raw / 10000 if price_raw else 0
            else:
                close_price = float(close_price)
            
            # 开盘价
            open_price = item.get("cc_open")
            if open_price is None:
                # 尝试 o 字段（日K格式）
                open_price = item.get("o")
                if open_price is not None:
                    # 检查是否需要除以10000（如果值过大，说明是原始值）
                    open_price = float(open_price)
                    if open_price > 100000:
                        open_price = open_price / 10000
                else:
                    # 尝试 open 字段（分时格式）
                    open_raw = item.get("open", 0)
                    open_price = open_raw / 10000 if open_raw else 0
            else:
                open_price = float(open_price)
            
            # 最高价
            high_price = item.get("cc_high")
            if high_price is None:
                # 尝试 h 字段（日K格式）
                high_price = item.get("h")
                if high_price is not None:
                    # 检查是否需要除以10000（如果值过大，说明是原始值）
                    high_price = float(high_price)
                    if high_price > 100000:
                        high_price = high_price / 10000
                else:
                    # 尝试 high 字段（分时格式）
                    high_raw = item.get("high", 0)
                    high_price = high_raw / 10000 if high_raw else 0
            else:
                high_price = float(high_price)
            
            # 最低价
            low_price = item.get("cc_low")
            if low_price is None:
                # 尝试 l 字段（日K格式）
                low_price = item.get("l")
                if low_price is not None:
                    # 检查是否需要除以10000（如果值过大，说明是原始值）
                    low_price = float(low_price)
                    if low_price > 100000:
                        low_price = low_price / 10000
                else:
                    # 尝试 low 字段（分时格式）
                    low_raw = item.get("low", 0)
                    low_price = low_raw / 10000 if low_raw else 0
            else:
                low_price = float(low_price)
            
            # 成交量
            volume = item.get("volume") or item.get("v", 0)
            
            df_data.append({
                "time": time_val,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume
            })
        
        # 检查是否有有效数据
        if not df_data:
            return {
                "error": "指定日期范围内没有有效的K线数据",
                "symbol": symbol,
                "stock_name": stock.stock_name,
                "market_type": market_type,
                "interval": interval,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "message": "可能原因：1) 该日期范围内市场休市 2) 日期范围超出数据可用范围 3) 股票在该时间段未交易"
            }
        
        df = pd.DataFrame(df_data)
        
        # 确保所有价格列都是浮点数类型
        try:
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(int)
        except KeyError as e:
            return {
                "error": f"数据格式错误，缺少必需字段: {str(e)}",
                "symbol": symbol,
                "stock_name": stock.stock_name,
                "interval": interval,
                "available_columns": list(df.columns) if len(df) > 0 else [],
                "message": "上游API返回的数据格式不符合预期"
            }
        
        # 过滤掉无效数据（价格为0或时间为空）
        df = df[(df['close'] > 0) & (df['time'].notna())].copy()
        
        # 对于 open/high/low 为 0 的情况，使用 close 价格填充
        mask_open = df['open'] == 0
        mask_high = df['high'] == 0
        mask_low = df['low'] == 0
        
        df.loc[mask_open, 'open'] = df.loc[mask_open, 'close']
        df.loc[mask_high, 'high'] = df.loc[mask_high, 'close']
        df.loc[mask_low, 'low'] = df.loc[mask_low, 'close']
        
        if len(df) == 0:
            return {
                "error": "过滤后没有有效的K线数据",
                "symbol": symbol,
                "stock_name": stock.stock_name,
                "market_type": market_type,
                "interval": interval,
                "message": "所有数据点的价格都为0或时间戳无效"
            }
        
        # 如果是周K及以下时间间隔且未指定日期范围，设置默认返回最近1个月的结果
        # 注意：不要在这里过滤df，因为需要用所有历史数据计算技术指标
        # 只需要记录日期范围，稍后过滤返回结果
        if apply_default_range and len(df) > 0 and not start_date and not end_date:
            from datetime import datetime, timedelta
            # 获取数据中的最新时间戳
            latest_timestamp = df['time'].max()
            # 计算1个月前的时间戳（30天）
            one_month_ago_timestamp = latest_timestamp - (30 * 24 * 60 * 60)
            # 记录自动设置的日期范围（用于后续过滤返回结果）
            start_date = datetime.fromtimestamp(one_month_ago_timestamp).strftime("%Y-%m-%d")
            end_date = datetime.fromtimestamp(latest_timestamp).strftime("%Y-%m-%d")
        
        # 如果是分时数据且需要重采样
        if resample_interval:
            from technical_indicators import resample_kline_data
            df = resample_kline_data(df, resample_interval)
            
            # 检查重采样后是否有足够的数据
            if len(df) < 20:
                return {
                    "error": f"重采样后数据不足（仅{len(df)}条），无法计算技术指标",
                    "symbol": symbol,
                    "stock_name": stock.stock_name,
                    "market_type": market_type,
                    "interval": interval
                }
        
        # 计算技术指标（返回时间序列）
        from technical_indicators import calculate_single_indicator, SUPPORTED_INDICATORS
        
        # 验证指标是否支持
        if indicator not in SUPPORTED_INDICATORS:
            return {
                "error": f"不支持的指标: {indicator}",
                "supported_indicators": list(SUPPORTED_INDICATORS.keys())
            }
        
        indicator_data = calculate_single_indicator(df, indicator, market_type, self._convert_timestamp_to_local_time, interval)
        
        # 检查是否有错误
        if isinstance(indicator_data, dict) and "error" in indicator_data:
            return {
                "error": indicator_data["error"],
                "symbol": symbol,
                "stock_name": stock.stock_name,
                "market_type": market_type
            }
        
        # 如果用户指定了日期范围，只返回该范围内的指标数据
        # 但计算时使用了所有历史数据，确保MACD等指标的准确性
        if start_date or end_date:
            from datetime import datetime
            filtered_data = {}
            
            for date_str, values in indicator_data.items():
                # 解析日期字符串
                try:
                    # 尝试解析不同的日期格式
                    if len(date_str) == 10:  # YYYY-MM-DD
                        item_date = datetime.strptime(date_str, "%Y-%m-%d")
                    else:  # YYYY-MM-DD HH:MM:SS
                        item_date = datetime.strptime(date_str.split()[0], "%Y-%m-%d")
                    
                    # 检查是否在日期范围内
                    if start_date:
                        req_start = datetime.strptime(start_date, "%Y-%m-%d")
                        if item_date < req_start:
                            continue
                    
                    if end_date:
                        req_end = datetime.strptime(end_date, "%Y-%m-%d")
                        if item_date > req_end:
                            continue
                    
                    filtered_data[date_str] = values
                except:
                    # 如果日期解析失败，保留该数据
                    filtered_data[date_str] = values
            
            indicator_data = filtered_data
        
        # 获取最新价格
        latest_price = df['close'].iloc[-1]
        
        # 获取时间范围（使用过滤后的数据）
        if indicator_data:
            # 获取第一个和最后一个日期
            dates = list(indicator_data.keys())
            first_date = dates[0]
            last_date = dates[-1]
        else:
            # 如果没有数据，使用原始df的范围
            start_time = int(df['time'].iloc[0])
            end_time = int(df['time'].iloc[-1])
            first_date = self._convert_timestamp_to_local_time(start_time, market_type)
            last_date = self._convert_timestamp_to_local_time(end_time, market_type)
        
        result = {
            "meta": {
                "symbol": symbol,
                "stock_name": stock.stock_name,
                "security_id": security_id,
                "market_type": market_type,
                "interval": interval,
                "indicator": indicator,
                "indicator_name": SUPPORTED_INDICATORS[indicator][0],
                "latest_price": float(latest_price),
                "data_points": len(indicator_data),
                "start_date": first_date,
                "end_date": last_date
            },
            "data": indicator_data
        }
        
        # 如果指定了日期范围，添加到meta中
        if start_date:
            result["meta"]["requested_start_date"] = start_date
        if end_date:
            result["meta"]["requested_end_date"] = end_date
        
        return result
