"""配置文件"""
import os
from dotenv import load_dotenv

load_dotenv()

# 富途API配置
FUTU_COOKIE = os.getenv("FUTU_COOKIE", "")

# 账户配置（按市场类型）
ACCOUNT_ID_HK = os.getenv("ACCOUNT_ID_HK", "")  # 港股账户
ACCOUNT_ID_US = os.getenv("ACCOUNT_ID_US", "")  # 美股模拟账户
ACCOUNT_ID_CN = os.getenv("ACCOUNT_ID_CN", "")  # A股账户
ACCOUNT_ID_US_COMPETITION = os.getenv("ACCOUNT_ID_US_COMPETITION", "")  # 美股比赛账户（可选）

# API服务配置
API_HOST = os.getenv("API_HOST", "0.0.0.0")
# Railway 会提供 PORT 环境变量，本地开发使用 API_PORT 或默认 9000
API_PORT = int(os.getenv("PORT", os.getenv("API_PORT", "9000")))

# API Key（用于接口鉴权）
API_KEY = os.getenv("API_KEY", "")

# 富途API端点
FUTU_BASE_URL = "https://www.futunn.com"
FUTU_MATCH_URL = "https://m-match.futunn.com"

# 市场类型映射（用于API请求）
MARKET_TYPE = {
    "US": 100,  # 美股
    "HK": 1,    # 港股
    "CN": 3,    # A股（沪深）
    "JP": 4,    # 日股
}

# 账户属性市场映射（用于账户列表）
ATTRIBUTE_MARKET = {
    1: "HK",  # 港股
    2: "US",  # 美股
    3: "CN",  # A股（沪深）
    4: "JP",  # 日股
}

# 账户映射配置（从环境变量构建）
def get_account_mapping():
    """
    从环境变量构建账户映射
    
    规则：
    1. 如果配置了美股比赛账户，则美股使用比赛账户
    2. 否则美股使用模拟账户
    3. 其他市场直接使用配置的账户
    """
    mapping = {}
    
    # 港股账户
    if ACCOUNT_ID_HK:
        mapping["HK"] = ACCOUNT_ID_HK
    
    # 美股账户（优先使用比赛账户）
    if ACCOUNT_ID_US_COMPETITION:
        mapping["US"] = ACCOUNT_ID_US_COMPETITION
    elif ACCOUNT_ID_US:
        mapping["US"] = ACCOUNT_ID_US
    
    # A股账户
    if ACCOUNT_ID_CN:
        mapping["CN"] = ACCOUNT_ID_CN
    
    return mapping

# 获取账户映射
ACCOUNT_MAPPING = get_account_mapping()

# 订单方向
ORDER_SIDE = {
    "BUY": "B",   # 买入
    "SELL": "A",  # 卖出（所有市场统一使用A）
}

# 订单类型（所有市场通用）
ORDER_TYPE = {
    "LIMIT": 1,      # 限价单
    "ODD_LOT": 2,    # 碎股单（所有市场统一定义）
    "MARKET": 3,     # 市价单（仅美股支持）
}

# 交易时段类型（所有市场通用）
PERIOD_TYPE = {
    "REGULAR": 1,    # 仅盘中交易（市价单只能盘中）
    "EXTENDED": 2,   # 全时段交易（盘前盘后+盘中，限价单可用）
}

# 证券类型
SECURITY_TYPE = {
    "STOCK": 1,      # 股票
    "ETF": 2,        # ETF
    "OPTION": 3,     # 期权
}
