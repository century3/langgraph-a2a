from langchain_core.tools import tool

from tools.market_data import fetch_financials, normalize_codes

@tool
def get_financial_report(stock_codes):
    """
    根据股票代码列表获取财报数据
    
    Parameters:
    -----------
    stock_codes : list
        股票代码列表
    
    Returns:
    --------
    dict
        包含每个股票代码对应的财报数据的字典
    """
    codes = normalize_codes(stock_codes)
    if not codes:
        return "股票代码无效，请提供6位代码，例如 688126。"

    def amount(value):
        if value in (None, ""):
            return "未知"
        return f"{float(value) / 100000000:.2f}亿元"

    def percent(value):
        if value in (None, ""):
            return "未知"
        return f"{float(value):.2f}%"

    summaries = []
    for code in codes:
        try:
            row = fetch_financials(code)
            if not row:
                summaries.append(f"{code}: 未查询到财报。")
                continue
            summaries.append(
                f"股票代码: {code}\n"
                f"名称: {row.get('SECURITY_NAME_ABBR', '未知')}\n"
                f"报告期: {str(row.get('REPORT_DATE', ''))[:10]} {row.get('REPORT_TYPE', '')}\n"
                f"营业总收入: {amount(row.get('TOTALOPERATEREVE'))}，同比 {percent(row.get('TOTALOPERATEREVETZ'))}\n"
                f"归母净利润: {amount(row.get('PARENTNETPROFIT'))}，同比 {percent(row.get('PARENTNETPROFITTZ'))}\n"
                f"加权净资产收益率: {percent(row.get('ROEJQ'))}\n"
                f"销售毛利率: {percent(row.get('XSMLL'))}\n"
                f"销售净利率: {percent(row.get('XSJLL'))}\n"
                f"资产负债率: {percent(row.get('ZCFZL'))}\n"
                f"基本每股收益: {row.get('EPSJB', '未知')}\n"
                f"每股净资产: {row.get('BPS', '未知')}"
            )
        except Exception as error:
            summaries.append(f"{code}: 查询财报失败: {error}")
    return "\n\n".join(summaries)

def load_data():
    import akshare as ak
    import pandas as pd

    df = ak.stock_yjbb_em(date="20241231")

    df.to_csv('financial_report.csv')

if __name__ == "__main__":
    print(get_financial_report.invoke({"stock_codes": ["688126"]}))


