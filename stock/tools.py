from langchain_core.tools import tool
import re
import requests
from typing import Literal
from pydantic import BaseModel
from llm import DeepSeek

class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str

def _market_symbol(code: str) -> str:
    if code.startswith(("6", "9")):
        return f"sh{code}"
    if code.startswith(("4", "8")):
        return f"bj{code}"
    return f"sz{code}"


def _quote_from_tencent(code: str) -> str:
    session = requests.Session()
    session.trust_env = False
    response = session.get(
        f"https://qt.gtimg.cn/q={_market_symbol(code)}",
        timeout=10,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()
    matched = re.search(r'="([^"]*)"', response.content.decode("gbk", errors="replace"))
    fields = matched.group(1).split("~") if matched else []
    if len(fields) < 35 or fields[2] != code:
        return f"未查询到股票 {code} 的行情。"
    return (
        f"股票代码: {fields[2]}\n"
        f"名称: {fields[1]}\n"
        f"最新价: {fields[3]}\n"
        f"昨收: {fields[4]}\n"
        f"今开: {fields[5]}\n"
        f"最高: {fields[33]}\n"
        f"最低: {fields[34]}\n"
        f"涨跌额: {fields[31]}\n"
        f"涨跌幅: {fields[32]}%"
    )


@tool
def get_stock_info(code: str) -> str:
    """可以根据传入的股票代码获取股票信息
    Args:
        code: 股票代码
    """
    matched = re.search(r"\d{6}", code or "")
    if not matched:
        return "股票代码无效，请提供6位代码，例如 688126。"
    stock_code = matched.group(0)
    try:
        return _quote_from_tencent(stock_code)
    except Exception as error:
        return f"查询股票 {stock_code} 失败: {error}"

tools = [get_stock_info, ResponseFormat]
llm = DeepSeek()
llm_with_tools = llm.bind_tools(tools)
