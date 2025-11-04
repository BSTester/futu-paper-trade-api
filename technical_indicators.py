"""技术指标计算模块"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta


def resample_kline_data(df: pd.DataFrame, interval: str) -> pd.DataFrame:
    """
    将分时数据重采样为指定时间间隔
    
    Args:
        df: 包含时间戳的OHLCV数据
        interval: 时间间隔 ('1min', '3min', '5min', '15min', '30min', '1h', '2h', '4h')
    
    Returns:
        重采样后的DataFrame
    """
    # 检查必需的列
    required_cols = ['time', 'open', 'high', 'low', 'close', 'volume']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"DataFrame missing required columns: {missing_cols}")
    
    # 确保有时间索引
    if 'time' in df.columns:
        df = df.copy()  # 避免修改原始DataFrame
        df['datetime'] = pd.to_datetime(df['time'], unit='s')
        df = df.set_index('datetime')
    
    # 定义重采样规则（使用 'min' 和 'h' 代替已弃用的 'T' 和 'H'）
    resample_rules = {
        '1min': '1min',
        '3min': '3min',
        '5min': '5min',
        '15min': '15min',
        '30min': '30min',
        '1h': '1h',
        '2h': '2h',
        '4h': '4h'
    }
    
    rule = resample_rules.get(interval, '1min')
    
    # 重采样OHLCV数据
    resampled = pd.DataFrame()
    resampled['open'] = df['open'].resample(rule).first()
    resampled['high'] = df['high'].resample(rule).max()
    resampled['low'] = df['low'].resample(rule).min()
    resampled['close'] = df['close'].resample(rule).last()
    resampled['volume'] = df['volume'].resample(rule).sum()
    
    # 删除空值行（只删除所有价格都为NaN的行）
    resampled = resampled.dropna(subset=['close'])
    
    # 填充可能的NaN值（用close价格填充）
    resampled['open'] = resampled['open'].fillna(resampled['close'])
    resampled['high'] = resampled['high'].fillna(resampled['close'])
    resampled['low'] = resampled['low'].fillna(resampled['close'])
    resampled['volume'] = resampled['volume'].fillna(0)
    
    # 重新添加 time 列（从索引转换回 Unix 时间戳）
    resampled['time'] = resampled.index.astype('int64') // 10**9
    
    # 重置索引，保持 time 列
    resampled = resampled.reset_index(drop=True)
    
    return resampled


def calculate_sma(df: pd.DataFrame, period: int, column: str = 'close') -> pd.Series:
    """计算简单移动平均线 (SMA)"""
    return df[column].rolling(window=period).mean()


def calculate_ema(df: pd.DataFrame, period: int, column: str = 'close') -> pd.Series:
    """计算指数移动平均线 (EMA)"""
    return df[column].ewm(span=period, adjust=False).mean()


def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
    """
    计算MACD指标
    
    Returns:
        dict: 包含 'macd', 'signal', 'histogram' 的字典
    """
    ema_fast = calculate_ema(df, fast)
    ema_slow = calculate_ema(df, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }


def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = 'close') -> pd.Series:
    """计算相对强弱指标 (RSI)"""
    delta = df[column].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0, column: str = 'close') -> Dict[str, pd.Series]:
    """
    计算布林带
    
    Returns:
        dict: 包含 'upper', 'middle', 'lower' 的字典
    """
    middle = calculate_sma(df, period, column)
    std = df[column].rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    
    return {
        'upper': upper,
        'middle': middle,
        'lower': lower
    }


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """计算平均真实范围 (ATR)"""
    high = df['high']
    low = df['low']
    close = df['close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr


def calculate_vwma(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """计算成交量加权移动平均线 (VWMA)"""
    return (df['close'] * df['volume']).rolling(window=period).sum() / df['volume'].rolling(window=period).sum()


def calculate_mfi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """计算资金流量指数 (MFI)"""
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    money_flow = typical_price * df['volume']
    
    positive_flow = money_flow.where(typical_price > typical_price.shift(), 0).rolling(window=period).sum()
    negative_flow = money_flow.where(typical_price < typical_price.shift(), 0).rolling(window=period).sum()
    
    mfi = 100 - (100 / (1 + positive_flow / negative_flow))
    return mfi


# 支持的技术指标配置
SUPPORTED_INDICATORS = {
    "close_50_sma": ("50 SMA", "close"),
    "close_200_sma": ("200 SMA", "close"),
    "close_10_ema": ("10 EMA", "close"),
    "macd": ("MACD", "close"),
    "macds": ("MACD Signal", "close"),
    "macdh": ("MACD Histogram", "close"),
    "rsi": ("RSI", "close"),
    "boll": ("Bollinger Middle", "close"),
    "boll_ub": ("Bollinger Upper Band", "close"),
    "boll_lb": ("Bollinger Lower Band", "close"),
    "atr": ("ATR", None),
    "vwma": ("VWMA", "close")
}

# 指标描述
INDICATOR_DESCRIPTIONS = {
    "close_50_sma": "50 SMA: A medium-term trend indicator. Usage: Identify trend direction and serve as dynamic support/resistance. Tips: It lags price; combine with faster indicators for timely signals.",
    "close_200_sma": "200 SMA: A long-term trend benchmark. Usage: Confirm overall market trend and identify golden/death cross setups. Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries.",
    "close_10_ema": "10 EMA: A responsive short-term average. Usage: Capture quick shifts in momentum and potential entry points. Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals.",
    "macd": "MACD: Computes momentum via differences of EMAs. Usage: Look for crossovers and divergence as signals of trend changes. Tips: Confirm with other indicators in low-volatility or sideways markets.",
    "macds": "MACD Signal: An EMA smoothing of the MACD line. Usage: Use crossovers with the MACD line to trigger trades. Tips: Should be part of a broader strategy to avoid false positives.",
    "macdh": "MACD Histogram: Shows the gap between the MACD line and its signal. Usage: Visualize momentum strength and spot divergence early. Tips: Can be volatile; complement with additional filters in fast-moving markets.",
    "rsi": "RSI: Measures momentum to flag overbought/oversold conditions. Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis.",
    "boll": "Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. Usage: Acts as a dynamic benchmark for price movement. Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals.",
    "boll_ub": "Bollinger Upper Band: Typically 2 standard deviations above the middle line. Usage: Signals potential overbought conditions and breakout zones. Tips: Confirm signals with other tools; prices may ride the band in strong trends.",
    "boll_lb": "Bollinger Lower Band: Typically 2 standard deviations below the middle line. Usage: Indicates potential oversold conditions. Tips: Use additional analysis to avoid false reversal signals.",
    "atr": "ATR: Averages true range to measure volatility. Usage: Set stop-loss levels and adjust position sizes based on current market volatility. Tips: It's a reactive measure, so use it as part of a broader risk management strategy.",
    "vwma": "VWMA: A moving average weighted by volume. Usage: Confirm trends by integrating price action with volume data. Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses."
}

# 指标计算函数映射
INDICATOR_CALC_FUNCS = {
    "close_50_sma": lambda df: calculate_sma(df, 50),
    "close_200_sma": lambda df: calculate_sma(df, 200),
    "close_10_ema": lambda df: calculate_ema(df, 10),
    "macd": lambda df: calculate_macd(df)['macd'],
    "macds": lambda df: calculate_macd(df)['signal'],
    "macdh": lambda df: calculate_macd(df)['histogram'],
    "rsi": lambda df: calculate_rsi(df, 14),
    "boll": lambda df: calculate_bollinger_bands(df)['middle'],
    "boll_ub": lambda df: calculate_bollinger_bands(df)['upper'],
    "boll_lb": lambda df: calculate_bollinger_bands(df)['lower'],
    "atr": lambda df: calculate_atr(df, 14),
    "vwma": lambda df: calculate_vwma(df, 20)
}


def format_timestamp(timestamp: int, date_only: bool = False) -> str:
    """
    将Unix时间戳转换为易读的日期时间格式
    
    Args:
        timestamp: Unix时间戳（秒）
        date_only: 是否只返回日期（不包含时间）
        
    Returns:
        格式化的日期时间字符串
        - date_only=True: YYYY-MM-DD
        - date_only=False: YYYY-MM-DD HH:MM:SS
    """
    dt = datetime.fromtimestamp(timestamp)
    if date_only:
        return dt.strftime('%Y-%m-%d')
    else:
        return dt.strftime('%Y-%m-%d %H:%M:%S')


def calculate_single_indicator(df: pd.DataFrame, indicator: str, market_type: str, time_converter, interval: str = "daily") -> Dict[str, Any]:
    """
    计算单个技术指标的时间序列数据
    
    Args:
        df: 包含OHLCV数据的DataFrame（必须有time列）
        indicator: 要计算的指标
        market_type: 市场类型（用于时间转换）
        time_converter: 时间转换函数
        interval: 时间间隔（用于决定日期格式）
        
    Returns:
        以日期为键的指标数据字典
    """
    # 确保有时间列
    if 'time' not in df.columns:
        return {"error": "DataFrame must have 'time' column"}
    
    if indicator not in SUPPORTED_INDICATORS:
        return {"error": f"Unsupported indicator: {indicator}"}
    
    # 检查必需的列（根据指标类型）
    required_cols = ['time', 'close']
    if indicator in ['atr', 'boll', 'boll_ub', 'boll_lb']:
        required_cols.extend(['open', 'high', 'low'])
    if indicator in ['vwma']:
        required_cols.extend(['volume'])
    
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return {"error": f"DataFrame missing required columns: {missing_cols}"}
    
    # 判断是否只显示日期（日K及以上）
    date_only_intervals = ["daily", "weekly", "monthly", "quarterly", "yearly"]
    use_date_only = interval in date_only_intervals
    
    try:
        # 计算指标
        calc_func = INDICATOR_CALC_FUNCS[indicator]
        
        # 特殊处理 MACD（返回三个值）
        # macds 和 macdh 也映射到 macd
        if indicator in ["macd", "macds", "macdh"]:
            macd_data = calculate_macd(df)
            results = {}
            
            for i in range(len(df)):
                time_val = df.iloc[i]['time']
                if pd.isna(time_val):
                    continue
                
                timestamp = int(time_val)
                # 使用当地时间作为键，根据间隔决定格式
                if use_date_only:
                    # 日K及以上只显示日期
                    date_str = format_timestamp(timestamp, date_only=True)
                else:
                    # 分钟级显示完整时间
                    date_str = time_converter(timestamp, market_type)
                
                macd_val = macd_data['macd'].iloc[i]
                signal_val = macd_data['signal'].iloc[i]
                hist_val = macd_data['histogram'].iloc[i]
                
                # 只添加有效数据
                if not pd.isna(macd_val) and not pd.isna(signal_val) and not pd.isna(hist_val):
                    results[date_str] = {
                        "MACD": f"{float(macd_val):.4f}",
                        "MACD_Signal": f"{float(signal_val):.4f}",
                        "MACD_Hist": f"{float(hist_val):.4f}"
                    }
            
            return results
        
        # 特殊处理布林带（返回三个值）
        # boll_ub 和 boll_lb 也映射到 boll
        elif indicator in ["boll", "boll_ub", "boll_lb"]:
            boll_data = calculate_bollinger_bands(df)
            results = {}
            
            for i in range(len(df)):
                time_val = df.iloc[i]['time']
                if pd.isna(time_val):
                    continue
                
                timestamp = int(time_val)
                if use_date_only:
                    date_str = format_timestamp(timestamp, date_only=True)
                else:
                    date_str = time_converter(timestamp, market_type)
                
                upper_val = boll_data['upper'].iloc[i]
                middle_val = boll_data['middle'].iloc[i]
                lower_val = boll_data['lower'].iloc[i]
                
                if not pd.isna(upper_val) and not pd.isna(middle_val) and not pd.isna(lower_val):
                    results[date_str] = {
                        "Boll_Upper": f"{float(upper_val):.4f}",
                        "Boll_Middle": f"{float(middle_val):.4f}",
                        "Boll_Lower": f"{float(lower_val):.4f}"
                    }
            
            return results
        
        # 其他单值指标
        else:
            values = calc_func(df)
            results = {}
            indicator_name = SUPPORTED_INDICATORS[indicator][0]
            
            for i in range(len(df)):
                time_val = df.iloc[i]['time']
                if pd.isna(time_val):
                    continue
                
                timestamp = int(time_val)
                if use_date_only:
                    date_str = format_timestamp(timestamp, date_only=True)
                else:
                    date_str = time_converter(timestamp, market_type)
                
                if i < len(values):
                    val = values.iloc[i]
                    if not pd.isna(val):
                        results[date_str] = {
                            indicator_name: f"{float(val):.4f}"
                        }
            
            return results
            
    except Exception as e:
        return {"error": str(e)}


def calculate_indicators_series(df: pd.DataFrame, indicators: list = None) -> Dict[str, Any]:
    """
    计算技术指标的时间序列数据
    
    Args:
        df: 包含OHLCV数据的DataFrame（必须有time列）
        indicators: 要计算的指标列表，如果为None则计算所有指标
        
    Returns:
        包含所有指标时间序列的字典，格式为 {日期: {指标名: 值}}
    """
    if indicators is None:
        indicators = list(SUPPORTED_INDICATORS.keys())
    
    # 确保有时间列
    if 'time' not in df.columns:
        return {"error": "DataFrame must have 'time' column"}
    
    # 计算所有指标
    indicator_values = {}
    for indicator in indicators:
        if indicator in SUPPORTED_INDICATORS:
            try:
                calc_func = INDICATOR_CALC_FUNCS[indicator]
                values = calc_func(df)
                indicator_values[indicator] = values
            except Exception as e:
                indicator_values[indicator] = None
    
    # 按日期组织数据
    results = {}
    for i in range(len(df)):
        time_val = df.iloc[i]['time']
        if pd.isna(time_val):
            continue
        
        timestamp = int(time_val)
        date_str = format_timestamp(timestamp)
        
        # 创建该日期的数据字典
        date_data = {}
        for indicator in indicators:
            if indicator in indicator_values and indicator_values[indicator] is not None:
                values = indicator_values[indicator]
                if i < len(values):
                    val = values.iloc[i]
                    if not pd.isna(val):
                        # 使用指标的显示名称
                        indicator_name = SUPPORTED_INDICATORS[indicator][0]
                        date_data[indicator_name] = f"{float(val):.4f}"
        
        # 只添加有数据的日期
        if date_data:
            results[date_str] = date_data
    
    return results
