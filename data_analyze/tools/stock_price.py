import numpy as np
from langchain_core.tools import tool

from tools.market_data import fetch_kline, normalize_codes

@tool
def analyze_stocks(stock_codes):
    """
    根据股票代码列表获取股票的起始价格，结束价格，区间涨跌幅，最大回撤，年化波动率
    
    Parameters:
    -----------
    stock_codes : list
        股票代码列表
    """

    codes = normalize_codes(stock_codes)
    if not codes:
        return "股票代码无效，请提供6位代码，例如 688126。"

    summaries = []
    for stock_code in codes:
        try:
            rows = fetch_kline(stock_code)
            if len(rows) < 2:
                summaries.append(f"{stock_code}: 行情数据不足。")
                continue
            closes = np.array([float(row[2]) for row in rows], dtype=float)
            returns = np.diff(closes) / closes[:-1]
            volatility = float(np.std(returns) * np.sqrt(252) * 100)
            peak = np.maximum.accumulate(closes)
            max_drawdown = float(np.max((peak - closes) / peak) * 100)
            start_price = float(closes[0])
            end_price = float(closes[-1])
            total_return = (end_price - start_price) / start_price * 100
            summaries.append(
                f"股票代码: {stock_code}\n"
                f"区间: {rows[0][0]} 至 {rows[-1][0]}（最近{len(rows)}个交易日）\n"
                f"起始价: {start_price:.2f}\n结束价: {end_price:.2f}\n"
                f"区间涨跌幅: {total_return:.2f}%\n"
                f"最大回撤: {max_drawdown:.2f}%\n"
                f"年化波动率: {volatility:.2f}%"
            )
        except Exception as error:
            summaries.append(f"{stock_code}: 查询股价失败: {error}")
    return "\n\n".join(summaries)
